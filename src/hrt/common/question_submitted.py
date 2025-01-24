from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_metric import QuestionMetric


class QuestionSubmitted(Question):
    def __init__(
        self,
        question_number: QuestionNumber,
        selected_choice: str | None = None,
        marked: bool = False,
    ):
        super().__init__("", [], "", question_number, None, QuestionMetric(question_number))
        self._question_number = question_number
        self._selected_choice = selected_choice
        self._marked = marked
        self._question_text = ""
        self._choices = []
        self._answer = ""
        self._category = None
        self._metric = QuestionMetric(question_number)
        self._explanation = ""
        self._references = []
        self._hints = []
        self._tags = []
        self._is_marked = False

    @property
    def question_number(self):
        return self._question_number

    @question_number.setter
    def question_number(self, value):
        self._question_number = value

    def __eq__(self, other):
        return (
            self.question_number == other.question_number
            and self.selected_choice == other.selected_choice
            and self.marked == other.marked
        )

    def __hash__(self):
        return hash(str(self.question_number) + self.selected_choice + str(self.marked))

    @property
    def selected_choice(self):
        return self._selected_choice

    @property
    def marked(self):
        return self._marked

    def __str__(self):
        return (
            f"{super().__str__()}, Selected Choice: {self.selected_choice} Marked: {self.marked}"
        )
