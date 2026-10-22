import shutil
from pathlib import Path
from backend.app.core.config import settings
from backend.app.storage.interface import StorageProvider

class LocalStorageProvider(StorageProvider):
    def __init__(self, root_dir: str = settings.STORAGE_DIR):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        job_dir = self.root_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def get_file_path(self, job_id: str, filename: str) -> Path:
        return self.root_dir / job_id / filename

    def file_exists(self, job_id: str, filename: str) -> bool:
        return (self.root_dir / job_id / filename).exists()

    def delete_job_files(self, job_id: str) -> bool:
        job_dir = self.root_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
            return True
        return False

storage_provider = LocalStorageProvider()
