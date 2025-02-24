import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock, mock_open

from hrt.scrapers.ca_scraper import CAScraper, select_option


class TestSelectOption(unittest.TestCase):
    def setUp(self):
        self.mock_element = MagicMock()
        self.mock_option1 = MagicMock()
        self.mock_option1.text = "Option 1"
        self.mock_option1.get_attribute.return_value = "value1"
        self.mock_option2 = MagicMock()
        self.mock_option2.text = "Option 2"
        self.mock_option2.get_attribute.return_value = "value2"
        self.mock_element.find_elements.return_value = [self.mock_option1, self.mock_option2]

    def test_select_option(self):
        with patch(
            "hrt.scrapers.ca_scraper.select_from_options", return_value="value1"
        ) as mock_select:
            select_option(self.mock_element, "Select an option")

            # Verify that the select_from_options function was called with the correct arguments
            mock_select.assert_called_once_with(
                {"Option 1": "value1", "Option 2": "value2"}, "Select an option"
            )

            # Verify that the send_keys method was called with the correct value
            self.mock_element.send_keys.assert_called_once_with("value1")

    def test_select_option_no_selection(self):
        with patch(
            "hrt.scrapers.ca_scraper.select_from_options", return_value=None
        ) as mock_select:
            select_option(self.mock_element, "Select an option")

            # Verify that the select_from_options function was called with the correct arguments
            mock_select.assert_called_once_with(
                {"Option 1": "value1", "Option 2": "value2"}, "Select an option"
            )

            # Verify that the send_keys method was called with an empty string
            self.mock_element.send_keys.assert_called_once_with("")


class TestCAScraper(unittest.TestCase):
    @patch("selenium.webdriver.Chrome")
    def setUp(self, mock_web_driver):
        self.mock_driver = mock_web_driver.return_value
        self.scraper = CAScraper(driver="path/to/chromedriver")

    @patch("requests.get")
    @patch("zipfile.ZipFile")
    def test_download_assigned_callsigns(self, mock_zipfile, mock_requests_get):
        mock_response = MagicMock()
        mock_response.content = b"fake-zip-content"
        mock_requests_get.return_value = mock_response

        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        with patch("builtins.open", mock_open()) as mock_file:
            self.scraper.download_assigned_callsigns(
                "https://example.com/assigned.zip", "/path/to/output"
            )

            mock_requests_get.assert_called_once_with(
                "https://example.com/assigned.zip", timeout=10
            )
            mock_zipfile.assert_called_once()
            mock_file.assert_called_once_with("/path/to/output", "wb")

    @patch("builtins.input", side_effect=["A", "B", "C"])
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    @patch("hrt.scrapers.ca_scraper.select_option")
    def test_download_available_callsigns(self, mock_select_option, mock_webdriver_wait, _):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element
        self.mock_driver.page_source = "No such call sign is available."

        callsigns = self.scraper.download_available_callsigns(
            "https://example.com/available", "/path/to/output"
        )

        self.mock_driver.get.assert_called_once_with("https://example.com/available")
        mock_select_option.assert_called()
        self.assertEqual(callsigns, [])

    @patch("builtins.input", side_effect=["Z", "Z", "A"])
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    @patch("hrt.scrapers.ca_scraper.select_option")
    def test_download_available_callsigns_with_results(
        self, mock_select_option, mock_webdriver_wait, _
    ):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element
        self.mock_driver.page_source = "Your search has returned 1 call signs:"

        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "VA1ZZA"
        mock_row.find_elements.return_value = [mock_cell]
        mock_table.find_elements.return_value = [mock_row]
        self.mock_driver.find_element.return_value = mock_table

        with patch("builtins.open", mock_open()) as mock_file:
            callsigns = self.scraper.download_available_callsigns(
                "https://example.com/available", "/path/to/output"
            )

            self.mock_driver.get.assert_called_once_with("https://example.com/available")
            mock_select_option.assert_called()
            mock_file.assert_called_once_with("/path/to/output", "w", encoding="utf-8")
            self.assertEqual(callsigns, ["VA1ZZA"])

    @patch("builtins.input", side_effect=["1", "A", "B", "C"])
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    @patch("hrt.scrapers.ca_scraper.select_option")
    @patch("builtins.open", new_callable=mock_open)
    def test_invalid_suffix(self, _, mock_webdriver_wait, __, ___):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        captured_output = StringIO()
        sys.stdout = captured_output

        self.scraper.download_available_callsigns(
            "https://example.com/available", "/path/to/output"
        )

        sys.stdout = sys.__stdout__

        self.assertIn("Invalid suffix. Please try again.", captured_output.getvalue())


if __name__ == "__main__":
    unittest.main()
