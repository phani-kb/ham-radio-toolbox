import unittest

from hrt.common.enums import QuestionAnswerDisplay
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question_category import QuestionCategory
from hrt.common.question_display import QuestionDisplay
from hrt.common.question_metric import QuestionMetric
from hrt.common.question import Question


class TestQuestion(unittest.TestCase):
    def setUp(self):
        self.question_text = "What is the capital of France?"
        self.choices = ["Paris", "London", "Berlin", "Madrid"]
        self.answer = "Paris"
        self.question_number = QuestionNumber("1")
        self.category = QuestionCategory("001", "Geography")
        self.metric = QuestionMetric(self.question_number)

    def test_question_initialization(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertEqual(question.question_text, self.question_text)
        self.assertIn(self.answer, question.choices)
        self.assertEqual(question.answer, self.answer)
        self.assertEqual(question.question_number, self.question_number)
        self.assertEqual(question.category, self.category)
        self.assertEqual(question.metric, self.metric)

    def test_question_format(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question.question_display = QuestionDisplay(
            answer_display=QuestionAnswerDisplay.WITH_QUESTION
        )
        formatted_question = question.format()
        self.assertIn(self.question_text, formatted_question)
        self.assertIn(self.answer, formatted_question)

    def test_question_format_quiz(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        formatted_quiz_question = question.format_quiz_question()
        self.assertIn(self.question_text, formatted_quiz_question)
        self.assertIn(Question.SKIP_CHOICE, formatted_quiz_question)

    def test_question_equality(self):
        question1 = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question2 = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertEqual(question1, question2)

    def test_question_hash(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertEqual(hash(question), hash(self.question_number))

    def test_question_invalid_answer(self):
        with self.assertRaises(ValueError) as context:
            Question(
                question_text=self.question_text,
                choices=self.choices,
                answer="Invalid Answer",
                question_number=self.question_number,
                category=self.category,
                metric=self.metric,
            )
        self.assertEqual(str(context.exception), "Answer is not in the choices")

    def test_question_default_metric(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
        )
        self.assertIsInstance(question.metric, QuestionMetric)
        self.assertEqual(question.metric.question_number, self.question_number)

    def test_is_marked_getter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertFalse(question.is_marked)  # Default value should be False

    def test_is_marked_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question.is_marked = True
        self.assertTrue(question.is_marked)
        question.is_marked = False
        self.assertFalse(question.is_marked)

    def test_correct_attempts_getter_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question.correct_attempts = 5
        self.assertEqual(question.correct_attempts, 5)

    def test_wrong_attempts_getter_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question.wrong_attempts = 3
        self.assertEqual(question.wrong_attempts, 3)

    def test_skip_count_getter_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        question.skip_count = 2
        self.assertEqual(question.skip_count, 2)

    def test_category_getter_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        new_category = QuestionCategory("002", "History")
        question.category = new_category
        self.assertEqual(question.category, new_category)

    def test_metric_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        new_metric = QuestionMetric(self.question_number)
        question.metric = new_metric
        self.assertEqual(question.metric, new_metric)

    def test_question_number_setter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        new_question_number = QuestionNumber("2")
        question.question_number = new_question_number
        self.assertEqual(question.question_number, new_question_number)

    def test_answer_index_getter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertEqual(question.answer_index, question.choices.index(self.answer))

    def test_existing_metric_getter(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        self.assertEqual(question.existing_metric, self.metric)

    def test_quiz_choices(self):
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        expected_choices = self.choices + [Question.SKIP_CHOICE]
        self.assertEqual(question.quiz_choices, expected_choices)

    def test_equals_non_question(self):
        """Test equals with a non-Question object."""
        question = Question(
            question_text=self.question_text,
            choices=self.choices,
            answer=self.answer,
            question_number=self.question_number,
            category=self.category,
            metric=self.metric,
        )
        other = "not a question"
        self.assertNotEqual(question, other)


if __name__ == "__main__":
    unittest.main()
