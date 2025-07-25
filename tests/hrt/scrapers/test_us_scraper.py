import unittest
from unittest.mock import patch
from hrt.scrapers.us_scraper import USScraper


class TestUSScraper(unittest.TestCase):
    @patch("selenium.webdriver.Chrome")
    def setUp(self, mock_web_driver):
        self.mock_driver = mock_web_driver.return_value
        self.scraper = USScraper(driver="path/to/chromedriver")

    def test_download_assigned_callsigns_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.scraper.download_assigned_callsigns(
                "https://example.com/assigned", "/path/to/output"
            )

    def test_download_available_callsigns_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.scraper.download_available_callsigns(
                "https://example.com/available", "/path/to/output"
            )


if __name__ == "__main__":
    unittest.main()
