#!/usr/bin/env python3
"""answer_marker.py - extract text from a PDF and report page count.

A tiny self-contained PDF text extractor: enough to verify what a rendered
document actually contains (page markers, CJK text, table cell values) without
installing poppler.
"""
from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path


def page_count(data: bytes) -> int:
    m = re.findall(rb"/Type\s*/Page[^s]", data)
    if m:
        return len(m)
    m = re.search(rb"/Count\s+(\d+)", data)
    return int(m.group(1)) if m else 0


def streams(data: bytes):
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        raw = data[start:end]
        try:
            yield zlib.decompress(raw)
        except Exception:
            yield raw


def main() -> None:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    print(f"file: {path.name}")
    print(f"bytes: {len(data)}")
    print(f"pages(by /Type /Page): {page_count(data)}")
    text = b"\n".join(streams(data))
    print(f"content-stream bytes: {len(text)}")
    print(f"has Tj/TJ ops: {text.count(b'Tj') + text.count(b'TJ')}")


if __name__ == "__main__":
    main()
