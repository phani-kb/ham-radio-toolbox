"""Processor for generating country specific questions."""

from hrt.processors.base_processor import BaseProcessor


class CountrySpecificProcessor(BaseProcessor):
    """Processor for generating country specific questions."""

    def __init__(self, config_reader, country_code, question_bank):
        super().__init__(config_reader)
        self.question_bank = question_bank
        self.country_code = country_code

    def generate_questions(self):
        return self.question_bank.get_questions(self.country_code, "quiz")

    def evaluate_answer(self, question, answer):
        correct_answer = question.get("answer")
        return answer == correct_answer

    def provide_feedback(self, question, answer, is_correct):
        if is_correct:
            return "Correct! Well done."
        return f"Sorry, the correct answer is: {question.get('answer')}"

    def update_question_bank(self):
        """Update the question bank."""
        self.question_bank.update_question_bank(self.country_code, "quiz")

    def get_country_code(self):
        """Get the country code."""
        return self.country_code

    def quiz(self, question_bank, config):
        """Generate a quiz for a specific country."""

    def practice_exam(self, question_bank, config):
        """Generate a practice exam for a specific country."""
