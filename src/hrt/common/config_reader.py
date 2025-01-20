import logging
import logging.config

import yaml

from hrt.common.constants import DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM
from hrt.common.enums import CountryCode, ExamType, QuestionAnswerDisplay

logger = logging.getLogger("hrt")


class HRTConfig:
    def __init__(self, data):
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

    def get(self, key) -> dict | str:
        return getattr(self, key)

    def get_country_settings(self, code):
        return self.countries.get(code)

    def get_input(self):
        return self.input

    def get_output(self):
        return self.output

    def get_callsign(self):
        return self.callsign

    def get_practice_exam_settings(self):
        return self.practice_exam


class ConfigReader:
    def __init__(self, file_path):
        self._file_path = file_path
        config_data: dict = self._read_config()
        self._config: HRTConfig = HRTConfig(config_data) if config_data else None
        self._configure_logging()

    @property
    def file_path(self):
        return self._file_path

    @property
    def config(self):
        return self._config

    def _read_config(self):
        try:
            with open(self.file_path, encoding="utf-8") as file:
                return yaml.safe_load(file.read())
        except FileNotFoundError:
            logging.exception(f"Error: The file {self.file_path} was not found.")
            return None
        except yaml.YAMLError as e:
            logging.exception(f"Error parsing YAML file: {e}")
            return None

    def _configure_logging(self):
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


def validate_config(hrt_config: HRTConfig):
    required_keys = ["input", "output", "print_question", "quiz", "practice_exam", "callsign"]
    for key in required_keys:
        if not hrt_config.get(key):
            logger.error(f"{key.replace('_', ' ').title()} settings not found in config file.")
        return False

    practice_exam_settings = hrt_config.get("practice_exam")
    qd: QuestionAnswerDisplay = DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM
    if not practice_exam_settings.get(qd.id):
        logger.error(
            f"Practice Exam settings for question answer display {qd.id} "
            f"not found in config file."
        )
        return False

    for country in CountryCode.supported_ids():
        if not validate_country_config(hrt_config, country):
            return False

    return True


def validate_country_config(hrt_config: HRTConfig, country: str) -> bool:
    country_config = hrt_config.get_country_settings(country)
    if not country_config:
        logger.error(f"{country} settings not found in config file.")
        return False

    qb_config = country_config.get("question_bank")
    if not qb_config:
        logger.error(f"Question Bank settings not found for {country} in config file.")
        return False

    for exam_type in ExamType.supported_ids():
        if not qb_config.get(exam_type):
            logger.error(
                f"Question Bank settings for {exam_type} "
                f"not found for {country} in config file."
            )
            return False

    return True
