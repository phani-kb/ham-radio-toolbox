from hrt.common.enums import ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.question import Question


class USQuiz:
    def pre_process(self):
        pass

    def post_process(self):
        pass

    def start(self):
        raise NotImplementedError("USQuiz.start() not supported yet")

    def __init__(
        self,
        number_of_questions: int,
        questions: list[Question],
        exam_type: ExamType,
        display_mode: QuestionDisplayMode,
        answer_display: QuizAnswerDisplay,
        quiz_config: dict,
    ):
        super().__init__(
            number_of_questions, questions, exam_type, display_mode, answer_display, quiz_config
        )
