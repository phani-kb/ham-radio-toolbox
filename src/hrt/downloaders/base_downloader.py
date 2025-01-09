from abc import ABC, abstractmethod

from hrt.common.enums import CallSignDownloadType, ExamType


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
