"""Processor for generating country specific questions."""

from typing import Dict, List

from hrt.processors.base_processor import BaseProcessor


class CountrySpecificProcessor(BaseProcessor):
    """Processor for generating country specific questions."""

    def __init__(
        self,
        config_reader: BaseProcessor,
        country_code: str,
        question_bank: Dict[str, List[str]],
    ):
        super().__init__(config_reader)
        self.question_bank = question_bank
        self.country_code = country_code

    def generate_questions(self) -> List[str]:
        return self.question_bank.get_questions(self.country_code, "quiz")

    def evaluate_answer(self, question: Dict[str, str], answer: str) -> bool:
        correct_answer = question.get("answer")
        return answer == correct_answer

    def provide_feedback(self, question: Dict[str, str], answer: str, is_correct: bool) -> str:
        if is_correct:
            return "Correct! Well done."
        return f"Sorry, the correct answer is: {question.get('answer')}"

    def update_question_bank(self) -> None:
        """Update the question bank."""
        self.question_bank.update_question_bank(self.country_code, "quiz")

    def get_country_code(self) -> str:
        """Get the country code."""
        return self.country_code

    def quiz(self, question_bank: Dict[str, List[str]], config: BaseProcessor) -> None:
        """Generate a quiz for a specific country."""
        pass

    def practice_exam(self, question_bank: Dict[str, List[str]], config: BaseProcessor) -> None:
        """Generate a practice exam for a specific country."""
        pass
