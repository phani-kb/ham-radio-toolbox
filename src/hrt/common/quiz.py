from abc import ABC, abstractmethod

from hrt.common.enums import ExamType
from hrt.common.question import Question


class IQuiz(ABC):
    @abstractmethod
    def pre_process(self):
        pass

    @abstractmethod
    def post_process(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def previous_question(self):
        pass

    @abstractmethod
    def next_question(self):
        pass

    @abstractmethod
    def submit(self, choice_index: int):
        pass

    @abstractmethod
    def mark(self, choice_index: int):
        pass

    @abstractmethod
    def unmark(self):
        pass

    @abstractmethod
    def skip(self):
        pass

    @abstractmethod
    def quit(self):
        pass

    @abstractmethod
    def finish(self):
        pass

    @abstractmethod
    def change_answer(self):
        pass

    @abstractmethod
    def get_number_of_questions(self) -> int:
        pass

    @abstractmethod
    def get_exam_type(self) -> ExamType:
        pass

    @abstractmethod
    def get_current_question(self) -> Question:
        pass

    @abstractmethod
    def get_current_index(self) -> int:
        pass

    @abstractmethod
    def set_current_index(self, index: int):
        pass

    @abstractmethod
    def get_question_by_index(self, index: int) -> Question:
        pass

    @abstractmethod
    def print_question(self, question: Question) -> str:
        pass

    @abstractmethod
    def get_actions(self, submitted: bool) -> (str, list[str]):
        pass

    @abstractmethod
    def get_questions(self) -> list[Question]:
        pass

    @abstractmethod
    def get_results(self) -> (int, int, int):
        pass

    @abstractmethod
    def get_progress(self) -> str:
        pass

    @abstractmethod
    def get_duration(self) -> int:
        pass

    @abstractmethod
    def get_marked_questions(self) -> list[Question]:
        pass


class Quiz(IQuiz, ABC):
    pass
