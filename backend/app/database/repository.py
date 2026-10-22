import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from backend.app.core.config import settings
from backend.app.database.models import JobRecord

class JobRepository:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        idempotency_key TEXT,
                        user_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        progress INTEGER NOT NULL,
                        current_stage TEXT NOT NULL,
                        request_json TEXT NOT NULL,
                        result_urls_json TEXT,
                        manifest_json TEXT,
                        error_json TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_idempotency ON jobs(idempotency_key)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
                conn.commit()

    def create_job(
        self,
        job_id: str,
        user_id: str,
        request_data: Dict,
        idempotency_key: Optional[str] = None
    ) -> JobRecord:
        now = datetime.now(timezone.utc).isoformat()
        record = JobRecord(
            job_id=job_id,
            idempotency_key=idempotency_key,
            user_id=user_id,
            status="queued",
            progress=0,
            current_stage="Job queued for processing",
            request_data=request_data,
            result_urls=None,
            manifest_data=None,
            error_data=None,
            created_at=now,
            updated_at=now
        )
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO jobs (
                        job_id, idempotency_key, user_id, status, progress, current_stage,
                        request_json, result_urls_json, manifest_json, error_json,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.job_id,
                    record.idempotency_key,
                    record.user_id,
                    record.status,
                    record.progress,
                    record.current_stage,
                    json.dumps(record.request_data),
                    None,
                    None,
                    None,
                    record.created_at,
                    record.updated_at
                ))
                conn.commit()
        return record

    def get_by_id(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
                if not row:
                    return None
                return self._row_to_record(row)

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[JobRecord]:
        if not idempotency_key:
            return None
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("SELECT * FROM jobs WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
                if not row:
                    return None
                return self._row_to_record(row)

    def update_progress(self, job_id: str, status: str, progress: int, current_stage: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE jobs
                    SET status = ?, progress = ?, current_stage = ?, updated_at = ?
                    WHERE job_id = ?
                """, (status, progress, current_stage, now, job_id))
                conn.commit()

    def complete_job(
        self,
        job_id: str,
        result_urls: Dict,
        manifest_data: Dict
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE jobs
                    SET status = 'succeeded', progress = 100, current_stage = 'Music generation complete',
                        result_urls_json = ?, manifest_json = ?, updated_at = ?
                    WHERE job_id = ?
                """, (json.dumps(result_urls), json.dumps(manifest_data), now, job_id))
                conn.commit()

    def fail_job(self, job_id: str, error_data: Dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE jobs
                    SET status = 'failed', current_stage = 'Job processing failed',
                        error_json = ?, updated_at = ?
                    WHERE job_id = ?
                """, (json.dumps(error_data), now, job_id))
                conn.commit()

    def list_jobs(self, user_id: Optional[str] = None, limit: int = 50) -> List[JobRecord]:
        with self._lock:
            with self._get_connection() as conn:
                if user_id:
                    cursor = conn.execute(
                        "SELECT * FROM jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                        (user_id, limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
                        (limit,)
                    )
                return [self._row_to_record(row) for row in cursor.fetchall()]

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
                conn.commit()
                return cursor.rowcount > 0

    def _row_to_record(self, row: sqlite3.Row) -> JobRecord:
        return JobRecord(
            job_id=row["job_id"],
            idempotency_key=row["idempotency_key"],
            user_id=row["user_id"],
            status=row["status"],
            progress=row["progress"],
            current_stage=row["current_stage"],
            request_data=json.loads(row["request_json"]),
            result_urls=json.loads(row["result_urls_json"]) if row["result_urls_json"] else None,
            manifest_data=json.loads(row["manifest_json"]) if row["manifest_json"] else None,
            error_data=json.loads(row["error_json"]) if row["error_json"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

job_repository = JobRepository()
