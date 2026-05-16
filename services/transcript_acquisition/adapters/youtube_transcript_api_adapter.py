from __future__ import annotations

from typing import Any

from services.transcript_acquisition.models import (
    AdapterResult,
    AdapterTranscript,
    TranscriptAcquisitionAttempt,
    TranscriptAcquisitionOutcome,
    TranscriptAcquisitionPath,
)


class YouTubeTranscriptApiAdapter:
    provider = "youtube-transcript-api"
    language_preferences = ["en", "en-IN", "hi"]

    def __init__(self, api: Any | None = None) -> None:
        self.api = api

    def acquire(self, *, video_id: str, source_url: str | None = None) -> AdapterResult:
        try:
            api = self.api or self._build_api()
            transcript = self._fetch_transcript(api, video_id)
            text = self._join_segments(transcript)
            language = self._language_from_transcript(transcript)
            if not text:
                return self._failure(source_url, "empty-transcript", "Transcript was empty.")
            return AdapterResult(
                attempt=TranscriptAcquisitionAttempt(
                    path=TranscriptAcquisitionPath.PRIMARY_YOUTUBE_AUTOMATED,
                    outcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                    provider=self.provider,
                    sourceUrl=source_url,
                    notes="Fetched transcript through youtube-transcript-api.",
                ),
                transcript=AdapterTranscript(
                    text=text,
                    language=language,
                    source=self.provider,
                ),
            )
        except Exception as exc:
            return self._failure(source_url, exc.__class__.__name__, str(exc))

    def _build_api(self) -> Any:
        from youtube_transcript_api import YouTubeTranscriptApi

        return YouTubeTranscriptApi()

    def _fetch_transcript(self, api: Any, video_id: str) -> Any:
        if hasattr(api, "list"):
            transcript_list = api.list(video_id)
            transcript = transcript_list.find_transcript(self.language_preferences)
            return transcript.fetch()
        if hasattr(api, "fetch"):
            return api.fetch(video_id, languages=self.language_preferences)
        raise RuntimeError("Unsupported youtube-transcript-api client.")

    @staticmethod
    def _join_segments(transcript: Any) -> str:
        segments = getattr(transcript, "snippets", transcript)
        lines: list[str] = []
        for segment in segments:
            if isinstance(segment, dict):
                value = segment.get("text")
            else:
                value = getattr(segment, "text", None)
            if value:
                lines.append(str(value).strip())
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _language_from_transcript(transcript: Any) -> str | None:
        return getattr(transcript, "language_code", None) or getattr(transcript, "language", None)

    def _failure(
        self,
        source_url: str | None,
        error_code: str,
        error_message: str,
    ) -> AdapterResult:
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=TranscriptAcquisitionPath.PRIMARY_YOUTUBE_AUTOMATED,
                outcome=TranscriptAcquisitionOutcome.FAILED,
                provider=self.provider,
                sourceUrl=source_url,
                errorCode=error_code,
                errorMessage=error_message,
            )
        )
