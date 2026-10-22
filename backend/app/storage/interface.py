from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class StorageProvider(ABC):
    @abstractmethod
    def get_job_dir(self, job_id: str) -> Path:
        pass

    @abstractmethod
    def get_file_path(self, job_id: str, filename: str) -> Path:
        pass

    @abstractmethod
    def file_exists(self, job_id: str, filename: str) -> bool:
        pass

    @abstractmethod
    def delete_job_files(self, job_id: str) -> bool:
        pass
