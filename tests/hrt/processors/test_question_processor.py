import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from hrt.common.config_reader import HRTConfig
from hrt.common.question import Question
from hrt.common.question_display import QuestionDisplay
from hrt.processors.question_processor import QuestionProcessor, get_answers
from hrt.common.enums import (
    CountryCode,
    ExamType,
    GeneralQuestionListingType,
    QuestionDisplayMode,
    MarkedQuestionListingType,
    QuestionAnswerDisplay,
    QuizAnswerDisplay,
)
from hrt.common.question_bank import IQuestionBank


class TestQuestionProcessor(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock(spec=HRTConfig)
        self.country = CountryCode.CANADA
        self.exam_type = ExamType.BASIC
        self.display_mode = QuestionDisplayMode.PRINT

        Question.question_display = QuestionDisplay(
            answer_display=QuestionAnswerDisplay.HIDE,
            show_explanation=True,
            show_hints=True,
            show_references=True,
            show_tags=True,
        )

        self.config.get_country_settings.return_value = {
            "question_bank": {
                self.exam_type.id: {"file": "questions.json", "categories_file": "categories.json"}
            }
        }
        self.config.get_input.return_value = {
            "folder": "input_folder",
            "files": {"marked_questions": "marked_questions.json"},
        }
        self.config.get_output.return_value = {"folder": "output_folder"}
        self.config.get.return_value = {"folder": "metrics_folder", "file": "metrics.json"}

        patcher = patch("pathlib.Path.exists", return_value=True)
        self.addCleanup(patcher.stop)
        self.mock_path_exists = patcher.start()

        self.processor = QuestionProcessor(
            self.config, self.country, self.exam_type, self.display_mode
        )

    @patch("hrt.processors.question_processor.QuestionBankFactory.get_question_bank")
    def test_initialization(self, mock_get_question_bank):
        mock_get_question_bank.return_value = MagicMock(spec=IQuestionBank)
        processor = QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertIsNotNone(processor._qb)
        mock_get_question_bank.assert_called_once()

    @patch("hrt.processors.question_processor.Path.exists")
    @patch("hrt.processors.question_processor.Path.touch")
    def test_initialize_paths(self, _, mock_exists):
        mock_exists.side_effect = [False, False, False, False]
        with self.assertRaises(FileNotFoundError):
            self.processor._initialize_paths()

    @patch(
        "hrt.processors.question_processor.QuestionDisplayModeFactory.get_question_display_mode"
    )
    def test_initialize_question_display(self, mock_get_question_display_mode):
        mock_display_mode = MagicMock()
        mock_get_question_display_mode.return_value.get_default_question_display.return_value = (
            mock_display_mode
        )
        self.processor._initialize_question_display()
        self.assertIsNotNone(mock_display_mode)

    @patch("hrt.processors.question_processor.utils.save_output")
    def test_save_to_file(self, mock_save_output):
        output = ["Header", "Question1", "Question2"]
        criteria = GeneralQuestionListingType.ALL
        self.processor._save_to_file(output, criteria)
        mock_save_output.assert_called_once()

    @patch("hrt.processors.question_processor.utils.get_header")
    @patch("hrt.processors.question_processor.QuestionProcessor._save_to_file")
    @patch("hrt.processors.question_processor.utils.save_output")
    def test_process_list_result(self, mock_save_output, mock_get_header, mock_save_to_file):
        result = [MagicMock()]
        result_text = ["Question1"]
        criteria = GeneralQuestionListingType.ALL
        mock_get_header.return_value = "Header"
        mock_save_output.return_value = "output"
        self.processor._process_list_result(result, result_text, criteria, True)
        mock_save_to_file.assert_called_once()

    @patch("hrt.processors.question_processor.QuestionProcessor._process_list_result")
    @patch("hrt.processors.question_processor.QuestionProcessor.get_question_bank")
    def test_list(self, _, mock_process_list_result):
        self.processor.list(GeneralQuestionListingType.ALL, QuestionAnswerDisplay.IN_THE_END)
        mock_process_list_result.assert_called_once()

    @patch("hrt.processors.question_processor.QuestionProcessor._process_list_result")
    def test_list_marked(self, mock_process_list_result):
        criteria = MarkedQuestionListingType.WRONG_ATTEMPT
        self.processor.list_marked(criteria, QuestionAnswerDisplay.IN_THE_END)
        mock_process_list_result.assert_called_once()

    @patch("hrt.processors.question_processor.QuestionBankFactory.get_question_bank")
    def test_get_question_bank(self, mock_get_question_bank):
        mock_question_bank_instance = MagicMock(spec=IQuestionBank)
        mock_get_question_bank.return_value = mock_question_bank_instance

        processor = QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)

        result = processor.get_question_bank()

        assert result == mock_question_bank_instance
        mock_get_question_bank.assert_called_once()

    def test_unsupported_exam_type(self):
        self.country = CountryCode.INDIA
        self.exam_type = ExamType.RESTRICTED_GRADE
        with self.assertRaises(ValueError) as context:
            QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertEqual(
            str(context.exception),
            f"Exam type {self.exam_type} for {self.country} is not supported",
        )

    def test_missing_questions_file(self):
        self.config.get_country_settings.return_value = {"question_bank": {self.exam_type.id: {}}}
        self.config.get_input.return_value = {"folder": "some_folder"}

        with self.assertRaises(ValueError) as context:
            QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertEqual(
            str(context.exception),
            f"Questions file not set for {self.country} and {self.exam_type}",
        )

    def test_missing_input_folder(self):
        self.config.get_country_settings.return_value = {
            "question_bank": {self.exam_type.id: {"file": "questions_file"}}
        }
        self.config.get_input.return_value = {}

        with self.assertRaises(ValueError) as context:
            QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertEqual(str(context.exception), "Input folder not found in the config file")

    @patch("hrt.processors.question_processor.Path.exists", side_effect=[True, False])
    def test_missing_categories_file(self, _):
        self.config.get_country_settings.return_value = {
            "question_bank": {
                self.exam_type.id: {
                    "file": "questions_file",
                    "categories_file": "missing_categories_file",
                }
            }
        }
        self.config.get_input.return_value = {"folder": "some_folder"}

        with self.assertRaises(FileNotFoundError) as context:
            QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertEqual(
            str(context.exception),
            "Categories file not found at some_folder/ca/missing_categories_file",
        )

    @patch("hrt.processors.question_processor.Path.touch")
    @patch("hrt.processors.question_processor.Path.exists", side_effect=[True, True, False, True])
    @patch("hrt.processors.question_processor.logger")
    def test_create_marked_questions_file(self, mock_logger, _, mock_path_touch):
        self.config.get_country_settings.return_value = {
            "question_bank": {
                self.exam_type.id: {"file": "questions_file", "categories_file": "categories_file"}
            }
        }
        self.config.get_input.return_value = {"folder": "some_folder"}

        QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)

        mock_path_touch.assert_called_once()
        mock_logger.warning.assert_called_once_with(
            "Marked questions file not found. Created new file at %s",
            Path(f"some_folder/{self.country.code}/{self.exam_type.id}/marked-questions.txt"),
        )

    @patch("hrt.processors.question_processor.Path.exists", side_effect=[True, True, True, True])
    def test_missing_output_folder(self, _):
        self.config.get_country_settings.return_value = {
            "question_bank": {
                self.exam_type.id: {"file": "questions_file", "categories_file": "categories_file"}
            }
        }
        self.config.get_input.return_value = {"folder": "some_folder"}
        self.config.get_output.return_value = {}

        with self.assertRaises(ValueError) as context:
            QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)
        self.assertEqual(str(context.exception), "Output folder not found in the config file")

    @patch("hrt.processors.question_processor.Path.touch")
    @patch("hrt.processors.question_processor.Path.exists", side_effect=[True, True, True, False])
    @patch("hrt.processors.question_processor.logger.warning")
    def test_create_metrics_file(self, mock_logger_warning, _, mock_path_touch):
        self.config.get_country_settings.return_value = {
            "question_bank": {
                self.exam_type.id: {"file": "questions_file", "categories_file": "categories_file"}
            }
        }
        self.config.get_input.return_value = {"folder": "some_folder"}
        self.config.get_output.return_value = {"folder": "output_folder"}
        self.config.get.return_value = {"folder": "metrics_folder", "file": "metrics_file"}

        QuestionProcessor(self.config, self.country, self.exam_type, self.display_mode)

        mock_path_touch.assert_called_once()
        mock_logger_warning.assert_called_once_with(
            "Metrics file not found. Created new file at %s",
            Path(f"metrics_folder/{self.country.code}/{self.exam_type.id}/metrics_file"),
        )

    @patch(
        "hrt.processors.question_processor.utils.get_header", side_effect=lambda x: f"Header: {x}"
    )
    @patch(
        "hrt.processors.question_processor.get_answers",
        return_value=["1: 1. Answer1", "2: 2. Answer2"],
    )
    def test_process_list_result(self, mock_get_answers, mock_get_header):
        result = [MagicMock(spec=Question), MagicMock(spec=Question)]
        result_text = ["Question1", "Question2"]
        criteria = MagicMock(spec=GeneralQuestionListingType)
        criteria.name = "TestCriteria"

        with patch("sys.stdout", new_callable=unittest.mock.MagicMock()) as mock_stdout:
            self.processor._process_list_result(result, result_text, criteria, save_to_file=False)
            output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
            expected_output = [
                "Header: TestCriteria",
                "Question1",
                "Question2",
                "Header: Answers",
                "1: 1. Answer1",
                "2: 2. Answer2",
                "Count: 2",
            ]
            output = output.split("\n")
            output = list(filter(None, output))
            self.assertEqual(output, expected_output)

    @patch("hrt.processors.question_processor.QuestionProcessor._save_to_file")
    @patch(
        "hrt.processors.question_processor.utils.get_header", side_effect=lambda x: f"Header: {x}"
    )
    @patch(
        "hrt.processors.question_processor.get_answers",
        return_value=["1: 1. Answer1", "2: 2. Answer2"],
    )
    def test_process_list_result_save_to_file(self, _, __, mock_save_to_file):
        result = [MagicMock(spec=Question), MagicMock(spec=Question)]
        result_text = ["Question1", "Question2"]
        criteria = MagicMock(spec=GeneralQuestionListingType)
        criteria.name = "TestCriteria"

        self.processor._process_list_result(result, result_text, criteria, save_to_file=True)

        expected_output = [
            "Header: TestCriteria",
            "Question1",
            "Question2",
            "Header: Answers",
            "1: 1. Answer1",
            "2: 2. Answer2",
            "Count: 2",
        ]

        mock_save_to_file.assert_called_once_with(expected_output, criteria)

    @patch("hrt.processors.question_processor.utils.load_question_metrics", return_value={})
    @patch("hrt.processors.question_processor.QuestionProcessor._process_list_result")
    @patch("hrt.common.question_bank.QuestionBank.get_marked_questions")
    def test_list_marked_sets_question_display(
        self, mock_get_marked_questions, mock_process_list_result, mock_load_question_metrics
    ):
        criteria = MagicMock(spec=MarkedQuestionListingType)
        answer_display = QuestionAnswerDisplay.IN_THE_END
        Question.question_display = None  # Resetting to None for the test 

        mock_process_list_result.return_value = None
        mock_get_marked_questions.return_value = (
            [MagicMock(), MagicMock()],
            ["Question1", "Question2"],
        )

        self.processor.list_marked(criteria, answer_display)

        self.assertIsInstance(Question.question_display, QuestionDisplay)
        self.assertEqual(Question.question_display.answer_display, answer_display)


class TestGetAnswers(unittest.TestCase):
    def setUp(self):
        self.question1 = MagicMock(spec=Question)
        self.question1.question_number = 1
        self.question1.answer_index = 0
        self.question1.answer = "Answer1"

        self.question2 = MagicMock(spec=Question)
        self.question2.question_number = 2
        self.question2.answer_index = 1
        self.question2.answer = "Answer2"

    def test_get_answers_in_the_end(self):
        Question.question_display = MagicMock()
        Question.question_display.answer_display = QuestionAnswerDisplay.IN_THE_END

        questions = [self.question1, self.question2]
        expected_answers = ["1: 1. Answer1", "2: 2. Answer2"]
        self.assertEqual(get_answers(questions), expected_answers)

    def test_get_answers_quiz_in_the_end(self):
        Question.question_display = MagicMock()
        Question.question_display.answer_display = QuizAnswerDisplay.IN_THE_END

        questions = [self.question1, self.question2]
        expected_answers = ["1: 1. Answer1", "2: 2. Answer2"]
        self.assertEqual(get_answers(questions), expected_answers)


if __name__ == "__main__":
    unittest.main()
