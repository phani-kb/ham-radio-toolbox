"""This module contains the implementation of the CAQuestionBank class."""

from pathlib import Path
from typing import Dict, List, Optional

from hrt.common import utils
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question, QuestionCategory
from hrt.common.question_bank import QuestionBank
from hrt.common.question_metric import QuestionMetric


def get_question_category_id(question_number: QuestionNumber) -> str:
    """Get the category ID from the question number."""
    return question_number.split("-")[1]


class CAQuestionBank(QuestionBank):
    """CA Question Bank class."""

    def __init__(
        self,
        exam_type: ExamType,
        filepath: Path,
        display_mode: QuestionDisplayMode = QuestionDisplayMode.PRINT,
        categories_filepath: Optional[Path] = None,
        marked_questions_filepath: Optional[Path] = None,
        metrics_filepath: Optional[Path] = None,
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

    def load_categories(self) -> List[QuestionCategory]:
        categories = utils.read_delim_file(self.categories_filepath, delimiter=":")
        return [
            QuestionCategory(category[0], category[1], int(category[2])) for category in categories
        ]

    def load_metrics(self) -> Dict[QuestionNumber, QuestionMetric]:
        metrics = utils.read_metrics_from_file(self.metrics_filepath)
        return {metric.question_number: metric for metric in metrics}

    def load_questions(self) -> List[Question]:
        result: List[Question] = []
        questions = utils.read_delim_file(
            self.filepath,
            delimiter=";",
            skip_header=True,
            header="question_id",
            fields_count=6,
        )
        for q in questions:
            question_number = q[0]
            question_text = q[1]
            # use the rest of the fields split by comma as choices
            choices = q[2:6]
            answer = q[2]
            category_id = get_question_category_id(QuestionNumber(question_number))
            category = self.get_category_by_id(category_id)
            metric = self.metrics.get(question_number)
            q = Question(
                question_text, choices, answer, QuestionNumber(question_number), category, metric
            )
            result.append(q)
        return result

    def get_category_by_id(self, category_id: str) -> Optional[QuestionCategory]:
        """Get the category by its ID."""
        for category in self.categories:
            if category.category_id == category_id:
                return category
        return None
