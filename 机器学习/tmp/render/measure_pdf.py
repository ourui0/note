#!/usr/bin/env python3
"""measure_pdf.py — report page count, font sizes, and text extents from a PDF.

Reads uncompressed content streams and looks at the text state operators so we
can verify what the renderer actually produced (page count, body point size,
line widths) without installing a PDF library.
"""
from __future__ import annotations

import re
import sys
import zlib
from collections import Counter
from pathlib import Path

NUM = r"-?\d*\.?\d+"


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
            pass


def main() -> None:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    text = b"\n".join(streams(data)).decode("latin-1")

    sizes = Counter(float(x) for x in re.findall(rf"(?m)^({NUM})\s+Tf", text))
    # text matrices: a b c d e f Tm  -> d is the vertical scale (approx font size)
    tm = [float(m.group(1)) for m in re.finditer(rf"(?m)^({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+Tm", text)]
    xs = [float(m.group(1)) for m in re.finditer(rf"(?m)^({NUM})\s+({NUM})\s+Td", text)]

    print(f"file:   {path.name}")
    print(f"bytes:  {len(data):,}")
    print(f"pages:  {pages}")
    print(f"font sizes (pt) used with Tf: {dict(sorted(sizes.items()))}")
    if xs:
        print(f"Td x-extent: min={min(xs):.1f} max={max(xs):.1f} span={max(xs) - min(xs):.1f}pt")
    # rough "how far right does text start" check
    print(f"content streams: {len(list(streams(data)))}")


if __name__ == "__main__":
    main()
