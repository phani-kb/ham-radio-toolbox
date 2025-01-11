import logging
import logging.config

import yaml

from hrt.common.enums import CountryCode

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
            with open(self.file_path) as file:
                hrt_config = yaml.safe_load(file.read())
            return hrt_config
        except FileNotFoundError:
            logging.exception(f"Error: The file {self.file_path} was not found.")
            return None
        except yaml.YAMLError as e:
            logging.exception(f"Error parsing YAML file: {e}")
            return None

    def _configure_logging(self):
        if self.config:
            log_config_file = self.config.log_config_file
            with open(log_config_file, "r") as file:
                log_config = yaml.safe_load(file.read())
                logging.config.dictConfig(log_config)
        else:
            logging.basicConfig(
                filename="logs/ham_radio_toolbox.log",
                filemode="a",
                level=logging.ERROR,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )
