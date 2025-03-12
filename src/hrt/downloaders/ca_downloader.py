"""
This module contains the implementation of the CADownloader class.
"""
from typing import Dict, Optional

from hrt.common.enums import CountryCode, DownloadType
from hrt.downloaders.base_downloader import BaseDownloader


class CADownloader(BaseDownloader):
    """This class is used to download files for Canada."""
    def __init__(
        self,
        chrome_driver_path: str,
        download_type: DownloadType,
        output_folder: str,
        config: Dict,
        app_config: Optional[Dict] = None
    ):
        super().__init__(
            chrome_driver_path,
            CountryCode.CANADA,
            download_type,
            output_folder,
            config,
            app_config,
        )

