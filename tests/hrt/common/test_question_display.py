import unittest
from hrt.common.enums import QuestionAnswerDisplay, QuizAnswerDisplay, QuestionDisplayMode
from hrt.common.question_display import (
    QuestionDisplay,
    QuizQuestionDisplay,
    QuestionDisplayModeFactory,
)


class TestQuestionDisplay(unittest.TestCase):
    def setUp(self):
        self.default_question_display_values = {
            "answer_display": QuestionAnswerDisplay.WITH_QUESTION,
            "show_explanation": False,
            "show_hints": False,
            "show_references": False,
            "show_tags": False,
            "show_marked_status": True,
            "show_metrics": False,
        }

        self.default_quiz_question_display_values = {
            "answer_display": QuizAnswerDisplay.AFTER_QUESTION,
            "show_explanation": False,
            "show_hints": False,
            "show_references": False,
            "show_tags": False,
            "show_marked_status": True,
            "show_metrics": False,
        }

    def assert_display_values(self, display, expected_values):
        self.assertEqual(display.answer_display, expected_values["answer_display"])
        self.assertEqual(display.show_explanation, expected_values["show_explanation"])
        self.assertEqual(display.show_hints, expected_values["show_hints"])
        self.assertEqual(display.show_references, expected_values["show_references"])
        self.assertEqual(display.show_tags, expected_values["show_tags"])
        self.assertEqual(display.show_marked_status, expected_values["show_marked_status"])
        self.assertEqual(display.show_metrics, expected_values["show_metrics"])

    def test_default_question_display1(self):
        display = QuestionDisplay()
        self.assert_display_values(display, self.default_question_display_values)

    def test_setters(self):
        display = QuestionDisplay()
        display.show_explanation = True
        display.show_hints = True
        display.show_references = True
        display.show_tags = True
        display.show_marked_status = False
        display.show_metrics = True

        self.assertTrue(display.show_explanation)
        self.assertTrue(display.show_hints)
        self.assertTrue(display.show_references)
        self.assertTrue(display.show_tags)
        self.assertFalse(display.show_marked_status)
        self.assertTrue(display.show_metrics)

    def test_str_method(self):
        display = QuestionDisplay()
        expected_str = (
            "Answer Display: with-question - With question, Show Hints: False, "
            "Show References: False, Show Tags: False, Marked Status: True, Show Metrics: False"
        )
        self.assertEqual(str(display), expected_str)

    def test_answer_display_setter(self):
        display = QuestionDisplay()
        display.answer_display = QuestionAnswerDisplay.IN_THE_END
        self.assertEqual(display.answer_display, QuestionAnswerDisplay.IN_THE_END)

    def test_default_quiz_question_display2(self):
        display = QuizQuestionDisplay()
        self.assert_display_values(display, self.default_quiz_question_display_values)


class TestQuestionDisplayModeFactory(unittest.TestCase):
    def test_get_question_display_mode_print(self):
        display = QuestionDisplayModeFactory.get_question_display_mode(QuestionDisplayMode.PRINT)
        self.assertIsInstance(display, QuestionDisplay)

    def test_get_question_display_mode_quiz(self):
        display = QuestionDisplayModeFactory.get_question_display_mode(QuestionDisplayMode.QUIZ)
        self.assertIsInstance(display, QuizQuestionDisplay)

    def test_invalid_display_mode(self):
        with self.assertRaises(ValueError):
            QuestionDisplayModeFactory.get_question_display_mode("INVALID_MODE")


if __name__ == "__main__":
    unittest.main()
