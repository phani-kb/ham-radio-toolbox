import unittest
from hrt.common.enums import (
    CallSignDownloadType,
    CACallSignDownloadType,
    CountryCode,
    CountrySpecificEnum,
    DownloadType,
    ExamType,
    GeneralQuestionListingType,
    HRTEnum,
    MarkedQuestionListingType,
    NumberOfLetters,
    QuestionAnswerDisplay,
    QuestionDisplayMode,
    QuestionListingType,
    QuestionRefType,
    QuizAnswerDisplay,
    QuizSource,
    SortBy,
    SupportedEnum,
    TopQuestionsListingType,
    USCallSignDownloadType,
)


class TestEnumClasses(unittest.TestCase):
    def test_hrt_enum(self):
        class SampleEnum(HRTEnum):
            OPTION_A = ("Option A", "Description A")
            OPTION_B = "Option B"

        self.assertEqual(str(SampleEnum.OPTION_A), "Option A - Description A")
        self.assertEqual(str(SampleEnum.OPTION_B), "Option B")
        self.assertEqual(SampleEnum.from_name("OPTION_A"), SampleEnum.OPTION_A)
        self.assertEqual(SampleEnum.from_id("Option A"), SampleEnum.OPTION_A)
        result = SampleEnum.ids()
        self.assertEqual(result, ["Option A", "Option B"])

    def test_hrt_from_value(self):
        result = CountryCode.from_value(CountryCode.CANADA)
        self.assertEqual(result, CountryCode.CANADA)

        result = QuizSource.from_value(QuizSource.ALL)
        self.assertEqual(result, QuizSource.ALL)

        result = CountryCode.from_value("non_existent_value")
        self.assertIsNone(result)

        result = CountryCode.from_value(None)
        self.assertIsNone(result)

        result = GeneralQuestionListingType.from_value("non_existent_value")
        self.assertIsNone(result)

    def test_supported_enum(self):
        class SampleSupportedEnum(SupportedEnum):
            OPTION_A = ("Option A", True, "Description A")
            OPTION_B = ("Option B", False, "Description B")

        self.assertEqual(SampleSupportedEnum.OPTION_A.is_supported, True)
        self.assertEqual(
            str(SampleSupportedEnum.OPTION_A), "Option A - Description A (Supported: True)"
        )
        self.assertEqual(SampleSupportedEnum.supported_ids(), ["Option A"])

    def test_country_code(self):
        self.assertEqual(CountryCode.CANADA.code, "ca")
        self.assertEqual(CountryCode.from_id("ca"), CountryCode.CANADA)
        self.assertEqual(CountryCode.UNITED_STATES.is_supported, False)
        self.assertEqual(CountryCode.INDIA.id, "in")
        self.assertEqual(CountryCode.from_value(CountryCode.CANADA), CountryCode.CANADA)
        self.assertIsNone(CountryCode.from_value("invalid"))

    def test_country_specific_enum(self):
        class SampleEnum(CountrySpecificEnum):
            OPTION_A = ("Option A", CountryCode.CANADA, True, "Description A")
            OPTION_B = ("Option B", CountryCode.UNITED_STATES, False, "Description B")

        self.assertEqual(SampleEnum.OPTION_A.country, CountryCode.CANADA)
        self.assertEqual(SampleEnum.supported_country_ids(CountryCode.CANADA), ["Option A"])
        self.assertIsNone(SampleEnum.from_id_and_country("Option B", CountryCode.CANADA))
        self.assertEqual(SampleEnum.supported_country_options(CountryCode.CANADA), ["Option A"])
        self.assertEqual(
            SampleEnum.from_value_and_country("Option A", CountryCode.CANADA), SampleEnum.OPTION_A
        )
        self.assertIsNone(SampleEnum.from_value_and_country("Invalid", CountryCode.CANADA))

    def test_download_type(self):
        self.assertEqual(DownloadType.CA_QUESTION_BANK.country, CountryCode.CANADA)
        self.assertEqual(
            DownloadType.supported_country_ids(CountryCode.CANADA),
            ["question-bank", "callsign"],
        )
        self.assertEqual(
            DownloadType.from_id_and_country("question-bank", CountryCode.UNITED_STATES),
            DownloadType.US_QUESTION_BANK,
        )
        self.assertEqual(
            DownloadType.from_value(DownloadType.CA_QUESTION_BANK), DownloadType.CA_QUESTION_BANK
        )
        self.assertIsNone(DownloadType.from_value("invalid"))

    def test_call_sign_download_type(self):
        self.assertEqual(
            list(CACallSignDownloadType.supported_country_ids(CountryCode.CANADA)),
            ["available", "assigned"],
        )
        self.assertIsNone(
            CACallSignDownloadType.from_id_and_country("available", CountryCode.UNITED_STATES)
        )
        self.assertEqual(CACallSignDownloadType.list(), ["available", "assigned"])

        # Test supported_country_options method
        self.assertEqual(
            CallSignDownloadType.supported_country_options(CountryCode.CANADA),
            ["available", "assigned"],
        )

        # Test from_value_and_country method
        self.assertEqual(
            CallSignDownloadType.from_value_and_country("available", CountryCode.CANADA),
            CACallSignDownloadType.AVAILABLE,
        )
        self.assertIsNone(
            CallSignDownloadType.from_value_and_country("invalid", CountryCode.CANADA)
        )

        # Test from_value method
        self.assertEqual(
            CACallSignDownloadType.from_value("available"), CACallSignDownloadType.AVAILABLE
        )
        self.assertIsNone(CACallSignDownloadType.from_value("invalid"))

    def test_us_call_sign_download_type(self):
        self.assertEqual(USCallSignDownloadType.ACTIVE.country, CountryCode.UNITED_STATES)
        self.assertEqual(USCallSignDownloadType.ACTIVE.description, "Active")
        self.assertFalse(USCallSignDownloadType.ACTIVE.is_supported)

    def test_number_of_letters(self):
        self.assertEqual(NumberOfLetters.SINGLE.word_match, False)
        self.assertEqual(
            NumberOfLetters.get_supported_number_of_letters("include"),
            ["1l", "2l", "3l", "el", "all"],
        )
        self.assertEqual(
            NumberOfLetters.get_supported_number_of_letters("word_match"),
            ["2l", "3l"],
        )

    def test_question_listing_type(self):
        class TestListingType(QuestionListingType):
            SAMPLE = ("sample", "Sample description")

        self.assertEqual(TestListingType.SAMPLE.id, "sample")
        self.assertEqual(TestListingType.SAMPLE.description, "Sample description")
        self.assertEqual(TestListingType.SAMPLE.get_filename(), "sample-questions.txt")

        # Test from_id method for base class and subclasses
        result = QuestionListingType.from_id("sample")
        self.assertEqual(result, TestListingType.SAMPLE)

        # Test from_id for GeneralQuestionListingType
        result = QuestionListingType.from_id("all")
        self.assertEqual(result, GeneralQuestionListingType.ALL)

    def test_general_question_listing_type(self):
        self.assertEqual(GeneralQuestionListingType.ALL.id, "all")
        self.assertEqual(GeneralQuestionListingType.ALL.description, "All questions")
        self.assertEqual(GeneralQuestionListingType.ALL.get_filename(), "all-questions.txt")

    def test_top_questions_listing_type(self):
        self.assertEqual(TopQuestionsListingType.LONGEST_QUESTION_TEXT.id, "longest-question-text")
        self.assertEqual(
            TopQuestionsListingType.LONGEST_QUESTION_TEXT.description, "Longest question text"
        )
        self.assertEqual(
            TopQuestionsListingType.LONGEST_QUESTION_TEXT.get_filename(),
            "longest-question-text-questions.txt",
        )

    def test_marked_question_listing_type(self):
        self.assertEqual(
            MarkedQuestionListingType.WRONG_ATTEMPT.get_filename(),
            "marked-wrong-attempt-questions.txt",
        )
        self.assertEqual(MarkedQuestionListingType.CORRECT_ANSWER.id, "correct-answer")
        self.assertEqual(MarkedQuestionListingType.SKIPPED.description, "Skipped")

    def test_hrt_enum_string_representation(self):
        self.assertEqual(str(SortBy.CALLSIGN), "callsign - Callsign")
        enum_str = str(DownloadType.CA_QUESTION_BANK)
        self.assertEqual(
            enum_str,
            "question-bank - Canadian Question Bank (Supported: True) (Country: ca - Canada (Supported: True))",  # noqa: E501, pylint: disable=C0301
        )
        self.assertEqual(
            str(NumberOfLetters.SINGLE),
            "1l - Single letter (Word Match: False) (Include: True) (Exclude: True)",
        )

    def test_exam_type(self):
        self.assertEqual(ExamType.supported_country_ids(CountryCode.CANADA), ["basic", "advanced"])
        self.assertIsNone(ExamType.from_id_and_country("technical", CountryCode.CANADA))
        self.assertEqual(ExamType.BASIC.country, CountryCode.CANADA)
        self.assertTrue(ExamType.BASIC.is_supported)
        self.assertFalse(ExamType.TECHNICAL.is_supported)

    def test_get_filename(self):
        marked_question = MarkedQuestionListingType.WRONG_ATTEMPT
        expected_filename = "marked-wrong-attempt-questions.txt"
        self.assertEqual(marked_question.get_filename(), expected_filename)

        question_listing = GeneralQuestionListingType.ALL
        expected_filename = "all-questions.txt"
        self.assertEqual(question_listing.get_filename(), expected_filename)

    def test_from_value(self):
        # Test for a valid value
        result = CACallSignDownloadType.from_id("available")
        self.assertIsNotNone(result)
        self.assertEqual(result.value[0], "available")
        # Test for an invalid value
        result = CACallSignDownloadType.from_id("non-existent")
        self.assertIsNone(result)

    def test_getitem(self):
        class SampleEnum(HRTEnum):
            OPTION_A = "Option A"
            OPTION_B = "Option B"

        self.assertEqual(SampleEnum["OPTION_A"], SampleEnum.OPTION_A)
        self.assertEqual(SampleEnum["OPTION_B"], SampleEnum.OPTION_B)

    def test_list_method(self):
        class SampleEnum(HRTEnum):
            OPTION_A = ("Option A", "Description A")
            OPTION_B = ("Option B", "Description B")

        expected_list = [SampleEnum.OPTION_A, SampleEnum.OPTION_B]
        self.assertEqual(SampleEnum.list(), expected_list)

    def test_list1(self):
        class SampleEnum(HRTEnum):
            OPTION_A = ("Option A",)
            OPTION_B = ("Option B",)

        expected = ["Option A", "Option B"]
        self.assertEqual(SampleEnum.ids(), expected)

    def test_list2(self):
        class SampleCallSignEnum(CallSignDownloadType):
            AVAILABLE = ("available", CountryCode.CANADA, True, "Available")
            ASSIGNED = ("assigned", CountryCode.CANADA, True, "Assigned")

        expected = ["available", "assigned"]
        self.assertEqual(SampleCallSignEnum.ids(), expected)
        result = SampleCallSignEnum.AVAILABLE.from_id_and_country("available", CountryCode.CANADA)
        self.assertEqual(result, SampleCallSignEnum.AVAILABLE)

    def test_exclude_property(self):
        self.assertTrue(NumberOfLetters.SINGLE.exclude)
        self.assertTrue(NumberOfLetters.TWO.exclude)
        self.assertTrue(NumberOfLetters.THREE.exclude)
        self.assertTrue(NumberOfLetters.END.exclude)
        self.assertTrue(NumberOfLetters.MULTIPLE.exclude)
        self.assertTrue(NumberOfLetters.ALL.exclude)

    def test_question_listing_type_from_id(self):
        class TestListingType(QuestionListingType):
            SAMPLE = ("sample", "Sample description")

        result = QuestionListingType.from_id("sample")
        self.assertIsNotNone(result)
        # Instead of direct equality, check the id and description
        self.assertEqual(result.id, TestListingType.SAMPLE.id)
        self.assertEqual(result.description, TestListingType.SAMPLE.description)

        result = TestListingType.from_id("non-existent")
        self.assertIsNone(result)

    def test_question_ref_type(self):
        self.assertEqual(QuestionRefType.BOOK.id, "book")
        self.assertEqual(QuestionRefType.WEBSITE.description, "Website reference")
        self.assertEqual(str(QuestionRefType.VIDEO), "video - Video reference")
        self.assertEqual(QuestionRefType.from_id("pdf"), QuestionRefType.PDF)
        self.assertIsNone(QuestionRefType.from_id("invalid"))

    def test_question_answer_display(self):
        self.assertEqual(QuestionAnswerDisplay.WITH_QUESTION.id, "with-question")
        self.assertEqual(QuestionAnswerDisplay.IN_THE_END.description, "In the end")
        self.assertEqual(str(QuestionAnswerDisplay.HIDE), "hide - Hide")

    def test_quiz_answer_display(self):
        self.assertEqual(QuizAnswerDisplay.AFTER_QUESTION.id, "after-question")
        self.assertEqual(QuizAnswerDisplay.IN_THE_END.description, "In the end")
        self.assertEqual(str(QuizAnswerDisplay.HIDE), "hide - Hide")

    def test_question_display_mode(self):
        self.assertEqual(QuestionDisplayMode.QUIZ.id, "quiz")
        self.assertEqual(QuestionDisplayMode.PRINT.description, "Print question")
        self.assertEqual(str(QuestionDisplayMode.PRACTICE_EXAM), "practice_exam - Practice exam")

    def test_quiz_source(self):
        self.assertEqual(QuizSource.ALL.id, "all")
        self.assertEqual(QuizSource.OLD.description, "Old questions")
        self.assertEqual(str(QuizSource.NEW), "new - New questions")
        self.assertEqual(QuizSource.from_name("MARKED"), QuizSource.MARKED)
        self.assertEqual(QuizSource.from_id("wrong"), QuizSource.WRONG_ANSWERS)


if __name__ == "__main__":
    unittest.main()
