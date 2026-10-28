#!/usr/bin/env python3
"""verify_pdf.py — check printed geometry of a Chromium-generated PDF.

Chromium writes its content streams in CSS px scaled by 0.72 to PDF points; the
text matrices (`a b c d e f Tm`) therefore carry page coordinates in the same
scaled space. This reports page count, the body font size actually used, and the
left/right text extents so margins can be checked against the intended layout.
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
        try:
            yield zlib.decompress(data[start:end]).decode("latin-1")
        except Exception:
            pass


def main() -> None:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))

    sizes: Counter[float] = Counter()
    xs: list[float] = []
    ys: list[float] = []
    for c in streams(data):
        for m in re.finditer(rf"(?m)/(F\d+)\s+({NUM})\s+Tf", c):
            sizes[round(float(m.group(2)), 2)] += 1
        for m in re.finditer(rf"(?m)^({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+Tm", c):
            xs.append(float(m.group(5)))
            ys.append(float(m.group(6)))

    print(f"file:  {path.name}")
    print(f"bytes: {len(data):,}")
    print(f"pages: {pages}")
    if sizes:
        top = ", ".join(f"{s}pt x{n}" for s, n in sorted(sizes.items(), key=lambda kv: -kv[1])[:6])
        print(f"font sizes (Tf): {top}")
    if xs:
        # scale: PDF pt = stream unit * (0.24 * 2.7419); extents are reported in mm
        k = 0.24 * 2.7419
        lo, hi = min(xs) * k, max(xs) * k
        print(f"text x-extent: {lo / 72 * 25.4:.1f}mm .. {hi / 72 * 25.4:.1f}mm "
              f"(width {(hi - lo) / 72 * 25.4:.1f}mm)")
        print(f"left margin ≈ {lo / 72 * 25.4:.1f}mm, right margin ≈ "
              f"{(595.276 - hi) / 72 * 25.4:.1f}mm")
        print(f"text y-extent: {min(ys) * k / 72 * 25.4:.1f}mm .. {max(ys) * k / 72 * 25.4:.1f}mm")


if __name__ == "__main__":
    main()
