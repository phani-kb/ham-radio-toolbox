import logging
import logging.config




from common.enums import CountryCode

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


