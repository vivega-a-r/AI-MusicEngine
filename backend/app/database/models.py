import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel

class JobRecord(BaseModel):
    job_id: str
    idempotency_key: Optional[str] = None
    user_id: str
    status: str # queued, running, succeeded, failed
    progress: int # 0 to 100
    current_stage: str
    request_data: Dict[str, Any]
    result_urls: Optional[Dict[str, Any]] = None
    manifest_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "idempotency_key": self.idempotency_key,
            "user_id": self.user_id,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "request_data": self.request_data,
            "result_urls": self.result_urls,
            "manifest_data": self.manifest_data,
            "error_data": self.error_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
