from __future__ import annotations

from typing import Protocol

from services.transcript_acquisition.models import AdapterResult


class TranscriptAdapter(Protocol):
    provider: str

    def acquire(self, *, video_id: str, source_url: str | None = None) -> AdapterResult:
        pass
