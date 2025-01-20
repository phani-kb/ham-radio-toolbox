from abc import ABC, abstractmethod
from pathlib import Path

from hrt.common.enums import (
    CountryCode,
    ExamType,
    QuestionListingType,
    TopQuestionsListingType,
)
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_metric import QuestionMetric


class IQuestionBank(ABC):
    @property
    @abstractmethod
    def country(self) -> CountryCode:
        pass

    @property
    @abstractmethod
    def exam_type(self) -> ExamType:
        pass

    @property
    @abstractmethod
    def filepath(self) -> Path:
        pass

    @property
    @abstractmethod
    def categories_filepath(self) -> Path:
        pass

    @abstractmethod
    def load_metrics(self) -> dict[QuestionNumber, QuestionMetric]:
        pass

    @abstractmethod
    def load_marked_questions(self) -> int:
        pass

    @property
    @abstractmethod
    def questions(self):
        pass

    @property
    @abstractmethod
    def categories(self):
        pass

    @abstractmethod
    def get_questions(
        self,
        criteria: QuestionListingType | TopQuestionsListingType,
        max_questions: int = 0,
    ) -> tuple[dict | list, list[str]]:
        pass

    @abstractmethod
    def get_qnum_answer_questions(self) -> dict[str, str]:
        pass

    @abstractmethod
    def get_marked_questions_filepath(self):
        pass
