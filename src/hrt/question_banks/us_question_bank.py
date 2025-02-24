"""This module contains the USQuestionBank class."""

from pathlib import Path

from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_bank import QuestionBank
from hrt.common.question_category import QuestionCategory
from hrt.common.question_metric import QuestionMetric


class USQuestionBank(QuestionBank):
    """US Question Bank class."""

    def __init__(
        self,
        exam_type: ExamType,
        filepath: Path,
        display_mode: QuestionDisplayMode = QuestionDisplayMode.PRINT,
        categories_filepath: Path = None,
        marked_questions_filepath: Path = None,
        metrics_filepath: Path = None,
    ):
        super().__init__(
            CountryCode.UNITED_STATES,
            exam_type,
            filepath,
            display_mode,
            categories_filepath,
            marked_questions_filepath,
            metrics_filepath,
        )

    def load_questions(self) -> list[Question]:
        raise NotImplementedError("USQuestionBank.load_questions() is not implemented")

    def load_categories(self) -> list[QuestionCategory]:
        raise NotImplementedError("USQuestionBank.load_categories() is not implemented")

    def load_metrics(self) -> dict[QuestionNumber, QuestionMetric]:
        raise NotImplementedError("USQuestionBank.load_metrics() is not implemented")
