"""Base class for downloaders."""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, cast

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CallSignDownloadType, CountryCode, DownloadType, ExamType
from hrt.scrapers.base_scraper import ScraperFactory


class IDownloader(ABC):
    """Interface for the downloaders."""

    @abstractmethod
    def pre_process(self) -> None:
        """Pre-process the downloader."""

    @abstractmethod
    def download_callsigns(self, callsigns_dt: CallSignDownloadType) -> None:
        """Download callsigns."""

    @abstractmethod
    def download_question_bank(self, exam_type: ExamType) -> None:
        """Download question bank."""

    @abstractmethod
    def get_output_folder(self) -> Optional[str]:
        """Get the output folder."""

    @abstractmethod
    def post_process(self) -> None:
        """Post-process the downloader."""


class BaseDownloader(IDownloader, ABC):
    """Base class for the downloaders."""

    def __init__(
        self,
        chrome_driver_path: str,
        country: CountryCode,
        download_type: DownloadType,
        output_folder: str,
        config: Dict,
        app_config: Optional[Dict] = None,
    ):
        self._chrome_driver_path = chrome_driver_path
        self._country = country
        self._download_type = download_type
        self._output_folder = output_folder
        self._config = config
        self._output_file_path = None
        self._app_config = app_config

    @property
    def chrome_driver_path(self) -> str:
        """Get the path to the Chrome driver."""
        return self._chrome_driver_path

    @property
    def country(self) -> CountryCode:
        """Get the country."""
        return self._country

    @property
    def config(self) -> Dict:
        """Get the configuration data."""
        return self._config

    @property
    def app_config(self) -> Optional[Dict]:
        """Get the app configuration data."""
        return self._app_config

    @property
    def output_folder(self) -> str:
        """Get the output folder."""
        return self._output_folder

    @property
    def download_type(self) -> DownloadType:
        """Get the download type."""
        return self._download_type

    def get_output_folder(self) -> Optional[str]:
        if not self.output_folder or self.output_folder.strip() == "":
            logger.error("Output folder not found")
            return None

        return os.path.join(self.output_folder, self.country.code)

    def download(
        self,
        url: str,
        output_file_path: str,
        zip_files: Optional[List[str]] = None,
    ) -> None:
        """Download the file from the URL."""
        self.pre_process()
        output_folder = os.path.dirname(output_file_path)
        utils.create_folder(output_folder)
        utils.download_file(url, output_file_path, zip_files)
        self.post_process()

    def pre_process(self) -> None:
        pass

    def post_process(self) -> None:
        pass

    def get_output_file_path(self, key: Union[CallSignDownloadType, ExamType]) -> str:
        """Get the output file path for the given key."""
        input_file_path = self.config.get(key.id, {}).get("file")
        if not input_file_path:
            logger.error(
                "Input file path not found for %s in country %s", key.id, self.country.code
            )
            return ""
        return os.path.join(
            str(self.get_output_folder()), str(self.download_type.id), cast(str, input_file_path)
        )

    def _download_file(self, key: ExamType, url_key: str, description: str) -> None:
        """Download a file for the given key."""
        output_file_path = self.get_output_file_path(key)
        url = self.config.get(key.id, {}).get(url_key)
        if not url:
            logger.error(
                "URL not found for %s in country %s for %s",
                description,
                self.country.code,
                key.id,
            )
            return
        zip_files = None
        if url.endswith(".zip"):
            zip_files = self.config.get(key.id, {}).get("zip_files")
        self.download(url, output_file_path, zip_files)

    def download_callsigns(self, callsigns_dt: CallSignDownloadType) -> None:
        """Download callsigns for the specified country."""
        dt_config = self.config.get(callsigns_dt.id, {})
        if not dt_config:
            logger.error("Config not found for callsign in country %s", self.country.id)
            return
        download_url = dt_config.get("download_url")
        if not download_url:
            logger.error(
                "URL not found for callsign in country %s for %s",
                self.country.id,
                callsigns_dt.id,
            )
            return
        scraper = ScraperFactory.get_scraper(
            self.chrome_driver_path, self.country, self.app_config
        )
        scraper.download_callsigns(
            callsigns_dt,
            download_url,
            self.get_output_file_path(callsigns_dt),
        )

    def download_question_bank(self, exam_type: ExamType) -> None:
        """Download question bank."""
        self._download_file(exam_type, "download_url", "question bank")


class DownloaderFactory:
    """Factory class to get the downloader."""

    @staticmethod
    def get_downloader(
        chrome_driver_path: str,
        country: CountryCode,
        download_type: DownloadType,
        output_folder: str,
        config: Dict,
        app_config: Optional[Dict] = None,
    ) -> BaseDownloader:
        """Get the downloader based on the country."""
        if country == CountryCode.CANADA:
            from hrt.downloaders.ca_downloader import CADownloader

            return CADownloader(
                chrome_driver_path, download_type, output_folder, config, app_config
            )
        if country == CountryCode.UNITED_STATES:
            from hrt.downloaders.us_downloader import USDownloader

            return USDownloader(
                chrome_driver_path, download_type, output_folder, config, app_config
            )
        raise ValueError("Invalid country code.")
