"""Base class for all processors."""
import logging
from typing import Any, Optional


class BaseProcessor:
    """Base class for all processors."""
    def __init__(self, config_reader: Any):
        self.config_reader = config_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_questions(self) -> None:
        """Generate questions."""

    def evaluate_answer(self, question: Any, answer: Any) -> Optional[bool]:
        """Evaluate the answer."""

    def provide_feedback(self, question: Any, answer: Any, is_correct: bool) -> Optional[str]:
        """Provide feedback on the answer."""
