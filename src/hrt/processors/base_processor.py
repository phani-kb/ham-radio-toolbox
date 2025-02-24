"""Base class for all processors."""

import logging


class BaseProcessor:
    """Base class for all processors."""

    def __init__(self, config_reader):
        self.config_reader = config_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_questions(self):
        """Generate questions."""

    def evaluate_answer(self, question, answer):
        """Evaluate the answer."""

    def provide_feedback(self, question, answer, is_correct):
        """Provide feedback on the answer."""
