import unittest
from hrt.common.enums import (
    CallSignDownloadType,
    CountryCode,
    CACallSignDownloadType,
    CountrySpecificEnum,
    DownloadType,
    GeneralQuestionListingType,
    HRTEnum,
    MarkedQuestionListingType,
    NumberOfLetters,
    QuestionListingType,
    RankBy,
    SortBy,
    SupportedEnum,
    ExamType,
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

    def test_country_specific_enum(self):
        class SampleEnum(CountrySpecificEnum):
            OPTION_A = ("Option A", CountryCode.CANADA, True, "Description A")
            OPTION_B = ("Option B", CountryCode.UNITED_STATES, False, "Description B")

        self.assertEqual(SampleEnum.OPTION_A.country, CountryCode.CANADA)
        self.assertEqual(SampleEnum.supported_country_ids(CountryCode.CANADA), ["Option A"])
        self.assertIsNone(SampleEnum.from_id_and_country("Option B", CountryCode.CANADA))

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

    def test_call_sign_download_type(self):
        self.assertEqual(
            list(CACallSignDownloadType.supported_country_ids(CountryCode.CANADA)),
            ["available", "assigned"],
        )
        self.assertIsNone(
            CACallSignDownloadType.from_id_and_country("available", CountryCode.UNITED_STATES)
        )

    def test_number_of_letters(self):
        self.assertEqual(NumberOfLetters.SINGLE.word_match, False)
        self.assertEqual(
            NumberOfLetters.get_supported_number_of_letters("include"),
            ["1l", "2l", "3l", "el", "all"],
        )

    def test_question_listing_type(self):
        class TestListingType(QuestionListingType):
            SAMPLE = {"name": "sample", "description": "Sample description"}

        listing = TestListingType.SAMPLE.value
        self.assertEqual(listing["name"], "sample")
        self.assertEqual(listing["description"], "Sample description")

    def test_marked_question_listing_type(self):
        self.assertEqual(
            MarkedQuestionListingType.WRONG_ATTEMPT.get_filename(),
            "marked-wrong-attempt-questions.txt",
        )

    def test_hrt_enum_string_representation(self):
        self.assertEqual(str(RankBy.EASE_OF_USE), "ease-of-use - Ease of use")
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
        self.assertEqual(result, TestListingType.SAMPLE)

        result = TestListingType.from_id("non-existent")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
