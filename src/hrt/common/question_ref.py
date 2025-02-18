"""Question reference classes for books, websites, videos, and PDFs."""

from abc import ABC, abstractmethod

from hrt.common.enums import QuestionRefType


class IQuestionRef(ABC):
    """Interface for a question reference."""

    @property
    @abstractmethod
    def type(self) -> QuestionRefType:
        """Type of the question reference."""

    @abstractmethod
    def details(self) -> str:
        """Details of the question reference."""


class QuestionRef(IQuestionRef, ABC):
    """Question reference class."""

    def __init__(self, qr_type: QuestionRefType):
        self._type = qr_type

    @property
    def type(self) -> QuestionRefType:
        return self._type

    def __str__(self):
        return f"{self.type.name}: {self.details()}"


class BookRef(QuestionRef):
    """Book reference class."""

    def __init__(self, title: str):
        super().__init__(QuestionRefType.BOOK)
        self._title = title

    @property
    def title(self):
        """Title of the book."""
        return self._title

    def details(self):
        """Details of the book reference."""
        return self.title


class WebRef(QuestionRef):
    """Base class for web references."""

    def __init__(self, url: str, qr_type: QuestionRefType = QuestionRefType.WEBSITE):
        super().__init__(qr_type)
        self._url = url

    @property
    def url(self):
        """URL of the web reference."""
        return self._url

    def details(self):
        return self.url


class VideoRef(WebRef):
    """Video reference class."""

    def __init__(self, url: str):
        super().__init__(url, QuestionRefType.VIDEO)
        self._url = url


class PDFRef(WebRef):
    """PDF reference class."""

    def __init__(self, url: str):
        super().__init__(url, QuestionRefType.PDF)
        self._url = url
