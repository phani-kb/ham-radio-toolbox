import logging


class BaseProcessor:
    def __init__(self, config_reader):
        self.config_reader = config_reader
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_questions(self):
        pass

    def evaluate_answer(self, question, answer):
        pass

    def provide_feedback(self, question, answer, is_correct):
        pass
