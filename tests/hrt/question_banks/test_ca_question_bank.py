import unittest
from unittest.mock import patch
from hrt.question_banks.ca_question_bank import CAQuestionBank, get_question_category_id
from hrt.common.enums import ExamType
from hrt.common.question import Question, QuestionCategory, QuestionMetric
from hrt.common.hrt_types import QuestionNumber
from pathlib import Path


class TestCAQuestionBank(unittest.TestCase):
    @patch("hrt.common.utils.read_delim_file")
    @patch("hrt.common.utils.read_metrics_from_file")
    @patch("os.path.exists", return_value=True)
    def setUp(self, _, mock_read_metrics_from_file, mock_read_delim_file):
        self.categories_file_content = [["001", "Category 1", "10"], ["002", "Category 2", "5"]]
        self.categories = [
            QuestionCategory("1", "Category 1", int(10)),
            QuestionCategory("2", "Category 2", int(5)),
        ]
        self.metrics = [
            QuestionMetric(QuestionNumber("A-001-789"), 5, 3, 0),
            QuestionMetric(QuestionNumber("987-654-321"), 2, 1, 0),
        ]
        self.questions_file_content = [
            ["A-001-789", "Question 1", "Choice 1", "Choice 2", "Choice 3", "Choice 4"],
            ["B-002-321", "Question 2", "Choice A", "Choice B", "Choice C", "Choice D"],
        ]
        self.questions = [
            Question(
                "Question 1",
                ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
                "Choice 1",
                QuestionNumber("A-001-789"),
                self.categories[0],
            ),
            Question(
                "Question 2",
                ["Choice A", "Choice B", "Choice C", "Choice D"],
                "Choice A",
                QuestionNumber("987-654-321"),
                self.categories[1],
            ),
        ]
        mock_read_delim_file.side_effect = [
            self.categories_file_content,
            self.questions_file_content,
            [],
        ]
        mock_read_metrics_from_file.return_value = self.metrics
        self.bank = CAQuestionBank(ExamType.BASIC, Path("dummy_path"))

    def test_get_question_category_id(self):
        question_number = QuestionNumber("A-001-789")
        expected_category_id = "001"
        self.assertEqual(get_question_category_id(question_number), expected_category_id)

    def test_get_category_by_id_not_found(self):
        category_id = "999"
        category = self.bank.get_category_by_id(category_id)
        self.assertIsNone(category)

    def test_load_categories(self):
        categories = self.bank.categories
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].category_id, "001")
        self.assertEqual(categories[0].name, "Category 1")
        self.assertEqual(categories[0].max_questions, 10)

    def test_load_metrics(self):
        metrics = self.bank.metrics
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[QuestionNumber("A-001-789")].question_number, "A-001-789")
        self.assertEqual(metrics[QuestionNumber("A-001-789")].correct_attempts, 5)
        self.assertEqual(metrics[QuestionNumber("A-001-789")].wrong_attempts, 3)

    def test_load_questions(self):
        questions = self.bank.questions
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].question_number, "A-001-789")
        self.assertEqual(questions[0].question_text, "Question 1")
        self.assertCountEqual(
            questions[0].choices, ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]
        )
        self.assertEqual(questions[0].answer, "Choice 1")
        self.assertEqual(questions[0].category.category_id, "001")


if __name__ == "__main__":
    unittest.main()
