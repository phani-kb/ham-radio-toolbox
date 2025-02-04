import unittest
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_metric import QuestionMetric


class TestQuestionMetric(unittest.TestCase):
    def setUp(self):
        self.question_number = QuestionNumber("1")
        self.metric = QuestionMetric(self.question_number)

    def test_initial_values(self):
        self.assertEqual(self.metric.question_number, self.question_number)
        self.assertEqual(self.metric.correct_attempts, 0)
        self.assertEqual(self.metric.wrong_attempts, 0)
        self.assertEqual(self.metric.skip_count, 0)

    def test_set_correct_attempts(self):
        self.metric.correct_attempts = 5
        self.assertEqual(self.metric.correct_attempts, 5)

    def test_set_wrong_attempts(self):
        self.metric.wrong_attempts = 3
        self.assertEqual(self.metric.wrong_attempts, 3)

    def test_set_skip_count(self):
        self.metric.skip_count = 2
        self.assertEqual(self.metric.skip_count, 2)

    def test_equality(self):
        other_metric = QuestionMetric(self.question_number)
        self.assertEqual(self.metric, other_metric)

    def test_hash(self):
        self.assertEqual(hash(self.metric), hash(self.question_number))

    def test_str(self):
        self.assertEqual(str(self.metric), "1: 0, 0, 0")


if __name__ == "__main__":
    unittest.main()
