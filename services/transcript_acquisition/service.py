from __future__ import annotations

import re

from services.transcript_acquisition.adapters import (
    ManualTranscriptAdapter,
    TranscriptAdapter,
    YouTubeTranscriptApiAdapter,
    YtDlpTranscriptAdapter,
)
from services.transcript_acquisition.jobs import (
    InMemoryJobStore,
    JobStore,
    append_attempt,
    complete_job,
)
from services.transcript_acquisition.models import (
    AdapterResult,
    ManualUpload,
    TranscriptAcquisitionMetadata,
    TranscriptAcquisitionOutcome,
    TranscriptAcquisitionPath,
    TranscriptAcquisitionResult,
    TranscriptJobStatus,
    TranscriptSourceType,
    utc_now,
)


VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class TranscriptAcquisitionService:
    def __init__(
        self,
        *,
        primary_adapter: TranscriptAdapter | None = None,
        fallback_adapter: TranscriptAdapter | None = None,
        manual_adapter: ManualTranscriptAdapter | None = None,
        job_store: JobStore | None = None,
    ) -> None:
        self.primary_adapter = primary_adapter or YouTubeTranscriptApiAdapter()
        self.fallback_adapter = fallback_adapter or YtDlpTranscriptAdapter()
        self.manual_adapter = manual_adapter or ManualTranscriptAdapter()
        self.job_store = job_store or InMemoryJobStore()

    def acquire_youtube(
        self,
        source: str,
        *,
        job_id: str | None = None,
    ) -> TranscriptAcquisitionResult:
        source_url, video_id, source_type = self._normalize_youtube_source(source)
        job = self.job_store.get(job_id) if job_id else None
        if job is None:
            job = self.job_store.create(source_url=source_url, video_id=video_id)

        job.status = TranscriptJobStatus.FETCHING_PRIMARY
        self.job_store.update(job)
        primary = self.primary_adapter.acquire(video_id=video_id, source_url=source_url)
        append_attempt(job, primary.attempt)
        self.job_store.update(job)
        if primary.succeeded:
            result = self._build_success_result(
                source_type=source_type,
                source_url=source_url,
                video_id=video_id,
                adapter_result=primary,
                attempts=job.attempts,
            )
            complete_job(job, result)
            self.job_store.update(job)
            return result

        job.status = TranscriptJobStatus.FETCHING_FALLBACK
        self.job_store.update(job)
        fallback = self.fallback_adapter.acquire(video_id=video_id, source_url=source_url)
        append_attempt(job, fallback.attempt)
        self.job_store.update(job)
        if fallback.succeeded:
            result = self._build_success_result(
                source_type=source_type,
                source_url=source_url,
                video_id=video_id,
                adapter_result=fallback,
                attempts=job.attempts,
            )
            complete_job(job, result)
            self.job_store.update(job)
            return result

        job.status = TranscriptJobStatus.MANUAL_REQUIRED
        result = self._build_manual_required_result(
            source_type=source_type,
            source_url=source_url,
            video_id=video_id,
            attempts=job.attempts,
        )
        job.result = result
        self.job_store.update(job)
        return result

    def acquire_manual_paste(
        self,
        text: str,
        *,
        source_url: str | None = None,
        video_id: str | None = None,
        job_id: str | None = None,
    ) -> TranscriptAcquisitionResult:
        job = self._manual_job(job_id=job_id, source_url=source_url, video_id=video_id)
        result = self.manual_adapter.acquire_paste(text, source_url=source_url)
        return self._complete_manual(
            job=job,
            adapter_result=result,
            source_type=TranscriptSourceType.MANUAL_PASTE,
            source_url=source_url,
            video_id=video_id,
        )

    def acquire_manual_upload(
        self,
        upload: ManualUpload,
        *,
        source_url: str | None = None,
        video_id: str | None = None,
        job_id: str | None = None,
    ) -> TranscriptAcquisitionResult:
        job = self._manual_job(job_id=job_id, source_url=source_url, video_id=video_id)
        result = self.manual_adapter.acquire_upload(upload, source_url=source_url)
        return self._complete_manual(
            job=job,
            adapter_result=result,
            source_type=TranscriptSourceType.MANUAL_UPLOAD,
            source_url=source_url,
            video_id=video_id,
        )

    def _manual_job(
        self,
        *,
        job_id: str | None,
        source_url: str | None,
        video_id: str | None,
    ):
        job = self.job_store.get(job_id) if job_id else None
        if job is None:
            job = self.job_store.create(source_url=source_url, video_id=video_id)
        return job

    def _complete_manual(
        self,
        *,
        job,
        adapter_result: AdapterResult,
        source_type: TranscriptSourceType,
        source_url: str | None,
        video_id: str | None,
    ) -> TranscriptAcquisitionResult:
        append_attempt(job, adapter_result.attempt)
        if adapter_result.succeeded:
            result = self._build_success_result(
                source_type=source_type,
                source_url=source_url,
                video_id=video_id,
                adapter_result=adapter_result,
                attempts=job.attempts,
                acquired_by="admin",
            )
            complete_job(job, result)
        else:
            job.status = TranscriptJobStatus.FAILED
            result = self._build_failure_result(
                source_type=source_type,
                source_url=source_url,
                video_id=video_id,
                adapter_result=adapter_result,
                attempts=job.attempts,
            )
            job.result = result
        self.job_store.update(job)
        return result

    def _build_success_result(
        self,
        *,
        source_type: TranscriptSourceType,
        source_url: str | None,
        video_id: str | None,
        adapter_result: AdapterResult,
        attempts,
        acquired_by: str | None = None,
    ) -> TranscriptAcquisitionResult:
        transcript = adapter_result.transcript
        assert transcript is not None
        acquired_at = utc_now()
        return TranscriptAcquisitionResult(
            metadata=TranscriptAcquisitionMetadata(
                sourceType=source_type,
                sourceUrl=source_url,
                videoId=video_id,
                acquisitionOutcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                acquisitionPath=adapter_result.attempt.path,
                attempts=attempts,
                transcriptTextPresent=True,
                transcriptLanguage=transcript.language,
                acquiredAt=acquired_at,
                acquiredBy=acquired_by,
                manualFallbackAvailable=True,
            ),
            rawTranscriptText=transcript.text,
            rawTranscriptFileName=transcript.file_name,
            rawTranscriptMimeType=transcript.mime_type,
            rawTranscriptSource=transcript.source,
        )

    def _build_manual_required_result(
        self,
        *,
        source_type: TranscriptSourceType,
        source_url: str | None,
        video_id: str | None,
        attempts,
    ) -> TranscriptAcquisitionResult:
        return TranscriptAcquisitionResult(
            metadata=TranscriptAcquisitionMetadata(
                sourceType=source_type,
                sourceUrl=source_url,
                videoId=video_id,
                acquisitionOutcome=TranscriptAcquisitionOutcome.MANUAL_REQUIRED,
                acquisitionPath=None,
                attempts=attempts,
                transcriptTextPresent=False,
                manualFallbackAvailable=True,
                audit={"nextStep": "manual-admin-paste-or-upload"},
            ),
            rawTranscriptSource=None,
            warnings=["Automated transcript acquisition failed; manual fallback is required."],
        )

    def _build_failure_result(
        self,
        *,
        source_type: TranscriptSourceType,
        source_url: str | None,
        video_id: str | None,
        adapter_result: AdapterResult,
        attempts,
    ) -> TranscriptAcquisitionResult:
        return TranscriptAcquisitionResult(
            metadata=TranscriptAcquisitionMetadata(
                sourceType=source_type,
                sourceUrl=source_url,
                videoId=video_id,
                acquisitionOutcome=TranscriptAcquisitionOutcome.FAILED,
                acquisitionPath=adapter_result.attempt.path,
                attempts=attempts,
                transcriptTextPresent=False,
                manualFallbackAvailable=True,
            ),
            warnings=[adapter_result.attempt.error_message or "Transcript acquisition failed."],
        )

    @staticmethod
    def _normalize_youtube_source(source: str) -> tuple[str | None, str, TranscriptSourceType]:
        value = source.strip()
        if VIDEO_ID_RE.match(value):
            return None, value, TranscriptSourceType.YOUTUBE_VIDEO_ID
        video_id = _extract_video_id(value)
        if not video_id:
            raise ValueError("Expected a YouTube URL or 11-character YouTube video ID.")
        return value, video_id, TranscriptSourceType.YOUTUBE_URL


def _extract_video_id(url: str) -> str | None:
    patterns = [
        r"[?&]v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
