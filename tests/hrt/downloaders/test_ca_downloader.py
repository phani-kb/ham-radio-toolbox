import unittest
from unittest.mock import patch, MagicMock
from hrt.downloaders.ca_downloader import CADownloader
from hrt.common.enums import CACallSignDownloadType, CountryCode, DownloadType, ExamType


class TestCADownloader(unittest.TestCase):
    def setUp(self):
        self.chrome_driver_path = "path/to/chromedriver"
        self.download_type = DownloadType.CA_CALLSIGN
        self.output_folder = "/path/to/output"
        self.config = {
            "basic": {
                "download_url": "https://example.com/questions.zip",
                "file": "questions.csv",
                "zip_files": ["file1.csv", "file2.csv"],
            },
            "advanced": {
                "file": "questions.csv",
                "zip_files": ["file1.csv", "file2.csv"],
            },
            "assigned": {
                "download_url": "https://example.com/callsigns.zip",
                "file": "callsigns.csv",
            },
        }
        self.downloader = CADownloader(
            self.chrome_driver_path,
            self.download_type,
            self.output_folder,
            self.config,
        )

    @patch("hrt.downloaders.base_downloader.ScraperFactory.get_scraper")
    @patch("hrt.downloaders.base_downloader.logger")
    def test_download_callsigns(self, mock_logger, mock_get_scraper):
        mock_scraper = MagicMock()
        mock_get_scraper.return_value = mock_scraper

        self.downloader.download_callsigns(CACallSignDownloadType.ASSIGNED)

        mock_get_scraper.assert_called_once_with(self.chrome_driver_path, CountryCode.CANADA, None)
        mock_scraper.download_callsigns.assert_called_once_with(
            CACallSignDownloadType.ASSIGNED,
            "https://example.com/callsigns.zip",
            "/path/to/output/ca/callsign/callsigns.csv",
        )
        mock_logger.error.assert_not_called()

    @patch("hrt.downloaders.base_downloader.logger")
    def test_download_callsigns_no_config(self, mock_logger):
        self.downloader._config = {}
        self.downloader.download_callsigns(CACallSignDownloadType.ASSIGNED)
        mock_logger.error.assert_called_once_with(
            "Config not found for callsign in country %s", "ca"
        )

    @patch("hrt.downloaders.base_downloader.logger")
    def test_download_callsigns_no_url(self, mock_logger):
        self.downloader._config = {"assigned": {"file": "callsigns.csv"}}
        self.downloader.download_callsigns(CACallSignDownloadType.ASSIGNED)
        mock_logger.error.assert_called_once_with(
            "URL not found for callsign in country %s for %s", "ca", "assigned"
        )

    @patch("hrt.downloaders.base_downloader.logger")
    def test_get_output_file_path_no_input_file_path(self, mock_logger):
        self.downloader._config = {
            "assigned": {"download_url": "https://example.com/callsigns.zip"}
        }
        result = self.downloader.get_output_file_path(CACallSignDownloadType.ASSIGNED)
        mock_logger.error.assert_called_once_with(
            "Input file path not found for %s in country %s", "assigned", "ca"
        )
        self.assertEqual(result, "")

    @patch("hrt.downloaders.base_downloader.BaseDownloader.download")
    @patch("hrt.downloaders.base_downloader.logger")
    def test_download_file(self, mock_logger, mock_download):
        key = ExamType.BASIC
        self.downloader._download_type = DownloadType.from_id_and_country(
            "question-bank", CountryCode.CANADA
        )
        self.downloader._download_file(key, "download_url", "basic")

        mock_download.assert_called_once_with(
            "https://example.com/questions.zip",
            "/path/to/output/ca/question-bank/questions.csv",
            ["file1.csv", "file2.csv"],
        )
        mock_logger.error.assert_not_called()

    @patch("hrt.downloaders.base_downloader.logger")
    def test_download_file_no_url(self, mock_logger):
        key = ExamType.ADVANCED
        self.downloader._download_type = DownloadType.from_id_and_country(
            "question-bank", CountryCode.CANADA
        )
        self.downloader._download_file(key, "download_url", "exam")

        mock_logger.error.assert_called_once_with(
            "URL not found for %s in country %s for %s", "exam", "ca", "advanced"
        )

    @patch.object(CADownloader, "_download_file")
    def test_download_question_bank(self, mock_download_file):
        exam_type = ExamType.BASIC
        self.downloader.download_question_bank(exam_type)
        mock_download_file.assert_called_once_with(exam_type, "download_url", "question bank")


if __name__ == "__main__":
    unittest.main()
