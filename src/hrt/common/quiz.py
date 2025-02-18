"""
This module contains the Quiz class which represents a quiz.
The Quiz class has the following attributes:
- number_of_questions: The number of questions in the quiz
- questions: A list of questions
- exam_type: The type of exam
- current_index: The index of the current question
- submitted_questions: A dictionary of questions that have been submitted
- mark_wrong_answers: A flag to mark wrong answers
- terminate_quiz: A flag to terminate the quiz
- display_mode: The display mode of the quiz
- start_time: The start time of the quiz
- end_time: The end time of the quiz
"""

from abc import ABC, abstractmethod

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.hrt_types import QuestionNumber
from hrt.common.question import Question
from hrt.common.question_display import QuizQuestionDisplay
from hrt.common.question_submitted import QuestionSubmitted


class IQuiz(ABC):
    """Quiz interface."""

    @abstractmethod
    def pre_process(self):
        """Pre-process the quiz."""

    @abstractmethod
    def post_process(self):
        """Post-process the quiz."""

    @abstractmethod
    def start(self):
        """Start the quiz."""

    @abstractmethod
    def previous_question(self):
        """Move to the previous question."""

    @abstractmethod
    def next_question(self):
        """Move to the next question."""

    @abstractmethod
    def submit(self, choice_index: int):
        """Submit the answer for the current question."""

    @abstractmethod
    def mark(self, choice_index: int):
        """Mark the current question."""

    @abstractmethod
    def unmark(self):
        """Unmark the current question."""

    @abstractmethod
    def skip(self):
        """Skip the current question"""

    @abstractmethod
    def quit(self):
        """Quit the quiz."""

    @abstractmethod
    def finish(self):
        """Finish the quiz."""

    @abstractmethod
    def change_answer(self):
        """Change the answer for the current question."""

    @abstractmethod
    def get_number_of_questions(self) -> int:
        """Get the number of questions in the quiz."""

    @abstractmethod
    def get_exam_type(self) -> ExamType:
        """Get the exam type of the quiz."""

    @abstractmethod
    def get_current_question(self) -> Question:
        """Get the current question."""

    @abstractmethod
    def get_current_index(self) -> int:
        """Get the current index."""

    @abstractmethod
    def set_current_index(self, index: int):
        """Set the current index."""

    @abstractmethod
    def get_question_by_index(self, index: int) -> Question:
        """Get the question at the given index."""

    @abstractmethod
    def print_question(self, question: Question) -> str:
        """Print the question."""

    @abstractmethod
    def get_actions(self, submitted: bool) -> tuple[str, list[str]]:
        """Get the actions for the current question."""

    @abstractmethod
    def get_questions(self) -> list[Question]:
        """Get the questions in the quiz."""

    @abstractmethod
    def get_results(self) -> tuple[int, int, int]:
        """Get the results of the quiz."""

    @abstractmethod
    def get_progress(self) -> str:
        """Get the progress of the quiz."""

    @abstractmethod
    def get_duration(self) -> int:
        """Get the duration of the quiz."""

    @abstractmethod
    def get_marked_questions(self) -> list[Question]:
        """Get the marked questions."""


class Quiz(IQuiz, ABC):
    """Quiz class."""

    def __init__(
        self,
        number_of_questions: int,
        questions: list[Question],
        exam_type: ExamType,
        display_mode: QuestionDisplayMode,
        answer_display: QuizAnswerDisplay,
        quiz_config: dict,
    ):
        if number_of_questions != len(questions):
            logger.warning(
                "Number of questions (%d) does not match the expected number (%d).",
                len(questions),
                number_of_questions,
            )
        self._number_of_questions = len(questions)
        self._questions = questions
        self._exam_type = exam_type
        self._current_index = 0
        self._submitted_questions = {}
        self._mark_wrong_answers = quiz_config["mark_wrong_answers"]
        self._terminate_quiz = False
        self._display_mode = display_mode
        Question.question_display = QuizQuestionDisplay(
            answer_display,
            quiz_config["show_explanation"],
            quiz_config["show_hints"],
            quiz_config["show_references"],
            quiz_config["show_tags"],
            quiz_config["show_marked_status"],
            quiz_config["show_metrics"],
        )
        self._start_time: float = 0
        self._end_time: float = 0

    def validate_exam_type(self, country: CountryCode):
        """Validate the exam type for the given country."""
        if self._exam_type.country != country:
            raise ValueError("Invalid exam type for the country.")

    def _display_question_and_get_action(self, skip_last=False):
        pass

    def previous_question(self):
        if self._current_index > 0:
            self._current_index -= 1
        else:
            print("No previous question available.")

    def next_question(self):
        if self._current_index < len(self._questions) - 1:
            self._current_index += 1
        else:
            print("No next question available.")

    def start(self):
        print(
            utils.get_header(
                f"\nQuiz: {self._exam_type.id} - "
                f"{self._exam_type.country.code} - {len(self._questions)} Questions"
            )
        )
        self._current_index = 0
        self._start_time = utils.get_current_time()
        self._display_question_and_get_action()

    def process_action(self, action: str, choice_index: int, actions: list[str]):
        """Process the action selected by the user."""
        if action not in actions:
            print("Invalid action. Please select a valid action.")
            return
        action_map = {
            "P": self.previous_question,
            "N": self.next_question,
            "S": lambda: self.submit(choice_index),
            "M": lambda: self.mark(choice_index),
            "U": self.unmark,
            "K": self.skip,
            "Q": self.quit,
            "F": self.finish,
            "C": self.change_answer,
        }
        action_map[action]()
        self._display_question_and_get_action()

    def submit(self, choice_index: int):
        cq = self.get_current_question()
        if cq.question_number in self._submitted_questions:
            return
        if choice_index == -1:
            logger.info("No choice selected.")
            return
        is_correct = choice_index == cq.quiz_choices.index(cq.answer)
        if is_correct:
            cq.correct_attempts += 1
            if cq.question_display.answer_display == QuizAnswerDisplay.AFTER_QUESTION:
                char = "\033[92m✓✓\033[0m"  # Two green checks
                print(f"{char}")
        else:
            cq.wrong_attempts += 1
            if cq.question_display.answer_display == QuizAnswerDisplay.AFTER_QUESTION:
                char = "\033[91m✗✗\033[0m"  # Two red cross-marks
                print(f"{char}\nCorrect Answer: ({cq.answer_index + 1}) {cq.answer}")
        self._submitted_questions[cq.question_number] = QuestionSubmitted(
            cq.question_number, cq.quiz_choices[choice_index]
        )

        if not is_correct and self._mark_wrong_answers:
            cq.is_marked = True

        print(self.get_progress())
        if len(self._submitted_questions) == self._number_of_questions:
            self.finish()
        else:
            self.next_question()

    def mark(self, choice_index: int):
        current_question = self.get_current_question()
        if not current_question.is_marked:
            current_question.is_marked = True
            print(f"Question {current_question.question_number} marked.")
        else:
            print(f"Question {current_question.question_number} is already marked.")
        if choice_index == -1:
            logger.info("No choice selected.")
            return
        if current_question.quiz_choices[choice_index] == Question.SKIP_CHOICE:
            self.skip()

        self.submit(choice_index)

    def unmark(self):
        current_question = self.get_current_question()
        if current_question.is_marked:
            current_question.is_marked = False
            print(f"Question {current_question.question_number} unmarked.")
        else:
            print(f"Question {current_question.question_number} is not marked.")

    def skip(self):
        current_question = self.get_current_question()
        if current_question.question_number in self._submitted_questions:
            return
        current_question.skip_count += 1
        if self._current_index == self._number_of_questions - 1:
            self._display_question_and_get_action(skip_last=True)
        else:
            self.next_question()

    def quit(self):
        self._end_time = utils.get_current_time()
        self._terminate_quiz = True

    def finish(self):
        pass

    def change_answer(self):
        pass

    def get_number_of_questions(self) -> int:
        return self._number_of_questions

    def get_exam_type(self) -> ExamType:
        return self._exam_type

    def get_display_mode(self) -> QuestionDisplayMode:
        """Get the display mode for the question bank."""
        return self._display_mode

    def get_questions(self) -> list[Question]:
        return self._questions

    def get_current_question(self) -> Question:
        return self._questions[self._current_index]

    def get_current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int):
        self._current_index = index

    def get_question_by_index(self, index: int) -> Question:
        return self._questions[index]

    def get_question_by_number(self, question_number: QuestionNumber) -> Question:
        """Get the question by question number."""
        return next((q for q in self._questions if q.question_number == question_number), None)

    def print_question(self, question: Question) -> str:
        output = (
            f"[{self._current_index + 1}/{self._number_of_questions}] "
            f"{question.question_number}: {question.question_text}\n"
        )
        for i, choice in enumerate(question.quiz_choices):
            if question.question_number in self._submitted_questions:
                if choice == self._submitted_questions[question.question_number].selected_choice:
                    char = "\033[92m✓\033[0m" if choice == question.answer else "\033[91m✗\033[0m"
                    output += f"{char}   {i + 1}. {choice}\n"
                elif choice == question.answer:
                    output += f"\033[92m✓\033[0m   {i + 1}. {choice}\n"
                else:
                    output += f"    {i + 1}. {choice}\n"
            else:
                output += f"    {i + 1}. {choice}\n"
        if question.is_marked:
            output += "*** Marked ***\n"
        if (
            question.question_display.show_metrics
            and self.get_display_mode() != QuestionDisplayMode.PRACTICE_EXAM
        ):
            em = question.existing_metric
            output += (
                f"\033[92m{em.correct_attempts}\033[0m "
                f"\033[91m{em.wrong_attempts}\033[0m "
                f"\033[94m{em.skip_count}\033[0m\n"
            )
        return output

    def get_actions(self, submitted: bool, skip_last: bool = False) -> tuple[str, list[str]]:
        action_descriptions = {
            "P": "Previous",
            "N": "Next",
            "S": "Submit",
            "M": "Mark",
            "U": "Unmark",
            "Q": "Quit",
            "F": "Finish",
            "C": "Change Answer",
        }
        base_actions = ["Q", "F"]
        if not submitted and not skip_last:
            base_actions.append("S")

        current_question = self.get_current_question()

        if current_question.question_number in self._submitted_questions:
            actions = (
                ["P", "N"]
                if self.get_current_index() not in [0, self.get_number_of_questions() - 1]
                else ["N"]
                if self.get_current_index() == 0
                else ["P"]
            )
        else:
            actions = (
                ["P", "N", "C"]
                if self.get_current_index() not in [0, self.get_number_of_questions() - 1]
                else ["N", "C"]
                if self.get_current_index() == 0
                else ["P", "C"]
            )

        if current_question.is_marked:
            actions.append("U")
        else:
            actions.append("M")

        actions += base_actions
        action_prompt = ", ".join(
            f"[{action}]:{action_descriptions[action]}" for action in actions
        )
        return action_prompt, actions

    def get_results(self) -> tuple[int, int, int]:
        correct_attempts = len([q for q in self._questions if q.correct_attempts > 0])
        wrong_attempts = len([q for q in self._questions if q.wrong_attempts > 0])
        skip_count = len([q for q in self._questions if q.skip_count > 0])
        return correct_attempts, wrong_attempts, skip_count

    def get_progress(self) -> str:
        progress = len(self._submitted_questions)
        output = f"Progress: {progress}/{self._number_of_questions}\n"
        if Question.question_display.answer_display == QuizAnswerDisplay.AFTER_QUESTION:
            correct_attempts = len([q for q in self._questions if q.correct_attempts > 0])
            output += f"Correct answers: {correct_attempts}/{self._number_of_questions}\n"
        return output

    def get_duration(self) -> int:
        return round(self._end_time - self._start_time)

    def get_marked_questions(self) -> list[Question]:
        return [q for q in self._questions if q.is_marked]
