import unittest
from unittest.mock import MagicMock
from hrt.processors.country_processor import CountrySpecificProcessor


class TestCountrySpecificProcessor(unittest.TestCase):
    def setUp(self):
        self.config_reader = MagicMock()
        self.question_bank = MagicMock()
        self.country_code = "US"
        self.processor = CountrySpecificProcessor(
            self.config_reader, self.country_code, self.question_bank
        )

    def test_initialization(self):
        self.assertEqual(self.processor.config_reader, self.config_reader)
        self.assertEqual(self.processor.country_code, self.country_code)
        self.assertEqual(self.processor.question_bank, self.question_bank)

    def test_evaluate_answer(self):
        question = {"answer": "correct_answer"}
        self.assertTrue(self.processor.evaluate_answer(question, "correct_answer"))
        self.assertFalse(self.processor.evaluate_answer(question, "wrong_answer"))

    def test_provide_feedback(self):
        question = {"answer": "correct_answer"}
        self.assertEqual(
            self.processor.provide_feedback(question, "correct_answer", True),
            "Correct! Well done.",
        )
        self.assertEqual(
            self.processor.provide_feedback(question, "wrong_answer", False),
            "Sorry, the correct answer is: correct_answer",
        )

    def test_get_country_code(self):
        self.assertEqual(self.processor.get_country_code(), self.country_code)

    def test_quiz(self):
        self.processor.quiz(self.question_bank, self.config_reader)

    def test_practice_exam(self):
        self.processor.practice_exam(self.question_bank, self.config_reader)


if __name__ == "__main__":
    unittest.main()
