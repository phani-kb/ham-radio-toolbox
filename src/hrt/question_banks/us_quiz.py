"""This module contains the USQuiz class."""

from hrt.common.enums import CountryCode
from hrt.common.quiz import Quiz


class USQuiz(Quiz):
    """US Quiz class."""

    def pre_process(self) -> None:
        super().validate_exam_type(CountryCode.UNITED_STATES)

    def post_process(self) -> None:
        pass

    def start(self) -> None:
        raise NotImplementedError("USQuiz.start() not supported yet")
