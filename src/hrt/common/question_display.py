from abc import ABC, abstractmethod

from hrt.common.enums import QuestionAnswerDisplay, QuestionDisplayMode, QuizAnswerDisplay


class IQuestionDisplay(ABC):
    @property
    @abstractmethod
    def answer_display(self) -> QuestionAnswerDisplay | QuizAnswerDisplay:
        pass

    @answer_display.setter
    @abstractmethod
    def answer_display(self, value: QuestionAnswerDisplay | QuizAnswerDisplay):
        pass

    @property
    @abstractmethod
    def show_explanation(self) -> bool:
        pass

    @show_explanation.setter
    @abstractmethod
    def show_explanation(self, value: bool):
        pass

    @property
    @abstractmethod
    def show_hints(self) -> bool:
        pass

    @show_hints.setter
    @abstractmethod
    def show_hints(self, value: bool):
        pass

    @property
    @abstractmethod
    def show_references(self) -> bool:
        pass

    @show_references.setter
    @abstractmethod
    def show_references(self, value: bool):
        pass

    @property
    @abstractmethod
    def show_tags(self) -> bool:
        pass

    @show_tags.setter
    @abstractmethod
    def show_tags(self, value: bool):
        pass

    @property
    @abstractmethod
    def show_marked_status(self) -> bool:
        pass

    @show_marked_status.setter
    @abstractmethod
    def show_marked_status(self, value: bool):
        pass

    @property
    @abstractmethod
    def show_metrics(self) -> bool:
        pass

    @show_metrics.setter
    @abstractmethod
    def show_metrics(self, value: bool):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def get_default_question_display(self) -> "IQuestionDisplay":
        pass


class BaseQuestionDisplay(IQuestionDisplay, ABC):
    def __init__(
        self,
        answer_display: QuestionAnswerDisplay | QuizAnswerDisplay = None,
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
    def answer_display(self) -> QuestionAnswerDisplay | QuizAnswerDisplay:
        return self._answer_display

    @answer_display.setter
    def answer_display(self, value: QuestionAnswerDisplay | QuizAnswerDisplay):
        self._answer_display = value

    @property
    def show_explanation(self) -> bool:
        return self._show_explanation

    @show_explanation.setter
    def show_explanation(self, value: bool):
        self._show_explanation = value

    @property
    def show_hints(self) -> bool:
        return self._show_hints

    @show_hints.setter
    def show_hints(self, value: bool):
        self._show_hints = value

    @property
    def show_references(self) -> bool:
        return self._show_references

    @show_references.setter
    def show_references(self, value: bool):
        self._show_references = value

    @property
    def show_tags(self) -> bool:
        return self._show_tags

    @show_tags.setter
    def show_tags(self, value: bool):
        self._show_tags = value

    @property
    def show_marked_status(self) -> bool:
        return self._show_marked_status

    @show_marked_status.setter
    def show_marked_status(self, value: bool):
        self._show_marked_status = value

    @property
    def show_metrics(self) -> bool:
        return self._show_metrics

    @show_metrics.setter
    def show_metrics(self, value: bool):
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
    @staticmethod
    def get_question_display_mode(display_mode: QuestionDisplayMode) -> IQuestionDisplay:
        display_classes = {
            QuestionDisplayMode.PRINT: QuestionDisplay,
            QuestionDisplayMode.QUIZ: QuizQuestionDisplay,
            QuestionDisplayMode.PRACTICE_EXAM: QuizQuestionDisplay,
        }
        try:
            return display_classes[display_mode]().get_default_question_display()
        except KeyError as err:
            raise ValueError("Invalid display mode") from err
