import unittest
from unittest.mock import MagicMock
from hrt.processors.base_processor import BaseProcessor


class TestBaseProcessor(unittest.TestCase):
    def setUp(self):
        self.config_reader = MagicMock()
        self.processor = BaseProcessor(self.config_reader)

    def test_initialization(self):
        self.assertEqual(self.processor.config_reader, self.config_reader)
        self.assertIsNotNone(self.processor.logger)

    def test_generate_questions(self):
        self.processor.generate_questions()

    def test_evaluate_answer(self):
        self.processor.evaluate_answer("question", "answer")

    def test_provide_feedback(self):
        self.processor.provide_feedback("question", "answer", True)


if __name__ == "__main__":
    unittest.main()
