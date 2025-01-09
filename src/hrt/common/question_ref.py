from abc import ABC, abstractmethod

from hrt.common.enums import QuestionRefType


class IQuestionRef(ABC):
    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def details(self):
        pass


class QuestionRef(IQuestionRef, ABC):
    def __init__(self, qr_type: QuestionRefType):
        self._type = qr_type

    @property
    def type(self) -> QuestionRefType:
        return self._type

    def __str__(self):
        return f"{self.type.name}: {self.details()}"


class BookRef(QuestionRef):
    def __init__(self, title: str):
        super().__init__(QuestionRefType.BOOK)
        self._title = title

    @property
    def title(self):
        return self._title

    def details(self):
        return self.title


class WebRef(QuestionRef):
    def __init__(self, url: str, qr_type: QuestionRefType = QuestionRefType.WEBSITE):
        super().__init__(qr_type)
        self._url = url

    @property
    def url(self):
        return self._url

    def details(self):
        return self.url


class VideoRef(WebRef):
    def __init__(self, url: str):
        super().__init__(url, QuestionRefType.VIDEO)
        self._url = url


class PDFRef(WebRef):
    def __init__(self, url: str):
        super().__init__(url, QuestionRefType.PDF)
        self._url = url
