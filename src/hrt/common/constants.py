"""Constants used in the application."""

from hrt.common.enums import QuestionAnswerDisplay

APP_NAME: str = "ham-radio-toolbox"
APP_VERSION: str = "0.1.0"
APP_DESCRIPTION: str = "A CLI tool to support the amateur radio community."
LOAD_WAIT_TIME: int = 5
SEARCH_WAIT_TIME: int = 15
REQUEST_TIMEOUT: int = 10
DOT: str = "."
DASH: str = "-"
CW_DOT_DASH_WEIGHT: dict = {DOT: 1, DASH: 3}
DEFAULT_TOP_QUESTIONS_COUNT: int = 10
MIN_TOP_QUESTIONS_COUNT: int = 1
MAX_TOP_QUESTIONS_COUNT: int = 50
MIN_MARKED_QUESTIONS_COUNT: int = 2
MAX_MARKED_QUESTIONS_COUNT: int = 20
ANSWER_DISPLAY_PREFIX: str = "--->"
MARKED_QUESTIONS_DELIMITER: str = ":"
DEFAULT_MARKED_QUESTIONS_FILENAME: str = "marked-questions.txt"
DEFAULT_QUIZ_QUESTION_COUNT: int = 10
DEFAULT_METRICS_FOLDER: str = "data/metrics"
DEFAULT_OUTPUT_FOLDER: str = "data/output"
DEFAULT_INPUT_FOLDER: str = "data/input"
DEFAULT_METRICS_DELIMITER: str = ":"
DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM: QuestionAnswerDisplay = QuestionAnswerDisplay.IN_THE_END
WARNING_MESSAGE = """
WARNING: This scraping functionality is provided for personal, educational, and research use only.
You are responsible for ensuring compliance with website Terms of Service and applicable laws.
Proceed at your own risk.
"""
