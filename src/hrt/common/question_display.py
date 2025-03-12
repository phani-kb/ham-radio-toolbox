"""Question display class."""

from abc import ABC, abstractmethod
from typing import Union

from hrt.common.enums import QuestionAnswerDisplay, QuestionDisplayMode, QuizAnswerDisplay


class IQuestionDisplay(ABC):
    """Question display interface."""

    @property
    @abstractmethod
    def answer_display(self) -> Union[QuestionAnswerDisplay, QuizAnswerDisplay]:
        """Answer display option."""

    @answer_display.setter
    @abstractmethod
    def answer_display(self, value: Union[QuestionAnswerDisplay, QuizAnswerDisplay]) -> None:
        """Answer display option."""

    @property
    @abstractmethod
    def show_explanation(self) -> bool:
        """Show explanation option."""

    @show_explanation.setter
    @abstractmethod
    def show_explanation(self, value: bool) -> None:
        """Show explanation option."""

    @property
    @abstractmethod
    def show_hints(self) -> bool:
        """Show hints option."""

    @show_hints.setter
    @abstractmethod
    def show_hints(self, value: bool) -> None:
        """Show hints option."""

    @property
    @abstractmethod
    def show_references(self) -> bool:
        """Show references option."""

    @show_references.setter
    @abstractmethod
    def show_references(self, value: bool) -> None:
        """Show references option."""

    @property
    @abstractmethod
    def show_tags(self) -> bool:
        """Show tags option."""

    @show_tags.setter
    @abstractmethod
    def show_tags(self, value: bool) -> None:
        """Show tags option."""

    @property
    @abstractmethod
    def show_marked_status(self) -> bool:
        """Show marked status option."""

    @show_marked_status.setter
    @abstractmethod
    def show_marked_status(self, value: bool) -> None:
        """Show marked status option."""

    @property
    @abstractmethod
    def show_metrics(self) -> bool:
        """Show metrics option."""

    @show_metrics.setter
    @abstractmethod
    def show_metrics(self, value: bool) -> None:
        """Show metrics option."""

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the question display options."""

    @abstractmethod
    def get_default_question_display(self) -> "IQuestionDisplay":
        """Get the default question display options."""


class BaseQuestionDisplay(IQuestionDisplay, ABC):
    """Base question display options."""

    def __init__(
        self,
        answer_display: Union[QuestionAnswerDisplay, QuizAnswerDisplay, None] = None,
        show_explanation: bool = False,
        show_hints: bool = False,
        show_references: bool = False,
        show_tags: bool = False,
        show_marked_status: bool = True,
        show_metrics: bool = False,
    ):
        self._answer_display = answer_display
        self._show_explanation = show_explanation
        self._show_hints = show_hints
        self._show_references = show_references
        self._show_tags = show_tags
        self._show_marked_status = show_marked_status
        self._show_metrics = show_metrics

    @property
    def answer_display(self) -> Union[QuestionAnswerDisplay, QuizAnswerDisplay]:
        return self._answer_display

    @answer_display.setter
    def answer_display(self, value: Union[QuestionAnswerDisplay, QuizAnswerDisplay]) -> None:
        self._answer_display = value

    @property
    def show_explanation(self) -> bool:
        return self._show_explanation

    @show_explanation.setter
    def show_explanation(self, value: bool) -> None:
        self._show_explanation = value

    @property
    def show_hints(self) -> bool:
        return self._show_hints

    @show_hints.setter
    def show_hints(self, value: bool) -> None:
        self._show_hints = value

    @property
    def show_references(self) -> bool:
        return self._show_references

    @show_references.setter
    def show_references(self, value: bool) -> None:
        self._show_references = value

    @property
    def show_tags(self) -> bool:
        return self._show_tags

    @show_tags.setter
    def show_tags(self, value: bool) -> None:
        self._show_tags = value

    @property
    def show_marked_status(self) -> bool:
        return self._show_marked_status

    @show_marked_status.setter
    def show_marked_status(self, value: bool) -> None:
        self._show_marked_status = value

    @property
    def show_metrics(self) -> bool:
        return self._show_metrics

    @show_metrics.setter
    def show_metrics(self, value: bool) -> None:
        self._show_metrics = value

    def __str__(self) -> str:
        return (
            f"Answer Display: {self.answer_display}, Show Hints: {self.show_hints}, "
            f"Show References: {self.show_references}, Show Tags: {self.show_tags}, "
            f"Marked Status: {self.show_marked_status}, Show Metrics: {self.show_metrics}"
        )

    def get_default_question_display(self) -> "IQuestionDisplay":
        return self.__class__(
            answer_display=self._answer_display,
            show_explanation=self._show_explanation,
            show_hints=self._show_hints,
            show_references=self._show_references,
            show_tags=self._show_tags,
            show_marked_status=self._show_marked_status,
            show_metrics=self._show_metrics,
        )


class QuestionDisplay(BaseQuestionDisplay):
    """Question display options."""

    def __init__(
        self,
        answer_display: QuestionAnswerDisplay = QuestionAnswerDisplay.WITH_QUESTION,
        show_explanation: bool = False,
        show_hints: bool = False,
        show_references: bool = False,
        show_tags: bool = False,
        show_marked_status: bool = True,
        show_metrics: bool = False,
    ):
        super().__init__(
            answer_display,
            show_explanation,
            show_hints,
            show_references,
            show_tags,
            show_marked_status,
            show_metrics,
        )


class QuizQuestionDisplay(BaseQuestionDisplay):
    """Quiz question display options."""

    def __init__(
        self,
        answer_display: QuizAnswerDisplay = QuizAnswerDisplay.AFTER_QUESTION,
        show_explanation: bool = False,
        show_hints: bool = False,
        show_references: bool = False,
        show_tags: bool = False,
        show_marked_status: bool = True,
        show_metrics: bool = False,
    ):
        super().__init__(
            answer_display,
            show_explanation,
            show_hints,
            show_references,
            show_tags,
            show_marked_status,
            show_metrics,
        )


class QuestionDisplayModeFactory:
    """Question display mode factory."""

    @staticmethod
    def get_question_display_mode(display_mode: QuestionDisplayMode) -> IQuestionDisplay:
        """Get the question display mode."""
        display_classes = {
            QuestionDisplayMode.PRINT: QuestionDisplay,
            QuestionDisplayMode.QUIZ: QuizQuestionDisplay,
            QuestionDisplayMode.PRACTICE_EXAM: QuizQuestionDisplay,
        }
        try:
            return display_classes[display_mode]().get_default_question_display()
        except KeyError as err:
            raise ValueError("Invalid display mode") from err
