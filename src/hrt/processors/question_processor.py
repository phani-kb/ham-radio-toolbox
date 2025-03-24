"""QuestionProcessor class to process questions based on the criteria"""
from pathlib import Path
from typing import List, Union

from hrt.common import constants, utils
from hrt.common.config_reader import HRTConfig, logger
from hrt.common.enums import (
    CountryCode,
    ExamType,
    MarkedQuestionListingType,
    QuestionAnswerDisplay,
    QuestionDisplayMode,
    QuestionListingType,
    QuizAnswerDisplay,
    TopQuestionsListingType,
)
from hrt.common.question import Question
from hrt.common.question_bank import IQuestionBank, QuestionBankFactory
from hrt.common.question_display import QuestionDisplay, QuestionDisplayModeFactory


def get_answers(questions: List[Question]) -> List[str]:
    """Get the answers for the questions."""
    return [
        f"{q.question_number}: {q.answer_index + 1}. {q.answer}"
        for q in questions
        if Question.question_display.answer_display == QuestionAnswerDisplay.IN_THE_END
        or Question.question_display.answer_display == QuizAnswerDisplay.IN_THE_END
    ]


class QuestionProcessor:
    """QuestionProcessor class to process questions based on the criteria"""

    def __init__(
        self,
        config: HRTConfig,
        country: CountryCode,
        exam_type: ExamType,
        display_mode: QuestionDisplayMode = QuestionDisplayMode.PRINT,
    ):
        self.config = config
        self.country = country
        self.exam_type = exam_type
        self.display_mode = display_mode
        self._initialize_paths()
        self._initialize_question_display()
        self._qb: IQuestionBank = QuestionBankFactory.get_question_bank(
            country,
            exam_type,
            self.file_path,
            self.display_mode,
            self.categories_file_path,
            self.marked_questions_file_path,
            self.metrics_file_path,
        )

    def get_question_bank(self) -> IQuestionBank:
        """Get the question bank."""
        return self._qb

    def _initialize_paths(self) -> None:
        country_settings = self.config.get_country_settings(self.country.code)
        exam_settings = country_settings.get("question_bank").get(self.exam_type.id)
        input_settings = self.config.get_input()
        if not self.exam_type.is_supported:
            raise ValueError(f"Exam type {self.exam_type} for {self.country} is not supported")
        file = exam_settings.get("file")
        if not file:
            raise ValueError(f"Questions file not set for {self.country} and {self.exam_type}")
        folder = input_settings.get("folder")
        if not folder:
            raise ValueError("Input folder not found in the config file")
        self.file_path = Path(folder) / self.country.code / self.exam_type.id / file
        if not self.file_path.exists():
            raise FileNotFoundError(f"Questions file not found at {self.file_path}")
        categories_file = exam_settings.get("categories_file")
        self.categories_file_path = (
            Path(folder) / self.country.code / categories_file if categories_file else None
        )
        if self.categories_file_path and not self.categories_file_path.exists():
            raise FileNotFoundError(f"Categories file not found at {self.categories_file_path}")
        marked_questions_file = input_settings.get("files", {}).get(
            "marked_questions",
            constants.DEFAULT_MARKED_QUESTIONS_FILENAME,
        )
        self.marked_questions_file_path = (
            Path(folder) / self.country.code / self.exam_type.id / marked_questions_file
        )
        if not self.marked_questions_file_path.exists():
            self.marked_questions_file_path.touch()
            logger.warning(
                "Marked questions file not found. Created new file at %s",
                self.marked_questions_file_path,
            )
        self.input_folder = folder
        self.output_folder = self.config.get_output().get("folder")
        if not self.output_folder:
            raise ValueError("Output folder not found in the config file")
        # set metrics file path
        metrics_config = self.config.get("metrics")
        metrics_folder = metrics_config.get("folder", constants.DEFAULT_METRICS_FOLDER)
        metrics_file = metrics_config.get("file")
        self.metrics_file_path = (
            Path(metrics_folder) / self.country.code / self.exam_type.id / metrics_file
        )
        if not self.metrics_file_path.exists():
            self.metrics_file_path.touch()
            logger.warning(
                "Metrics file not found. Created new file at %s", self.metrics_file_path
            )

    def _initialize_question_display(self) -> None:
        question_display = QuestionDisplayModeFactory.get_question_display_mode(
            self.display_mode
        ).get_default_question_display()
        display_config = self.config.get(self.display_mode.id.lower())
        if display_config:
            for key, value in display_config.items():
                setattr(question_display, key, value)

    def _process_list_result(
        self,
        result: List[Question],
        result_text: List[str],
        criteria: Union[QuestionListingType, TopQuestionsListingType, MarkedQuestionListingType],
        save_to_file: bool,
    ) -> None:
        output = [utils.get_header(criteria.name)]
        output.extend(result_text)
        answers = get_answers(result)
        if answers:
            output.append(utils.get_header("Answers"))
            output.extend(answers)
        output.append(f"Count: {len(result)}")
        if save_to_file:
            self._save_to_file(output, criteria)
        else:
            for line in output:
                print(line)

    def _save_to_file(
        self,
        output: List[str],
        criteria: Union[QuestionListingType, TopQuestionsListingType, MarkedQuestionListingType],
    ) -> None:
        filename = criteria.get_filename()
        output_file = Path(self.country.code) / self.exam_type.id / filename
        utils.save_output(output_file, "\n".join(output), self.output_folder)
        logger.info("Questions saved to %s", criteria.get_filename())

    def list(
        self,
        criteria: Union[QuestionListingType, TopQuestionsListingType],
        answer_display: Union[QuestionAnswerDisplay, QuizAnswerDisplay],
        max_questions: int = constants.DEFAULT_TOP_QUESTIONS_COUNT,
        save_to_file: bool = True,
    ) -> None:
        """List the questions based on the criteria."""
        if answer_display:
            Question.question_display.answer_display = answer_display
        result, result_text = self._qb.get_questions(criteria, max_questions)
        self._process_list_result(result, result_text, criteria, save_to_file)

    def list_marked(
        self,
        criteria: MarkedQuestionListingType,
        answer_display: Union[QuestionAnswerDisplay, QuizAnswerDisplay],
        questions_count: int = constants.MIN_MARKED_QUESTIONS_COUNT,
        save_to_file: bool = True,
    ) -> None:
        """List marked questions based on the criteria."""
        if Question.question_display is None:
            Question.question_display = QuestionDisplay(answer_display)
        if answer_display:
            Question.question_display.answer_display = answer_display
        metrics = utils.load_question_metrics(self.metrics_file_path)
        result, result_text = self._qb.get_marked_questions(criteria, metrics, questions_count)
        self._process_list_result(result, result_text, criteria, save_to_file)
