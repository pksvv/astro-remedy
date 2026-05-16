from __future__ import annotations

import html
import re

from services.transcript_acquisition.parsers.txt_parser import parse_txt


TIMESTAMP_RE = re.compile(
    r"^\s*(?:\d{2}:)?\d{2}:\d{2}\.\d{3}\s+-->\s+"
    r"(?:\d{2}:)?\d{2}:\d{2}\.\d{3}(?:\s+.*)?$"
)
TAG_RE = re.compile(r"<[^>]+>")


def parse_vtt(content: str | bytes) -> str:
    text = parse_txt(content)
    lines: list[str] = []
    previous = ""
    in_note = False

    for raw_line in text.splitlines():
        line = raw_line.strip("\ufeff ").strip()
        if not line:
            in_note = False
            continue
        if line == "WEBVTT" or line.startswith(("Kind:", "Language:", "STYLE")):
            continue
        if line.startswith("NOTE"):
            in_note = True
            continue
        if in_note or TIMESTAMP_RE.match(line):
            continue
        if "-->" in line:
            continue

        cleaned = html.unescape(TAG_RE.sub("", line)).strip()
        if cleaned and cleaned != previous:
            lines.append(cleaned)
            previous = cleaned

    return parse_txt("\n".join(lines))
