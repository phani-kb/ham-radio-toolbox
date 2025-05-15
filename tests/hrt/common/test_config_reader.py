import unittest
from unittest.mock import patch, mock_open
import yaml
from hrt.common.config_reader import ConfigReader, HRTConfig, validate_config
from hrt.common.constants import DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM
from hrt.common.enums import CountryCode, ExamType


class TestConfigReader(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            "log_config_file": "logging.yml",
            "web_driver": "chrome",
            "input": {"source": "input_source"},
            "output": {"folder": "output_folder"},
            "metrics": {"enabled": True},
            "print_question": {"enabled": True},
            "quiz": {"enabled": True},
            "practice_exam": {"in-the-end": {"enabled": True}, "enabled": True},
            "callsign": {"prefix": "K"},
            "us": {
                "country": "usa",
                "question_bank": {
                    "technical": {"path": "exam1_path"},
                    "general": {"path": "exam2_path"},
                    "extra": {"path": "exam3_path"},
                },
            },
            "ca": {
                "country": "canada",
                "question_bank": {
                    "basic": {"path": "exam1_path"},
                    "advanced": {"path": "exam2_path"},
                },
            },
        }
        self.config_yaml = yaml.dump(self.config_data)
        self.log_config_data = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
            },
        }
        self.log_config_yaml = yaml.dump(self.log_config_data)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_config_file_not_found1(self, _):
        config_reader = ConfigReader("non_existent_file.yml")
        self.assertIsNone(config_reader.config)

    def test_read_config_file_not_found2(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            config_reader = ConfigReader("non_existent_file.yml")
            assert config_reader._read_config() is None

    def test_read_config_yaml_error(self):
        with patch("builtins.open", mock_open(read_data="invalid: yaml: data")):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError):
                config_reader = ConfigReader("invalid_yaml_file.yml")
                assert config_reader._read_config() is None

    @patch("builtins.open", new_callable=mock_open, read_data=None)
    def test_read_config_success(self, mock_file):
        mock_file.return_value.read.side_effect = [self.config_yaml, self.log_config_yaml]
        config_reader = ConfigReader("valid_file.yml")
        self.assertIsNotNone(config_reader.config)
        self.assertIsInstance(config_reader.config, HRTConfig)
        self.assertEqual(config_reader.config.web_driver, "chrome")
        self.assertEqual(config_reader.config.get("output_folder"), "output_folder")
        self.assertEqual(config_reader.config.get("log_config_file"), "logging.yml")
        self.assertEqual(config_reader.config.get_input(), {"source": "input_source"})
        self.assertEqual(config_reader.config.get_output(), {"folder": "output_folder"})
        self.assertEqual(config_reader.config.get_callsign(), {"prefix": "K"})
        self.assertEqual(config_reader.config.get_country_settings("ca"), self.config_data["ca"])
        self.assertEqual(config_reader.config.get_country_settings("us"), None)

    def test_validate_config_success(self):
        hrt_config = HRTConfig(self.config_data)
        self.assertTrue(validate_config(hrt_config))

    def test_validate_config_failure(self):
        invalid_config_data = self.config_data.copy()
        invalid_config_data.pop("input")
        hrt_config = HRTConfig(invalid_config_data)
        self.assertFalse(validate_config(hrt_config))

    def test_get_practice_exam_settings(self):
        hrt_config = HRTConfig(self.config_data)
        practice_exam_settings = hrt_config.get_practice_exam_settings()
        self.assertEqual(practice_exam_settings, self.config_data["practice_exam"])


class TestValidateConfig(unittest.TestCase):
    def setUp(self):
        self.default_data = {
            "input": {"some_key": "some_value"},
            "output": {"folder": "output"},
            "print_question": {"some_key": "some_value"},
            "quiz": {"some_key": "some_value"},
            "practice_exam": {
                "in-the-end": {"some_value"},
                "enabled": True,
            },
            "callsign": {"some_key": "some_value"},
            "us": {"country": "usa", "question_bank": {"some_key": "some_value"}},
            "ca": {
                "country": "canada",
                "question_bank": {
                    "basic": {
                        "number_of_questions": "10",
                    },
                    "advanced": {
                        "number_of_questions": "5",
                    },
                    "some_key": "some_value",
                },
            },
        }

    def test_validate_config_missing_input(self):
        data = self.default_data.copy()
        del data["input"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_output(self):
        data = self.default_data.copy()
        del data["output"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_print_question(self):
        data = self.default_data.copy()
        del data["print_question"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_quiz(self):
        data = self.default_data.copy()
        del data["quiz"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_practice_exam(self):
        data = self.default_data.copy()
        del data["practice_exam"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_callsign(self):
        data = self.default_data.copy()
        del data["callsign"]
        hrt_config = HRTConfig(data)
        self.assertFalse(validate_config(hrt_config))

    def test_validate_config_missing_country_settings(self):
        for country in CountryCode.supported_ids():
            data = self.default_data.copy()
            del data[country]
            hrt_config = HRTConfig(data)
            self.assertFalse(validate_config(hrt_config))

    @patch("hrt.common.config_reader.logger")
    def test_validate_config_missing_practice_exam_display(self, mock_logger):
        data = self.default_data.copy()
        del data["practice_exam"][DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM.id]
        hrt_config = HRTConfig(data)
        result = validate_config(hrt_config)
        self.assertFalse(result)
        mock_logger.error.assert_called_with(
            f"Practice Exam settings for question answer display %s " f"not found in config file.",
            DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM.id,
        )

    @patch("hrt.common.config_reader.logger")
    def test_validate_config_missing_question_bank1(self, mock_logger):
        for country in CountryCode.supported_ids():
            data = self.default_data.copy()
            del data[country]["question_bank"]
            hrt_config = HRTConfig(data)
            result = validate_config(hrt_config)
            self.assertFalse(result)
            mock_logger.error.assert_called_with(
                f"Question Bank settings not found for %s in config file.", country
            )

    @patch("hrt.common.config_reader.logger")
    def test_validate_config_missing_question_bank2(self, mock_logger):
        for country in CountryCode.supported_ids():
            data = self.default_data.copy()
            for exam_type in ExamType.supported_ids():
                del data[country]["question_bank"][exam_type]
            hrt_config = HRTConfig(data)
            result = validate_config(hrt_config)
            self.assertFalse(result)
            self.assertEqual(mock_logger.error.call_count, 1)


if __name__ == "__main__":
    unittest.main()
