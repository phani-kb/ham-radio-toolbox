# flake8: noqa: E501
from hrt.common.enums import QuestionAnswerDisplay

LOAD_WAIT_TIME: int = 5
SEARCH_WAIT_TIME: int = 15
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
USER_AGENTS: list[str] = [
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.4; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/114.0",
    # Chrome
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    # Edge
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/113.0.1774.57"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/113.0.1774.57"
    ),
    # Safari
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/16.0 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 "
        "(KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11"
    ),
]
