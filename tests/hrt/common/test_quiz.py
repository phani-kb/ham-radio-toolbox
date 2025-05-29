import unittest

from hrt.common.quiz import Quiz
from hrt.common.enums import QuestionDisplayMode


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
        # Implement the pre_process method
        pass


if __name__ == "__main__":
    unittest.main()
