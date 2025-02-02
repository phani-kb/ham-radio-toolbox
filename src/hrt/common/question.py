import random
from typing import TYPE_CHECKING

from hrt.common.constants import ANSWER_DISPLAY_PREFIX
from hrt.common.enums import QuestionAnswerDisplay
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_category import QuestionCategory
from hrt.common.question_display import IQuestionDisplay
from hrt.common.question_metric import QuestionMetric

if TYPE_CHECKING:
    from hrt.common.question_ref import QuestionRef  # pragma: no cover


class Question:
    question_display: IQuestionDisplay = None
    SKIP_CHOICE: str = "Skip or Don't Know"

    def __init__(
        self,
        question_text: str,
        choices: list[str],
        answer: str,
        question_number: QuestionNumber = None,
        category: QuestionCategory = None,
        metric: QuestionMetric = None,
    ):
        self._question_text = question_text
        self._choices = choices
        if len(choices) > 0 and answer not in choices:
            raise ValueError("Answer is not in the choices")
        self._answer = answer
        random.shuffle(self._choices)
        self._answer_index: int = self.choices.index(self.answer) if len(self.choices) > 0 else -1
        self._category = category
        if not metric:
            metric = QuestionMetric(question_number)
        self._metric = metric
        self._question_number: QuestionNumber = question_number if question_number else id(self)
        self._explanation: str = ""
        self._references: list[QuestionRef] = []
        self._hints: list[str] = []
        self._tags: list[str] = []
        self._is_marked: bool = False
        self._current_metric = QuestionMetric(self.question_number)

    def __str__(self):
        return f"Question: {self.question_text}, Answer: {self.answer}"

    def __eq__(self, other):
        return self.question_number == other.question_number

    def __hash__(self):
        return hash(self.question_number)

    @property
    def category(self):
        return self._category

    @property
    def is_marked(self):
        return self._is_marked

    @is_marked.setter
    def is_marked(self, is_marked):
        self._is_marked = is_marked

    @property
    def question_number(self) -> QuestionNumber:
        return self._question_number

    @property
    def question_text(self):
        return self._question_text

    @property
    def correct_attempts(self):
        return self._current_metric.correct_attempts

    @correct_attempts.setter
    def correct_attempts(self, correct_attempts):
        self._current_metric.correct_attempts = correct_attempts

    @property
    def existing_metric(self):
        return self._metric

    @property
    def skip_count(self):
        return self._current_metric.skip_count

    @skip_count.setter
    def skip_count(self, skip_count):
        self._current_metric.skip_count = skip_count

    @property
    def wrong_attempts(self):
        return self._current_metric.wrong_attempts

    @wrong_attempts.setter
    def wrong_attempts(self, wrong_attempts):
        self._current_metric.wrong_attempts = wrong_attempts

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def metric(self):
        return self._current_metric

    @metric.setter
    def metric(self, metric):
        self._metric = metric

    @question_number.setter
    def question_number(self, question_number):
        self._question_number = question_number

    @property
    def choices(self):
        return self._choices

    @property
    def quiz_choices(self):
        choices = self.choices.copy()
        choices.append(self.SKIP_CHOICE)
        return choices

    @property
    def answer(self):
        return self._answer

    @property
    def answer_index(self):
        return self._answer_index

    def format(self) -> str:
        question_output = [f"{self.question_number}: {self.question_text}"]
        all_choices = self.choices
        for i, choice in enumerate(all_choices):
            if (
                self.question_display.answer_display == QuestionAnswerDisplay.WITH_QUESTION
                and choice == self.answer
            ):
                question_output.append(f"{ANSWER_DISPLAY_PREFIX}{i + 1}. {choice}")
            else:
                question_output.append(f"    {i + 1}. {choice}")
        question_output.append("")
        return "\n".join(question_output)

    def format_quiz_question(self) -> str:
        question_output = [f"{self.question_number}: {self.question_text}"]
        all_choices = self.choices
        for i, choice in enumerate(all_choices):
            question_output.append(f"{i + 1}. {choice}")
        # Add the skip choice
        question_output.append(f"{len(all_choices) + 1}. {self.SKIP_CHOICE}")
        question_output.append("")
        return "\n".join(question_output)
