"""Test module for USQuestionBank."""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Dict, List

from hrt.question_banks.us_question_bank import USQuestionBank
from hrt.common.enums import ExamType, CountryCode, QuestionDisplayMode
from hrt.common.question import Question
from hrt.common.question_category import QuestionCategory
from hrt.common.question_metric import QuestionMetric
from hrt.common.hrt_types import QuestionNumber


class TestUSQuestionBank(unittest.TestCase):
    """Test the USQuestionBank class."""

    @patch.object(USQuestionBank, 'load_categories', return_value=[])
    @patch.object(USQuestionBank, 'load_questions', return_value=[])
    @patch.object(USQuestionBank, 'load_metrics', return_value={})
    def setUp(self, mock_load_metrics, mock_load_questions, mock_load_categories):
        """Set up the test fixture."""
        # Create an instance of USQuestionBank for testing
        self.bank = USQuestionBank(
            exam_type=ExamType.BASIC,
            filepath=Path("dummy_path"),
            display_mode=QuestionDisplayMode.PRINT
        )
        # Store the mocks for later use
        self.mock_load_categories = mock_load_categories
        self.mock_load_questions = mock_load_questions
        self.mock_load_metrics = mock_load_metrics

    def test_init(self):
        """Test initialization of USQuestionBank."""
        # Test that the bank has correct values
        self.assertEqual(self.bank._country, CountryCode.UNITED_STATES)
        self.assertEqual(self.bank.exam_type, ExamType.BASIC)
        self.assertEqual(self.bank.filepath, Path("dummy_path"))
        self.assertEqual(self.bank.display_mode, QuestionDisplayMode.PRINT)
        self.assertIsNone(self.bank.categories_filepath)
        self.assertIsNone(self.bank.marked_questions_filepath)
        self.assertIsNone(self.bank.metrics_filepath)

    @patch.object(USQuestionBank, 'load_categories', return_value=[])
    @patch.object(USQuestionBank, 'load_questions', return_value=[])
    @patch.object(USQuestionBank, 'load_metrics', return_value={})
    def test_init_with_all_parameters(self, mock_load_metrics, mock_load_questions, mock_load_categories):
        """Test initialization with all parameters specified."""
        bank = USQuestionBank(
            exam_type=ExamType.ADVANCED,
            filepath=Path("questions_path"),
            display_mode=QuestionDisplayMode.QUIZ,
            categories_filepath=Path("categories_path"),
            marked_questions_filepath=Path("marked_path"),
            metrics_filepath=Path("metrics_path")
        )
        
        self.assertEqual(bank._country, CountryCode.UNITED_STATES)
        self.assertEqual(bank.exam_type, ExamType.ADVANCED)
        self.assertEqual(bank.filepath, Path("questions_path"))
        self.assertEqual(bank.display_mode, QuestionDisplayMode.QUIZ)
        self.assertEqual(bank.categories_filepath, Path("categories_path"))
        self.assertEqual(bank.marked_questions_filepath, Path("marked_path"))
        self.assertEqual(bank.metrics_filepath, Path("metrics_path"))

    def test_load_questions_raises_not_implemented(self):
        """Test that load_questions raises NotImplementedError."""
        # Reset the mock to allow the real method to be called
        self.mock_load_questions.side_effect = USQuestionBank.load_questions
        
        with self.assertRaises(NotImplementedError) as context:
            self.bank.load_questions()
        self.assertEqual(
            str(context.exception),
            "USQuestionBank.load_questions() is not implemented"
        )

    def test_load_categories_raises_not_implemented(self):
        """Test that load_categories raises NotImplementedError."""
        # Reset the mock to allow the real method to be called
        self.mock_load_categories.side_effect = USQuestionBank.load_categories
        
        with self.assertRaises(NotImplementedError) as context:
            self.bank.load_categories()
        self.assertEqual(
            str(context.exception),
            "USQuestionBank.load_categories() is not implemented"
        )

    def test_load_metrics_raises_not_implemented(self):
        """Test that load_metrics raises NotImplementedError."""
        # Reset the mock to allow the real method to be called
        self.mock_load_metrics.side_effect = USQuestionBank.load_metrics
        
        with self.assertRaises(NotImplementedError) as context:
            self.bank.load_metrics()
        self.assertEqual(
            str(context.exception),
            "USQuestionBank.load_metrics() is not implemented"
        )


if __name__ == "__main__":
    unittest.main()