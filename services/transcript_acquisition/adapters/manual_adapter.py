from __future__ import annotations

from pathlib import Path

from services.transcript_acquisition.models import (
    AdapterResult,
    AdapterTranscript,
    ManualUpload,
    TranscriptAcquisitionAttempt,
    TranscriptAcquisitionOutcome,
    TranscriptAcquisitionPath,
)
from services.transcript_acquisition.parsers import parse_srt, parse_txt, parse_vtt


class ManualTranscriptAdapter:
    provider = "manual-admin"

    def acquire_paste(self, text: str, *, source_url: str | None = None) -> AdapterResult:
        parsed = parse_txt(text)
        if not parsed:
            return self._failure(
                TranscriptAcquisitionPath.MANUAL_ADMIN_PASTE,
                source_url,
                "empty-manual-paste",
                "Manual paste transcript was empty.",
            )
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=TranscriptAcquisitionPath.MANUAL_ADMIN_PASTE,
                outcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                provider=self.provider,
                sourceUrl=source_url,
                notes="Transcript acquired by admin paste.",
            ),
            transcript=AdapterTranscript(text=parsed, source="manual-paste"),
        )

    def acquire_upload(self, upload: ManualUpload, *, source_url: str | None = None) -> AdapterResult:
        extension = Path(upload.file_name).suffix.lower()
        parser = {
            ".txt": parse_txt,
            ".vtt": parse_vtt,
            ".srt": parse_srt,
        }.get(extension)
        if parser is None:
            return self._failure(
                TranscriptAcquisitionPath.MANUAL_ADMIN_UPLOAD,
                source_url,
                "unsupported-file-type",
                f"Unsupported transcript upload type: {extension or 'unknown'}",
            )

        parsed = parser(upload.content)
        if not parsed:
            return self._failure(
                TranscriptAcquisitionPath.MANUAL_ADMIN_UPLOAD,
                source_url,
                "empty-manual-upload",
                "Manual upload transcript was empty after parsing.",
            )
        mime_type = upload.mime_type or self._mime_type(extension)
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=TranscriptAcquisitionPath.MANUAL_ADMIN_UPLOAD,
                outcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                provider=self.provider,
                sourceUrl=source_url,
                notes="Transcript acquired by admin upload.",
            ),
            transcript=AdapterTranscript(
                text=parsed,
                file_name=upload.file_name,
                mime_type=mime_type,
                source="manual-upload",
            ),
        )

    @staticmethod
    def _mime_type(extension: str) -> str:
        return {
            ".txt": "text/plain",
            ".vtt": "text/vtt",
            ".srt": "application/x-subrip",
        }[extension]

    def _failure(
        self,
        path: TranscriptAcquisitionPath,
        source_url: str | None,
        error_code: str,
        error_message: str,
    ) -> AdapterResult:
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=path,
                outcome=TranscriptAcquisitionOutcome.FAILED,
                provider=self.provider,
                sourceUrl=source_url,
                errorCode=error_code,
                errorMessage=error_message,
            )
        )
