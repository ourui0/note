#!/usr/bin/env python3
"""pdf_text_extent.py — report per-page text extent and any overflow.

Chromium content streams use `a b c d e f Tm` text matrices in a scaled page
space (0.24 * 2.7419 per PDF point). Sampling every text-showing operator at the
current matrix gives the real printed extent, so we can tell whether a table,
equation, or figure runs past the 6in text block (152.4mm) or off the 210mm page.
"""
from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path

NUM = r"-?\d*\.?\d+"
K = 0.24 * 2.7419  # stream unit -> PDF pt
PAGE_W_PT = 595.276
PAGE_H_PT = 841.89
TEXT_BLOCK_MM = 152.4
LEFT_MM = 26.4


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

    worst_over = 0.0
    per_page = []
    for pi, c in enumerate(streams(data), 1):
        xs, ys, sizes = [], [], set()
        for m in re.finditer(rf"(?m)^({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+Tm", c):
            xs.append(float(m.group(5)))
            ys.append(float(m.group(6)))
        for m in re.finditer(rf"(?m)^\S+\s+({NUM})\s+Tf", c):
            sizes.add(round(float(m.group(1)), 2))
        if not xs:
            continue
        lo, hi = min(xs) * K, max(xs) * K
        per_page.append((pi, lo, hi, sizes))
        over_pt = hi - (LEFT_MM / 25.4 * 72 + TEXT_BLOCK_MM / 25.4 * 72)
        worst_over = max(worst_over, over_pt)

    print(f"file: {path.name}   pages: {pages}")
    for pi, lo, hi, sizes in per_page:
        right_mm = hi / 72 * 25.4
        print(f"  stream {pi}: x {lo / 72 * 25.4:6.1f}mm .. {right_mm:6.1f}mm "
              f"(used {right_mm - lo / 72 * 25.4:5.1f}mm)  sizes={sorted(sizes)[:4]}")
    if worst_over > 2:
        print(f"  !! overflow past the text block by up to {worst_over / 72 * 25.4:.1f}mm")
    else:
        print("  ok: nothing exceeds the 6in text block")


if __name__ == "__main__":
    main()
