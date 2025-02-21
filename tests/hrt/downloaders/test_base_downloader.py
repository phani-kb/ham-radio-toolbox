import unittest
from unittest.mock import patch
from hrt.downloaders.base_downloader import DownloaderFactory
from hrt.common.enums import CountryCode, DownloadType
from hrt.downloaders.ca_downloader import CADownloader


class TestBaseDownloader(unittest.TestCase):
    def setUp(self):
        from hrt.downloaders.ca_downloader import CADownloader

        self.chrome_driver_path = "path/to/chromedriver"
        self.country = CountryCode.CANADA
        self.download_type = DownloadType.CA_CALLSIGN
        self.output_folder = "/path/to/output"
        self.config = {"key": "value"}
        self.downloader = CADownloader(
            self.chrome_driver_path,
            self.download_type,
            self.output_folder,
            self.config,
        )

    def test_chrome_driver_path(self):
        self.assertEqual(self.downloader.chrome_driver_path, self.chrome_driver_path)

    def test_config(self):
        self.assertEqual(self.downloader.config, self.config)

    def test_get_output_folder(self):
        expected_output_folder = "/path/to/output/" + self.country.code
        self.assertEqual(self.downloader.get_output_folder(), expected_output_folder)

    @patch("hrt.downloaders.base_downloader.logger")
    def test_get_output_folder_no_output_folder(self, mock_logger):
        output_folder = self.downloader.output_folder
        self.downloader._output_folder = ""
        result = self.downloader.get_output_folder()
        mock_logger.error.assert_called_once_with("Output folder not found")
        self.assertIsNone(result)
        self.downloader._output_folder = output_folder

    def test_download_type(self):
        self.assertEqual(self.downloader.download_type, self.download_type)

    @patch("hrt.common.utils.create_folder")
    @patch("hrt.common.utils.download_file")
    def test_download(self, mock_download_file, mock_create_folder):
        url = "https://example.com/file.zip"
        output_file_path = "/path/to/output/file.zip"
        zip_files = ["file1.zip", "file2.zip"]

        self.downloader.download(url, output_file_path, zip_files)

        mock_create_folder.assert_called_once_with("/path/to/output")
        mock_download_file.assert_called_once_with(url, output_file_path, zip_files)

    def test_pre_process(self):
        self.downloader.pre_process()
        # Add assertions if pre_process has any side effects

    def test_post_process(self):
        self.downloader.post_process()
        # Add assertions if post_process has any side effects


class TestDownloaderFactory(unittest.TestCase):
    def setUp(self):
        self.chrome_driver_path = "path/to/chromedriver"
        self.download_type = DownloadType.CA_CALLSIGN
        self.output_folder = "/path/to/output"
        self.config = {"key": "value"}

    def test_get_downloader_canada(self):
        from hrt.downloaders.ca_downloader import CADownloader

        downloader = DownloaderFactory.get_downloader(
            self.chrome_driver_path,
            CountryCode.CANADA,
            self.download_type,
            self.output_folder,
            self.config,
        )
        self.assertIsInstance(downloader, CADownloader)

    def test_get_downloader_united_states(self):
        from hrt.downloaders.us_downloader import USDownloader

        downloader = DownloaderFactory.get_downloader(
            self.chrome_driver_path,
            CountryCode.UNITED_STATES,
            self.download_type,
            self.output_folder,
            self.config,
        )
        self.assertIsInstance(downloader, USDownloader)

    def test_get_downloader_invalid_country(self):
        with self.assertRaises(ValueError):
            DownloaderFactory.get_downloader(
                self.chrome_driver_path,
                "INVALID_COUNTRY",
                self.download_type,
                self.output_folder,
                self.config,
            )


if __name__ == "__main__":
    unittest.main()
