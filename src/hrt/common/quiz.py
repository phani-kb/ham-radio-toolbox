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
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode, QuizAnswerDisplay
from hrt.common.question import Question
from hrt.common.question_display import QuizQuestionDisplay
from hrt.common.question_submitted import QuestionSubmitted

if TYPE_CHECKING:
    from hrt.common.hrt_types import QuestionNumber  # pragma: no cover


class IQuiz(ABC):
    """Quiz interface."""

    @abstractmethod
    def pre_process(self) -> None:
        """Pre-process the quiz."""

    @abstractmethod
    def post_process(self) -> None:
        """Post-process the quiz."""

    @abstractmethod
    def start(self) -> None:
        """Start the quiz."""

    @abstractmethod
    def previous_question(self) -> None:
        """Move to the previous question."""

    @abstractmethod
    def next_question(self) -> None:
        """Move to the next question."""

    @abstractmethod
    def submit(self, choice_index: int) -> None:
        """Submit the answer for the current question."""

    @abstractmethod
    def mark(self, choice_index: int) -> None:
        """Mark the current question."""

    @abstractmethod
    def unmark(self) -> None:
        """Unmark the current question."""

    @abstractmethod
    def skip(self) -> None:
        """Skip the current question"""

    @abstractmethod
    def quit(self) -> None:
        """Quit the quiz."""

    @abstractmethod
    def finish(self) -> None:
        """Finish the quiz."""

    @abstractmethod
    def change_answer(self) -> None:
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
    def set_current_index(self, index: int) -> None:
        """Set the current index."""

    @abstractmethod
    def get_question_by_index(self, index: int) -> Question:
        """Get the question at the given index."""

    @abstractmethod
    def print_question(self, question: Question) -> str:
        """Print the question."""

    @abstractmethod
    def get_actions(self, submitted: bool, skip_last: bool = False) -> Tuple[str, List[str]]:
        """Get the actions for the current question."""

    @abstractmethod
    def process_action(self, action: str, choice_index: int, actions: List[str]) -> None:
        """Process the action selected by the user."""

    @abstractmethod
    def get_questions(self) -> List[Question]:
        """Get the questions in the quiz."""

    @abstractmethod
    def get_results(self) -> Tuple[int, int, int]:
        """Get the results of the quiz."""

    @abstractmethod
    def get_progress(self) -> str:
        """Get the progress of the quiz."""

    @abstractmethod
    def get_duration(self) -> int:
        """Get the duration of the quiz."""

    @abstractmethod
    def get_marked_questions(self) -> List[Question]:
        """Get the marked questions."""


class Quiz(IQuiz, ABC):
    """Quiz class."""

    # Common pass percentages for quizzes
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
        self._submitted_questions: Dict[QuestionNumber, QuestionSubmitted] = {}
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

    def validate_exam_type(self, country: CountryCode) -> None:
        """Validate the exam type for the given country."""
        if self._exam_type.country != country:
            raise ValueError("Invalid exam type for the country.")

    def _display_question_and_get_action(self, skip_last: bool = False) -> None:
        while not self._terminate_quiz:
            if self._current_index >= self._number_of_questions:
                print("No next question available.")
                break
            cq = self.get_current_question()
            print(self.print_question(cq))
            if skip_last:
                _, _ = self.get_actions(submitted=True, skip_last=skip_last)
                cq.skip_count += 1
            elif cq.question_number in self._submitted_questions:
                _, _ = self.get_actions(submitted=True)
            else:
                choice_index = utils.get_user_input_index(cq.quiz_choices, "Enter choice: ")
                if (
                    choice_index == len(cq.quiz_choices) - 1
                    and self._current_index == self._number_of_questions - 1
                ):
                    cq = self.get_current_question()
                    cq.skip_count += 1
                    action_prompt, actions = self.get_actions(submitted=False, skip_last=True)
                    print(action_prompt)
                    action = utils.get_user_input_option(actions, "Please select an action: ")
                    self.process_action(action, choice_index, actions)
                    break
                if choice_index == len(cq.quiz_choices) - 1:
                    self.skip()
                    continue
                action_prompt, actions = self.get_actions(submitted=False)
                print(action_prompt)
                action = utils.get_user_input_option(actions, "Please select an action: ")
                self.process_action(action, choice_index, actions)
                break
            if len(self._submitted_questions) == self._number_of_questions:
                self._terminate_quiz = True
                self.finish()
                break
            action_prompt, actions = self.get_actions(submitted=True)
            print(action_prompt)
            action = utils.get_user_input_option(actions, "Please select an action: ")
            if action == "P" and self._current_index == 0:
                print("No previous question available.")
                break
            self.process_action(action, -1, actions)

    def previous_question(self) -> None:
        if self._current_index > 0:
            self._current_index -= 1
        else:
            print("No previous question available.")

    def next_question(self) -> None:
        if self._current_index < len(self._questions) - 1:
            self._current_index += 1
        else:
            print("No next question available.")

    def start(self) -> None:
        """Start the quiz."""
        print(
            utils.get_header(
                f"\nQuiz: {self._exam_type.id} - "
                f"{self._exam_type.country.code} - {len(self._questions)} Questions"
            )
        )
        self._current_index = 0
        self._start_time = utils.get_current_time()
        self._display_question_and_get_action()

    def process_action(self, action: str, choice_index: int, actions: List[str]) -> None:
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

    def submit(self, choice_index: int) -> None:
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
        print(self.get_progress() + "\n")
        if len(self._submitted_questions) == self._number_of_questions:
            self.finish()
        else:
            self.next_question()

    def mark(self, choice_index: int) -> None:
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

    def unmark(self) -> None:
        current_question = self.get_current_question()
        if current_question.is_marked:
            current_question.is_marked = False
            print(f"Question {current_question.question_number} unmarked.")
        else:
            print(f"Question {current_question.question_number} is not marked.")

    def skip(self) -> None:
        current_question = self.get_current_question()
        if current_question.question_number in self._submitted_questions:
            return
        current_question.skip_count += 1
        if self._current_index == self._number_of_questions - 1:
            self._display_question_and_get_action(skip_last=True)
        else:
            self.next_question()

    def quit(self) -> None:
        self._end_time = utils.get_current_time()
        self._terminate_quiz = True

    def finish(self) -> None:
        if not self._terminate_quiz:  # Check if the quiz is already terminated
            if len(self._submitted_questions) < self._number_of_questions:
                not_submitted = [
                    q.question_number
                    for q in self._questions
                    if q.question_number not in self._submitted_questions
                ]
                print(f"Warning: {len(not_submitted)} questions are not submitted.")
                confirm = utils.get_user_input_option(
                    ["Y", "N"], "Do you really want to finish the quiz? (Y/N): "
                )
                if confirm == "N":
                    self._terminate_quiz = False
                    self._display_question_and_get_action()
                    return
                for q in not_submitted:
                    self._submitted_questions[q] = QuestionSubmitted(q, Question.SKIP_CHOICE)
            print("Quiz completed.")
            self._end_time = utils.get_current_time()
            self.quit()

    def change_answer(self) -> None:
        current_question = self.get_current_question()
        if current_question.question_number in self._submitted_questions:
            print("Cannot change answer for a submitted question.")
            return
        choice_index = utils.get_user_input_index(
            current_question.quiz_choices, "Enter new choice: "
        )
        skip_last = False
        if choice_index == len(current_question.quiz_choices) - 1:
            skip_last = True
        action_prompt, actions = self.get_actions(submitted=False, skip_last=skip_last)
        print(action_prompt)
        action = utils.get_user_input_option(actions, "Please select an action: ")
        self.process_action(action, choice_index, actions)

    def get_number_of_questions(self) -> int:
        return self._number_of_questions

    def get_exam_type(self) -> ExamType:
        return self._exam_type

    def get_display_mode(self) -> QuestionDisplayMode:
        """Get the display mode for the question bank."""
        return self._display_mode

    def get_questions(self) -> List[Question]:
        return self._questions

    def get_current_question(self) -> Question:
        return self._questions[self._current_index]

    def get_current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int) -> None:
        self._current_index = index

    def get_question_by_index(self, index: int) -> Question:
        if 0 <= index < self._number_of_questions:
            return self._questions[index]
        raise IndexError("Index out of range")

    def get_question_by_number(self, question_number: "QuestionNumber") -> Optional[Question]:
        """Get a question by its question number."""
        for question in self._questions:
            if question.question_number == question_number:
                return question
        return None

    def print_question(self, question: Question) -> str:
        """Print the question."""
        question_text = question.format_quiz_question()
        progress_text = self.get_progress()
        if question.is_marked and question.question_display.show_marked_status:
            question_text += f"Marked: {'Yes' if question.is_marked else 'No'}\n"
        question_text += f"\n{progress_text}"
        return question_text

    def get_actions(self, submitted: bool, skip_last: bool = False) -> Tuple[str, List[str]]:
        """Get the actions for the current question."""
        if submitted:
            if self._current_index == 0:
                action_prompt = "Actions: [N]ext, [Q]uit"
                actions = ["N", "Q"]
            elif self._current_index == self._number_of_questions - 1:
                action_prompt = "Actions: [P]revious, [Q]uit, [F]inish"
                actions = ["P", "Q", "F"]
            else:
                action_prompt = "Actions: [P]revious, [N]ext, [Q]uit, [F]inish"
                actions = ["P", "N", "Q", "F"]
        else:
            cq = self.get_current_question()
            if cq.is_marked:
                action_prompt = "Actions: [S]ubmit, [M]ark, [U]nmark, [C]hange, [K]skip, [Q]uit"
                actions = ["S", "M", "U", "C", "K", "Q"]
            else:
                action_prompt = "Actions: [S]ubmit, [M]ark, [C]hange, [K]skip, [Q]uit"
                actions = ["S", "M", "C", "K", "Q"]

        return action_prompt, actions

    def get_results(self) -> Tuple[int, int, int]:
        """Get the results of the quiz.
        Returns a tuple of (correct, wrong, skipped).
        """
        correct = 0
        wrong = 0
        skipped = 0
        for q in self._questions:
            correct += q.correct_attempts
            wrong += q.wrong_attempts
            skipped += q.skip_count

        return correct, wrong, skipped

    def get_progress(self) -> str:
        """Get the progress of the quiz."""
        current = self._current_index + 1
        total = self._number_of_questions
        return f"Progress: {current}/{total}"

    def get_duration(self) -> int:
        if self._end_time == 0:
            duration = int(utils.get_current_time() - self._start_time)
        else:
            duration = int(self._end_time - self._start_time)
        return duration

    def get_marked_questions(self) -> List[Question]:
        return [q for q in self._questions if q.is_marked]

    def post_process(self) -> None:
        """Common post-processing for all quiz types.
        Displays quiz results and calculates pass/fail status.
        """
        total_questions = self.get_number_of_questions()
        correct, wrong, _ = self.get_results()
        percentage = round((correct / total_questions) * 100)
        attempted_questions = correct + wrong

        print(f"Attempted: {attempted_questions} out of {total_questions}")
        print(
            f"You got {correct} out of {total_questions} correct. "
            f"Duration: {self.get_duration()} seconds"
        )

        result = (
            "Fail"
            if percentage < self.PASS_PERCENTAGE
            else "Pass"
            if percentage < self.PASS_PERCENTAGE_WITH_HONOURS
            else "Pass with Honours"
        )

        print(f"Percentage: {percentage}% {result}")


class QuizFactory:
    """Factory class to create quizzes."""

    @staticmethod
    def get_quiz(
        number_of_questions: int,
        questions: List[Question],
        exam_type: ExamType,
        display_mode: QuestionDisplayMode,
        answer_display: QuizAnswerDisplay,
        quiz_config: Dict,
    ) -> Quiz:
        """Get a quiz."""
        if exam_type.country == CountryCode.CANADA:
            from hrt.question_banks.ca_quiz import CAQuiz

            return CAQuiz(
                number_of_questions,
                questions,
                exam_type,
                display_mode,
                answer_display,
                quiz_config,
            )
        if exam_type.country == CountryCode.UNITED_STATES:
            from hrt.question_banks.us_quiz import USQuiz

            return USQuiz(
                number_of_questions,
                questions,
                exam_type,
                display_mode,
                answer_display,
                quiz_config,
            )
        raise ValueError(f"Unsupported exam type: {exam_type}")
