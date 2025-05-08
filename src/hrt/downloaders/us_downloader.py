"""
This module contains the implementation of the USDownloader class.
"""

from typing import Dict, Optional

from hrt.common.enums import CallSignDownloadType, CountryCode, DownloadType, ExamType
from hrt.downloaders.base_downloader import BaseDownloader


class USDownloader(BaseDownloader):
    """This class is used to download files for the US."""

    def __init__(
        self,
        chrome_driver_path: str,
        download_type: DownloadType,
        output_folder: str,
        config: Dict,
        app_config: Optional[Dict] = None,
    ):
        super().__init__(
            chrome_driver_path,
            CountryCode.UNITED_STATES,
            download_type,
            output_folder,
            config,
            app_config,
        )

    def download_callsigns(self, callsigns_dt: CallSignDownloadType) -> None:
        """Download callsigns for the US."""
        raise NotImplementedError("download_callsigns not implemented for US")

    def download_question_bank(self, exam_type: ExamType) -> None:
        """Download question bank for the US."""
        raise NotImplementedError("download_question_bank not implemented for US")
