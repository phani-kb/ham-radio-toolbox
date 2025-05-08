"""US scraper for scraping US callsigns."""

from typing import Dict, List, Optional

from hrt.common.config_reader import logger
from hrt.common.enums import CountryCode
from hrt.scrapers.base_scraper import BaseScraper


class USScraper(BaseScraper):
    """US scraper."""

    def __init__(self, driver: str, app_config: Optional[Dict] = None):
        super().__init__(driver, CountryCode.UNITED_STATES, app_config)

    def download_assigned_callsigns(self, url: str, output_file_path: str) -> None:
        """Download assigned callsigns."""
        logger.warning("Not implemented for US")
        raise NotImplementedError("download_assigned_callsigns not implemented for US")

    def download_available_callsigns(self, url: str, output_file_path: str) -> List[str]:
        """Download available callsigns."""
        logger.warning("Not implemented for US")
        raise NotImplementedError("download_available_callsigns not implemented for US")
