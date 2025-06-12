import re
import unittest
from pathlib import Path
from typing import List
from unittest.mock import patch

from hrt.common.enums import (
    CountryCode,
    ExamType,
    GeneralQuestionListingType,
    MarkedQuestionListingType,
    QuestionAnswerDisplay,
    QuestionDisplayMode,
)
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_bank import QuestionBank, process_dict_result
from hrt.common.question_display import QuestionDisplay
from hrt.common.question_metric import QuestionMetric


def _extract_questions_in_result(result) -> List[str]:
    questions_with_choices = []
    for line in result:
        if "Choices: " in line:
            questions_with_choices.append(line)
        elif "\n" in line:
            question_text, choices_text = line.split("\n", 1)
            choices = [
                choice.split(". ", 1)[1].strip() for choice in choices_text.strip().split("\n")
            ]
            sorted_choices = sorted(choices)
            questions_with_choices.append((question_text, sorted_choices))
        else:
            questions_with_choices.append(line)
    return questions_with_choices


class ConcreteQuestionBank(QuestionBank):
    def load_categories(self):
        self._categories = []
        return []

    def load_metrics(self):
        self._metrics = {}
        return []

    def load_questions(self):
        self._questions = [
            Question(
                question_number=QuestionNumber("Q1"),
                question_text="Question 1",
                choices=["A", "B", "C"],
                answer="A",
            ),
            Question(
                question_number=QuestionNumber("Q2"),
                question_text="Question 2",
                choices=["A", "B", "C"],
                answer="B",
            ),
            Question(
                question_number=QuestionNumber("Q3"),
                question_text="Question 3",
                choices=["A", "B", "C"],
                answer="C",
            ),
            Question(
                question_number=QuestionNumber("Q4"),
                question_text="Question 4",
                choices=["A", "B", "C"],
                answer="A",
            ),
        ]
        return self._questions


class TestQuestionBank(unittest.TestCase):
    def setUp(self):
        self.country = CountryCode.CANADA
        self.exam_type = ExamType.BASIC
        self.filepath = Path("dummy_path")
        self.display_mode = QuestionDisplayMode.PRINT
        self.categories_filepath = Path("dummy_categories_path")
        self.marked_questions_filepath = Path("dummy_marked_questions_path")
        self.metrics_filepath = Path("dummy_metrics_path")

        self.question_bank = ConcreteQuestionBank(
            self.country,
            self.exam_type,
            self.filepath,
            self.display_mode,
            self.categories_filepath,
            self.marked_questions_filepath,
            self.metrics_filepath,
        )

        Question.question_display = QuestionDisplay(
            answer_display=QuestionAnswerDisplay.HIDE,
            show_explanation=True,
            show_hints=True,
            show_references=True,
            show_tags=True,
        )

        self.question_bank._metrics = {
            "Q1": QuestionMetric(
                question_number=QuestionNumber("Q1"),
                correct_attempts=3,
                wrong_attempts=1,
                skip_count=0,
            ),
            "Q2": QuestionMetric(
                question_number=QuestionNumber("Q2"),
                correct_attempts=1,
                wrong_attempts=2,
                skip_count=1,
            ),
        }

    def _set_questions(self):
        self.question_bank._questions = [
            Question(
                question_number=QuestionNumber("Q1"),
                question_text="Sample question 1",
                choices=["A", "B"],
                answer="A",
            ),
            Question(
                question_number=QuestionNumber("Q2"),
                question_text="Sample question 2",
                choices=["A", "B"],
                answer="B",
            ),
            Question(
                question_number=QuestionNumber("Q3"),
                question_text="Sample question 3",
                choices=["A", "B"],
                answer="A",
            ),
        ]
        self.question_bank._questions[0].is_marked = True
        self.question_bank._questions[1].is_marked = False
        self.question_bank._questions[2].is_marked = True

    def test_str_method(self):
        self.assertEqual(
            str(self.question_bank),
            "ca - Canada (Supported: True) - basic - Basic exam (Supported: True) (Country: ca - Canada (Supported: True))",
        )

    @patch("hrt.common.utils.read_delim_file", return_value=[["Q1"], ["Q3"]])
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_marked_questions(self, _, __):
        count = self.question_bank.load_marked_questions()
        self.assertEqual(count, 2)
        self.assertTrue(self.question_bank._questions[0].is_marked)
        self.assertFalse(self.question_bank._questions[1].is_marked)
        self.assertTrue(self.question_bank._questions[2].is_marked)

    def test_get_all_questions(self):
        self.question_bank._questions = [
            Question("What is 1+1?", ["2", "3"], "2", QuestionNumber("Q1"))
        ]
        questions = self.question_bank.get_all_questions()
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].question_number, "Q1")

    def test_get_same_answer_questions(self):
        self.question_bank._questions = [
            Question("What is 1+1?", ["2", "3"], "2", QuestionNumber("Q1")),
            Question("What is 2+2?", ["3", "4"], "4", QuestionNumber("Q2")),
            Question("What is 3+3?", ["5", "6"], "6", QuestionNumber("Q3")),
            Question("What is 4+4?", ["7", "8"], "8", QuestionNumber("Q4")),
            Question("What is 5+5?", ["9", "10"], "10", QuestionNumber("Q5")),
        ]
        same_answer_questions = self.question_bank.get_same_answer_questions()
        self.assertEqual(len(same_answer_questions), 0)

    def test_get_random_questions(self):
        self.question_bank._questions = [
            Question("What is 1+1?", ["2", "3"], "2", QuestionNumber("Q1")),
            Question("What is 2+2?", ["3", "4"], "4", QuestionNumber("Q2")),
        ]
        random_questions = self.question_bank.get_random_questions(1, False, [], [])
        self.assertEqual(len(random_questions), 1)

    def test_get_longest_question_text(self):
        self.question_bank._questions = [
            Question("What is 1+1?", ["2", "3"], "2", QuestionNumber("Q1")),
            Question("What is the sum of 2 and 2?", ["3", "4"], "4", QuestionNumber("Q2")),
        ]
        longest_questions = self.question_bank.get_longest_question_text(1)
        self.assertEqual(len(longest_questions), 1)
        self.assertEqual(longest_questions[0].question_number, "Q2")

    def test_process_dict_result_same_answer(self):
        criteria = GeneralQuestionListingType.SAME_ANSWER
        result = {
            "Answer1": [
                Question(
                    "Question text 1",
                    ["Choice1", "Choice2", "Answer1"],
                    "Answer1",
                    QuestionNumber("Q1"),
                )
            ],
            "Answer2": [
                Question(
                    "Question text 2",
                    ["Choice1", "Choice2", "Answer2"],
                    "Answer2",
                    QuestionNumber("Q2"),
                )
            ],
        }
        expected_output = [
            "Answer: Answer1",
            "Q1: Question text 1\n    1. Choice1\n    2. Choice2\n    3. Answer1\n",
            "Answer: Answer2",
            "Q2: Question text 2\n    1. Choice1\n    2. Choice2\n    3. Answer2\n",
        ]
        result = process_dict_result(criteria, result)

        # extract questions with choices for comparison
        questions_with_choices = _extract_questions_in_result(result)
        expected_questions_with_choices = _extract_questions_in_result(expected_output)

        self.assertEqual(questions_with_choices, expected_questions_with_choices)

    def test_process_dict_result_same_choices(self):
        criteria = GeneralQuestionListingType.SAME_CHOICES
        result = {
            ("Choice1", "Choice2"): [
                Question(
                    "Question text 1",
                    ["Choice1", "Choice2", "Answer1"],
                    "Answer1",
                    QuestionNumber("Q1"),
                )
            ]
        }
        expected_output = [
            "Choices: ('Choice1', 'Choice2')",
            "Q1: Question text 1\n    1. Answer1\n    2. Choice1\n    3. Choice2\n",
        ]
        result = process_dict_result(criteria, result)

        # extract questions with choices for comparison
        questions_with_choices = _extract_questions_in_result(result)
        expected_questions_with_choices = _extract_questions_in_result(expected_output)

        self.assertEqual(questions_with_choices, expected_questions_with_choices)

    def test_process_dict_result_qn_answer(self):
        criteria = GeneralQuestionListingType.QN_ANSWER
        result = {"Q1": "Answer1", "Q2": "Answer2"}
        expected_output = ["Q1: Answer1", "Q2: Answer2"]
        assert process_dict_result(criteria, result) == expected_output

    def test_get_random_quiz_questions(self):
        random_questions = self.question_bank.get_random_quiz_questions(2)
        self.assertEqual(len(random_questions), 2)
        for question in random_questions:
            self.assertIn(question, self.question_bank.questions)

    def test_get_two_or_more_same_choices_questions(self):
        result = self.question_bank.get_two_or_more_same_choices_questions()
        all_qnums = [q.question_number for q in result]
        self.assertIn("Q1", all_qnums)
        self.assertIn("Q2", all_qnums)
        self.assertIn("Q3", all_qnums)
        self.assertIn("Q4", all_qnums)

        dict_result = self.question_bank._get_two_or_more_same_choices_dict()
        self.assertTrue(len(dict_result) > 0)
        all_keys_qnums = [q.question_number for q in dict_result.keys()]
        self.assertTrue(any(qn in all_keys_qnums for qn in ["Q1", "Q2", "Q3", "Q4"]))

    def test_get_questions(self):
        criteria = GeneralQuestionListingType.SAME_ANSWER
        result, result_text = self.question_bank.get_questions(criteria)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result_text, list)

    def test_get_questions_invalid_criteria(self):
        with self.assertRaises(ValueError) as context:
            self.question_bank.get_questions("INVALID_CRITERIA")
        self.assertEqual(str(context.exception), "Method for Criteria INVALID_CRITERIA not found")

    def test_get_questions_with_same_choices(self):
        result, result_text = self.question_bank.get_questions(
            GeneralQuestionListingType.TWO_OR_MORE_SAME_CHOICES
        )
        pattern = re.compile(r"Q1, Q2, Q3")
        self.assertTrue(any(pattern.search(text) for text in result_text))

    def test_get_qnum_answer_questions(self):
        result, result_text = self.question_bank.get_questions(
            GeneralQuestionListingType.QN_ANSWER
        )
        self.assertIn("Q1: A", result_text)
        self.assertIn("Q2: B", result_text)
        self.assertIn("Q3: C", result_text)

    @patch("hrt.common.question_bank.QuestionBank.load_questions")
    @patch("hrt.common.question_bank.QuestionBank.load_categories")
    @patch("hrt.common.question_bank.QuestionBank.load_metrics")
    @patch("hrt.common.question_bank.QuestionBank.load_marked_questions")
    def test_get_questions_process_list_result(
        self, mock_load_marked, mock_load_metrics, mock_load_categories, mock_load_questions
    ):
        mock_load_questions.return_value = [
            Question(
                question_number=QuestionNumber("Q1"),
                question_text="Sample question",
                choices=["A", "B"],
                answer="A",
            )
        ]
        mock_load_categories.return_value = []
        mock_load_metrics.return_value = {}
        mock_load_marked.return_value = 0

        qb = ConcreteQuestionBank(
            country=CountryCode.CANADA,
            exam_type=ExamType.BASIC,
            filepath=Path("/path/to/questions"),
        )
        result, result_text = qb.get_questions(GeneralQuestionListingType.ALL)

        self.assertEqual(len(result), 4)

    def test_get_marked_questions(self):
        self.question_bank._metrics = {
            "1": QuestionMetric(
                question_number=QuestionNumber("1"),
                correct_attempts=3,
                wrong_attempts=1,
                skip_count=0,
            ),
            "2": QuestionMetric(
                question_number=QuestionNumber("2"),
                correct_attempts=1,
                wrong_attempts=2,
                skip_count=1,
            ),
        }
        criteria = MarkedQuestionListingType.CORRECT_ANSWER
        result, result_text = self.question_bank.get_marked_questions(
            criteria, list(self.question_bank._metrics.values()), 2
        )
        self.assertIsInstance(result, list)
        self.assertIsInstance(result_text, list)

    def test_get_marked_questions_wrong_attempt(self):
        metrics = [
            QuestionMetric(
                question_number=QuestionNumber("Q1"),
                correct_attempts=3,
                wrong_attempts=1,
                skip_count=0,
            ),
            QuestionMetric(
                question_number=QuestionNumber("Q2"),
                correct_attempts=2,
                wrong_attempts=2,
                skip_count=1,
            ),
            QuestionMetric(
                question_number=QuestionNumber("Q3"),
                correct_attempts=1,
                wrong_attempts=3,
                skip_count=2,
            ),
        ]
        result, _ = self.question_bank.get_marked_questions(
            MarkedQuestionListingType.WRONG_ATTEMPT, metrics, 2
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].question_number, "Q2")
        self.assertEqual(result[1].question_number, "Q3")

    def test_get_marked_questions_skipped(self):
        metrics = [
            QuestionMetric(
                question_number=QuestionNumber("Q1"),
                correct_attempts=3,
                wrong_attempts=1,
                skip_count=0,
            ),
            QuestionMetric(
                question_number=QuestionNumber("Q2"),
                correct_attempts=2,
                wrong_attempts=2,
                skip_count=1,
            ),
            QuestionMetric(
                question_number=QuestionNumber("Q3"),
                correct_attempts=1,
                wrong_attempts=3,
                skip_count=2,
            ),
        ]
        result, _ = self.question_bank.get_marked_questions(
            MarkedQuestionListingType.SKIPPED, metrics, 1
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].question_number, "Q2")
        self.assertEqual(result[1].question_number, "Q3")

    def test_get_marked_questions_invalid_criteria(self):
        with self.assertRaises(ValueError) as context:
            self.question_bank.get_marked_questions("INVALID_CRITERIA", [], 0)
        self.assertEqual(str(context.exception), "Criteria INVALID_CRITERIA not found")

    def test_get_same_choices_questions(self):
        self.question_bank._questions = [
            Question("What is 1+1?", ["A", "B", "C"], "A", QuestionNumber("Q1")),
            Question("What is 2+2?", ["A", "B", "C"], "B", QuestionNumber("Q2")),
            Question("What is 3+3?", ["A", "B", "C"], "C", QuestionNumber("Q3")),
            Question("What is 4+4?", ["A", "B", "C"], "A", QuestionNumber("Q4")),
        ]
        result = self.question_bank.get_same_choices_questions()
        self.assertEqual(len(result), 4)

        # Check if all questions have the expected choices
        for question in result:
            self.assertEqual(sorted(question.choices), ["A", "B", "C"])

        dict_result = self.question_bank._get_same_choices_dict()
        self.assertIn(("A", "B", "C"), dict_result)
        self.assertEqual(len(dict_result[("A", "B", "C")]), 4)

    def test_get_longest_correct_choice(self):
        self.question_bank._questions = [
            Question(
                question_number=QuestionNumber("1"),
                question_text="Question 1",
                choices=["A", "B", "C"],
                answer="A",
            ),
            Question(
                question_number=QuestionNumber("2"),
                question_text="Question 2",
                choices=["A", "BB", "C"],
                answer="BB",
            ),
            Question(
                question_number=QuestionNumber("3"),
                question_text="Question 3",
                choices=["A", "B", "CCC"],
                answer="CCC",
            ),
        ]
        result = self.question_bank.get_longest_correct_choice(3)
        self.assertEqual(result[0].answer, "CCC")
        self.assertEqual(result[1].answer, "BB")
        self.assertEqual(result[2].answer, "A")

    def test_get_marked_questions_filepath(self):
        self.assertEqual(
            self.question_bank.get_marked_questions_filepath(), "dummy_marked_questions_path"
        )

    def test_get_all_marked_questions(self):
        self._set_questions()
        marked_questions = self.question_bank.get_all_marked_questions()
        self.assertEqual(len(marked_questions), 2)
        self.assertEqual(marked_questions[0].question_number, "Q1")

    @patch("hrt.common.question_bank.logger")
    def test_get_random_quiz_questions_more_than_available(self, mock_logger):
        result = self.question_bank.get_random_quiz_questions(5)
        mock_logger.warning.assert_called_once_with(
            "Number of questions requested %d is greater than available questions %d", 5, 4
        )
        self.assertEqual(len(result), 4)

    def test_get_random_questions_include_marked(self):
        self._set_questions()
        included_questions = ["Q1", "Q2"]
        excluded_questions = ["Q3"]

        result = self.question_bank.get_random_questions(
            number_of_questions=2,
            include_marked=True,
            included_questions=included_questions,
            excluded_questions=excluded_questions,
        )
        self.assertEqual(len(result), 1)
        for question in result:
            self.assertTrue(question.is_marked)
            self.assertIn(question.question_number, included_questions)
            self.assertNotIn(question.question_number, excluded_questions)


if __name__ == "__main__":
    unittest.main()
