from __future__ import annotations

import re


def parse_txt(content: str | bytes) -> str:
    text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text
