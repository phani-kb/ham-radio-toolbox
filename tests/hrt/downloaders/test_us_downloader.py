import unittest
from hrt.downloaders.us_downloader import USDownloader
from hrt.common.enums import DownloadType, ExamType


class TestUSDownloader(unittest.TestCase):
    def setUp(self):
        self.chrome_driver_path = "path/to/chromedriver"
        self.download_type = DownloadType.US_CALLSIGN
        self.output_folder = "/path/to/output"
        self.config = {}
        self.downloader = USDownloader(
            self.chrome_driver_path,
            self.download_type,
            self.output_folder,
            self.config,
        )

    def test_download_callsigns(self):
        with self.assertRaises(NotImplementedError):
            self.downloader.download_callsigns(None)

    def test_download_question_bank(self):
        with self.assertRaises(NotImplementedError):
            self.downloader.download_question_bank(ExamType.TECHNICAL)


if __name__ == "__main__":
    unittest.main()
