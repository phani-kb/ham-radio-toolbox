import unittest
from unittest.mock import patch

import pytest

from hrt.question_banks.us_quiz import USQuiz
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.question import Question


class TestUSQuiz(unittest.TestCase):
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
        self.quiz = USQuiz(
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
        mock_validate_exam_type.assert_called_once_with(CountryCode.UNITED_STATES)

    def test_post_process(self):
        self.quiz.post_process()

    def test_start(self):
        with pytest.raises(NotImplementedError, match=r"USQuiz\.start\(\) not supported yet"):
            self.quiz.start()


if __name__ == "__main__":
    unittest.main()
