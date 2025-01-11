import random
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from hrt.common.config_reader import logger
from hrt.common.constants import USER_AGENTS
from hrt.common.enums import CACallSignDownloadType, CallSignDownloadType, CountryCode


class IWebScrapper(ABC):
    @abstractmethod
    def download_callsigns(
        self, callsign_download_type: CallSignDownloadType, url, output_file_path
    ):
        pass

    @abstractmethod
    def download_assigned_callsigns(self, url, output_file_path):
        pass

    @abstractmethod
    def download_available_callsigns(self, url, output_file_path):
        pass


class BaseScrapper(IWebScrapper, ABC):
    def __init__(self, driver, country: CountryCode, headless=True):
        self.country = country
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.driver_service = Service(driver)
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)

    def download_callsigns(
        self, callsign_download_type: CallSignDownloadType, url, output_file_path
    ):
        user_agent = random.choice(USER_AGENTS)
        try:
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

            if callsign_download_type == CACallSignDownloadType.ASSIGNED:
                self.download_assigned_callsigns(url, output_file_path)
                return
            if callsign_download_type == CACallSignDownloadType.AVAILABLE:
                self.download_available_callsigns(url, output_file_path)
                return
            raise ValueError("Invalid Callsign download type.")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error downloading callsigns for {self.country}: {e}")
            raise e

    @abstractmethod
    def download_assigned_callsigns(self, url, output_file_path):
        pass

    @abstractmethod
    def download_available_callsigns(self, url, output_file_path):
        pass


class ScrapperFactory:
    @staticmethod
    def get_scrapper(driver, country: CountryCode):
        if country == CountryCode.CANADA:
            from hrt.scrappers.ca_scrapper import CAScrapper

            return CAScrapper(driver)
        if country == CountryCode.UNITED_STATES:
            from hrt.scrappers.us_scrapper import USScrapper

            return USScrapper(driver)
        raise ValueError("Invalid country code.")
