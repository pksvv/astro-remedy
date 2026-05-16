from __future__ import annotations

import html
import re

from services.transcript_acquisition.parsers.txt_parser import parse_txt


TIMESTAMP_RE = re.compile(
    r"^\s*(?:\d+\s+)?\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+"
    r"\d{2}:\d{2}:\d{2},\d{3}(?:\s+.*)?$"
)
TAG_RE = re.compile(r"<[^>]+>")


def parse_srt(content: str | bytes) -> str:
    text = parse_txt(content)
    lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.isdigit() or TIMESTAMP_RE.match(line):
            continue
        cleaned = html.unescape(TAG_RE.sub("", line)).strip()
        if cleaned:
            lines.append(cleaned)

    return parse_txt("\n".join(lines))
