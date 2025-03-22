"""
This module contains the CAQuiz class which represents a Canadian quiz.
The CAQuiz class is a subclass of the Quiz class and has the following attributes:
- PASS_PERCENTAGE: The pass percentage for the quiz
- PASS_PERCENTAGE_WITH_HONOURS: The pass percentage with honours for the quiz
"""
from typing import Dict, List

from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.question import Question
from hrt.common.quiz import Quiz


class CAQuiz(Quiz):
    """Canadian Quiz class."""
    PASS_PERCENTAGE: int = 70
    PASS_PERCENTAGE_WITH_HONOURS: int = 80

    def __init__(
        self,
        number_of_questions: int,
        questions: List[Question],
        exam_type: ExamType,
        display_mode: QuestionDisplayMode,
        answer_display: QuizAnswerDisplay,
        quiz_config: Dict,
    ):
        super().__init__(
            number_of_questions, questions, exam_type, display_mode, answer_display, quiz_config
        )

    def pre_process(self) -> None:
        super().validate_exam_type(CountryCode.CANADA)

    # Using the common post_process method from the base Quiz class
