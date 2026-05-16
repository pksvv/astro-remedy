from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import hashlib
import re

from services.transcript_acquisition.models import (
    TranscriptAcquisitionMetadata,
    TranscriptChunk,
    TranscriptProcessingMetadata,
    TranscriptProcessingResult,
    TranscriptProcessingRule,
    TranscriptSourceType,
)


DEFAULT_MAX_CHUNK_CHARS = 1200
MIN_MAX_CHUNK_CHARS = 300

TIMESTAMP_RE = re.compile(
    r"^(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?(?:\s*-->\s*"
    r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?)?$"
)
CAPTION_SEQUENCE_RE = re.compile(r"^\d{1,5}$")
NOISE_MARKER_RE = re.compile(
    r"^\s*(?:\[|\()?(?:music|applause|laughter|silence|intro|outro)"
    r"(?:\]|\))?\s*$",
    re.IGNORECASE,
)
WEBVTT_RE = re.compile(r"^(?:WEBVTT|Kind:|Language:)", re.IGNORECASE)
SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")
SPACE_RE = re.compile(r"[ \t\f\v]+")


PROCESSING_RULES = [
    TranscriptProcessingRule(
        code="normalize-newlines",
        description="Convert Windows and classic Mac line endings to Unix newlines.",
    ),
    TranscriptProcessingRule(
        code="normalize-whitespace",
        description="Trim each kept line and collapse repeated inline whitespace.",
    ),
    TranscriptProcessingRule(
        code="drop-caption-noise",
        description="Drop standalone timestamps, caption sequence numbers, WEBVTT headers, and simple sound markers.",
    ),
    TranscriptProcessingRule(
        code="collapse-blank-lines",
        description="Collapse repeated blank lines into paragraph boundaries.",
    ),
    TranscriptProcessingRule(
        code="dedupe-adjacent-lines",
        description="Drop consecutive duplicate spoken lines after normalization.",
    ),
    TranscriptProcessingRule(
        code="deterministic-chunking",
        description="Build stable chunks in source order up to the configured character target.",
    ),
]


@dataclass(frozen=True)
class _Segment:
    text: str
    source_start: int
    source_end: int
    paragraph_break_before: bool = False


class TranscriptProcessingService:
    def process_text(
        self,
        raw_text: str,
        *,
        metadata: TranscriptAcquisitionMetadata | None = None,
        source_type: TranscriptSourceType | None = None,
        source_url: str | None = None,
        video_id: str | None = None,
        max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    ) -> TranscriptProcessingResult:
        if max_chunk_chars < MIN_MAX_CHUNK_CHARS:
            raise ValueError(f"max_chunk_chars must be at least {MIN_MAX_CHUNK_CHARS}.")

        normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        segments = self._clean_segments(normalized)
        cleaned_text = self._join_segments(segments)
        chunks = self._chunk_segments(
            segments,
            max_chunk_chars=max_chunk_chars,
            source_key=self._source_key(
                source_url=source_url or metadata.source_url if metadata else source_url,
                video_id=video_id or metadata.video_id if metadata else video_id,
                raw_text=raw_text,
            ),
        )
        resolved_source_type = source_type or (metadata.source_type if metadata else None)
        resolved_source_url = source_url or (metadata.source_url if metadata else None)
        resolved_video_id = video_id or (metadata.video_id if metadata else None)
        warnings: list[str] = []
        if raw_text.strip() and not cleaned_text:
            warnings.append("Transcript text was present but all lines matched cleaning noise rules.")

        return TranscriptProcessingResult(
            metadata=TranscriptProcessingMetadata(
                sourceType=resolved_source_type,
                sourceUrl=resolved_source_url,
                videoId=resolved_video_id,
                rawCharacterCount=len(raw_text),
                cleanedCharacterCount=len(cleaned_text),
                chunkCount=len(chunks),
                maxChunkChars=max_chunk_chars,
                rules=PROCESSING_RULES,
            ),
            cleanedText=cleaned_text,
            chunks=chunks,
            warnings=warnings,
        )

    def process_acquisition_result(
        self,
        result: Any,
        *,
        max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    ) -> TranscriptProcessingResult:
        raw_text = result.raw_transcript_text or ""
        return self.process_text(
            raw_text,
            metadata=result.metadata,
            max_chunk_chars=max_chunk_chars,
        )

    def _clean_segments(self, text: str) -> list[_Segment]:
        segments: list[_Segment] = []
        previous_key: str | None = None
        pending_paragraph_break = False
        cursor = 0

        for raw_line in text.splitlines(keepends=True):
            line_start = cursor
            cursor += len(raw_line)
            content = raw_line.rstrip("\n")
            stripped = content.strip()

            if not stripped:
                if segments:
                    pending_paragraph_break = True
                continue
            if self._is_noise_line(stripped):
                continue

            normalized = SPACE_RE.sub(" ", stripped)
            line_key = normalized.casefold()
            if line_key == previous_key:
                continue

            leading_ws = len(content) - len(content.lstrip())
            source_start = line_start + leading_ws
            source_end = line_start + len(content.rstrip())
            segments.append(
                _Segment(
                    text=normalized,
                    source_start=source_start,
                    source_end=source_end,
                    paragraph_break_before=pending_paragraph_break,
                )
            )
            previous_key = line_key
            pending_paragraph_break = False

        return segments

    @staticmethod
    def _is_noise_line(line: str) -> bool:
        return bool(
            TIMESTAMP_RE.match(line)
            or CAPTION_SEQUENCE_RE.match(line)
            or NOISE_MARKER_RE.match(line)
            or WEBVTT_RE.match(line)
        )

    @staticmethod
    def _join_segments(segments: list[_Segment]) -> str:
        parts: list[str] = []
        for segment in segments:
            if not parts:
                parts.append(segment.text)
            elif segment.paragraph_break_before:
                parts.append("\n\n" + segment.text)
            else:
                parts.append("\n" + segment.text)
        return "".join(parts)

    def _chunk_segments(
        self,
        segments: list[_Segment],
        *,
        max_chunk_chars: int,
        source_key: str,
    ) -> list[TranscriptChunk]:
        expanded_segments: list[_Segment] = []
        for segment in segments:
            expanded_segments.extend(self._split_long_segment(segment, max_chunk_chars))

        chunks: list[TranscriptChunk] = []
        current: list[_Segment] = []
        current_text = ""

        for segment in expanded_segments:
            separator = self._separator_for(current, segment)
            candidate = f"{current_text}{separator}{segment.text}" if current else segment.text
            if current and len(candidate) > max_chunk_chars:
                chunks.append(self._build_chunk(current, len(chunks), source_key))
                current = [segment]
                current_text = segment.text
            else:
                current.append(segment)
                current_text = candidate

        if current:
            chunks.append(self._build_chunk(current, len(chunks), source_key))
        return chunks

    def _split_long_segment(self, segment: _Segment, max_chunk_chars: int) -> list[_Segment]:
        if len(segment.text) <= max_chunk_chars:
            return [segment]

        sentences = SENTENCE_BOUNDARY_RE.split(segment.text)
        if len(sentences) == 1:
            return [segment]

        split_segments: list[_Segment] = []
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if current and len(candidate) > max_chunk_chars:
                split_segments.append(
                    _Segment(
                        text=current,
                        source_start=segment.source_start,
                        source_end=segment.source_end,
                        paragraph_break_before=segment.paragraph_break_before
                        if not split_segments
                        else False,
                    )
                )
                current = sentence
            else:
                current = candidate
        if current:
            split_segments.append(
                _Segment(
                    text=current,
                    source_start=segment.source_start,
                    source_end=segment.source_end,
                    paragraph_break_before=segment.paragraph_break_before
                    if not split_segments
                    else False,
                )
            )
        return split_segments

    @staticmethod
    def _separator_for(current: list[_Segment], segment: _Segment) -> str:
        if not current:
            return ""
        return "\n\n" if segment.paragraph_break_before else "\n"

    def _build_chunk(
        self,
        segments: list[_Segment],
        zero_based_sequence: int,
        source_key: str,
    ) -> TranscriptChunk:
        text = self._join_segments(segments)
        source_start = min(segment.source_start for segment in segments)
        source_end = max(segment.source_end for segment in segments)
        sequence = zero_based_sequence + 1
        stable_id = self._chunk_id(
            source_key=source_key,
            sequence=sequence,
            source_start=source_start,
            source_end=source_end,
        )
        return TranscriptChunk(
            id=stable_id,
            sequence=sequence,
            text=text,
            sourceStartChar=source_start,
            sourceEndChar=source_end,
            characterCount=len(text),
        )

    @staticmethod
    def _chunk_id(
        *,
        source_key: str,
        sequence: int,
        source_start: int,
        source_end: int,
    ) -> str:
        digest = hashlib.sha256(
            f"{source_key}:{sequence}:{source_start}:{source_end}".encode("utf-8")
        ).hexdigest()[:12]
        return f"chunk-{sequence:04d}-{digest}"

    @staticmethod
    def _source_key(
        *,
        source_url: str | None,
        video_id: str | None,
        raw_text: str,
    ) -> str:
        if video_id:
            return f"video:{video_id}"
        if source_url:
            return f"url:{source_url}"
        return f"raw:{hashlib.sha256(raw_text.encode('utf-8')).hexdigest()[:16]}"
