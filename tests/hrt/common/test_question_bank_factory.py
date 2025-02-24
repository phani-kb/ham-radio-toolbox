import unittest
from pathlib import Path
from hrt.common.enums import CountryCode, ExamType, QuestionDisplayMode
from hrt.common.question_bank import QuestionBankFactory


class TestQuestionBankFactory(unittest.TestCase):
    def test_get_question_bank_canada(self):
        question_bank = QuestionBankFactory.get_question_bank(
            country=CountryCode.CANADA,
            exam_type=ExamType.BASIC,
            filepath=Path("/path/to/questions"),
            display_mode=QuestionDisplayMode.PRINT,
            categories_filepath=Path("/path/to/categories"),
            marked_questions_filepath=Path("/path/to/marked"),
            metrics_filepath=Path("/path/to/metrics"),
        )
        from hrt.question_banks.ca_question_bank import CAQuestionBank

        self.assertIsInstance(question_bank, CAQuestionBank)

    def test_get_question_bank_unsupported_country(self):
        with self.assertRaises(ValueError) as context:
            QuestionBankFactory.get_question_bank(
                country=CountryCode.UNITED_STATES,
                exam_type=ExamType.BASIC,
                filepath=Path("/path/to/questions"),
                display_mode=QuestionDisplayMode.PRINT,
                categories_filepath=Path("/path/to/categories"),
                marked_questions_filepath=Path("/path/to/marked"),
                metrics_filepath=Path("/path/to/metrics"),
            )
        self.assertEqual(
            str(context.exception), "Country us - United States (Supported: False) not supported"
        )


if __name__ == "__main__":
    unittest.main()
