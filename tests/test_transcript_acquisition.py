from __future__ import annotations

from pathlib import Path

import pytest

from services.transcript_acquisition.jobs import InMemoryJobStore
from services.transcript_acquisition.adapters.youtube_transcript_api_adapter import (
    YouTubeTranscriptApiAdapter,
)
from services.transcript_acquisition.adapters.ytdlp_adapter import YtDlpTranscriptAdapter
from services.transcript_acquisition.models import (
    AdapterResult,
    AdapterTranscript,
    ManualUpload,
    TranscriptAcquisitionAttempt,
    TranscriptAcquisitionOutcome,
    TranscriptAcquisitionPath,
    TranscriptJobStatus,
    TranscriptSourceType,
)
from services.transcript_acquisition.parsers import parse_srt, parse_txt, parse_vtt
from services.transcript_acquisition.processing import TranscriptProcessingService
from services.transcript_acquisition.service import (
    TranscriptAcquisitionService,
    _extract_video_id,
)


FIXTURES = Path(__file__).parent / "fixtures"


class FakeAdapter:
    def __init__(
        self,
        *,
        path: TranscriptAcquisitionPath,
        provider: str,
        text: str | None = None,
        language: str | None = "en",
    ) -> None:
        self.path = path
        self.provider = provider
        self.text = text
        self.language = language

    def acquire(self, *, video_id: str, source_url: str | None = None) -> AdapterResult:
        if self.text is None:
            return AdapterResult(
                attempt=TranscriptAcquisitionAttempt(
                    path=self.path,
                    outcome=TranscriptAcquisitionOutcome.FAILED,
                    provider=self.provider,
                    sourceUrl=source_url,
                    errorCode="fake-failure",
                    errorMessage=f"{self.provider} failed",
                )
            )
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=self.path,
                outcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                provider=self.provider,
                sourceUrl=source_url,
            ),
            transcript=AdapterTranscript(
                text=self.text,
                language=self.language,
                source=self.provider,
            ),
        )


def service_with(primary_text: str | None, fallback_text: str | None):
    store = InMemoryJobStore()
    service = TranscriptAcquisitionService(
        primary_adapter=FakeAdapter(
            path=TranscriptAcquisitionPath.PRIMARY_YOUTUBE_AUTOMATED,
            provider="youtube-transcript-api",
            text=primary_text,
        ),
        fallback_adapter=FakeAdapter(
            path=TranscriptAcquisitionPath.FALLBACK_YOUTUBE_AUTOMATED,
            provider="yt-dlp",
            text=fallback_text,
        ),
        job_store=store,
    )
    return service, store


def test_primary_youtube_success_records_metadata() -> None:
    service, store = service_with("primary transcript", None)

    result = service.acquire_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert result.metadata.acquisition_outcome == TranscriptAcquisitionOutcome.SUCCEEDED
    assert result.metadata.acquisition_path == TranscriptAcquisitionPath.PRIMARY_YOUTUBE_AUTOMATED
    assert result.raw_transcript_text == "primary transcript"
    assert result.metadata.video_id == "dQw4w9WgXcQ"
    assert result.metadata.source_type == TranscriptSourceType.YOUTUBE_URL
    assert [attempt.outcome for attempt in result.metadata.attempts] == [
        TranscriptAcquisitionOutcome.SUCCEEDED
    ]
    job = next(iter(store.jobs.values()))
    assert job.status == TranscriptJobStatus.COMPLETED


@pytest.mark.parametrize(
    ("source", "expected_source_type"),
    [
        ("https://youtu.be/dQw4w9WgXcQ", TranscriptSourceType.YOUTUBE_URL),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", TranscriptSourceType.YOUTUBE_URL),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", TranscriptSourceType.YOUTUBE_URL),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", TranscriptSourceType.YOUTUBE_URL),
        ("dQw4w9WgXcQ", TranscriptSourceType.YOUTUBE_VIDEO_ID),
    ],
)
def test_youtube_source_normalization_supports_common_link_shapes(
    source: str,
    expected_source_type: TranscriptSourceType,
) -> None:
    service, _ = service_with("primary transcript", None)

    result = service.acquire_youtube(source)

    assert result.metadata.video_id == "dQw4w9WgXcQ"
    assert result.metadata.source_type == expected_source_type


@pytest.mark.parametrize(
    ("source", "expected_video_id"),
    [
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=test", "dQw4w9WgXcQ"),
    ],
)
def test_extract_video_id_handles_supported_url_patterns(
    source: str,
    expected_video_id: str,
) -> None:
    assert _extract_video_id(source) == expected_video_id


def test_invalid_youtube_source_raises_value_error() -> None:
    service, _ = service_with("primary transcript", None)

    with pytest.raises(ValueError, match="YouTube URL or 11-character YouTube video ID"):
        service.acquire_youtube("https://example.com/not-youtube")


def test_primary_failure_fallback_success() -> None:
    service, store = service_with(None, "fallback transcript")

    result = service.acquire_youtube("dQw4w9WgXcQ")

    assert result.metadata.acquisition_outcome == TranscriptAcquisitionOutcome.SUCCEEDED
    assert result.metadata.acquisition_path == TranscriptAcquisitionPath.FALLBACK_YOUTUBE_AUTOMATED
    assert result.metadata.source_type == TranscriptSourceType.YOUTUBE_VIDEO_ID
    assert [attempt.outcome for attempt in result.metadata.attempts] == [
        TranscriptAcquisitionOutcome.FAILED,
        TranscriptAcquisitionOutcome.SUCCEEDED,
    ]
    assert [attempt.provider for attempt in result.metadata.attempts] == [
        "youtube-transcript-api",
        "yt-dlp",
    ]
    job = next(iter(store.jobs.values()))
    assert job.status == TranscriptJobStatus.COMPLETED


def test_automated_failures_return_manual_required() -> None:
    service, store = service_with(None, None)

    result = service.acquire_youtube("dQw4w9WgXcQ")

    assert result.metadata.acquisition_outcome == TranscriptAcquisitionOutcome.MANUAL_REQUIRED
    assert result.metadata.manual_fallback_available is True
    assert result.metadata.transcript_text_present is False
    assert result.raw_transcript_text is None
    assert len(result.metadata.attempts) == 2
    job = next(iter(store.jobs.values()))
    assert job.status == TranscriptJobStatus.MANUAL_REQUIRED


def test_manual_paste_success() -> None:
    service, _ = service_with(None, None)

    result = service.acquire_manual_paste(
        "  pasted transcript\n\n\nsecond line  ",
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_id="dQw4w9WgXcQ",
    )

    assert result.metadata.acquisition_path == TranscriptAcquisitionPath.MANUAL_ADMIN_PASTE
    assert result.metadata.acquired_by == "admin"
    assert result.raw_transcript_source == "manual-paste"
    assert result.raw_transcript_text == "pasted transcript\n\nsecond line"


def test_txt_upload_parsing() -> None:
    assert parse_txt((FIXTURES / "sample.txt").read_text()) == (
        "First line of transcript.\n\nSecond line after extra spacing."
    )


def test_vtt_upload_parsing() -> None:
    service, _ = service_with(None, None)
    upload = ManualUpload(
        fileName="sample.vtt",
        content=(FIXTURES / "sample.vtt").read_text(),
        mimeType="text/vtt",
    )

    result = service.acquire_manual_upload(upload)

    assert result.metadata.acquisition_path == TranscriptAcquisitionPath.MANUAL_ADMIN_UPLOAD
    assert result.raw_transcript_text == (
        "Welcome to the remedy discussion.\nChant the mantra with attention."
    )
    assert "00:00" not in result.raw_transcript_text


def test_srt_upload_parsing() -> None:
    parsed = parse_srt((FIXTURES / "sample.srt").read_text())

    assert parsed == "Welcome to the remedy discussion.\nChant the mantra with attention."
    assert "00:00" not in parsed
    assert "\n1\n" not in parsed


def test_unsupported_manual_file_type_is_structured_failure() -> None:
    service, _ = service_with(None, None)
    upload = ManualUpload(fileName="transcript.pdf", content="not supported")

    result = service.acquire_manual_upload(upload)

    assert result.metadata.acquisition_outcome == TranscriptAcquisitionOutcome.FAILED
    assert result.metadata.attempts[-1].error_code == "unsupported-file-type"


def test_copyright_metadata_defaults_are_present() -> None:
    service, _ = service_with("primary transcript", None)

    result = service.acquire_youtube("dQw4w9WgXcQ")

    assert result.metadata.copyright.attribution_required is True
    assert result.metadata.copyright.rights_status == "unknown"
    assert result.metadata.copyright.short_citation_only is True


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ((FIXTURES / "sample.vtt").read_text(), "Welcome to the remedy discussion."),
        ((FIXTURES / "sample.srt").read_text(), "Chant the mantra with attention."),
    ],
)
def test_caption_parsers_preserve_spoken_text(content: str, expected: str) -> None:
    parser = parse_vtt if content.startswith("WEBVTT") else parse_srt
    assert expected in parser(content)


def test_youtube_transcript_api_adapter_joins_mock_response() -> None:
    class FakeApi:
        def fetch(self, video_id, languages):
            assert video_id == "dQw4w9WgXcQ"
            assert languages == ["en", "en-IN", "hi"]
            return [{"text": "first"}, {"text": "second"}]

    result = YouTubeTranscriptApiAdapter(api=FakeApi()).acquire(
        video_id="dQw4w9WgXcQ",
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )

    assert result.succeeded is True
    assert result.transcript is not None
    assert result.transcript.text == "first\nsecond"


def test_ytdlp_caption_selection_prefers_manual_language_order() -> None:
    adapter = YtDlpTranscriptAdapter(ydl_class=object)
    info = {
        "automatic_captions": {
            "en": [{"ext": "vtt", "url": "https://example.com/auto.vtt"}],
        },
        "subtitles": {
            "hi": [{"ext": "vtt", "url": "https://example.com/manual-hi.vtt"}],
        },
    }

    selected = adapter._select_caption(info)

    assert selected == {
        "url": "https://example.com/manual-hi.vtt",
        "extension": "vtt",
        "language": "hi",
        "kind": "manual",
    }


def test_transcript_processing_cleans_noise_and_adjacent_duplicates() -> None:
    raw = (
        "WEBVTT\n\n"
        "1\n"
        "00:00:01.000 --> 00:00:03.000\n"
        "  Chant the mantra with attention.  \n"
        "Chant the mantra with attention.\n"
        "[Music]\n\n"
        "Offer water before sunrise.\n"
    )

    result = TranscriptProcessingService().process_text(
        raw,
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_id="dQw4w9WgXcQ",
    )

    assert result.cleaned_text == "Chant the mantra with attention.\n\nOffer water before sunrise."
    assert len(result.chunks) == 1
    assert result.chunks[0].source_start_char == raw.index("Chant")
    assert result.chunks[0].source_end_char == raw.index("Offer water before sunrise.") + len(
        "Offer water before sunrise."
    )
    assert result.metadata.chunk_count == 1
    assert {rule.code for rule in result.metadata.rules} >= {
        "drop-caption-noise",
        "dedupe-adjacent-lines",
        "deterministic-chunking",
    }


def test_transcript_processing_chunks_deterministically_with_traceability() -> None:
    raw = "\n\n".join(
        [
            "First remedy paragraph has enough detail for review.",
            "Second remedy paragraph has another practical instruction.",
            "Third remedy paragraph should move into a later chunk.",
        ]
    )
    service = TranscriptProcessingService()

    first = service.process_text(raw, video_id="dQw4w9WgXcQ", max_chunk_chars=300)
    second = service.process_text(raw, video_id="dQw4w9WgXcQ", max_chunk_chars=300)

    assert [chunk.id for chunk in first.chunks] == [chunk.id for chunk in second.chunks]
    assert first.chunks[0].sequence == 1
    assert first.chunks[0].source_start_char == 0
    assert first.chunks[0].source_end_char <= len(raw)
    assert first.chunks[0].text.startswith("First remedy paragraph")


def test_transcript_processing_rejects_too_small_chunk_target() -> None:
    with pytest.raises(ValueError, match="max_chunk_chars must be at least 300"):
        TranscriptProcessingService().process_text("short transcript", max_chunk_chars=100)
