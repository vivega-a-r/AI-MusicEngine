import concurrent.futures
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.workers.processor import process_music_job

class TaskQueue:
    def __init__(self, max_workers: int = settings.MAX_WORKER_CONCURRENCY):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"Initialized TaskQueue with {max_workers} worker threads")

    def enqueue_job(self, job_id: str) -> None:
        """Enqueues a music generation job for asynchronous background execution."""
        logger.info(f"Enqueuing job {job_id} into background executor", extra={"job_id": job_id})
        self.executor.submit(process_music_job, job_id)

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False)

task_queue = TaskQueue()
