"""Question submitted class."""

from typing import TYPE_CHECKING, List, Optional

from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_metric import QuestionMetric

if TYPE_CHECKING:
    from hrt.common.question_category import QuestionCategory  # pragma: no cover


class QuestionSubmitted(Question):
    """Question submitted class."""

    def __init__(
        self,
        question_number: QuestionNumber,
        selected_choice: Optional[str] = None,
        marked: bool = False,
    ):
        super().__init__("", [], "", question_number, None, QuestionMetric(question_number))
        self._question_number = question_number
        self._selected_choice = selected_choice
        self._marked = marked
        self._question_text = ""
        self._choices: List[str] = []
        self._answer = ""
        self._category: Optional[QuestionCategory] = None
        self._metric = QuestionMetric(question_number)
        self._explanation = ""
        self._references = []
        self._hints: List[str] = []
        self._tags: List[str] = []
        self._is_marked = False

    @property
    def question_number(self) -> QuestionNumber:
        return self._question_number

    @question_number.setter
    def question_number(self, value: QuestionNumber) -> None:
        self._question_number = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuestionSubmitted):
            return NotImplemented
        return (
            self.question_number == other.question_number
            and self.selected_choice == other.selected_choice
            and self.marked == other.marked
        )

    def __hash__(self) -> int:
        return hash(str(self.question_number) + str(self.selected_choice) + str(self.marked))

    @property
    def selected_choice(self) -> Optional[str]:
        """Selected choice for the question."""
        return self._selected_choice

    @selected_choice.setter
    def selected_choice(self, value: Optional[str]) -> None:
        self._selected_choice = value

    @property
    def marked(self) -> bool:
        """Returns whether the question is marked."""
        return self._marked

    def __str__(self) -> str:
        return (
            f"{super().__str__()}, Selected Choice: {self.selected_choice} Marked: {self.marked}"
        )
