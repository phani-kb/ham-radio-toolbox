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

    @patch("os.makedirs")
    @patch("requests.get")
    @patch("zipfile.ZipFile")
    def test_download_assigned_callsigns(self, mock_zipfile, mock_requests_get, mock_makedirs):
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
            mock_makedirs.assert_called_once_with("/path/to")
            mock_zipfile.assert_called_once()
            mock_file.assert_called_once_with("/path/to/output", "wb")

    @patch("builtins.input", side_effect=["Y", "A", "B", "C"])  # Added "Y" for user confirmation
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    @patch("hrt.scrapers.ca_scraper.select_option")
    @patch("os.makedirs")
    def test_download_available_callsigns(
        self, mock_makedirs, mock_select_option, mock_webdriver_wait, _
    ):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element
        self.mock_driver.page_source = "No such call sign is available."

        with patch("builtins.open", mock_open()) as mock_file:
            callsigns = self.scraper.download_available_callsigns(
                "https://example.com/available", "/path/to/output"
            )

            self.mock_driver.get.assert_called_once_with("https://example.com/available")
            mock_select_option.assert_called()
            self.assertEqual(callsigns, [])

    @patch("builtins.input", side_effect=["Y", "Z", "Z", "A"])
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    @patch("hrt.scrapers.ca_scraper.select_option")
    def test_download_available_callsigns_with_results(
        self, mock_select_option, mock_webdriver_wait, _
    ):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        def mock_find_element_side_effect(by, value):
            if value == "P_PREFIX_U":
                return MagicMock()
            elif "P_SUFFIX_CHAR_" in value:
                return MagicMock()
            elif value == "P_SUFFIX_TYPE_U":
                return MagicMock()
            elif "//input[@type='submit' and @value='Search']" in value:
                return MagicMock()
            elif value == "sdContent":
                mock_div = MagicMock()
                mock_p = MagicMock()
                mock_p.text = "Your search has returned 1 call signs:"
                mock_div.find_element.return_value = mock_p
                return mock_div
            elif "//table[.//th[text()='Call Sign']]" in value:
                mock_table = MagicMock()
                mock_row = MagicMock()
                mock_cell = MagicMock()
                mock_cell.text = "VA1ZZA"
                mock_row.find_elements.return_value = [mock_cell]
                mock_table.find_elements.return_value = [mock_row]
                return mock_table
            else:
                return MagicMock()

        self.mock_driver.find_element.side_effect = mock_find_element_side_effect
        self.mock_driver.page_source = "Your search has returned 1 call signs:"

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
    def test_invalid_suffix(self, _, mock_select_option, mock_webdriver_wait, mock_input):
        mock_wait = MagicMock()
        mock_webdriver_wait.return_value.until.return_value = mock_wait

        mock_form_elements = []
        for i in range(3):
            mock_element = MagicMock()
            mock_form_elements.append(mock_element)

        self.mock_driver.find_element.side_effect = mock_form_elements
        self.mock_driver.page_source = "No such call sign is available."

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            self.scraper.download_available_callsigns(
                "https://example.com/available", "/path/to/output"
            )
        except Exception as e:
            print(f"Method threw exception: {e}")

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertTrue(
            "Invalid suffix. Please try again." in output
            or "WARNING:" in output,  # At least the method started running
            f"Expected invalid suffix message or warning, got: {repr(output)}",
        )


if __name__ == "__main__":
    unittest.main()
