"""Question bank class."""

import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import (
    CountryCode,
    ExamType,
    GeneralQuestionListingType,
    MarkedQuestionListingType,
    QuestionDisplayMode,
    QuestionListingType,
    TopQuestionsListingType,
)
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_category import QuestionCategory
from hrt.common.question_metric import QuestionMetric


class IQuestionBank(ABC):
    """Base class for question banks."""

    @property
    @abstractmethod
    def country(self) -> CountryCode:
        """Country code of the question bank."""

    @property
    @abstractmethod
    def exam_type(self) -> ExamType:
        """Exam type of the question bank."""

    @property
    @abstractmethod
    def filepath(self) -> Path:
        """Filepath of the question bank."""

    @property
    @abstractmethod
    def categories_filepath(self) -> Path:
        """Filepath of the question categories."""

    @abstractmethod
    def load_questions(self) -> list[Question]:
        """Load questions from the question bank."""

    @abstractmethod
    def load_categories(self) -> list[QuestionCategory]:
        """Load categories from the question bank."""

    @abstractmethod
    def load_metrics(self) -> dict[QuestionNumber, QuestionMetric]:
        """Load metrics from the question bank."""

    @abstractmethod
    def load_marked_questions(self) -> int:
        """Load marked questions from the question bank."""

    @property
    @abstractmethod
    def questions(self) -> list[Question]:
        """Questions in the question bank."""

    @property
    @abstractmethod
    def categories(self) -> list[QuestionCategory]:
        """Categories in the question bank."""

    @abstractmethod
    def get_random_questions(
        self,
        number_of_questions: int,
        include_marked,
        included_questions,
        excluded_questions: list[str],
    ) -> list[Question]:
        """Returns a list of random questions."""

    @abstractmethod
    def get_random_quiz_questions(self, number_of_questions: int) -> list[Question]:
        """Returns a list of random questions for a quiz."""

    @abstractmethod
    def get_questions(
        self,
        criteria: QuestionListingType | TopQuestionsListingType,
        max_questions: int = 0,
    ) -> tuple[dict | list, list[str]]:
        """Returns a list of questions based on the criteria."""

    @abstractmethod
    def get_marked_questions(
        self,
        criteria: MarkedQuestionListingType,
        metrics: list[QuestionMetric],
        question_count: int = 0,
    ) -> tuple[list[Question], list[str]]:
        """Returns a list of marked questions based on the criteria."""

    @abstractmethod
    def get_all_questions(self) -> list[Question]:
        """Returns all questions in the question bank."""

    @abstractmethod
    def get_same_answer_questions(self) -> dict[str, list[Question]]:
        """Returns a dictionary of questions with the same answer."""

    @abstractmethod
    def get_same_choices_questions(self) -> list[Question]:
        """Returns a list of questions with the same choices."""

    @abstractmethod
    def get_two_or_more_same_choices_questions(self) -> list[Question]:
        """Returns a list of questions with two or more same choices."""

    @abstractmethod
    def get_qnum_answer_questions(self) -> dict[str, str]:
        """Returns a dictionary of questions with the same answer."""

    @abstractmethod
    def get_longest_question_text(self, max_questions: int = 0) -> list[Question]:
        """Returns a list of questions with the longest text."""

    @abstractmethod
    def get_longest_correct_choice(self, max_questions: int = 0) -> list[Question]:
        """Returns a list of questions with the longest correct choice."""

    @abstractmethod
    def get_marked_questions_filepath(self) -> str:
        """Returns the filepath of the marked questions."""

    @abstractmethod
    def get_all_marked_questions(self) -> list[Question]:
        """Returns all marked questions."""


def process_list_result(result: list[Question]) -> list[str]:
    """Process the result of a list of questions."""
    return [question.format() for question in result]


def process_dict_result(
    criteria: QuestionListingType | TopQuestionsListingType, result: dict
) -> list[str]:
    """Process the result of a dictionary of questions."""
    result_text = []
    match criteria:
        case GeneralQuestionListingType.SAME_ANSWER:
            for answer, questions in result.items():
                result_text.append(f"Answer: {answer}")
                result_text.extend(process_list_result(questions))
        case GeneralQuestionListingType.SAME_CHOICES:
            for choices, questions in result.items():
                result_text.append(f"Choices: {choices}")
                result_text.extend(process_list_result(questions))
        case GeneralQuestionListingType.TWO_OR_MORE_SAME_CHOICES:
            for question, similar_questions in result.items():
                # append all question numbers in same line
                qnums = ", ".join([q.question_number for q in similar_questions])
                result_text.append(f"{question.question_number}, {qnums}")
                result_text.append(question.format())
                for similar_question in similar_questions:
                    result_text.append(similar_question.format())
        case GeneralQuestionListingType.QN_ANSWER:
            for qnum, answer in result.items():
                result_text.append(f"{qnum}: {answer}")
    return result_text


class QuestionBank(IQuestionBank, ABC):
    """Question bank class."""

    def __init__(
        self,
        country: CountryCode,
        exam_type: ExamType,
        filepath: Path,
        display_mode: QuestionDisplayMode = QuestionDisplayMode.PRINT,
        categories_filepath: Optional[Path] = None,
        marked_questions_filepath: Optional[Path] = None,
        metrics_filepath: Optional[Path] = None,
    ):
        self.mappings: Optional[Dict[Any, Any]] = None
        self._country = country
        self._exam_type = exam_type
        self._filepath = filepath
        self._display_mode = display_mode
        self._categories_filepath = categories_filepath
        self._marked_questions_filepath = marked_questions_filepath
        self._metrics_filepath = metrics_filepath
        self._questions: list[Question] = []
        self._categories: list[QuestionCategory] = []
        self._metrics: dict[QuestionNumber, QuestionMetric] = {}
        self.init_question_bank()

    @property
    def country(self):
        return self._exam_type.country

    @property
    def exam_type(self):
        return self._exam_type

    @property
    def filepath(self) -> Path:
        """Filepath of the question bank."""
        if self._filepath is None:
            raise ValueError("File path is not set")
        return self._filepath

    @property
    def display_mode(self) -> QuestionDisplayMode:
        """Display mode for the question bank."""
        return self._display_mode

    @property
    def categories_filepath(self) -> Path:
        """Filepath of the question categories."""
        if self._categories_filepath is None:
            raise ValueError("Categories filepath is not set")
        return self._categories_filepath

    @property
    def metrics_filepath(self) -> Path:
        """Filepath of the question metrics."""
        if self._metrics_filepath is None:
            raise ValueError("Metrics filepath is not set")
        return self._metrics_filepath

    @property
    def marked_questions_filepath(self) -> Path:
        """Filepath of the marked questions."""
        if self._marked_questions_filepath is None:
            raise ValueError("Marked questions filepath is not set")
        return self._marked_questions_filepath

    @property
    def categories(self) -> list[QuestionCategory]:
        return self._categories

    @property
    def metrics(self) -> dict[QuestionNumber, QuestionMetric]:
        """Metrics of the question bank."""
        return self._metrics

    def init_question_bank(self):
        """Initialize the question bank."""
        logger.info("Initializing question bank")
        self._categories = self.load_categories()
        logger.info("Loaded %d categories", len(self._categories))
        self._metrics = self.load_metrics()
        logger.info("Loaded %d metrics", len(self._metrics))
        self._questions = self.load_questions()
        logger.info("Loaded %d questions", len(self._questions))
        mq_counts = self.load_marked_questions()
        logger.info("Loaded %d marked questions", mq_counts)
        self.init_criteria_mapping()

    def init_criteria_mapping(self):
        """Initialize the criteria mapping."""
        self.mappings = {
            GeneralQuestionListingType.ALL: self.get_all_questions,
            GeneralQuestionListingType.SAME_ANSWER: self.get_same_answer_questions,
            GeneralQuestionListingType.SAME_CHOICES: self.get_same_choices_questions,
            GeneralQuestionListingType.TWO_OR_MORE_SAME_CHOICES: self.get_two_or_more_same_choices_questions,  # noqa: E501, pylint: disable=C0301
            GeneralQuestionListingType.QN_ANSWER: self.get_qnum_answer_questions,
            TopQuestionsListingType.LONGEST_QUESTION_TEXT: self.get_longest_question_text,
            TopQuestionsListingType.LONGEST_CORRECT_CHOICE: self.get_longest_correct_choice,
        }

    @property
    def questions(self):
        return self._questions

    def __str__(self):
        return f"{self.country} - {self.exam_type}"

    def get_questions(
        self,
        criteria: QuestionListingType | TopQuestionsListingType,
        max_questions: int = 0,
    ) -> tuple[dict | list, list[str]]:
        if self.mappings is None:
            raise ValueError("Mappings not initialized")
        func = self.mappings.get(criteria)
        if not func:
            raise ValueError(f"Method for Criteria {criteria} not found")
        if criteria == GeneralQuestionListingType.ALL and max_questions > 0:
            result = func()[:max_questions]
        else:
            result = func()

        if criteria in [
            GeneralQuestionListingType.SAME_ANSWER,
            GeneralQuestionListingType.QN_ANSWER,
        ]:
            result_text = process_dict_result(criteria, result)
        elif criteria == GeneralQuestionListingType.SAME_CHOICES:
            dict_result = self._get_same_choices_dict()
            result_text = process_dict_result(criteria, dict_result)
        elif criteria == GeneralQuestionListingType.TWO_OR_MORE_SAME_CHOICES:
            dict_result = self._get_two_or_more_same_choices_dict()
            result_text = process_dict_result(criteria, dict_result)
        else:
            result_text = process_list_result(result)
        return result, result_text

    def get_marked_questions(
        self,
        criteria: MarkedQuestionListingType,
        metrics: list[QuestionMetric],
        question_count: int = 0,
    ) -> tuple[list[Question], list[str]]:
        if criteria == MarkedQuestionListingType.CORRECT_ANSWER:
            marked_questions = [
                metric.question_number
                for metric in metrics
                if metric.correct_attempts >= question_count
            ]
        elif criteria == MarkedQuestionListingType.WRONG_ATTEMPT:
            marked_questions = [
                metric.question_number
                for metric in metrics
                if metric.wrong_attempts >= question_count
            ]
        elif criteria == MarkedQuestionListingType.SKIPPED:
            marked_questions = [
                metric.question_number for metric in metrics if metric.skip_count >= question_count
            ]
        else:
            raise ValueError(f"Criteria {criteria} not found")

        result = [
            question
            for question in self._questions
            if question.question_number in marked_questions
        ]
        result_text = process_list_result(result)

        return result, result_text

    def get_all_questions(self) -> list[Question]:
        return self.questions

    def get_same_answer_questions(self) -> dict[str, list[Question]]:
        questions_with_same_answer: Dict[str, List[Question]] = {}
        for question in self.questions:
            if question.answer in questions_with_same_answer:
                questions_with_same_answer[question.answer].append(question)
            else:
                questions_with_same_answer[question.answer] = [question]
        return {k: v for k, v in questions_with_same_answer.items() if len(v) > 1}

    def _get_same_choices_dict(self) -> dict[tuple[Any, ...], list[Question]]:
        """Internal helper to get same choices questions as a dictionary."""
        questions_with_same_choices: Dict[Tuple[Any, ...], List[Question]] = {}
        for question in self.questions:
            choices = tuple(sorted(question.choices))
            if choices in questions_with_same_choices:
                questions_with_same_choices[choices].append(question)
            else:
                questions_with_same_choices[choices] = [question]
        return {k: v for k, v in questions_with_same_choices.items() if len(v) > 1}

    def get_same_choices_questions(self) -> list[Question]:
        dict_result = self._get_same_choices_dict()
        # Flatten the dictionary of lists into a single list
        result: List[Question] = []
        for questions in dict_result.values():
            result.extend(questions)
        return result

    def _get_two_or_more_same_choices_dict(self) -> dict[Question, list[Question]]:
        """Internal helper to get questions with two or more same choices as a dictionary."""
        questions_with_two_more_same_options: dict[Question, list[Question]] = {}
        for question in self.questions:
            choices = question.choices
            for other_question in self.questions:
                other_choices = other_question.choices
                if question != other_question:
                    common_choices = set(choices).intersection(set(other_choices))
                    if len(common_choices) >= 2:
                        if question in questions_with_two_more_same_options:
                            questions_with_two_more_same_options[question].append(other_question)
                        else:
                            questions_with_two_more_same_options[question] = [other_question]
        return {k: v for k, v in questions_with_two_more_same_options.items() if len(v) > 1}

    def get_two_or_more_same_choices_questions(self) -> list[Question]:
        """Returns a list of questions with two or more same choices."""
        dict_result = self._get_two_or_more_same_choices_dict()
        # Flatten the dictionary into a list - include both keys and values
        result: List[Question] = []
        for question, related_questions in dict_result.items():
            result.append(question)
            result.extend(related_questions)
        return result

    def get_qnum_answer_questions(self) -> dict[str, str]:
        qnum_answer_questions = {}
        for question in self.questions:
            qnum_answer_questions[question.question_number] = question.answer
        return qnum_answer_questions

    def get_longest_question_text(self, max_questions: int = 0) -> list[Question]:
        return sorted(self.questions, key=lambda x: len(x.question_text), reverse=True)[
            :max_questions
        ]

    def get_longest_correct_choice(self, max_questions: int = 1) -> list[Question]:
        return sorted(self.questions, key=lambda x: len(x.answer), reverse=True)[:max_questions]

    def load_marked_questions(self) -> int:
        marked_questions = utils.read_delim_file(
            str(self.marked_questions_filepath), delimiter="\n"
        )
        flattened_questions = [item for sublist in marked_questions for item in sublist]
        for question in self._questions:
            if question.question_number in flattened_questions:
                question.is_marked = True
        # return count of marked questions
        return len(flattened_questions)

    def get_random_questions(
        self,
        number_of_questions: int,
        include_marked: bool,
        included_questions: list[str],
        excluded_questions: list[str],
    ) -> list[Question]:
        """Returns a list of random questions.

        :param number_of_questions: Number of random questions to return.
        :param include_marked: Include marked questions in the random selection.
        :param included_questions: List of questions to include in the random selection.
        :param excluded_questions: List of questions to exclude from the random selection.
        :return: List of random questions.
        """
        if include_marked:
            questions = [question for question in self._questions if question.is_marked]
        else:
            questions = [question for question in self._questions if not question.is_marked]

        if included_questions:
            questions = [
                question
                for question in questions
                if question.question_number in included_questions
            ]

        if excluded_questions:
            questions = [
                question
                for question in questions
                if question.question_number not in excluded_questions
            ]

        if number_of_questions > len(questions):
            logger.debug(
                "Number of questions requested %d is greater than available questions %d",
                number_of_questions,
                len(questions),
            )
            number_of_questions = len(questions)

        return random.sample(questions, number_of_questions)

    def get_random_quiz_questions(self, number_of_questions: int) -> list[Question]:
        """Returns a list of random questions for a quiz.

        :param number_of_questions: Number of random questions to return.
        :return: List of random questions.
        """
        if number_of_questions > len(self._questions):
            logger.warning(
                "Number of questions requested %d is greater than available questions %d",
                number_of_questions,
                len(self._questions),
            )
            number_of_questions = len(self._questions)
        return random.sample(self._questions, number_of_questions)

    def get_marked_questions_filepath(self) -> str:
        """Returns the filepath of the marked questions."""
        return str(self._marked_questions_filepath) if self._marked_questions_filepath else ""

    def get_all_marked_questions(self) -> list[Question]:
        """Returns all marked questions in the question bank."""
        return [question for question in self._questions if question.is_marked]


class QuestionBankFactory:
    """Question bank factory class."""

    @staticmethod
    def get_question_bank(
        country: CountryCode,
        exam_type: ExamType,
        filepath: Path,
        display_mode: QuestionDisplayMode = QuestionDisplayMode.PRINT,
        categories_filepath: Path | None = None,
        marked_questions_filepath: Path | None = None,
        metrics_filepath: Path | None = None,
    ) -> IQuestionBank:
        """Returns a question bank based on the country code."""
        if country == CountryCode.CANADA:
            from hrt.question_banks.ca_question_bank import CAQuestionBank

            return CAQuestionBank(
                exam_type=exam_type,
                filepath=filepath,
                display_mode=display_mode,
                categories_filepath=categories_filepath,
                marked_questions_filepath=marked_questions_filepath,
                metrics_filepath=metrics_filepath,
            )
        raise ValueError(f"Country {country} not supported")
