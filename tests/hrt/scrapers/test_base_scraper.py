import os
import unittest
from unittest.mock import MagicMock, patch

from hrt.scrapers.base_scraper import BaseScraper, ScraperFactory
from hrt.common.enums import CACallSignDownloadType, CountryCode
from hrt.scrapers.ca_scraper import CAScraper
from hrt.scrapers.us_scraper import USScraper

import yaml


class TestScraperFactory(unittest.TestCase):
    def setUp(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "config", "config.yml"
        )
        if not os.path.exists(config_path):
            self.skipTest(f"{config_path} not found")
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        self.driver = config["web_driver"]

    def test_get_scraper_canada(self):
        scraper = ScraperFactory.get_scraper(self.driver, CountryCode.CANADA)
        self.assertIsInstance(scraper, CAScraper)

    def test_get_scraper_united_states(self):
        scraper = ScraperFactory.get_scraper(self.driver, CountryCode.UNITED_STATES)
        self.assertIsInstance(scraper, USScraper)

    def test_get_scraper_invalid_country(self):
        with self.assertRaises(ValueError):
            ScraperFactory.get_scraper(self.driver, "INVALID_COUNTRY")


class MockBaseScraper(BaseScraper):
    def download_assigned_callsigns(self, url, output_file_path):
        pass

    def download_available_callsigns(self, url, output_file_path):
        pass


class TestDownloadCallsigns(unittest.TestCase):
    @patch("hrt.scrapers.base_scraper.webdriver.Chrome")
    def setUp(self, mock_web_driver):
        self.mock_driver = mock_web_driver.return_value
        self.scraper = MockBaseScraper(driver="path/to/chromedriver", country=CountryCode.CANADA)

    @patch("hrt.scrapers.base_scraper.random.choice")
    def test_download_callsigns_assigned(self, mock_random_choice):
        mock_random_choice.return_value = "test-user-agent"
        self.scraper.download_assigned_callsigns = MagicMock()

        self.scraper.download_callsigns(
            callsign_download_type=CACallSignDownloadType.ASSIGNED,
            url="https://example.com/assigned",
            output_file_path="/path/to/output",
        )

        self.scraper.download_assigned_callsigns.assert_called_once_with(
            "https://example.com/assigned", "/path/to/output"
        )

    @patch("hrt.scrapers.base_scraper.random.choice")
    def test_download_callsigns_available(self, mock_random_choice):
        mock_random_choice.return_value = "test-user-agent"
        self.scraper.download_available_callsigns = MagicMock()

        self.scraper.download_callsigns(
            callsign_download_type=CACallSignDownloadType.AVAILABLE,
            url="https://example.com/available",
            output_file_path="/path/to/output",
        )

        self.scraper.download_available_callsigns.assert_called_once_with(
            "https://example.com/available", "/path/to/output"
        )

    def test_download_callsigns_invalid_type(self):
        with self.assertRaises(ValueError):
            self.scraper.download_callsigns(
                callsign_download_type="INVALID_TYPE",
                url="https://example.com/invalid",
                output_file_path="/path/to/output",
            )

    @patch("hrt.scrapers.base_scraper.random.choice")
    @patch("hrt.scrapers.base_scraper.logger.error")
    def test_download_callsigns_error_handling(self, mock_logger_error, mock_random_choice):
        mock_random_choice.return_value = "test-user-agent"
        self.scraper.download_assigned_callsigns = MagicMock(
            side_effect=Exception("Test Exception")
        )

        with self.assertRaises(Exception):
            self.scraper.download_callsigns(
                callsign_download_type=CACallSignDownloadType.ASSIGNED,
                url="https://example.com/assigned",
                output_file_path="/path/to/output",
            )

        mock_logger_error.assert_called_once_with(
            f"Error downloading callsigns for {CountryCode.CANADA}: Test Exception"
        )


if __name__ == "__main__":
    unittest.main()
