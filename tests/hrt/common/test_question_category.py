import unittest
from hrt.common.question_category import QuestionCategory


class TestQuestionCategory(unittest.TestCase):
    def test_initialization(self):
        category = QuestionCategory(category_id="1", name="Math", max_questions=10)
        self.assertEqual(category.category_id, "1")
        self.assertEqual(category.name, "Math")
        self.assertEqual(category.max_questions, 10)

    def test_initialization_without_max_questions(self):
        category = QuestionCategory(category_id="2", name="Science")
        self.assertEqual(category.category_id, "2")
        self.assertEqual(category.name, "Science")
        self.assertEqual(category.max_questions, 0)

    def test_initialization_without_category_id(self):
        category = QuestionCategory(category_id="", name="History")
        self.assertIsNotNone(category.category_id)
        self.assertEqual(category.name, "History")
        self.assertEqual(category.max_questions, 0)

    def test_initialization_with_empty_name(self):
        with self.assertRaises(ValueError):
            QuestionCategory(category_id="3", name="")

    def test_str_method(self):
        category = QuestionCategory(category_id="4", name="Geography")
        self.assertEqual(str(category), "4:Geography")


if __name__ == "__main__":
    unittest.main()
