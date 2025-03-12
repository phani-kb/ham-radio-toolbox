"""Question category class."""


class QuestionCategory:
    """Question category class."""

    def __init__(self, category_id: str, name: str, max_questions: int = 0):
        if not category_id:
            category_id = str(id(self))
        self._category_id = category_id
        if not name:
            raise ValueError("Name cannot be empty")
        self._name = name
        self._max_questions = max_questions

    @property
    def category_id(self) -> str:
        """Returns the category id."""
        return self._category_id

    @property
    def name(self) -> str:
        """Returns the category name."""
        return self._name

    @property
    def max_questions(self) -> int:
        """Returns the maximum number of questions in the category."""
        return self._max_questions

    def __str__(self) -> str:
        return f"{self.category_id}:{self.name}"
