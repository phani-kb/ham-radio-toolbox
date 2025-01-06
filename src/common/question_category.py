class QuestionCategory:
    def __init__(self, category_id: str, name: str, max_questions: int = 0):
        if not category_id:
            category_id = id(self)
        self._category_id = category_id
        if not name:
            raise ValueError("Name cannot be empty")
        self._name = name
        self._max_questions = max_questions

    @property
    def category_id(self) -> str:
        return self._category_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def max_questions(self) -> int:
        return self._max_questions

    def __str__(self):
        return f"{self.category_id}:{self.name}"
