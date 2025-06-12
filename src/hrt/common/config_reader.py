"""Read configuration file."""

import logging
import logging.config
from typing import Any, Dict, Optional, Union

import yaml

from hrt.common.constants import DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM
from hrt.common.enums import CountryCode, ExamType, QuestionAnswerDisplay

logger = logging.getLogger("hrt")


class HRTConfig:
    """Class to hold configuration data."""

    def __init__(self, data: Dict[str, Any]):
        self.application = data.get("application", {})
        self.log_config_file = data.get("log_config_file", "logging.yml")
        self.web_driver = data.get("web_driver", "chrome")
        self.input = data.get("input", {})
        self.output = data.get("output", {})
        self.metrics = data.get("metrics", {})
        self.print_question = data.get("print_question", {})
        self.quiz = data.get("quiz", {})
        self.practice_exam = data.get("practice_exam", {})
        self.callsign = data.get("callsign", {})
        self.output_folder = data.get("output", {}).get("folder", "output")
        self.countries = {}
        for country in CountryCode.supported_ids():
            self.countries[country] = data.get(country, {})

    def get(self, key: str) -> Union[Dict[str, Any], str]:
        """Get the value of a key in the configuration data."""
        return getattr(self, key)

    def get_country_settings(self, code: str) -> Optional[Dict[str, Any]]:
        """Get the settings for a specific country."""
        return self.countries.get(code)

    def get_input(self) -> Dict[str, Any]:
        """Get the input settings."""
        return self.input

    def get_output(self) -> Dict[str, Any]:
        """Get the output settings."""
        return self.output

    def get_callsign(self) -> Dict[str, Any]:
        """Get the callsign settings."""
        return self.callsign

    def get_practice_exam_settings(self) -> Dict[str, Any]:
        """Get the practice exam settings."""
        return self.practice_exam


class ConfigReader:
    """Read configuration file."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        config_data: Optional[Dict[str, Any]] = self._read_config()
        self._config: Optional[HRTConfig] = HRTConfig(config_data) if config_data else None
        self._configure_logging()

    @property
    def file_path(self) -> str:
        """Get the path to the configuration file."""
        return self._file_path

    @property
    def config(self) -> Optional[HRTConfig]:
        """Get the configuration data."""
        return self._config

    def _read_config(self) -> Optional[Dict[str, Any]]:
        try:
            with open(self.file_path, encoding="utf-8") as file:
                return yaml.safe_load(file.read())
        except FileNotFoundError:
            logging.exception("Error: The file %s was not found.", self.file_path)
            return None
        except yaml.YAMLError as e:
            logging.exception("Error parsing YAML file: %s", e)
            return None

    def _configure_logging(self) -> None:
        if self.config:
            log_config_file = self.config.log_config_file
            with open(log_config_file, "r", encoding="utf-8") as file:
                log_config = yaml.safe_load(file.read())
                logging.config.dictConfig(log_config)
        else:
            logging.basicConfig(
                filename="logs/ham_radio_toolbox.log",
                filemode="a",
                level=logging.ERROR,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )


def validate_config(hrt_config: HRTConfig) -> bool:
    """Validate the configuration data."""
    if not validate_general_settings(hrt_config):
        return False
    if not validate_practice_exam_settings(hrt_config):
        return False
    return validate_country_settings(hrt_config)


def validate_general_settings(hrt_config: HRTConfig) -> bool:
    """Validate general settings in the configuration data."""
    if not hrt_config.get("input"):
        logger.error("Input settings not found in config file.")
        return False
    if not hrt_config.get("output"):
        logger.error("Output settings not found in config file.")
        return False
    if not hrt_config.get("print_question"):
        logger.error("Print Question settings not found in config file.")
        return False
    if not hrt_config.get("quiz"):
        logger.error("Quiz settings not found in config file.")
        return False
    if not hrt_config.get("callsign"):
        logger.error("Callsign settings not found in config file.")
        return False
    return True


def validate_practice_exam_settings(hrt_config: HRTConfig) -> bool:
    """Validate practice exam settings in the configuration data."""
    practice_exam_settings = hrt_config.get("practice_exam")
    if not practice_exam_settings:
        logger.error("Practice Exam settings not found in config file.")
        return False
    if not isinstance(practice_exam_settings, dict):
        logger.error("Practice Exam settings should be a dictionary.")
        return False
    qd: QuestionAnswerDisplay = DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM
    if not practice_exam_settings.get(qd.id):
        logger.error(
            "Practice Exam settings for question answer display %s not found in config file.",
            qd.id,
        )
        return False
    return True


def validate_country_settings(hrt_config: HRTConfig) -> bool:
    """Validate country-specific settings in the configuration data."""
    for country in CountryCode.supported_ids():
        country_config = hrt_config.get_country_settings(country)
        if not country_config:
            logger.error("%s settings not found in config file.", country)
            return False
        qb_config = country_config.get("question_bank")
        if not qb_config:
            logger.error("Question Bank settings not found for %s in config file.", country)
            return False
        for exam_type in ExamType.supported_ids():
            if not qb_config.get(exam_type):
                logger.error(
                    "Question Bank settings for %s not found for %s in config file.",
                    exam_type,
                    country,
                )
                return False
    return True
