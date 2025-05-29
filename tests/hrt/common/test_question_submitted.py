"""Test question submitted module."""

import unittest
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_submitted import QuestionSubmitted


class TestQuestionSubmitted(unittest.TestCase):
    """Test question submitted class."""

    def setUp(self):
        """Set up test case."""
        self.question_number = QuestionNumber("Q1")
        self.question_submitted = QuestionSubmitted(self.question_number)

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.question_submitted.question_number, self.question_number)
        self.assertIsNone(self.question_submitted.selected_choice)
        self.assertFalse(self.question_submitted.marked)

    def test_question_number_setter(self):
        """Test question number setter."""
        new_number = QuestionNumber("Q2")
        self.question_submitted.question_number = new_number
        self.assertEqual(self.question_submitted.question_number, new_number)

    def test_selected_choice_setter(self):
        """Test selected choice setter."""
        choice = "A"
        self.question_submitted.selected_choice = choice
        self.assertEqual(self.question_submitted.selected_choice, choice)

    def test_equals(self):
        """Test equality."""
        other = QuestionSubmitted(self.question_number)
        self.assertEqual(self.question_submitted, other)

        other = QuestionSubmitted(QuestionNumber("Q2"))
        self.assertNotEqual(self.question_submitted, other)

    def test_equals_non_question_submitted(self):
        """Test equality with non QuestionSubmitted object."""
        other = "not a question submitted"
        self.assertNotEqual(self.question_submitted, other)

    def test_hash(self):
        """Test hash."""
        expected = hash(
            str(self.question_number)
            + str(self.question_submitted.selected_choice)
            + str(self.question_submitted.marked)
        )
        self.assertEqual(hash(self.question_submitted), expected)

    def test_str(self):
        """Test string representation."""
        self.assertEqual(
            str(self.question_submitted),
            f"{super(QuestionSubmitted, self.question_submitted).__str__()}, "
            f"Selected Choice: {self.question_submitted.selected_choice} "
            f"Marked: {self.question_submitted.marked}",
        )


if __name__ == "__main__":
    unittest.main()
