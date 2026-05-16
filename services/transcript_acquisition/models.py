from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TranscriptSourceType(StrEnum):
    YOUTUBE_URL = "youtube-url"
    YOUTUBE_VIDEO_ID = "youtube-video-id"
    MANUAL_PASTE = "manual-paste"
    MANUAL_UPLOAD = "manual-upload"


class TranscriptAcquisitionPath(StrEnum):
    PRIMARY_YOUTUBE_AUTOMATED = "primary-youtube-automated"
    FALLBACK_YOUTUBE_AUTOMATED = "fallback-youtube-automated"
    MANUAL_ADMIN_PASTE = "manual-admin-paste"
    MANUAL_ADMIN_UPLOAD = "manual-admin-upload"


class TranscriptAcquisitionOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    MANUAL_REQUIRED = "manual-required"


class TranscriptJobStatus(StrEnum):
    QUEUED = "queued"
    FETCHING_PRIMARY = "fetching-primary"
    FETCHING_FALLBACK = "fetching-fallback"
    MANUAL_REQUIRED = "manual-required"
    COMPLETED = "completed"
    FAILED = "failed"


class CopyrightMetadata(BaseModel):
    attribution_required: bool = Field(default=True, alias="attributionRequired")
    rights_status: str = Field(default="unknown", alias="rightsStatus")
    short_citation_only: bool = Field(default=True, alias="shortCitationOnly")


class TranscriptAcquisitionAttempt(BaseModel):
    path: TranscriptAcquisitionPath
    attempted_at: datetime = Field(default_factory=utc_now, alias="attemptedAt")
    outcome: TranscriptAcquisitionOutcome
    provider: str
    source_url: str | None = Field(default=None, alias="sourceUrl")
    error_code: str | None = Field(default=None, alias="errorCode")
    error_message: str | None = Field(default=None, alias="errorMessage")
    notes: str | None = None


class TranscriptAcquisitionMetadata(BaseModel):
    source_type: TranscriptSourceType = Field(alias="sourceType")
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    acquisition_outcome: TranscriptAcquisitionOutcome = Field(alias="acquisitionOutcome")
    acquisition_path: TranscriptAcquisitionPath | None = Field(
        default=None,
        alias="acquisitionPath",
    )
    attempts: list[TranscriptAcquisitionAttempt] = Field(default_factory=list)
    transcript_text_present: bool = Field(default=False, alias="transcriptTextPresent")
    transcript_language: str | None = Field(default=None, alias="transcriptLanguage")
    copyright: CopyrightMetadata = Field(default_factory=CopyrightMetadata)
    acquired_at: datetime | None = Field(default=None, alias="acquiredAt")
    acquired_by: str | None = Field(default=None, alias="acquiredBy")
    manual_fallback_available: bool = Field(
        default=True,
        alias="manualFallbackAvailable",
    )
    audit: dict[str, Any] = Field(default_factory=dict)


class TranscriptAcquisitionResult(BaseModel):
    metadata: TranscriptAcquisitionMetadata
    raw_transcript_text: str | None = Field(default=None, alias="rawTranscriptText")
    raw_transcript_file_name: str | None = Field(
        default=None,
        alias="rawTranscriptFileName",
    )
    raw_transcript_mime_type: str | None = Field(
        default=None,
        alias="rawTranscriptMimeType",
    )
    raw_transcript_source: str | None = Field(default=None, alias="rawTranscriptSource")
    warnings: list[str] = Field(default_factory=list)


class TranscriptProcessingRule(BaseModel):
    code: str
    description: str


class TranscriptChunk(BaseModel):
    id: str
    sequence: int
    text: str
    source_start_char: int = Field(alias="sourceStartChar")
    source_end_char: int = Field(alias="sourceEndChar")
    character_count: int = Field(alias="characterCount")


class TranscriptProcessingMetadata(BaseModel):
    source_type: TranscriptSourceType | None = Field(default=None, alias="sourceType")
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    raw_character_count: int = Field(alias="rawCharacterCount")
    cleaned_character_count: int = Field(alias="cleanedCharacterCount")
    chunk_count: int = Field(alias="chunkCount")
    max_chunk_chars: int = Field(alias="maxChunkChars")
    rules: list[TranscriptProcessingRule]


class TranscriptProcessingResult(BaseModel):
    metadata: TranscriptProcessingMetadata
    cleaned_text: str = Field(alias="cleanedText")
    chunks: list[TranscriptChunk]
    warnings: list[str] = Field(default_factory=list)


class AdapterTranscript(BaseModel):
    text: str
    language: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    source: str
    notes: str | None = None


class AdapterResult(BaseModel):
    attempt: TranscriptAcquisitionAttempt
    transcript: AdapterTranscript | None = None

    @property
    def succeeded(self) -> bool:
        return self.attempt.outcome == TranscriptAcquisitionOutcome.SUCCEEDED


class ManualUpload(BaseModel):
    file_name: str = Field(alias="fileName")
    content: str | bytes
    mime_type: str | None = Field(default=None, alias="mimeType")


class TranscriptAcquisitionJob(BaseModel):
    id: str
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    status: TranscriptJobStatus
    created_at: datetime = Field(default_factory=utc_now, alias="createdAt")
    updated_at: datetime = Field(default_factory=utc_now, alias="updatedAt")
    attempts: list[TranscriptAcquisitionAttempt] = Field(default_factory=list)
    result: TranscriptAcquisitionResult | None = None
    error_code: str | None = Field(default=None, alias="errorCode")
    error_message: str | None = Field(default=None, alias="errorMessage")

    model_config = {"populate_by_name": True}
