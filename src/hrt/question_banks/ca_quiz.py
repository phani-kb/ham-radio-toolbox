"""
This module contains the CAQuiz class which represents a Canadian quiz.
The CAQuiz class is a subclass of the Quiz class and has the following attributes:
- PASS_PERCENTAGE: The pass percentage for the quiz
- PASS_PERCENTAGE_WITH_HONOURS: The pass percentage with honours for the quiz
"""

from hrt.common.quiz import Quiz


class CAQuiz(Quiz):
    """Canadian Quiz class."""

    PASS_PERCENTAGE = 70
    PASS_PERCENTAGE_WITH_HONOURS = 80

    def pre_process(self):
        pass

    def post_process(self):
        pass
