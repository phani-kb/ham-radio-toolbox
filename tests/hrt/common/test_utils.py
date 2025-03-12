import os
import tempfile
import unittest
import logging
from unittest.mock import MagicMock, patch, mock_open, call
import zipfile

from hrt.common import constants
from hrt.common.utils import (
    create_folder,
    get_current_time,
    get_header,
    get_user_agent,
    get_word_combinations,
    permutations,
    read_delim_file,
    read_filename,
    read_number_from_input,
    save_output,
    select_from_options,
    select_option_from_list,
    download_zip_file,
    read_words_from_file,
    write_output,
)

logger = logging.getLogger("hrt")


class TestReadDelimFile(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="iso-8859-1")
        self.test_file.write("header1,header2,header3\nvalue1,value2,value3\nvalue4,value5,value6")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)

    def test_read_delim_file_default(self):
        result = read_delim_file(self.test_file.name)
        expected = [
            ["header1", "header2", "header3"],
            ["value1", "value2", "value3"],
            ["value4", "value5", "value6"],
        ]
        self.assertEqual(result, expected)

    def test_read_delim_file_skip_header(self):
        result = read_delim_file(self.test_file.name, skip_header=True, header="header1")
        expected = [["value1", "value2", "value3"], ["value4", "value5", "value6"]]
        self.assertEqual(result, expected)

    def test_read_delim_file_with_fields_count(self):
        result = read_delim_file(self.test_file.name, fields_count=2)
        expected = [["header1", "header2"], ["value1", "value2"], ["value4", "value5"]]
        self.assertEqual(result, expected)

    def test_read_delim_file_file_not_found(self):
        result = read_delim_file("non_existent_file.csv")
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open)
    def test_read_delim_file_exception(self, _):
        # Configure the mock to raise an exception when called
        _.side_effect = Exception("Test exception")

        # Call the function with a test file path
        result = read_delim_file("test_file.csv")

        # Check that the result is an empty list
        self.assertEqual(result, [])

        # Call the function with a test file path
        with self.assertLogs(logger, level="ERROR") as log:
            result = read_delim_file("test_file.csv")
            self.assertEqual(result, [])
            self.assertIn(
                "ERROR:hrt:An error occurred reading the file at test_file.csv: Test exception",
                log.output,
            )


class TestSaveOutput(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)

    def test_save_output(self):
        save_output(self.test_file.name, "Test output")
        with open(self.test_file.name, "r") as file:
            content = file.read()
        self.assertEqual(content, "Test output")

    def test_save_output_with_folder(self):
        folder = tempfile.mkdtemp()
        test_file_path = os.path.join(folder, "test_output.txt")
        save_output("test_output.txt", "Test output", folder)
        with open(test_file_path, "r") as file:
            content = file.read()
        self.assertEqual(content, "Test output")
        os.remove(test_file_path)
        os.rmdir(folder)


class TestGetHeader(unittest.TestCase):
    def test_get_header(self):
        result = get_header("Test Header")
        expected = "Test Header\n-----------"
        self.assertEqual(result, expected)


class TestReadNumberFromInput(unittest.TestCase):
    @patch("click.prompt")
    def test_read_number_from_input_valid(self, mock_prompt):
        mock_prompt.return_value = "5"
        result = read_number_from_input("Enter a number:", 1, 10)
        self.assertEqual(result, 5)

    @patch("click.prompt")
    def test_read_number_from_input_invalid(self, mock_prompt):
        mock_prompt.side_effect = ["invalid", "15", "5"]
        result = read_number_from_input("Enter a number:", 1, 10)
        self.assertEqual(result, 5)


class TestReadFilename(unittest.TestCase):
    @patch("builtins.input", return_value="test_file.txt")
    def test_read_filename_with_input(self, _):
        result = read_filename("default.txt")
        self.assertEqual(result, "test_file.txt")

    @patch("builtins.input", return_value="")
    def test_read_filename_default(self, _):
        result = read_filename("default.txt")
        self.assertEqual(result, "default.txt")


class TestCreateFolder(unittest.TestCase):
    def test_create_folder(self):
        test_folder = "test_folder"
        create_folder(test_folder)
        self.assertTrue(os.path.exists(test_folder))
        os.rmdir(test_folder)


class TestPermutations(unittest.TestCase):
    def test_permutations(self):
        result = permutations("abc")
        expected = ["abc", "acb", "bac", "bca", "cab", "cba"]
        self.assertEqual(sorted(result), sorted(expected))


class TestGetWordCombinations(unittest.TestCase):
    def test_get_word_combinations(self):
        result = get_word_combinations("abc")
        expected = ["abc", "acb", "bac", "bca", "cab", "cba"]
        self.assertEqual(sorted(result), sorted(expected))


class TestSelectFromOptions(unittest.TestCase):
    @patch("click.prompt")
    def test_select_from_options(self, mock_prompt):
        mock_prompt.return_value = "2"
        options = {"option1": "desc1", "option2": "desc2", "option3": "desc3"}
        result = select_from_options(options, "Select an option")
        self.assertEqual(result, "option2")

    @patch("hrt.common.utils.logger")
    def test_select_from_options_no_options(self, mock_logger):
        result = select_from_options({}, "Select an option")

        assert result is None

        mock_logger.error.assert_called_once_with("No options provided.")

    def test_select_from_options_single_option(self):
        options = {"option1": "Option 1"}

        result = select_from_options(options, "Select an option")

        assert result == "option1"

    @patch("hrt.common.utils.logger")
    @patch("builtins.print")
    @patch("click.prompt", side_effect=["invalid", "1"])
    def test_select_from_options_invalid_input(self, mock_logger, mock_print, _):
        options = {"option1": "Option 1", "option2": "Option 2"}

        result = select_from_options(options, "Select an option")

        assert result == "option1"

        mock_logger.error.assert_not_called()
        mock_print.assert_any_call("Invalid input. Please enter a number.")

    @patch("hrt.common.utils.logger")
    @patch("builtins.print")
    @patch("click.prompt", side_effect=["4", "1"])
    def test_select_from_options_invalid_choice(self, mock_logger, mock_print, _):
        options = {"option1": "Option 1", "option2": "Option 2"}

        result = select_from_options(options, "Select an option")

        assert result == "option1"

        mock_logger.error.assert_not_called()
        mock_print.assert_any_call("Invalid choice. Please select a number between 1 and 2.")


class TestSelectOptionFromList(unittest.TestCase):
    @patch("click.prompt")
    def test_select_option_from_list(self, mock_prompt):
        mock_prompt.return_value = "2"
        options = ["option1", "option2", "option3"]
        result = select_option_from_list(options, "Select an option")
        self.assertEqual(result, "option2")

    @patch("hrt.common.utils.logger")
    def test_select_option_from_list_no_options(self, mock_logger):
        result = select_option_from_list([], "Select an option")
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with("No options provided.")

    def test_select_option_from_list_single_option(self):
        options = ["option1"]
        result = select_option_from_list(options, "Select an option")
        self.assertEqual(result, "option1")

    @patch("builtins.print")
    @patch("click.prompt")
    def test_select_option_from_list_invalid_choice(self, mock_prompt, mock_print):
        options = ["option1", "option2", "option3"]
        mock_prompt.side_effect = [
            "4",
            "invalid",
            "2",
        ]

        result = select_option_from_list(options, "Select an option")

        self.assertEqual(result, "option2")
        mock_print.assert_has_calls(
            [
                call("Invalid choice. Please select a number between 1 and 3."),
                call("Invalid input. Please enter a number."),
            ]
        )


class TestLoadQuestionMetrics(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.test_file.write("Q1:1:2:3\nQ2:4:5:6\n")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)


class TestReadMetricsFromFile(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.test_file.write("Q1:1:2:3\nQ2:4:5:6\n")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)


class TestDownloadZipFile(unittest.TestCase):
    @patch("requests.get")
    @patch("zipfile.ZipFile.open", new_callable=MagicMock)
    @patch("zipfile.ZipFile")
    def test_download_zip_file(self, _, mock_zipfile_open, mock_get):
        mock_get.return_value.content = b"Test zip content"
        mock_zipfile_instance = MagicMock()
        mock_zipfile_instance.__enter__.return_value.infolist.return_value = [
            zipfile.ZipInfo("file.txt")
        ]
        mock_zipfile_instance.__enter__.return_value.open.return_value.read.return_value = (
            b"Test file content"
        )
        mock_zipfile_open.return_value = mock_zipfile_instance

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        download_zip_file("https://example.com/file.zip", temp_file_path)
        with open(temp_file_path, "rb") as file:
            content = file.read()
        self.assertEqual(content, b"")
        os.remove(temp_file_path)

    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            download_zip_file("https://example.com/file.txt", "output_path")
        self.assertEqual(
            str(context.exception),
            "Invalid URL https://example.com/file.txt. Expected a ZIP file URL.",
        )


class TestReadWordsFromFile(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.test_file.write("word1\nword2\nword3\n")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)

    def test_read_words_from_file(self):
        result = read_words_from_file(self.test_file.name)
        expected = ["word1", "word2", "word3"]
        self.assertEqual(result, expected)


class TestWriteOutput(unittest.TestCase):
    def test_write_output_to_file(self):
        output = ["line1", "line2", "line3"]
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        write_output(output, filename=temp_file_path)
        with open(temp_file_path, "r") as file:
            content = file.read().splitlines()
        self.assertEqual(content, output)
        os.remove(temp_file_path)

    def test_write_output_to_console(self):
        output = ["line1", "line2", "line3"]
        with patch("builtins.print") as mock_print:
            write_output(output)
            mock_print.assert_any_call("line1")
            mock_print.assert_any_call("line2")
            mock_print.assert_any_call("line3")


class TestUtils(unittest.TestCase):
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_folder(self, mock_makedirs, mock_exists):
        # Test when folder does not exist
        mock_exists.return_value = False
        create_folder("test_folder")
        mock_exists.assert_called_once_with("test_folder")
        mock_makedirs.assert_called_once_with("test_folder")

        # Test when folder already exists
        mock_exists.reset_mock()
        mock_makedirs.reset_mock()
        mock_exists.return_value = True
        create_folder("test_folder")
        mock_exists.assert_called_once_with("test_folder")
        mock_makedirs.assert_not_called()

    @patch("os.path.join")
    def test_write_output_file_path(self, mock_join):
        # Test file path construction
        write_output(["line1", "line2"], filename="test_file.txt", folder="test_folder")
        mock_join.assert_called_once_with("test_folder", "test_file.txt")


class TestLoadCallsignsFromFile(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.test_file.write("CALLSIGN1\nCALLSIGN2\nCALLSIGN1\nCALLSIGN3\n")
        self.test_file.close()

    def tearDown(self):
        os.remove(self.test_file.name)


class TestGetCurrentTime(unittest.TestCase):
    @patch("time.time", return_value=1633072800.0)
    def test_get_current_time(self, _):
        result = get_current_time()
        self.assertEqual(result, 1633072800.0)


class TestDownloadZipFile2(unittest.TestCase):
    def tearDown(self):
        if os.path.exists("output-hrt.zip"):
            os.remove("output-hrt.zip")

    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("zipfile.ZipFile")
    @patch("hrt.common.utils.logger")
    def test_valid_url_no_filter(
        self, mock_logger, mock_zipfile, mock_tempfile, mock_requests_get
    ):
        url = "https://example.com/valid.zip"
        output_file_path = "output-hrt.zip"

        mock_requests_get.return_value = MagicMock(content=b"ZIP content")
        mock_tempfile.return_value.__enter__.return_value = MagicMock()  # Mock temporary file
        mock_zipfile.return_value.infolist.return_value = [MagicMock(filename="file1.txt")]

        download_zip_file(url, output_file_path)

        mock_requests_get.assert_called_once_with(url, timeout=10)
        mock_logger.info.assert_has_calls(
            [
                call(f"Extracted %s to %s", url, output_file_path),
            ]
        )

    @patch("requests.get")
    def test_invalid_url(self, _):
        """Tests handling of an invalid URL (not ending in .zip)."""
        url = "https://example.com/invalid"
        output_file_path = "output-hrt.zip"

        with self.assertRaises(ValueError) as cm:
            download_zip_file(url, output_file_path)

        self.assertEqual(
            str(cm.exception), "Invalid URL https://example.com/invalid. Expected a ZIP file URL."
        )

    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("zipfile.ZipFile")
    @patch("logging.info")
    def test_download_error(self, mock_logging_info, _, __, mock_requests_get):
        url = "https://example.com/valid.zip"
        output_file_path = "output-hrt.zip"

        mock_requests_get.side_effect = Exception("Download error")

        with self.assertRaises(Exception) as cm:
            download_zip_file(url, output_file_path)

        self.assertEqual(str(cm.exception), "Download error")
        mock_logging_info.assert_not_called()  # No logging calls expected

    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("zipfile.ZipFile")
    @patch("hrt.common.utils.logger")
    def test_zip_file_filtering(self, mock_logger, mock_zipfile, mock_tempfile, mock_requests_get):
        url = "https://example.com/valid.zip"
        output_file_path = "output-hrt.zip"
        zip_files = ["file2.txt"]

        mock_requests_get.return_value = MagicMock(content=b"ZIP content")
        mock_tempfile.return_value.__enter__.return_value = MagicMock()  # Mock temporary file
        mock_zipfile.return_value.infolist.return_value = [
            MagicMock(filename="file1.txt"),
            MagicMock(filename="file2.txt"),
        ]

        download_zip_file(url, output_file_path, zip_files)

        mock_logger.info.assert_has_calls(
            [
                call(f"Extracted %s to %s", url, output_file_path),
            ]
        )

    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("zipfile.ZipFile")
    @patch("hrt.common.utils.logger")
    def test_zip_file_filtering_no_match(
        self, mock_logger, mock_zipfile, mock_tempfile, mock_requests_get
    ):
        url = "https://example.com/valid.zip"
        output_file_path = "output-hrt.zip"
        zip_files = ["nonexistent.txt"]

        mock_requests_get.return_value = MagicMock(content=b"ZIP content")
        mock_tempfile.return_value.__enter__.return_value = MagicMock()  # Mock temporary file
        mock_zipfile.return_value.infolist.return_value = [
            MagicMock(filename="file1.txt"),
            MagicMock(filename="file2.txt"),
        ]

        download_zip_file(url, output_file_path, zip_files)

        mock_logger.info.assert_has_calls(
            [
                call(f"Extracted %s to %s", url, output_file_path),
            ]
        )

    @patch("requests.get")
    @patch("tempfile.NamedTemporaryFile")
    @patch("zipfile.ZipFile")
    @patch("hrt.common.utils.logger")
    def test_zip_file_filtering_with_match(
        self, mock_logger, mock_zipfile, mock_tempfile, mock_requests_get
    ):
        url = "https://example.com/valid.zip"
        output_file_path = "output-hrt.zip"
        zip_files = ["file2.txt"]

        mock_requests_get.return_value = MagicMock(content=b"ZIP content")
        mock_tempfile.return_value.__enter__.return_value = MagicMock()
        mock_zipfile_instance = mock_zipfile.return_value.__enter__.return_value
        file1_info = MagicMock(filename="file1.txt")
        file2_info = MagicMock(filename="file2.txt")
        mock_zipfile_instance.infolist.return_value = [file1_info, file2_info]

        mock_file1 = MagicMock()
        mock_file1.read.return_value = b""
        mock_file2 = MagicMock()
        mock_file2.read.return_value = b"file2_content"
        mock_zipfile_instance.open.side_effect = [mock_file1, mock_file2]

        download_zip_file(url, output_file_path, zip_files)

        mock_logger.info.assert_called_with(f"Extracted %s to %s", url, output_file_path)


class TestGetUserAgent(unittest.TestCase):
    def test_get_user_agent_with_config(self):
        app_config = {"name": "TestApp", "version": "1.0.0", "description": "Test application"}
        expected_user_agent = f"TestApp/1.0.0 ({constants.GITHUB_URL}; Test application)"
        self.assertEqual(get_user_agent(app_config), expected_user_agent)

    def test_get_user_agent_without_config(self):
        expected_user_agent = (
            f"{constants.APP_NAME}/{constants.APP_VERSION} ({constants.GITHUB_URL}; )"
        )
        self.assertEqual(get_user_agent(None), expected_user_agent)


if __name__ == "__main__":
    unittest.main()
