from abc import ABC, abstractmethod

from common.enums import CallSignDownloadType


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
