import os

from hrt.common.config_reader import logger
from hrt.common.enums import CallSignDownloadType, CountryCode, ExamType
from hrt.downloaders.base_downloader import BaseDownloader


class CADownloader(BaseDownloader):
    def __init__(self, chrome_driver_path, download_type, output_folder, config):
        super().__init__(
            chrome_driver_path,
            CountryCode.CANADA,
            download_type,
            output_folder,
            config,
        )

    def download_callsigns(self, callsigns_dt: CallSignDownloadType):
        pass

    def get_output_file_path(self, key: CallSignDownloadType | ExamType) -> str:
        input_file_path = self.config.get(key.id, {}).get("file")

        if not input_file_path:
            logger.error(f"Input file path not found for {key.id} in country {self.country.code}")
            return ""

        return os.path.join(self.get_output_folder(), self.download_type.id, input_file_path)

    def _download_file(self, key: ExamType, url_key, description):
        pass

    def download_question_bank(self, exam_type):
        pass
