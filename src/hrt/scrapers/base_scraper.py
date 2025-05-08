"""Base scraper class and factory to get scraper based on country code."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CACallSignDownloadType, CallSignDownloadType, CountryCode


class IWebScraper(ABC):
    @abstractmethod
    def download_callsigns(
        self, callsign_download_type: CallSignDownloadType, url: str, output_file_path: str
    ) -> None:
        pass

    @abstractmethod
    def download_assigned_callsigns(self, url: str, output_file_path: str) -> None:
        pass

    @abstractmethod
    def download_available_callsigns(self, url: str, output_file_path: str) -> None:
        pass


class BaseScraper(IWebScraper, ABC):
    def __init__(
        self,
        driver: str,
        country: CountryCode,
        app_config: Optional[Dict] = None,
        headless: bool = True,
    ):
        self.country = country
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        self.driver_service = Service(driver)
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)
        self.app_config = app_config

    def download_callsigns(
        self, callsign_download_type: CallSignDownloadType, url: str, output_file_path: str
    ) -> None:
        user_agent = utils.get_user_agent(app_config=self.app_config)
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
    def download_assigned_callsigns(self, url: str, output_file_path: str) -> None:
        pass

    @abstractmethod
    def download_available_callsigns(self, url: str, output_file_path: str) -> None:
        pass


class ScraperFactory:
    @staticmethod
    def get_scraper(
        driver: str,
        country: CountryCode,
        app_config: Optional[Dict] = None,
    ) -> BaseScraper:
        if country == CountryCode.CANADA:
            from hrt.scrapers.ca_scraper import CAScraper

            return CAScraper(driver, app_config)
        if country == CountryCode.UNITED_STATES:
            from hrt.scrapers.us_scraper import USScraper

            return USScraper(driver, app_config)
        raise ValueError("Invalid country code.")
