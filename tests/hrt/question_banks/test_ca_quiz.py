import unittest
from unittest.mock import patch
from hrt.question_banks.ca_quiz import CAQuiz
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.question import Question


class TestCAQuiz(unittest.TestCase):
    def setUp(self):
        self.questions = [
            Question("Question 1", ["Choice 1", "Choice 2", "Choice 3", "Choice 4"], "Choice 1"),
            Question("Question 2", ["Choice A", "Choice B", "Choice C", "Choice D"], "Choice A"),
        ]
        self.quiz_config = {
            "mark_wrong_answers": True,
            "show_explanation": True,
            "show_hints": True,
            "show_references": True,
            "show_tags": True,
            "show_marked_status": True,
            "show_metrics": True,
        }
        self.quiz = CAQuiz(
            number_of_questions=2,
            questions=self.questions,
            exam_type=ExamType.BASIC,
            display_mode=QuestionDisplayMode.PRINT,
            answer_display=QuizAnswerDisplay.AFTER_QUESTION,
            quiz_config=self.quiz_config,
        )

    @patch("hrt.common.quiz.Quiz.validate_exam_type")
    def test_pre_process(self, mock_validate_exam_type):
        self.quiz.pre_process()
        mock_validate_exam_type.assert_called_once_with(CountryCode.CANADA)

    @patch("hrt.common.quiz.Quiz.get_number_of_questions", return_value=2)
    @patch("hrt.common.quiz.Quiz.get_results", return_value=(2, 0, 0))
    @patch("hrt.common.quiz.Quiz.get_duration", return_value=120)
    @patch("builtins.print")
    def test_post_process(
        self, mock_print, mock_get_duration, mock_get_results, mock_get_number_of_questions
    ):
        self.quiz.post_process()
        mock_print.assert_any_call("Attempted: 2 out of 2")
        mock_print.assert_any_call("You got 2 out of 2 correct. Duration: 120 seconds")
        mock_print.assert_any_call("Percentage: 100% Pass with Honours")

    @patch("hrt.common.quiz.Quiz.start")
    def test_start(self, mock_start):
        self.quiz.start()
        mock_start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
