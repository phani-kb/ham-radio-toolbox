from pathlib import Path

from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_category import QuestionCategory
from hrt.common.question_metric import QuestionMetric


def get_question_category_id(question_number: QuestionNumber) -> str:
    return question_number.split("-")[1]


class CAQuestionBank:
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
            CountryCode.CANADA,
            exam_type,
            filepath,
            display_mode,
            categories_filepath,
            marked_questions_filepath,
            metrics_filepath,
        )

    def load_categories(self) -> list[QuestionCategory]:
        pass

    def load_metrics(self) -> dict[QuestionNumber, QuestionMetric]:
        pass

    def load_questions(self) -> list[Question]:
        result: list[Question] = []

        return result

    def get_category_by_id(self, category_id: str) -> QuestionCategory | None:
        return None
