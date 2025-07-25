"""
This module contains the Question class which represents a question in the quiz.
The Question class has the following attributes:
- question_text: The text of the question
- choices: A list of possible answers
- answer: The correct answer
- question_number: The number of the question
- question_category: The category of the question
- question_metric: The metric associated with the question
"""

import random
from typing import TYPE_CHECKING, List, Optional

from hrt.common.constants import ANSWER_DISPLAY_PREFIX
from hrt.common.enums import QuestionAnswerDisplay
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_category import QuestionCategory
from hrt.common.question_display import IQuestionDisplay
from hrt.common.question_metric import QuestionMetric

if TYPE_CHECKING:
    from hrt.common.question_ref import QuestionRef  # pragma: no cover


class Question:
    """Question class."""

    question_display: Optional[IQuestionDisplay] = None
    SKIP_CHOICE: str = "Skip or Don't Know"

    def __init__(
        self,
        question_text: str,
        choices: List[str],
        answer: str,
        question_number: Optional[QuestionNumber] = None,
        category: Optional[QuestionCategory] = None,
        metric: Optional[QuestionMetric] = None,
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
            metric = QuestionMetric(
                question_number if question_number else QuestionNumber(str(id(self)))
            )
        self._metric = metric
        self._question_number: QuestionNumber = (
            question_number if question_number else QuestionNumber(str(id(self)))
        )
        self._explanation: str = ""
        self._references: List["QuestionRef"] = []
        self._hints: List[str] = []
        self._tags: List[str] = []
        self._is_marked: bool = False
        self._current_metric = QuestionMetric(self.question_number)

    def __str__(self) -> str:
        return f"Question: {self.question_text}, Answer: {self.answer}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Question):
            return NotImplemented
        return self.question_number == other.question_number

    def __hash__(self) -> int:
        return hash(self.question_number)

    @property
    def category(self) -> Optional[QuestionCategory]:
        """Returns the category of the question."""
        return self._category

    @category.setter
    def category(self, category: Optional[QuestionCategory]) -> None:
        self._category = category

    @property
    def is_marked(self) -> bool:
        """Returns True if the question is marked, False otherwise."""
        return self._is_marked

    @is_marked.setter
    def is_marked(self, is_marked: bool) -> None:
        self._is_marked = is_marked

    @property
    def question_number(self) -> QuestionNumber:
        """Returns the number of the question."""
        return self._question_number

    @question_number.setter
    def question_number(self, question_number: QuestionNumber) -> None:
        """Sets the number of the question."""
        self._question_number = question_number

    @property
    def question_text(self) -> str:
        """Returns the text of the question."""
        return self._question_text

    @property
    def correct_attempts(self) -> int:
        """Returns the number of correct attempts."""
        return self._current_metric.correct_attempts

    @correct_attempts.setter
    def correct_attempts(self, correct_attempts: int) -> None:
        self._current_metric.correct_attempts = correct_attempts

    @property
    def existing_metric(self) -> QuestionMetric:
        """Returns the metric associated with the question."""
        return self._metric

    @property
    def skip_count(self) -> int:
        """Returns the number of skip attempts."""
        return self._current_metric.skip_count

    @skip_count.setter
    def skip_count(self, skip_count: int) -> None:
        self._current_metric.skip_count = skip_count

    @property
    def wrong_attempts(self) -> int:
        """Returns the number of wrong attempts."""
        return self._current_metric.wrong_attempts

    @wrong_attempts.setter
    def wrong_attempts(self, wrong_attempts: int) -> None:
        self._current_metric.wrong_attempts = wrong_attempts

    @property
    def metric(self) -> QuestionMetric:
        """Returns the metric associated with the question."""
        return self._current_metric

    @metric.setter
    def metric(self, metric: QuestionMetric) -> None:
        self._metric = metric

    @property
    def choices(self) -> List[str]:
        """Returns the choices for the question."""
        return self._choices

    @property
    def quiz_choices(self) -> List[str]:
        """Returns the choices for the question in a quiz format."""
        choices = self.choices.copy()
        choices.append(self.SKIP_CHOICE)
        return choices

    @property
    def answer(self) -> str:
        """Returns the answer to the question."""
        return self._answer

    @property
    def answer_index(self) -> int:
        """Returns the index of the answer in the choices."""
        return self._answer_index

    def format(self) -> str:
        """Formats the question for display."""
        question_output = [f"{self.question_number}: {self.question_text}"]
        all_choices = self.choices
        for i, choice in enumerate(all_choices):
            if (
                self.question_display
                and self.question_display.answer_display == QuestionAnswerDisplay.WITH_QUESTION
                and choice == self.answer
            ):
                question_output.append(f"{ANSWER_DISPLAY_PREFIX}{i + 1}. {choice}")
            else:
                question_output.append(f"    {i + 1}. {choice}")
        question_output.append("")
        return "\n".join(question_output)

    def format_quiz_question(self) -> str:
        """Formats the question for display in a quiz."""
        question_output = [f"{self.question_number}: {self.question_text}"]
        all_choices = self.choices
        for i, choice in enumerate(all_choices):
            question_output.append(f"{i + 1}. {choice}")
        # Add the skip choice
        question_output.append(f"{len(all_choices) + 1}. {self.SKIP_CHOICE}")
        question_output.append("")
        return "\n".join(question_output)
