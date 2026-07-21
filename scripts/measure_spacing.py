#!/usr/bin/env python3
"""Diagnose bullet line spacing in a rendered CV.

    python scripts/measure_spacing.py <slug>

For pdftotext to group a wrapped bullet as one block, the gap between lines
INSIDE a bullet must be smaller than the gap BETWEEN bullets. When that ordering
inverts, every continuation line extracts as a separate paragraph and the ATS
parseability score collapses.

Also reports anomalous gaps, which indicate an empty line box has been inserted
(usually by a stray space before a \\vspace in horizontal mode).

`analyze()` is imported by build_cv.py so the invariant is enforced on every
build, not only when this script is run by hand.
"""

from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# A continuation line sits in this x band, just right of the bullet glyph.
CONT_MIN, CONT_MAX = 46.0, 70.0
ANOMALY_PT = 16.0


@dataclass
class Spacing:
    intra: float = 0.0
    inter: float = 0.0
    n_intra: int = 0
    n_inter: int = 0
    anomalies: list[tuple[float, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.inter > self.intra and not self.anomalies


def analyze(pdf: Path) -> Spacing:
    rows = []
    doc = fitz.open(pdf)
    for pno in range(doc.page_count):
        for block in doc[pno].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"])
                rows.append((pno, line["bbox"][1], line["bbox"][0], text))
    doc.close()
    rows.sort(key=lambda r: (r[0], r[1]))

    intra: list[float] = []
    inter: list[float] = []
    anomalies: list[tuple[float, str]] = []

    for i in range(1, len(rows)):
        (_, y0, x0, t0), (_, y1, x1, t1) = rows[i - 1], rows[i]
        gap = y1 - y0
        prev_bullet = t0.startswith("•")
        prev_cont = CONT_MIN < x0 < CONT_MAX
        if t1.startswith("•") and (prev_bullet or prev_cont):
            inter.append(gap)
            if gap > ANOMALY_PT:
                anomalies.append((gap, t1[:52]))
        elif CONT_MIN < x1 < CONT_MAX and prev_bullet:
            intra.append(gap)
            if gap > ANOMALY_PT:
                anomalies.append((gap, t1[:52]))

    return Spacing(
        intra=statistics.median(intra) if intra else 0.0,
        inter=statistics.median(inter) if inter else 0.0,
        n_intra=len(intra),
        n_inter=len(inter),
        anomalies=anomalies,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    pdf = ROOT / f"{argv[1]}.pdf"
    if not pdf.exists():
        print(f"missing {pdf.name}")
        return 1

    s = analyze(pdf)
    print(f"intra-bullet line gap (median): {s.intra:.1f}pt   [n={s.n_intra}]")
    print(f"inter-bullet line gap (median): {s.inter:.1f}pt   [n={s.n_inter}]")

    if s.inter > s.intra:
        print(f"[ok]   ordering correct: inter ({s.inter:.1f}) > intra "
              f"({s.intra:.1f}) by {s.inter - s.intra:.1f}pt")
    else:
        print(f"[FAIL] ordering INVERTED: intra ({s.intra:.1f}) >= inter "
              f"({s.inter:.1f}) — pdftotext will split every wrapped bullet")

    if s.anomalies:
        print(f"[FAIL] {len(s.anomalies)} anomalous gap(s), likely empty line boxes:")
        for gap, txt in s.anomalies:
            print(f"  - {gap:.1f}pt before: {txt!r}")
    else:
        print("[ok]   no anomalous gaps between bullets")

    return 0 if s.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
