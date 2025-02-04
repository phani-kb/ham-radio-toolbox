import unittest
from hrt.common.enums import QuestionRefType
from hrt.common.question_ref import BookRef, WebRef, VideoRef, PDFRef


class TestQuestionRef(unittest.TestCase):
    def test_book_ref(self):
        book_ref = BookRef("Python Programming")
        self.assertEqual(book_ref.type, QuestionRefType.BOOK)
        self.assertEqual(book_ref.title, "Python Programming")
        self.assertEqual(book_ref.details(), "Python Programming")
        self.assertEqual(str(book_ref), "BOOK: Python Programming")

    def test_web_ref(self):
        web_ref = WebRef("https://example.com")
        self.assertEqual(web_ref.type, QuestionRefType.WEBSITE)
        self.assertEqual(web_ref.url, "https://example.com")
        self.assertEqual(web_ref.details(), "https://example.com")
        self.assertEqual(str(web_ref), "WEBSITE: https://example.com")

    def test_video_ref(self):
        video_ref = VideoRef("https://example.com/video")
        self.assertEqual(video_ref.type, QuestionRefType.VIDEO)
        self.assertEqual(video_ref.url, "https://example.com/video")
        self.assertEqual(video_ref.details(), "https://example.com/video")
        self.assertEqual(str(video_ref), "VIDEO: https://example.com/video")

    def test_pdf_ref(self):
        pdf_ref = PDFRef("https://example.com/document.pdf")
        self.assertEqual(pdf_ref.type, QuestionRefType.PDF)
        self.assertEqual(pdf_ref.url, "https://example.com/document.pdf")
        self.assertEqual(pdf_ref.details(), "https://example.com/document.pdf")
        self.assertEqual(str(pdf_ref), "PDF: https://example.com/document.pdf")


if __name__ == "__main__":
    unittest.main()
