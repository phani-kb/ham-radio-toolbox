"""This module contains the USDownloader class."""

from hrt.common.enums import CountryCode
from hrt.downloaders.base_downloader import BaseDownloader


class USDownloader(BaseDownloader):
    """This class is used to download files for the US."""

    def __init__(self, chrome_driver_path, download_type, output_folder, config, app_config=None):
        super().__init__(
            chrome_driver_path,
            CountryCode.UNITED_STATES,
            download_type,
            output_folder,
            config,
            app_config,
        )

    def download_callsigns(self, callsigns_dt):
        raise NotImplementedError("USDownloader does not support downloading callsigns")

    def download_question_bank(self, exam_type):
        raise NotImplementedError("USDownloader does not support downloading question bank")
