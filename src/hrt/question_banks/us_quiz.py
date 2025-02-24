"""This module contains the USQuiz class."""

from hrt.common.enums import CountryCode
from hrt.common.quiz import Quiz


class USQuiz(Quiz):
    """US Quiz class."""

    def pre_process(self):
        super().validate_exam_type(CountryCode.UNITED_STATES)

    def post_process(self):
        pass

    def start(self):
        raise NotImplementedError("USQuiz.start() not supported yet")
