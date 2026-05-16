from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from services.transcript_acquisition.models import (
    TranscriptAcquisitionAttempt,
    TranscriptAcquisitionJob,
    TranscriptAcquisitionResult,
    TranscriptJobStatus,
    utc_now,
)


class JobStore(Protocol):
    def create(self, *, source_url: str | None, video_id: str | None) -> TranscriptAcquisitionJob:
        pass

    def update(self, job: TranscriptAcquisitionJob) -> TranscriptAcquisitionJob:
        pass

    def get(self, job_id: str) -> TranscriptAcquisitionJob | None:
        pass


class InMemoryJobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, TranscriptAcquisitionJob] = {}

    def create(self, *, source_url: str | None, video_id: str | None) -> TranscriptAcquisitionJob:
        job = TranscriptAcquisitionJob(
            id=str(uuid4()),
            sourceUrl=source_url,
            videoId=video_id,
            status=TranscriptJobStatus.QUEUED,
        )
        self.jobs[job.id] = job
        return job

    def update(self, job: TranscriptAcquisitionJob) -> TranscriptAcquisitionJob:
        job.updated_at = utc_now()
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> TranscriptAcquisitionJob | None:
        return self.jobs.get(job_id)


class JsonFileJobStore(InMemoryJobStore):
    """Small durable scaffold until a DB-backed ingestion store exists."""

    def __init__(self, path: Path | str = ".cache/transcript_acquisition_jobs.json") -> None:
        super().__init__()
        self.path = Path(path)
        self._load()

    def update(self, job: TranscriptAcquisitionJob) -> TranscriptAcquisitionJob:
        updated = super().update(job)
        self._save()
        return updated

    def create(self, *, source_url: str | None, video_id: str | None) -> TranscriptAcquisitionJob:
        job = super().create(source_url=source_url, video_id=video_id)
        self._save()
        return job

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw_jobs = json.loads(self.path.read_text(encoding="utf-8"))
        self.jobs = {
            item["id"]: TranscriptAcquisitionJob.model_validate(item)
            for item in raw_jobs
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            job.model_dump(mode="json", by_alias=True)
            for job in self.jobs.values()
        ]
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_attempt(job: TranscriptAcquisitionJob, attempt: TranscriptAcquisitionAttempt) -> None:
    job.attempts.append(attempt)
    job.error_code = attempt.error_code
    job.error_message = attempt.error_message


def complete_job(job: TranscriptAcquisitionJob, result: TranscriptAcquisitionResult) -> None:
    job.status = TranscriptJobStatus.COMPLETED
    job.result = result
    job.error_code = None
    job.error_message = None
