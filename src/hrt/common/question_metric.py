"""Question metric class."""

from typing import Any

from hrt.common.hrt_types import QuestionNumber


class QuestionMetric:
    """Question metric class."""

    def __init__(
        self,
        question_number: QuestionNumber,
        correct_attempts: int = 0,
        wrong_attempts: int = 0,
        skip_count: int = 0,
    ):
        self._question_number: QuestionNumber = question_number
        self._correct_attempts = correct_attempts
        self._wrong_attempts = wrong_attempts
        self._skip_count = skip_count

    @property
    def question_number(self) -> QuestionNumber:
        """Question number."""
        return self._question_number

    @property
    def correct_attempts(self) -> int:
        """Correct attempts."""
        return self._correct_attempts

    @property
    def wrong_attempts(self) -> int:
        """Wrong attempts."""
        return self._wrong_attempts

    @property
    def skip_count(self) -> int:
        """Skip count."""
        return self._skip_count

    @correct_attempts.setter
    def correct_attempts(self, correct_attempts: int) -> None:
        self._correct_attempts = correct_attempts

    @wrong_attempts.setter
    def wrong_attempts(self, wrong_attempts: int) -> None:
        self._wrong_attempts = wrong_attempts

    @skip_count.setter
    def skip_count(self, skip_count: int) -> None:
        self._skip_count = skip_count

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, QuestionMetric):
            return NotImplemented
        return self.question_number == other.question_number

    def __hash__(self) -> int:
        return hash(self.question_number)

    def __str__(self) -> str:
        return (
            f"{self.question_number}: {self.correct_attempts}, "
            f"{self.wrong_attempts}, {self.skip_count}"
        )
