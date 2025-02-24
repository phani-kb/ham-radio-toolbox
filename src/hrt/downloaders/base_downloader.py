"""Base class for downloaders."""

import os
from abc import ABC, abstractmethod

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CallSignDownloadType, CountryCode, DownloadType, ExamType


class IDownloader(ABC):
    """Interface for the downloaders."""

    @abstractmethod
    def pre_process(self):
        """Pre-process the downloader."""

    @abstractmethod
    def download_callsigns(self, callsigns_dt: CallSignDownloadType):
        """Download callsigns."""

    @abstractmethod
    def download_question_bank(self, exam_type: ExamType):
        """Download question bank."""

    @abstractmethod
    def get_output_folder(self) -> str:
        """Get the output folder."""

    @abstractmethod
    def post_process(self):
        """Post-process the downloader."""


class BaseDownloader(IDownloader, ABC):
    """Base class for the downloaders."""

    def __init__(
        self,
        chrome_driver_path: str,
        country: CountryCode,
        download_type: DownloadType,
        output_folder: str,
        config: dict,
        app_config: dict,
    ):
        self._chrome_driver_path = chrome_driver_path
        self._country = country
        self._download_type = download_type
        self._output_folder = output_folder
        self._config = config
        self._output_file_path = None
        self._app_config = app_config

    @property
    def chrome_driver_path(self):
        """Get the path to the Chrome driver."""
        return self._chrome_driver_path

    @property
    def country(self):
        """Get the country."""
        return self._country

    @property
    def config(self):
        """Get the configuration data."""
        return self._config

    @property
    def app_config(self):
        """Get the app configuration data."""
        return self._app_config

    @property
    def output_folder(self):
        """Get the output folder."""
        return self._output_folder

    @property
    def download_type(self):
        """Get the download type."""
        return self._download_type

    def get_output_folder(self):
        if not self.output_folder or self.output_folder.strip() == "":
            logger.error("Output folder not found")
            return None

        return os.path.join(self.output_folder, self.country.code)

    def download(self, url, output_file_path, zip_files: list[str] = None):
        """Download the file from the URL."""
        self.pre_process()
        output_folder = os.path.dirname(output_file_path)
        utils.create_folder(output_folder)
        utils.download_file(url, output_file_path, zip_files)
        self.post_process()

    def pre_process(self):
        pass

    def post_process(self):
        pass


class DownloaderFactory:
    """Factory class to get the downloader."""

    @staticmethod
    def get_downloader(
        chrome_driver_path: str,
        country: CountryCode,
        download_type: DownloadType,
        output_folder: str,
        config: dict,
        app_config: dict = None,
    ):
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
