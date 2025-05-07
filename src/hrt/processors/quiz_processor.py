"""QuizProcessor class to process the quiz based on the quiz source"""
import os
from typing import TYPE_CHECKING, Dict, List, Optional

from hrt.common import utils
from hrt.common.enums import QuestionDisplayMode, QuizAnswerDisplay, QuizSource
from hrt.common.question_bank import IQuestionBank
from hrt.common.question_metric import QuestionMetric
from hrt.common.quiz import IQuiz, QuizFactory
from hrt.common.utils import get_header

if TYPE_CHECKING:
    from hrt.common.question import Question  # pragma: no cover


class QuizProcessor:
    """QuizProcessor class to process the quiz based on the quiz source"""

    def __init__(
        self,
        question_bank: IQuestionBank,
        number_of_questions: int,
        display_mode: QuestionDisplayMode,
        answer_display: QuizAnswerDisplay,
        quiz_source: QuizSource,
        quiz_config: Dict,
        print_config: Dict,
        metrics_config: Dict,
    ):
        self._question_bank = question_bank
        self._number_of_questions = number_of_questions
        self._display_mode = display_mode
        self._answer_display = answer_display
        self._quiz_source = quiz_source
        self._quiz_config = quiz_config
        self._print_config = print_config
        self._metrics_config = metrics_config
        self._quiz: Optional[IQuiz] = None
        self._initialize_quiz()

    def _initialize_quiz(self) -> None:
        excluded_questions: List[str] = []
        included_questions: List[str] = []
        include_marked = False
        if self._quiz_source == QuizSource.MARKED:
            include_marked = True
        elif self._quiz_source == QuizSource.NEW:
            excluded = self._get_metric_questions()
            excluded_questions = [q.question_number for q in excluded]
        elif self._quiz_source == QuizSource.SKIPPED_QUESTIONS:
            excluded = self._get_metric_questions()
            excluded_questions = [
                q.question_number for q in excluded if q.skip_count > 0 and q.correct_attempts == 0
            ]
        elif self._quiz_source == QuizSource.EXCLUDE_CORRECT_ANSWERS:
            excluded = self._get_metric_questions()
            excluded_questions = [q.question_number for q in excluded if q.correct_attempts > 0]
        elif self._quiz_source == QuizSource.WRONG_ANSWERS:
            included = self._get_metric_questions()
            included_questions = [q.question_number for q in included if q.wrong_attempts > 0]
            include_marked = True
        elif self._quiz_source == QuizSource.OLD:
            included = self._get_metric_questions()
            included_questions = [q.question_number for q in included]
            include_marked = True
        elif self._quiz_source == QuizSource.ALL:
            pass
        else:
            raise ValueError(f"Invalid quiz source: {self._quiz_source}")

        questions = self._question_bank.get_random_questions(
            self._number_of_questions, include_marked, included_questions, excluded_questions
        )
        if not questions:
            print("No questions found for the quiz.")
            return
        self._quiz = QuizFactory.get_quiz(
            self._number_of_questions,
            questions,
            self._question_bank.exam_type,
            self._display_mode,
            self._answer_display,
            self._quiz_config,
        )

    def process(self) -> None:
        """Process the quiz"""
        if not self._quiz:
            print("Quiz not initialized. Exiting...")
            return
        self._quiz.pre_process()
        self._quiz.start()
        self._quiz.post_process()
        self._display_answers()
        self._save_marked_questions()
        self._save_metrics()

    def _display_answers(self) -> None:
        if self._answer_display == QuizAnswerDisplay.IN_THE_END:
            print(get_header(f"\nAnswer display: {self._answer_display.id} for wrong answers"))
            for count, q in enumerate(self._quiz.get_questions(), start=1):
                if q.metric.wrong_attempts > 0:
                    print(f"[{count}] {q.question_number} ({q.answer_index + 1}) {q.answer}")

    def _save_marked_questions(self) -> None:
        marked_questions_file = self._question_bank.get_marked_questions_filepath()
        if not marked_questions_file:
            raise ValueError("Marked questions file path not found")

        marked_questions_dir = os.path.dirname(marked_questions_file)
        os.makedirs(marked_questions_dir, exist_ok=True)

        with open(marked_questions_file, "w", encoding="utf-8") as f:
            mqs: List["Question"] = self._quiz.get_marked_questions()
            question_numbers = [q.question_number for q in mqs]
            questions = self._question_bank.get_all_marked_questions()
            for q in questions:
                if q.question_number not in question_numbers:
                    question_numbers.append(q.question_number)
                    mqs.append(q)

            question_numbers.sort()
            for q in question_numbers:
                f.write(f"{q}\n")

    def _get_metrics_file_path(self) -> str:
        et = self._question_bank.exam_type
        country = et.country
        exam_type = et.id
        metrics_dir = self._metrics_config.get("folder")
        if not metrics_dir:
            raise ValueError("Metrics folder not found in the config file")
        metrics_dir = os.path.join(metrics_dir, country.code, exam_type)
        return os.path.join(str(metrics_dir), self._metrics_config.get("filename", "metrics.txt"))

    def _get_metric_questions(self) -> List[QuestionMetric]:
        metrics_file = self._get_metrics_file_path()
        return utils.read_metrics_from_file(metrics_file)

    def _save_metrics(self) -> None:
        metrics_file = self._get_metrics_file_path()
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

        existing_metrics = self._get_metric_questions()
        for q in self._quiz.get_questions():
            metric = q.metric
            if metric:
                existing_metric = next(
                    (m for m in existing_metrics if m.question_number == metric.question_number),
                    None,
                )
                if existing_metric:
                    existing_metric.correct_attempts += metric.correct_attempts
                    existing_metric.wrong_attempts += metric.wrong_attempts
                    existing_metric.skip_count += metric.skip_count
                else:
                    existing_metrics.append(metric)

        existing_metrics.sort(key=lambda x: str(x.question_number))

        with open(metrics_file, "w", encoding="utf-8") as f:
            for metric in existing_metrics:
                f.write(
                    f"{metric.question_number}:"
                    f"{metric.correct_attempts}:"
                    f"{metric.wrong_attempts}:"
                    f"{metric.skip_count}\n"
                )
