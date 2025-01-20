from hrt.common.question_display import IQuestionDisplay


class Question:
    question_display: IQuestionDisplay = None
    SKIP_CHOICE: str = "Skip or Don't Know"

    pass
