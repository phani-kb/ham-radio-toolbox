"""Enumeration classes for HRT."""

from enum import Enum
from typing import Iterable, Optional

OUTPUT_FILE_SUFFIX = "-questions"
OUTPUT_FILE_EXTENSION = ".txt"
MARKED_OUTPUT_FILE_PREFIX = "marked-"


class HRTEnum(Enum):
    """Base class for HRT enumerations (name = value)."""

    def __init__(self, eid: str, description: str = ""):
        self._id = eid
        self._description = description

    @property
    def id(self):
        """Get the id of the enumeration."""
        return self._id

    @property
    def description(self):
        """Get the description of the enumeration."""
        return self._description

    def __str__(self):
        if self._description:
            return f"{self.id} - {self.description}"
        return self.id

    @classmethod
    def from_id(cls, eid: str) -> Optional["HRTEnum"]:
        """Get the enumeration from the given id."""
        return next((enum for enum in cls if enum.id == eid), None)

    @classmethod
    def from_name(cls, name: str) -> Optional["HRTEnum"]:
        """Get the enumeration from the given name."""
        return next((enum for enum in cls if enum.name == name), None)

    @classmethod
    def ids(cls) -> list[str]:
        """Get the ids for the enumeration."""
        return [enum.id for enum in cls]

    @classmethod
    def list(cls):
        """Get the list of the enumeration."""
        return list(cls)


class SupportedEnum(HRTEnum):
    """Base class for supported enumerations."""

    def __init__(self, eid: str, is_supported: bool, description: str = ""):
        super().__init__(eid, description)
        self._is_supported = is_supported

    def __str__(self):
        return f"{self.id} - {self.description} (Supported: {self.is_supported})"

    @property
    def is_supported(self):
        """Check if the enumeration is supported."""
        return self._is_supported

    @classmethod
    def supported_ids(cls):
        """Get the supported ids for the enumeration."""
        return [enum.id for enum in cls if enum.is_supported]


class CountryCode(SupportedEnum):
    """Enumeration for country codes."""

    CANADA = ("ca", True, "Canada")
    UNITED_STATES = ("us", False, "United States")
    INDIA = ("in", False, "India")

    @property
    def code(self):
        """Get the code of the country."""
        return self.id


class CountrySpecificEnum(SupportedEnum):
    """Base class for country specific enumerations."""

    def __init__(
        self,
        eid: str,
        country: CountryCode,
        is_supported: bool,
        description: str = "",
    ):
        super().__init__(eid, is_supported, description)
        self._country = country

    def __str__(self):
        return f"{super().__str__()} (Country: {self.country})"

    @property
    def country(self):
        """Get the country of the enumeration."""
        return self._country

    @classmethod
    def supported_country_ids(cls, country: CountryCode) -> Iterable[str]:
        """Get the supported ids for the enumeration for the given country."""
        return [enum.id for enum in cls if enum.country == country and enum.is_supported]

    @classmethod
    def from_id_and_country(
        cls, eid: str, country: CountryCode
    ) -> Optional["CountrySpecificEnum"]:
        """Get the enumeration from the given id and country."""
        return next((enum for enum in cls if enum.id == eid and enum.country == country), None)


class DownloadType(CountrySpecificEnum):
    """Enumeration for download types."""

    CA_QUESTION_BANK = ("question-bank", CountryCode.CANADA, True, "Canadian Question Bank")
    CA_CALLSIGN = ("callsign", CountryCode.CANADA, True, "Canadian Callsign")
    US_QUESTION_BANK = ("question-bank", CountryCode.UNITED_STATES, False, "US Question Bank")
    US_CALLSIGN = ("callsign", CountryCode.UNITED_STATES, False, "US Callsign")


class CallSignDownloadType(CountrySpecificEnum):
    """Enumeration for Callsign download types."""


class CACallSignDownloadType(CallSignDownloadType):
    """Enumeration for Canadian Callsign download types."""

    AVAILABLE = ("available", CountryCode.CANADA, True)
    ASSIGNED = ("assigned", CountryCode.CANADA, True)


class USCallSignDownloadType(CallSignDownloadType):
    """Enumeration for US Callsign download types."""

    ACTIVE = ("active", CountryCode.UNITED_STATES, False, "Active")
    CANCELLED = ("cancelled", CountryCode.UNITED_STATES, False, "Cancelled")
    EXPIRED = ("expired", CountryCode.UNITED_STATES, False, "Expired")
    TERMINATED = ("terminated", CountryCode.UNITED_STATES, False, "Terminated")
    NOT_LISTED = ("not-listed", CountryCode.UNITED_STATES, False, "Not listed")
    RESTRICTED = ("restricted", CountryCode.UNITED_STATES, False, "Restricted")
    AVAILABLE = ("available", CountryCode.UNITED_STATES, False, "Available")


class NumberOfLetters(HRTEnum):
    """Enumeration for the number of letters."""

    SINGLE = ("1l", False, True, True, "Single letter")
    TWO = ("2l", True, True, True, "Two letters")
    THREE = ("3l", True, True, True, "Three letters")
    END = ("el", False, True, True, "Ends with letter")
    MULTIPLE = ("ml", False, False, True, "Multiple letters")
    ALL = ("all", False, True, True, "All options")

    def __init__(self, eid, word_match, include, exclude, description):
        super().__init__(eid, description)
        self._word_match = word_match
        self._include = include
        self._exclude = exclude

    def __str__(self):
        return (
            f"{super().__str__()} (Word Match: {self.word_match}) "
            f"(Include: {self.include}) (Exclude: {self.exclude})"
        )

    @property
    def include(self):
        """Get the include option of the number of letters."""
        return self._include

    @property
    def exclude(self):
        """Get the exclude option of the number of letters."""
        return self._exclude

    @property
    def word_match(self):
        """Get the word match supported option of the number of letters."""
        return self._word_match

    @classmethod
    def get_supported_number_of_letters(cls, option_type: str):
        """Get the supported number of letters for a given option type."""
        return [number.id for number in cls if getattr(number, option_type)]


class QuestionListingType(HRTEnum):
    """Enumeration for question listing types."""

    @classmethod
    def from_id(cls, eid: str) -> Optional["QuestionListingType"]:
        """Get the enumeration from the given id."""
        for subclass in cls.__subclasses__():
            enum = next((enum for enum in subclass if enum.id == eid), None)
            if enum:
                return enum
        return None

    def get_filename(self):
        """Get the filename for the question listing type."""
        return self.id + OUTPUT_FILE_SUFFIX + OUTPUT_FILE_EXTENSION


class GeneralQuestionListingType(QuestionListingType):
    """Enumeration for general question listing types."""

    ALL = ("all", "All questions")
    SAME_ANSWER = ("same-answer", "Same answer")
    SAME_CHOICES = ("same-choices", "Same choices")
    TWO_OR_MORE_SAME_CHOICES = ("two-or-more-same-choices", "Two or more same choices")
    QN_ANSWER = ("qn-answer", "Question answer")


class TopQuestionsListingType(QuestionListingType):
    """Enumeration for top questions listing types."""

    LONGEST_QUESTION_TEXT = ("longest-question-text", "Longest question text")
    LONGEST_CORRECT_CHOICE = ("longest-correct-choice", "Longest correct choice")


class MarkedQuestionListingType(QuestionListingType):
    """Enumeration for marked question listing types."""

    WRONG_ATTEMPT = ("wrong-attempt", "Wrong attempt")
    CORRECT_ANSWER = ("correct-answer", "Correct answer")
    SKIPPED = ("skipped", "Skipped")

    def get_filename(self):
        """Get the filename for the marked question listing type."""
        return MARKED_OUTPUT_FILE_PREFIX + self.id + OUTPUT_FILE_SUFFIX + OUTPUT_FILE_EXTENSION


class RankBy(HRTEnum):
    """Enumeration for ranking criteria."""

    EASE_OF_USE = ("ease-of-use", "Ease of use")
    PHONETIC_CLARITY = ("phonetic-clarity", "Phonetic clarity")
    CONFUSING_PAIR = ("confusing-pair", "Confusing pair")
    CW_WEIGHT = ("cw-weight", "Morse code weight")


class SortBy(HRTEnum):
    """Enumeration for sorting criteria."""

    CALLSIGN = ("callsign", "Callsign")
    SCORE = ("score", "Score")


class ExamType(CountrySpecificEnum):
    """Enumeration for exam types."""

    BASIC = ("basic", CountryCode.CANADA, True, "Basic exam")
    ADVANCED = ("advanced", CountryCode.CANADA, True, "Advanced exam")
    TECHNICAL = ("technical", CountryCode.UNITED_STATES, False, "Technical exam")
    GENERAL = ("general", CountryCode.UNITED_STATES, False, "General exam")
    EXTRA = ("extra", CountryCode.UNITED_STATES, False, "Extra exam")
    GENERAL_GRADE = ("general-grade", CountryCode.INDIA, False, "General grade exam")
    RESTRICTED_GRADE = ("restricted-grade", CountryCode.INDIA, False, "Restricted grade exam")


class QuestionRefType(HRTEnum):
    """Enumeration for question reference types."""

    BOOK = ("book", "Book reference")
    WEBSITE = ("website", "Website reference")
    VIDEO = ("video", "Video reference")
    PDF = ("pdf", "PDF reference")


class QuestionAnswerDisplay(HRTEnum):
    """Enumeration for question answer display options."""

    WITH_QUESTION = ("with-question", "With question")
    IN_THE_END = ("in-the-end", "In the end")
    HIDE = ("hide", "Hide")


class QuizAnswerDisplay(HRTEnum):
    """Enumeration for quiz answer display options."""

    AFTER_QUESTION = ("after-question", "After question")
    IN_THE_END = ("in-the-end", "In the end")
    HIDE = ("hide", "Hide")


class QuestionDisplayMode(HRTEnum):
    """Enumeration for question display modes."""

    QUIZ = ("quiz", "Quiz")
    PRINT = ("print", "Print question")
    PRACTICE_EXAM = ("practice_exam", "Practice exam")


class QuizSource(HRTEnum):
    """Enumeration for quiz source types."""

    ALL = ("all", "All questions")
    OLD = ("old", "Old questions")
    NEW = ("new", "New questions")
    MARKED = ("marked", "Marked questions")
    WRONG_ANSWERS = ("wrong", "Questions with wrong answers")
    SKIPPED_QUESTIONS = ("skipped", "Skipped questions")
    EXCLUDE_CORRECT_ANSWERS = ("x-ca", "Exclude correct answers")
    EXCLUDE_MARKED_QUESTIONS = ("x-mq", "Exclude marked questions")
