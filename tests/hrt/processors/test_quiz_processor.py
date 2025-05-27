"""Test quiz processor."""

import unittest
import os
from unittest.mock import MagicMock, patch

from hrt.common.enums import (
    CountryCode,
    ExamType,
    QuestionDisplayMode,
    QuizAnswerDisplay,
    QuizSource,
)
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_bank import IQuestionBank
from hrt.common.question_metric import QuestionMetric
from hrt.processors.quiz_processor import QuizProcessor


class TestQuizProcessor(unittest.TestCase):
    """Test QuizProcessor class."""

    def setUp(self):
        """Set up test cases."""
        self.question_bank = MagicMock(spec=IQuestionBank)
        mock_exam_type = MagicMock()
        mock_exam_type.country = CountryCode.CANADA
        mock_exam_type.id = "basic"
        self.question_bank.exam_type = mock_exam_type
        self.question_bank.get_random_questions.return_value = []  # Default return value

        self.question = Question(
            "Test Question?", ["A", "B", "C", "D"], "A", QuestionNumber("Q1"), 0
        )
        self.quiz_config = {
            "mark_wrong_answers": True,
            "show_explanation": True,
            "show_hints": True,
            "show_references": True,
            "show_tags": True,
            "show_marked_status": True,
            "show_metrics": True,
        }
        self.print_config = {"answer_display": QuizAnswerDisplay.AFTER_QUESTION.id}
        self.metrics_config = {"folder": "test_metrics", "filename": "metrics.txt"}
        self.processor = QuizProcessor(
            self.question_bank,
            1,
            QuestionDisplayMode.QUIZ,
            QuizAnswerDisplay.AFTER_QUESTION,
            QuizSource.ALL,
            self.quiz_config,
            self.print_config,
            self.metrics_config,
        )

    def test_initialize_quiz_all_source(self):
        """Test initialize quiz with ALL source."""
        self.question_bank.reset_mock()
        self.question_bank.get_random_questions.return_value = [self.question]
        self.processor._initialize_quiz()
        self.assertIsNotNone(self.processor._quiz)
        self.question_bank.get_random_questions.assert_called_once_with(1, False, [], [])

    def test_initialize_quiz_marked_source(self):
        """Test initialize quiz with MARKED source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.MARKED
        self.question_bank.get_random_questions.return_value = [self.question]
        self.processor._initialize_quiz()
        self.assertIsNotNone(self.processor._quiz)
        self.question_bank.get_random_questions.assert_called_once_with(1, True, [], [])

    def test_initialize_quiz_new_source(self):
        """Test initialize quiz with NEW source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.NEW
        metric = QuestionMetric(QuestionNumber("Q1"))
        with patch.object(self.processor, "_get_metric_questions", return_value=[metric]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            self.question_bank.get_random_questions.assert_called_once_with(1, False, [], ["Q1"])

    def test_initialize_quiz_skipped_questions(self):
        """Test initialize quiz with SKIPPED_QUESTIONS source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.SKIPPED_QUESTIONS
        metric = QuestionMetric(QuestionNumber("Q1"))
        metric.skip_count = 1
        metric.correct_attempts = 0
        with patch.object(self.processor, "_get_metric_questions", return_value=[metric]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            self.question_bank.get_random_questions.assert_called_once_with(1, False, [], ["Q1"])

    def test_initialize_quiz_exclude_correct(self):
        """Test initialize quiz excluding correct answers."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.EXCLUDE_CORRECT_ANSWERS
        metric = QuestionMetric(QuestionNumber("Q1"))
        metric.correct_attempts = 1
        with patch.object(self.processor, "_get_metric_questions", return_value=[metric]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            self.question_bank.get_random_questions.assert_called_once_with(1, False, [], ["Q1"])

    def test_initialize_quiz_old(self):
        """Test initialize quiz with OLD source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.OLD
        metric = QuestionMetric(QuestionNumber("Q1"))
        with patch.object(self.processor, "_get_metric_questions", return_value=[metric]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            self.question_bank.get_random_questions.assert_called_once_with(1, True, ["Q1"], [])

    def test_initialize_quiz_invalid_source(self):
        """Test initialize quiz with invalid source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = MagicMock()
        self.processor._quiz_source.name = "INVALID"
        with self.assertRaises(ValueError) as context:
            self.processor._initialize_quiz()
        self.assertTrue("Invalid quiz source:" in str(context.exception))

    @patch("os.makedirs")
    def test_save_marked_questions(self, mock_makedirs):
        """Test save marked questions."""
        self.question_bank.get_marked_questions_filepath.return_value = "test_path/marked.txt"
        self.processor._quiz = MagicMock()
        self.processor._quiz.get_marked_questions.return_value = [self.question]
        self.question_bank.get_all_marked_questions.return_value = []

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            self.processor._save_marked_questions()
            mock_makedirs.assert_called_once_with("test_path", exist_ok=True)
            mock_file.assert_called_once_with("test_path/marked.txt", "w", encoding="utf-8")
            mock_file().write.assert_called_once_with("Q1\n")

    def test_save_marked_questions_no_filepath(self):
        """Test save marked questions with no filepath."""
        self.question_bank.get_marked_questions_filepath.return_value = None
        self.processor._quiz = MagicMock()
        with self.assertRaises(ValueError) as context:
            self.processor._save_marked_questions()
        self.assertEqual(str(context.exception), "Marked questions file path not found")

    def test_save_marked_questions_with_existing(self):
        """Test save marked questions when there are already existing marked questions."""
        self.question_bank.get_marked_questions_filepath.return_value = "test_path/marked.txt"
        self.processor._quiz = MagicMock()

        # Current quiz marked question
        current_marked = Question(
            "Test Question?", ["A", "B", "C", "D"], "A", QuestionNumber("Q1"), 0
        )
        self.processor._quiz.get_marked_questions.return_value = [current_marked]

        # Previously marked question
        existing_marked = Question(
            "Test Question 2?", ["A", "B", "C", "D"], "B", QuestionNumber("Q2"), 0
        )
        self.question_bank.get_all_marked_questions.return_value = [existing_marked]

        with patch("os.makedirs"), patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            self.processor._save_marked_questions()
            mock_file.assert_called_once_with("test_path/marked.txt", "w", encoding="utf-8")
            # Both Q1 and Q2 should be written to the file in sorted order
            mock_file().write.assert_has_calls(
                [unittest.mock.call("Q1\n"), unittest.mock.call("Q2\n")]
            )

    def test_get_metrics_file_path(self):
        """Test get metrics file path."""
        expected_path = "test_metrics/ca/basic/metrics.txt"
        self.assertEqual(self.processor._get_metrics_file_path(), expected_path)

    def test_get_metrics_file_path_no_folder(self):
        """Test get metrics file path with no folder in config."""
        self.processor._metrics_config = {}
        with self.assertRaises(ValueError) as context:
            self.processor._get_metrics_file_path()
        self.assertEqual(str(context.exception), "Metrics folder not found in the config file")

    def test_save_metrics_new_question(self):
        """Test save metrics for new question."""
        self.processor._quiz = MagicMock()
        question = self.question
        question.metric = QuestionMetric(QuestionNumber("Q1"))
        question.metric.correct_attempts = 1
        self.processor._quiz.get_questions.return_value = [question]

        with (
            patch("os.makedirs"),
            patch.object(self.processor, "_get_metric_questions", return_value=[]),
            patch("builtins.open", unittest.mock.mock_open()) as mock_file,
        ):
            self.processor._save_metrics()
            mock_file().write.assert_called_once_with("Q1:1:0:0\n")

    def test_save_metrics_existing_question(self):
        """Test save metrics for existing question."""
        self.processor._quiz = MagicMock()
        question = self.question
        question.metric = QuestionMetric(QuestionNumber("Q1"))
        question.metric.correct_attempts = 1
        existing_metric = QuestionMetric(QuestionNumber("Q1"))
        existing_metric.correct_attempts = 2

        self.processor._quiz.get_questions.return_value = [question]

        with (
            patch("os.makedirs"),
            patch.object(self.processor, "_get_metric_questions", return_value=[existing_metric]),
            patch("builtins.open", unittest.mock.mock_open()) as mock_file,
        ):
            self.processor._save_metrics()
            mock_file().write.assert_called_once_with("Q1:3:0:0\n")

    def test_save_metrics_no_questions(self):
        """Test save metrics with no questions."""
        self.processor._quiz = MagicMock()
        self.processor._quiz.get_questions.return_value = []
        expected_path = "test_metrics/ca/basic/metrics.txt"

        with (
            patch("os.makedirs"),
            patch.object(self.processor, "_get_metric_questions", return_value=[]),
            patch("builtins.open", unittest.mock.mock_open()) as mock_file,
        ):
            self.processor._save_metrics()
            # File should be opened to write the empty metrics
            mock_file.assert_called_once_with(expected_path, "w", encoding="utf-8")

    def test_save_metrics_question_without_metric(self):
        """Test save metrics when a question has no metric data."""
        self.processor._quiz = MagicMock()
        question = self.question
        question.metric = None  # Question without metric data
        self.processor._quiz.get_questions.return_value = [question]
        expected_path = "test_metrics/ca/basic/metrics.txt"

        with (
            patch("os.makedirs"),
            patch.object(self.processor, "_get_metric_questions", return_value=[]),
            patch("builtins.open", unittest.mock.mock_open()) as mock_file,
        ):
            self.processor._save_metrics()
            # File should be opened and default metrics written (0:0:0)
            mock_file.assert_called_once_with(expected_path, "w", encoding="utf-8")
            mock_file().write.assert_called_once_with("Q1:0:0:0\n")

    def test_display_answers_in_the_end(self):
        """Test display answers in the end."""
        self.processor._answer_display = QuizAnswerDisplay.IN_THE_END
        self.processor._quiz = MagicMock()

        # Create a new question with the desired properties
        question = Question("Test Question?", ["A", "B", "C", "D"], "A", QuestionNumber("Q1"), 0)
        question.metric = QuestionMetric(QuestionNumber("Q1"))
        question.metric.wrong_attempts = 1

        self.processor._quiz.get_questions.return_value = [question]

        with patch("builtins.print") as mock_print:
            self.processor._display_answers()
            mock_print.assert_any_call(
                "\nAnswer display: in-the-end for wrong answers\n---------------------------------------------"
            )
            # Use assert_any_call to be more flexible about the output format
            calls = [call[0][0] for call in mock_print.call_args_list]
            # Check if any call contains the required information
            self.assertTrue(any("Q1" in call and "A" in call for call in calls))

    def test_display_answers_none(self):
        """Test display answers with NONE setting."""
        # Instead of trying to use NONE enum value which doesn't exist,
        # we'll mock the _display_answers method to check its behavior based on the value
        with patch("hrt.processors.quiz_processor.QuizAnswerDisplay") as mock_enum:
            # Create a mock enum instance that works like NONE
            none_value = MagicMock()
            none_value.value = "none"  # This is the value checked in the implementation

            # Set up our processor
            self.processor._quiz = MagicMock()
            self.processor._answer_display = none_value

            with patch("builtins.print") as mock_print:
                self.processor._display_answers()
                mock_print.assert_not_called()

    def test_display_answers_after_question_with_no_wrong(self):
        """Test display answers after question with no wrong questions."""
        self.processor._answer_display = QuizAnswerDisplay.AFTER_QUESTION
        self.processor._quiz = MagicMock()
        question = Question("Test Question?", ["A", "B", "C", "D"], "A", QuestionNumber("Q1"), 0)
        question.metric = QuestionMetric(QuestionNumber("Q1"))
        question.metric.wrong_attempts = 0  # No wrong attempts
        self.processor._quiz.get_questions.return_value = [question]

        with patch("builtins.print") as mock_print:
            self.processor._display_answers()
            # For AFTER_QUESTION mode, nothing should be printed at the end
            mock_print.assert_not_called()

    def test_process(self):
        """Test process method."""
        self.processor._quiz = MagicMock()
        with (
            patch.object(self.processor, "_display_answers") as mock_display,
            patch.object(self.processor, "_save_marked_questions") as mock_save_marked,
            patch.object(self.processor, "_save_metrics") as mock_save_metrics,
        ):
            self.processor.process()
            self.processor._quiz.pre_process.assert_called_once()
            self.processor._quiz.start.assert_called_once()
            self.processor._quiz.post_process.assert_called_once()
            mock_display.assert_called_once()
            mock_save_marked.assert_called_once()
            mock_save_metrics.assert_called_once()

    def test_process_no_quiz(self):
        """Test process method with no quiz."""
        self.processor._quiz = None
        with patch("builtins.print") as mock_print:
            self.processor.process()
            mock_print.assert_called_once_with("Quiz not initialized. Exiting...")

    def test_initialize_quiz_wrong_answers(self):
        """Test initialize quiz with wrong answers source."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.WRONG_ANSWERS
        metric = QuestionMetric(QuestionNumber("Q1"))
        metric.wrong_attempts = 1
        with patch.object(self.processor, "_get_metric_questions", return_value=[metric]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            self.question_bank.get_random_questions.assert_called_once_with(1, True, ["Q1"], [])

    def test_initialize_quiz_wrong_answers_no_metrics(self):
        """Test initialize quiz with wrong answers source but no metrics."""
        self.question_bank.reset_mock()
        self.processor._quiz_source = QuizSource.WRONG_ANSWERS
        with patch.object(self.processor, "_get_metric_questions", return_value=[]):
            self.question_bank.get_random_questions.return_value = [self.question]
            self.processor._initialize_quiz()
            self.assertIsNotNone(self.processor._quiz)
            # In the actual implementation, it calls with shuffle=True since there are no wrong answers to filter by
            self.question_bank.get_random_questions.assert_called_once_with(1, True, [], [])

    @patch("os.path.exists", return_value=False)
    def test_get_metric_questions_no_file(self, mock_exists):
        """Test get metric questions with no metrics file."""
        with patch.object(
            self.processor, "_get_metrics_file_path", return_value="nonexistent.txt"
        ):
            result = self.processor._get_metric_questions()
            self.assertEqual(result, [])

    @patch("os.path.exists", return_value=True)
    def test_get_metric_questions_empty_file(self, mock_exists):
        """Test get metric questions with empty metrics file."""
        with (
            patch.object(self.processor, "_get_metrics_file_path", return_value="metrics.txt"),
            patch("builtins.open", unittest.mock.mock_open(read_data="")),
        ):
            result = self.processor._get_metric_questions()
            self.assertEqual(result, [])

    @patch("os.path.exists", return_value=True)
    def test_get_metric_questions_invalid_format(self, mock_exists):
        """Test get metric questions with invalid format in metrics file."""
        with (
            patch.object(self.processor, "_get_metrics_file_path", return_value="metrics.txt"),
            patch("builtins.open", unittest.mock.mock_open(read_data="invalid_format\n")),
        ):
            result = self.processor._get_metric_questions()
            self.assertEqual(result, [])  # Should handle invalid formats gracefully

    def test_initialize_quiz_no_questions(self):
        """Test initialize quiz when no questions are found."""
        self.question_bank.reset_mock()
        self.question_bank.get_random_questions.return_value = []
        with patch("builtins.print") as mock_print:
            self.processor._initialize_quiz()
            self.assertIsNone(self.processor._quiz)
            mock_print.assert_called_once_with("No questions found for the quiz.")
