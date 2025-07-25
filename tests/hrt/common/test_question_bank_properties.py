import unittest
from pathlib import Path

from hrt.common.enums import (
    CountryCode,
    ExamType,
    QuestionDisplayMode,
)
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_bank import QuestionBank


class ConcreteQuestionBank(QuestionBank):
    def load_categories(self):
        self._categories = []
        return []

    def load_metrics(self):
        self._metrics = {}
        return []

    def load_questions(self):
        self._questions = [
            Question(
                question_number=QuestionNumber("Q1"),
                question_text="Question 1",
                choices=["A", "B", "C"],
                answer="A",
            ),
            Question(
                question_number=QuestionNumber("Q2"),
                question_text="Question 2",
                choices=["A", "B", "C"],
                answer="B",
            ),
            Question(
                question_number=QuestionNumber("Q3"),
                question_text="Question 3",
                choices=["A", "B", "C"],
                answer="C",
            ),
            Question(
                question_number=QuestionNumber("Q4"),
                question_text="Question 4",
                choices=["A", "B", "C"],
                answer="A",
            ),
        ]
        return self._questions


class TestQuestionBankProperties(unittest.TestCase):
    def setUp(self):
        self.question_bank = ConcreteQuestionBank(
            country=CountryCode.CANADA,
            exam_type=ExamType.BASIC,
            filepath=Path("/path/to/questions"),
            display_mode=QuestionDisplayMode.PRINT,
            categories_filepath=Path("/path/to/categories"),
            marked_questions_filepath=Path("/path/to/marked"),
            metrics_filepath=Path("/path/to/metrics"),
        )

    def test_country_property(self):
        self.assertEqual(self.question_bank.country, CountryCode.CANADA)

    def test_exam_type_property(self):
        self.assertEqual(self.question_bank.exam_type, ExamType.BASIC)

    def test_filepath_property(self):
        self.assertEqual(self.question_bank.filepath, Path("/path/to/questions"))

    def test_display_mode_property(self):
        self.assertEqual(self.question_bank.display_mode, QuestionDisplayMode.PRINT)

    def test_categories_filepath_property(self):
        self.assertEqual(self.question_bank.categories_filepath, Path("/path/to/categories"))

    def test_metrics_filepath_property(self):
        self.assertEqual(self.question_bank.metrics_filepath, Path("/path/to/metrics"))

    def test_marked_questions_filepath_property(self):
        self.assertEqual(self.question_bank.marked_questions_filepath, Path("/path/to/marked"))

    def test_categories_property(self):
        self.assertEqual(self.question_bank.categories, [])

    def test_metrics_property(self):
        self.assertEqual(self.question_bank.metrics, [])


if __name__ == "__main__":
    unittest.main()
