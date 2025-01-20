import os
from abc import ABC, abstractmethod

from hrt.common import utils
from hrt.common.config_reader import logger
from hrt.common.enums import CallSignDownloadType, CountryCode, DownloadType, ExamType


class IDownloader(ABC):
    """Interface for the downloaders."""

    @abstractmethod
    def pre_process(self):
        pass

    @abstractmethod
    def download_callsigns(self, callsigns_dt: CallSignDownloadType):
        pass

    @abstractmethod
    def download_question_bank(self, exam_type: ExamType):
        pass

    @abstractmethod
    def get_output_folder(self) -> str:
        pass

    @abstractmethod
    def post_process(self):
        pass


class BaseDownloader(IDownloader, ABC):
    def __init__(
        self,
        chrome_driver_path: str,
        country: CountryCode,
        download_type: DownloadType,
        output_folder: str,
        config: dict,
    ):
        self._chrome_driver_path = chrome_driver_path
        self._country = country
        self._download_type = download_type
        self._output_folder = output_folder
        self._config = config
        self._output_file_path = None

    @property
    def chrome_driver_path(self):
        return self._chrome_driver_path

    @property
    def country(self):
        return self._country

    @property
    def config(self):
        return self._config

    @property
    def output_folder(self):
        return self._output_folder

    @property
    def download_type(self):
        return self._download_type

    def get_output_folder(self):
        if not self.output_folder or self.output_folder.strip() == "":
            logger.error("Output folder not found")
            return None

        return os.path.join(self.output_folder, self.country.code)

    def download(self, url, output_file_path, zip_files: list[str] = None):
        self.pre_process()
        output_folder = os.path.dirname(output_file_path)
        utils.create_folder(output_folder)
        utils.download_file(url, output_file_path, zip_files)
        self.post_process()

    def pre_process(self):
        pass

    def post_process(self):
        pass
