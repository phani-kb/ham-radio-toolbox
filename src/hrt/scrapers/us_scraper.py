from hrt.common.enums import CountryCode
from hrt.scrapers.base_scraper import BaseScraper


class USScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver, CountryCode.UNITED_STATES)

    def download_assigned_callsigns(self, url, output_file_path):
        raise NotImplementedError

    def download_available_callsigns(self, url, output_file_path):
        raise NotImplementedError
