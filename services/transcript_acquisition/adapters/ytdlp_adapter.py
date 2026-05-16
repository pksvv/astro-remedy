from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from services.transcript_acquisition.models import (
    AdapterResult,
    AdapterTranscript,
    TranscriptAcquisitionAttempt,
    TranscriptAcquisitionOutcome,
    TranscriptAcquisitionPath,
)
from services.transcript_acquisition.parsers import parse_srt, parse_vtt


class YtDlpTranscriptAdapter:
    provider = "yt-dlp"
    language_preferences = ["en", "en-IN", "hi"]

    def __init__(self, ydl_class: Any | None = None) -> None:
        self.ydl_class = ydl_class

    def acquire(self, *, video_id: str, source_url: str | None = None) -> AdapterResult:
        url = source_url or f"https://www.youtube.com/watch?v={video_id}"
        try:
            with tempfile.TemporaryDirectory(prefix="arip-ytdlp-") as temp_dir:
                info = self._extract_info(url, temp_dir)
                caption = self._select_caption(info)
                if caption is None:
                    return self._failure(source_url, "captions-unavailable", "No preferred captions found.")
                file_path = self._download_caption(caption["url"], temp_dir, caption["extension"])
                text = self._parse_file(file_path)
                if not text:
                    return self._failure(source_url, "empty-caption", "Downloaded caption text was empty.")
                return AdapterResult(
                    attempt=TranscriptAcquisitionAttempt(
                        path=TranscriptAcquisitionPath.FALLBACK_YOUTUBE_AUTOMATED,
                        outcome=TranscriptAcquisitionOutcome.SUCCEEDED,
                        provider=self.provider,
                        sourceUrl=source_url,
                        notes=f"Fetched {caption['kind']} captions in {caption['language']}.",
                    ),
                    transcript=AdapterTranscript(
                        text=text,
                        language=caption["language"],
                        file_name=file_path.name,
                        mime_type="text/vtt" if file_path.suffix == ".vtt" else "application/x-subrip",
                        source=self.provider,
                    ),
                )
        except Exception as exc:
            return self._failure(source_url, exc.__class__.__name__, str(exc))

    def _ydl_class(self) -> Any:
        if self.ydl_class is not None:
            return self.ydl_class
        from yt_dlp import YoutubeDL

        return YoutubeDL

    def _extract_info(self, url: str, temp_dir: str) -> dict[str, Any]:
        options = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitlesformat": "vtt/srt/best",
            "outtmpl": str(Path(temp_dir) / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with self._ydl_class()(options) as ydl:
            return ydl.extract_info(url, download=False)

    def _select_caption(self, info: dict[str, Any]) -> dict[str, str] | None:
        for key, kind in (("subtitles", "manual"), ("automatic_captions", "auto")):
            captions = info.get(key) or {}
            selected = self._select_language_caption(captions, kind)
            if selected:
                return selected
        return None

    def _select_language_caption(
        self,
        captions: dict[str, list[dict[str, Any]]],
        kind: str,
    ) -> dict[str, str] | None:
        for language in self.language_preferences:
            entries = captions.get(language) or []
            for extension in ("vtt", "srt"):
                for entry in entries:
                    if entry.get("url") and entry.get("ext") == extension:
                        return {
                            "url": entry["url"],
                            "extension": extension,
                            "language": language,
                            "kind": kind,
                        }
        return None

    def _download_caption(self, url: str, temp_dir: str, extension: str) -> Path:
        output_path = Path(temp_dir) / f"caption.{extension}"
        with self._ydl_class()({"quiet": True, "no_warnings": True}) as ydl:
            output_path.write_bytes(ydl.urlopen(url).read())
        return output_path

    @staticmethod
    def _parse_file(path: Path) -> str:
        content = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".srt":
            return parse_srt(content)
        return parse_vtt(content)

    def _failure(
        self,
        source_url: str | None,
        error_code: str,
        error_message: str,
    ) -> AdapterResult:
        return AdapterResult(
            attempt=TranscriptAcquisitionAttempt(
                path=TranscriptAcquisitionPath.FALLBACK_YOUTUBE_AUTOMATED,
                outcome=TranscriptAcquisitionOutcome.FAILED,
                provider=self.provider,
                sourceUrl=source_url,
                errorCode=error_code,
                errorMessage=error_message,
            )
        )
