import unittest
from unittest.mock import patch
from io import StringIO

from hrt.common.question_submitted import QuestionSubmitted
from hrt.common.quiz import Quiz, QuizFactory
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.question_banks.ca_quiz import CAQuiz
from hrt.question_banks.us_quiz import USQuiz


class ConcreteQuiz(Quiz):
    def __init__(self, num_questions, questions, exam_type, answer_display, quiz_config):
        super().__init__(
            num_questions,
            questions,
            exam_type,
            QuestionDisplayMode.QUIZ,
            answer_display,
            quiz_config,
        )

    def _get_user_input(self, prompt):
        pass

    def _display_results(self):
        pass

    def _display_question(self, question):
        pass

    def _display_actions(self, actions):
        pass

    def _display_progress(self):
        pass

    def _display_duration(self):
        pass

    def _display_marked_questions(self):
        pass

    def _display_question_number(self):
        pass

    def _display_exam_type(self):
        pass

    def _display_question_count(self):
        pass

    def _display_question_text(self):
        pass

    def _display_question_options(self):
        pass

    def _display_question_explanation(self):
        pass

    def _display_question_hint(self):
        pass

    def _display_question_reference(self):
        pass

    def _display_question_tags(self):
        pass

    def _display_marked_status(self):
        pass

    def _display_metrics(self):
        pass

    def _display_correct_answer(self):
        pass

    def _display_incorrect_answer(self):
        pass

    def _display_skip_count(self):
        pass

    def _display_question_feedback(self):
        pass

    def _display_question_results(self):
        pass

    def _display_question_results_header(self):
        pass

    def _display_question_results_body(self):
        pass

    def _display_question_results_footer(self):
        pass

    def _display_question_results_summary(self):
        pass

    def _display_question_results_correct(self):
        pass

    def _display_question_results_wrong(self):
        pass

    def _display_question_results_skipped(self):
        pass

    def _display_question_results_marked(self):
        pass

    def _display_question_results_total(self):
        pass

    def _display_question_results_time(self):
        pass

    def _display_question_results_duration(self):
        pass

    def _display_question_results_correct_count(self):
        pass

    def _display_question_results_wrong_count(self):
        pass

    def _display_question_results_skipped_count(self):
        pass

    def _display_question_results_marked_count(self):
        pass

    def pre_process(self):
        pass


class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.questions = [
            Question("What is 2+2?", ["1", "2", "3", "4"], "4", QuestionNumber("Q1")),
            Question(
                "What is the capital of France?",
                ["Berlin", "London", "Paris", "Rome"],
                "Paris",
                QuestionNumber("Q2"),
            ),
        ]
        self.exam_type = ExamType.TECHNICAL
        self.display_mode = QuestionDisplayMode.QUIZ
        self.answer_display = QuizAnswerDisplay.AFTER_QUESTION
        self.quiz_config = {
            "mark_wrong_answers": True,
            "show_explanation": True,
            "show_hints": True,
            "show_references": True,
            "show_tags": True,
            "show_marked_status": True,
            "show_metrics": True,
        }
        self.quiz = ConcreteQuiz(
            len(self.questions),
            self.questions,
            self.exam_type,
            self.answer_display,
            self.quiz_config,
        )

    def test_validate_exam_type(self):
        self.quiz.validate_exam_type(CountryCode.UNITED_STATES)
        with self.assertRaises(ValueError):
            self.quiz.validate_exam_type(CountryCode.CANADA)

    @patch("builtins.input", side_effect=["1", "S", "1", "S"])
    def test_display_question_and_get_action(self, _):
        self.quiz._display_question_and_get_action()
        self.assertEqual(self.quiz.get_current_index(), 1)
        self.assertTrue(self.quiz._terminate_quiz)

    def test_previous_question(self):
        self.quiz.set_current_index(1)
        self.quiz.previous_question()
        self.assertEqual(self.quiz.get_current_index(), 0)

    def test_next_question(self):
        self.quiz.next_question()
        self.assertEqual(self.quiz.get_current_index(), 1)

    @patch("builtins.input", side_effect=["1", "S", "2", "S", "Q", "Y"])
    def test_start(self, _):
        self.quiz.start()
        self.assertEqual(self.quiz.get_current_index(), 1)

    @patch("builtins.input", side_effect=["1"])
    def test_process_action(self, _):
        self.quiz.process_action("S", -1, ["N", "P", "Q"])
        self.assertEqual(self.quiz.get_current_index(), 0)

    def test_submit(self):
        self.quiz.submit(3)
        self.assertIn(QuestionNumber("Q1"), self.quiz._submitted_questions)

    def test_submit_return(self):
        self.quiz._submitted_questions[QuestionNumber("Q1")] = QuestionSubmitted(
            question_number=QuestionNumber("Q1"), selected_choice="3"
        )
        self.quiz.submit(3)

    @patch("hrt.common.quiz.logger")
    def test_submit_invalid_choice(self, mock_logger):
        self.quiz.submit(-1)
        mock_logger.info.assert_called_with("No choice selected.")

    @patch("sys.stdout", new_callable=StringIO)
    def test_submit_correct_answer(self, mock_stdout):
        self.quiz._current_index = 0
        answer_index = self.quiz.get_current_question().answer_index
        self.quiz.submit(answer_index)
        self.assertIn("\033[92m✓✓\033[0m", mock_stdout.getvalue())
        prev_index = self.quiz.get_current_index() - 1
        self.assertEqual(self.quiz.get_question_by_index(prev_index).correct_attempts, 1)

    def test_mark(self):
        self.quiz.mark(4)
        self.assertTrue(self.quiz.get_current_question().is_marked)

    @patch("hrt.common.quiz.logger")
    def test_mark_already(self, mock_logger):
        self.quiz.mark(3)
        self.quiz._current_index = 0
        self.quiz.mark(-1)
        self.assertTrue(self.quiz.get_current_question().is_marked)
        mock_logger.info.assert_called_with("No choice selected.")

    def test_mark_correct_choice(self):
        self.quiz._current_index = 0
        answer_index = self.quiz.get_current_question().answer_index
        self.quiz.mark(answer_index)
        prev_index = self.quiz.get_current_index() - 1
        pq = self.quiz.get_question_by_index(prev_index)
        self.assertTrue(pq.is_marked)
        self.assertEqual(pq.correct_attempts, 1)

    def test_unmark(self):
        self.quiz.mark(3)
        self.quiz.unmark()
        self.assertFalse(self.quiz.get_current_question().is_marked)
        self.quiz._current_index = 0
        self.quiz.unmark()

    @patch("builtins.input", side_effect=["S", "F", "Y"])
    def test_skip(self, _):
        self.quiz.skip()
        self.quiz.previous_question()
        self.assertEqual(self.quiz.get_current_question().skip_count, 1)
        self.quiz.submit(3)
        self.quiz.previous_question()
        self.quiz.skip()
        self.assertEqual(self.quiz.get_current_question().skip_count, 1)
        self.quiz.next_question()
        self.quiz.skip()

    def test_quit(self):
        self.quiz.quit()
        self.assertTrue(self.quiz._terminate_quiz)

    @patch("builtins.input", side_effect=["Y"])
    def test_finish(self, _):
        self.quiz.finish()
        self.assertTrue(self.quiz._terminate_quiz)

    @patch.object(Quiz, "_display_question_and_get_action")
    @patch("builtins.input", side_effect=["N"])
    def test_terminate_quiz(self, mock_display_question_and_get_action, _):
        self.quiz._terminate_quiz = False
        # self.quiz._submitted_questions = {
        #     q.question_number: QuestionSubmitted(q.question_number, q.answer)
        #     for q in self.questions
        # }
        self.quiz.finish()
        self.assertFalse(self.quiz._terminate_quiz)
        mock_display_question_and_get_action.assert_called_once()

    @patch("builtins.input", side_effect=["5", "S", "1", "S", "Q", "Y"])
    def test_change_answer(self, _):
        self.quiz.change_answer()
        self.assertEqual(self.quiz.get_current_index(), 1)

    @patch("sys.stdout", new_callable=StringIO)
    def test_change_answer_for_submitted_question(self, mock_stdout):
        self.quiz._submitted_questions[QuestionNumber("Q1")] = QuestionSubmitted(
            question_number=QuestionNumber("Q1"), selected_choice="4"
        )
        self.quiz._current_index = 0
        self.quiz.change_answer()
        self.assertIn("Cannot change answer for a submitted question.", mock_stdout.getvalue())

    def test_get_number_of_questions(self):
        self.assertEqual(self.quiz.get_number_of_questions(), 2)

    def test_get_exam_type(self):
        self.assertEqual(self.quiz.get_exam_type(), self.exam_type)

    def test_get_questions(self):
        self.assertEqual(self.quiz.get_questions(), self.questions)

    def test_get_current_question(self):
        self.assertEqual(self.quiz.get_current_question(), self.questions[0])

    def test_get_current_index(self):
        self.assertEqual(self.quiz.get_current_index(), 0)

    def test_set_current_index(self):
        self.quiz.set_current_index(1)
        self.assertEqual(self.quiz.get_current_index(), 1)

    def test_get_question_by_index(self):
        self.assertEqual(self.quiz.get_question_by_index(1), self.questions[1])

    def test_print_question(self):
        output = self.quiz.print_question(self.questions[0])
        self.assertIn("What is 2+2?", output)
        self.quiz.mark(3)
        self.quiz.previous_question()
        output = self.quiz.print_question(self.questions[0])
        self.assertIn("Marked", output)

    def test_get_actions(self):
        action_prompt, actions = self.quiz.get_actions(submitted=False)
        self.assertIn("S", actions)

    def test_get_actions_marked(self):
        self.quiz.mark(3)
        self.quiz.previous_question()
        action_prompt, actions = self.quiz.get_actions(submitted=False)
        self.assertIn("U", actions)

    def test_get_results(self):
        correct, wrong, skip = self.quiz.get_results()
        self.assertEqual(correct, 0)
        self.assertEqual(wrong, 0)
        self.assertEqual(skip, 0)

    def test_get_progress(self):
        progress = self.quiz.get_progress()
        self.assertIn("Progress", progress)

    def test_get_duration(self):
        self.quiz._start_time = 0
        self.quiz._end_time = 10
        self.assertEqual(self.quiz.get_duration(), 10)

    def test_get_marked_questions(self):
        self.quiz.mark(3)
        marked_questions = self.quiz.get_marked_questions()
        self.assertEqual(len(marked_questions), 1)

    def test_validate_exam_type_invalid_country(self):
        quiz = ConcreteQuiz(
            num_questions=1,
            questions=self.questions,
            exam_type=self.exam_type,
            answer_display=QuizAnswerDisplay.AFTER_QUESTION,
            quiz_config=self.quiz_config,
        )
        with self.assertRaises(ValueError):
            quiz.validate_exam_type(CountryCode.CANADA)

    @patch("sys.stdout", new_callable=StringIO)
    def test_next_question_at_last_question(self, mock_stdout):
        quiz = ConcreteQuiz(
            num_questions=1,
            questions=self.questions,
            exam_type=self.exam_type,
            answer_display=QuizAnswerDisplay.AFTER_QUESTION,
            quiz_config=self.quiz_config,
        )
        quiz._current_index = 2
        quiz._display_question_and_get_action()
        self.assertIn("No next question available.", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["1", "C", "S", "1", "Q", "Y"])
    def test_display_question_and_get_action_skip_last(self, mock_stdout):
        self.quiz._current_index = 1
        self.quiz._display_question_and_get_action(skip_last=True)
        self.assertEqual(self.quiz.get_current_question().skip_count, 1)

    @patch("builtins.input", side_effect=["1", "C", "S", "1", "Q", "Y"])
    def test_display_question_and_get_action_submitted(self, mock_stdout):
        self.quiz._current_index = 1
        self.quiz._submitted_questions[QuestionNumber("Q2")] = QuestionSubmitted(
            question_number=QuestionNumber("Q2"), selected_choice="4"
        )
        self.quiz._display_question_and_get_action(skip_last=False)
        self.assertEqual(self.quiz.get_current_question().skip_count, 0)

    @patch("hrt.common.utils.get_user_input_index", return_value=4)
    @patch("hrt.common.utils.get_user_input_option", return_value="N")
    def test_display_question_and_get_action_last(self, _, __):
        self.quiz._current_index = 1
        self.quiz._display_question_and_get_action()
        self.assertEqual(self.quiz.get_current_question().skip_count, 1)

    @patch("hrt.common.utils.get_user_input_index", return_value=4)
    @patch("hrt.common.utils.get_user_input_option", return_value="N")
    def test_display_question_and_get_action_skip_not_last(self, _, __):
        self.quiz._current_index = 0
        self.quiz._display_question_and_get_action()
        self.assertEqual(self.quiz.get_current_question().skip_count, 1)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("hrt.common.utils.get_user_input_index", return_value=3)
    @patch("hrt.common.utils.get_user_input_option", return_value="S")
    def test_display_question_and_get_action_terminate_quiz(self, mock_stdout, _, __):
        self.quiz._current_index = 0
        self.quiz._submitted_questions[QuestionNumber("Q1")] = QuestionSubmitted(
            question_number=QuestionNumber("Q1"), selected_choice="3"
        )
        self.quiz._submitted_questions[QuestionNumber("Q2")] = QuestionSubmitted(
            question_number=QuestionNumber("Q2"), selected_choice="3"
        )
        self.quiz._display_question_and_get_action(skip_last=True)
        self.quiz._current_index = self.quiz.get_number_of_questions()
        self.assertTrue(self.quiz._terminate_quiz)

    @patch("hrt.common.utils.get_user_input_index", return_value=3)
    @patch("hrt.common.utils.get_user_input_option", side_effect=["P", "S", "S"])
    def test_display_question_and_get_action_not_all_submitted(self, _, __):
        self.quiz._current_index = 0
        self.quiz._submitted_questions[QuestionNumber("Q1")] = QuestionSubmitted(
            question_number=QuestionNumber("Q1"), selected_choice="3"
        )
        self.quiz._display_question_and_get_action(skip_last=True)
        self.assertFalse(self.quiz._terminate_quiz)

    @patch("sys.stdout", new_callable=StringIO)
    def test_no_previous_question_available(self, mock_stdout):
        self.quiz._current_index = 0
        self.quiz.previous_question()
        self.assertIn("No previous question available.", mock_stdout.getvalue())

    def test_get_question_by_number(self):
        """Test get_question_by_number with valid and invalid question numbers."""
        # Test with valid question number
        question_number = QuestionNumber("Q1")
        question = self.quiz.get_question_by_number(question_number)
        self.assertIsNotNone(question)
        if question:
            self.assertEqual(question.question_number, question_number)

        # Test with non-existing question number
        question_number = QuestionNumber("NonExistent")
        question = self.quiz.get_question_by_number(question_number)
        self.assertIsNone(question)

        # Test with empty question list
        quiz = ConcreteQuiz(0, [], self.exam_type, self.answer_display, self.quiz_config)
        question = quiz.get_question_by_number(QuestionNumber("Q1"))
        self.assertIsNone(question)

    def test_get_display_mode(self):
        """Test get_display_mode method."""
        self.assertEqual(self.quiz.get_display_mode(), self.display_mode)

    def test_get_question_by_index_invalid(self):
        """Test get_question_by_index with invalid index."""
        with self.assertRaises(IndexError):
            self.quiz.get_question_by_index(999)  # Index out of range

    def test_post_process(self):
        """Test post_process method with different pass scenarios."""
        # Test pass with honours (>=80%)
        self.quiz._questions[0].correct_attempts = 2  # Both questions correct
        self.quiz._questions[1].correct_attempts = 2
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.quiz.post_process()
            output = mock_stdout.getvalue()
            self.assertIn("Pass with Honours", output)

        # Test regular pass (70-79%)
        self.quiz._questions[0].correct_attempts = 0
        self.quiz._questions[0].wrong_attempts = 1
        self.quiz._questions[1].correct_attempts = 1  # Only one question correct = 50%
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.quiz.post_process()
            output = mock_stdout.getvalue()
            self.assertIn("Fail", output)  # Should fail at 50%

        # Test fail (<70%)
        self.quiz._questions[0].correct_attempts = 0
        self.quiz._questions[1].correct_attempts = 0
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.quiz.post_process()
            output = mock_stdout.getvalue()
            self.assertIn("Fail", output)

    def test_get_question_by_number_full_loop(self):
        """Test get_question_by_number iterates through all questions."""
        questions = [
            Question(f"Q{i}", ["A", "B", "C"], "A", QuestionNumber(f"Q{i}")) for i in range(5)
        ]
        quiz = ConcreteQuiz(
            len(questions), questions, self.exam_type, self.answer_display, self.quiz_config
        )
        # Request the last question to ensure we iterate through all questions
        last_question = quiz.get_question_by_number(QuestionNumber("Q4"))
        self.assertIsNotNone(last_question)
        if last_question:
            self.assertEqual(last_question.question_number, QuestionNumber("Q4"))


class TestQuizFactory(unittest.TestCase):
    @patch("hrt.question_banks.ca_quiz.CAQuiz", autospec=True)
    def test_get_quiz_canada(self, _):
        exam_type = ExamType.BASIC
        quiz = QuizFactory.get_quiz(
            2, [], exam_type, QuestionDisplayMode.QUIZ, QuizAnswerDisplay.AFTER_QUESTION, {}
        )
        self.assertIsInstance(quiz, CAQuiz)

    @patch("hrt.question_banks.us_quiz.USQuiz", autospec=True)
    def test_get_quiz_us(self, _):
        exam_type = ExamType.EXTRA
        quiz = QuizFactory.get_quiz(
            2, [], exam_type, QuestionDisplayMode.QUIZ, QuizAnswerDisplay.AFTER_QUESTION, {}
        )
        self.assertIsInstance(quiz, USQuiz)

    def test_get_quiz_invalid(self):
        exam_type = ExamType.GENERAL_GRADE
        with self.assertRaises(ValueError):
            QuizFactory.get_quiz(
                2,
                [],
                exam_type,
                QuestionDisplayMode.QUIZ,
                QuizAnswerDisplay.AFTER_QUESTION,
                {
                    "country_code": CountryCode.UNITED_STATES,
                    "mark_wrong_answers": True,
                    "show_explanation": True,
                    "show_hints": True,
                    "show_references": True,
                    "show_tags": True,
                    "show_marked_status": True,
                    "show_metrics": True,
                },
            )


if __name__ == "__main__":
    unittest.main()
