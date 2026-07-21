#!/usr/bin/env python3
"""Count keyword frequency across a role's job-listings benchmark.

    python scripts/keyword_freq.py <role-slug>              rebuild the table
    python scripts/keyword_freq.py <role-slug> --coverage   score the built CV

Reads:
    config/job-listings/<slug>.md   the benchmark — every `Technologies
                                    required:` line is one listing's demand set
    config/keyword-synonyms.yaml    alias merges and stopterms
    config/cv-config.yaml           tier cutoffs

Writes:
    config/job-listings/<slug>.md   the `## Keyword frequency` section, in place
    build/<slug>/keyword-coverage.md   (--coverage only)

Why this is code and not a judgement call: the ATS grader used to re-derive the
keyword set on every run, so the same CV could score differently twice and a
high-frequency term could be traded away for a rare one without anyone noticing.
A term's weight is a fact about the benchmark file, and the benchmark file does
not change between iterations. Counting it once, deterministically, is what
makes iteration-to-iteration score movement mean something.

Output is a pure function of the inputs — no timestamps — so a rerun that
changes nothing produces a byte-identical file.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
BUILD = ROOT / "build"

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# One listing's demand set. Tolerates the backticked form used in the benchmark
# files (`Technologies required:`) and a bare one, since the section is written
# by hand.
TECH_LINE = re.compile(r"^\s*`?Technologies required:`?\s*(.+)$", re.IGNORECASE)

SECTION_HEADING = "## Keyword frequency"

# Coverage status, worst to best. Ordering is what makes regression detection
# possible: a term moving DOWN this list between builds is a real loss.
STATUS_ORDER = ["MISSING", "ALIAS-ONLY", "SKILLS-ONLY", "IN-BULLET"]


class KeywordError(Exception):
    """Fatal problem — reported to the caller."""


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise KeywordError(f"missing required file: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def listings_path(slug: str) -> Path:
    return CONFIG / "job-listings" / f"{slug}.md"


def load_synonyms() -> tuple[dict[str, str], set[str]]:
    """Return (alias -> canonical display form, stopterms).

    The canonical key maps to itself so a posting that already uses the
    preferred spelling takes the same path as one using an alias.
    """
    raw = load_yaml(CONFIG / "keyword-synonyms.yaml")
    alias_map: dict[str, str] = {}
    for display, aliases in (raw.get("canonical") or {}).items():
        alias_map[norm(display)] = display
        for alias in aliases or []:
            existing = alias_map.get(norm(alias))
            if existing and existing != display:
                raise KeywordError(
                    f"alias {alias!r} maps to both {existing!r} and {display!r} "
                    "in config/keyword-synonyms.yaml — one of them is wrong"
                )
            alias_map[norm(alias)] = display
    stop = {norm(t) for t in (raw.get("stopterms") or [])}
    return alias_map, stop


def norm(term: str) -> str:
    """Fold a term to its comparison key: lowercase, collapsed whitespace."""
    return re.sub(r"\s+", " ", term.strip().lower())


# --------------------------------------------------------------------------
# counting
# --------------------------------------------------------------------------

def parse_listings(text: str) -> list[list[str]]:
    """One entry per listing, holding that listing's raw term strings."""
    listings = []
    for line in text.splitlines():
        m = TECH_LINE.match(line)
        if not m:
            continue
        terms = [t.strip(" `.") for t in m.group(1).split(",")]
        listings.append([t for t in terms if t])
    return listings


def count_terms(
    listings: list[list[str]],
    alias_map: dict[str, str],
    stop: set[str],
) -> tuple[Counter, dict[str, Counter]]:
    """Count listings-containing-term, not total mentions.

    A posting that says "Python" three times still demands Python once. Counting
    mentions would let one verbose listing outvote ten terse ones.
    """
    counts: Counter = Counter()
    surfaces: dict[str, Counter] = defaultdict(Counter)

    for terms in listings:
        seen = set()
        for raw in terms:
            key = norm(raw)
            if not key or key in stop:
                continue
            display = alias_map.get(key)
            if display is None:
                # Unknown term: it is its own canonical form. Track the surface
                # spellings so the table shows the one the market uses most.
                display = raw.strip()
                bucket = key
            else:
                bucket = norm(display)
            if bucket in stop:
                continue
            surfaces[bucket][display] += 1
            seen.add(bucket)
        for bucket in seen:
            counts[bucket] += 1

    return counts, surfaces


def display_form(bucket: str, surfaces: dict[str, Counter], alias_map: dict[str, str]) -> str:
    """The spelling to print — and the one the CV should match verbatim."""
    canonical = alias_map.get(bucket)
    if canonical:
        return canonical
    # Most common surface spelling; ties broken alphabetically so the output is
    # deterministic across runs.
    ranked = sorted(surfaces[bucket].items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[0][0] if ranked else bucket


def tier_of(pct: float, critical: float, important: float) -> str:
    if pct >= critical:
        return "CRITICAL"
    if pct >= important:
        return "IMPORTANT"
    return "PERIPHERAL"


def build_table(slug: str) -> tuple[str, list[dict], int]:
    """Return (rendered section, rows, listing count)."""
    config = load_yaml(CONFIG / "cv-config.yaml")
    kw = config.get("keywords") or {}
    critical = float(kw.get("critical_pct", 0.50))
    important = float(kw.get("important_pct", 0.25))

    path = listings_path(slug)
    if not path.exists():
        raise KeywordError(f"no benchmark for {slug!r}: {path.relative_to(ROOT)}")

    alias_map, stop = load_synonyms()
    listings = parse_listings(path.read_text(encoding="utf-8"))
    if not listings:
        raise KeywordError(
            f"{path.relative_to(ROOT)} has no `Technologies required:` lines — "
            "nothing to count"
        )

    counts, surfaces = count_terms(listings, alias_map, stop)
    total = len(listings)

    rows = []
    for bucket, count in counts.items():
        pct = count / total
        rows.append({
            "term": display_form(bucket, surfaces, alias_map),
            "count": count,
            "pct": round(pct * 100),
            "tier": tier_of(pct, critical, important),
        })
    rows.sort(key=lambda r: (-r["count"], r["term"].lower()))

    lines = [
        SECTION_HEADING,
        "",
        f"<!-- generated by scripts/keyword_freq.py from {total} listings.",
        f"     Do not hand-edit: rerun the script. Tier cutoffs from",
        f"     cv-config.yaml keywords: CRITICAL >= {critical:.0%} of listings,",
        f"     IMPORTANT >= {important:.0%}, PERIPHERAL below that. -->",
        "",
        "| Term | Count | % | Tier |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['term']} | {r['count']} | {r['pct']}% | {r['tier']} |")
    lines.append("")

    return "\n".join(lines), rows, total


# --------------------------------------------------------------------------
# writing the section back
# --------------------------------------------------------------------------

def splice_section(text: str, section: str) -> str:
    """Replace the frequency section, or insert it above the first `##` heading.

    Idempotent: the section is delimited by its own heading and the next `##`,
    so rerunning replaces rather than stacks.
    """
    lines = text.splitlines()
    start = next(
        (i for i, ln in enumerate(lines) if ln.strip() == SECTION_HEADING), None
    )

    if start is not None:
        end = next(
            (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
            len(lines),
        )
        return "\n".join(lines[:start] + section.splitlines() + [""] + lines[end:])

    first_heading = next(
        (i for i, ln in enumerate(lines) if ln.startswith("## ")), len(lines)
    )
    return "\n".join(
        lines[:first_heading] + section.splitlines() + [""] + lines[first_heading:]
    )


def write_table(slug: str) -> int:
    section, rows, total = build_table(slug)
    path = listings_path(slug)
    updated = splice_section(path.read_text(encoding="utf-8"), section)
    if not updated.endswith("\n"):
        updated += "\n"
    path.write_text(updated, encoding="utf-8")

    tiers = Counter(r["tier"] for r in rows)
    print(f"[ok]   {path.relative_to(ROOT)}: {len(rows)} terms from {total} listings")
    print(f"[info] {tiers['CRITICAL']} CRITICAL, {tiers['IMPORTANT']} IMPORTANT, "
          f"{tiers['PERIPHERAL']} PERIPHERAL")

    config = load_yaml(CONFIG / "cv-config.yaml")
    listings_cfg = config.get("listings") or {}
    floor = int(listings_cfg.get("hard_floor", 30))
    minimum = int(listings_cfg.get("min_required", 50))
    if total < floor:
        print(f"[FAIL] only {total} listings, below listings.hard_floor ({floor}). "
              "Frequencies from this few postings are noise — gather more.")
        return 1
    if total < minimum:
        print(f"[warn] {total} listings is below listings.min_required ({minimum}); "
              "tier boundaries will be unstable")
    return 0


# --------------------------------------------------------------------------
# coverage
# --------------------------------------------------------------------------

def parse_table(text: str) -> list[dict]:
    """Read back a rendered frequency table. Used by coverage and by build_cv."""
    rows = []
    in_section = False
    for line in text.splitlines():
        if line.strip() == SECTION_HEADING:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0] in ("Term", "---"):
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        try:
            count = int(cells[1])
        except ValueError:
            continue
        rows.append({
            "term": cells[0],
            "count": count,
            "pct": cells[2],
            "tier": cells[3],
        })
    return rows


def term_pattern(term: str) -> re.Pattern:
    """Whole-token match tolerant of plurals, safe for C++, C#, .NET, CI/CD.

    \\b is useless here: it treats "+" and "#" as boundaries, so \\bC\\b matches
    inside "C++" and \\bC++\\b never matches at all. Explicit lookarounds over
    the character class that can appear inside a technology name work instead.

    The trailing class also blocks superscripts, so the one-letter language name
    "R" does not match the "R" of an R-squared figure (rendered as R² by the
    template's $R^2$). Single-letter terms like R and C are common in this
    domain and are exactly where a loose boundary invents coverage.
    """
    return re.compile(
        r"(?<![A-Za-z0-9+#])" + re.escape(term) + r"s?(?![A-Za-z0-9+#²³^_])",
        re.IGNORECASE,
    )


def split_regions(cv_text: str) -> tuple[str, str]:
    """Split the extracted CV into (substantive body, skills list).

    A term that appears only under Technical Skills is a claim with no evidence
    behind it. Both the ATS rubric and every recruiter discount those, so the
    two regions have to be scored separately.
    """
    m = re.search(r"^\s*Technical Skills\s*$", cv_text, re.MULTILINE)
    if not m:
        return cv_text, ""
    return cv_text[:m.start()], cv_text[m.end():]


def classify(term: str, aliases: list[str], body: str, skills: str) -> tuple[str, str]:
    """Return (status, note)."""
    pat = term_pattern(term)
    if pat.search(body):
        return "IN-BULLET", ""
    if pat.search(skills):
        return "SKILLS-ONLY", ""
    for alias in aliases:
        apat = term_pattern(alias)
        where = "bullet" if apat.search(body) else ("skills" if apat.search(skills) else None)
        if where:
            return "ALIAS-ONLY", f"CV says {alias!r} ({where}); listings say {term!r}"
    return "MISSING", ""


_ALIAS_CACHE: dict[str, list[str]] | None = None


def aliases_for(display: str) -> list[str]:
    global _ALIAS_CACHE
    if _ALIAS_CACHE is None:
        raw = load_yaml(CONFIG / "keyword-synonyms.yaml")
        _ALIAS_CACHE = {
            norm(key): list(aliases or [])
            for key, aliases in (raw.get("canonical") or {}).items()
        }
    return _ALIAS_CACHE.get(norm(display), [])


def coverage_path(slug: str) -> Path:
    return BUILD / slug / "keyword-coverage.md"


def compute_coverage(slug: str) -> list[dict]:
    """Classify every CRITICAL and IMPORTANT term against the built CV text."""
    bench = listings_path(slug)
    if not bench.exists():
        raise KeywordError(f"no benchmark for {slug!r}: {bench.relative_to(ROOT)}")
    rows = parse_table(bench.read_text(encoding="utf-8"))
    if not rows:
        raise KeywordError(
            f"{bench.relative_to(ROOT)} has no '{SECTION_HEADING}' section — "
            f"run: python scripts/keyword_freq.py {slug}"
        )

    txt = BUILD / slug / f"{slug}.txt"
    if not txt.exists():
        raise KeywordError(f"no extracted CV text: {txt.relative_to(ROOT)}")
    body, skills = split_regions(txt.read_text(encoding="utf-8"))

    out = []
    for row in rows:
        if row["tier"] == "PERIPHERAL":
            continue
        status, note = classify(row["term"], aliases_for(row["term"]), body, skills)
        out.append({**row, "status": status, "note": note})
    return out


def render_coverage(slug: str, rows: list[dict]) -> str:
    total = len(rows)
    crit = [r for r in rows if r["tier"] == "CRITICAL"]
    crit_ok = [r for r in crit if r["status"] == "IN-BULLET"]

    lines = [
        f"# {slug} — keyword coverage",
        "",
        "<!-- generated by scripts/keyword_freq.py --coverage. Working notes for",
        "     the generating agent. NEITHER GRADER MAY READ THIS FILE: it is",
        "     derived from the answer key, and a grader that sees it scores our",
        "     analysis instead of the page. -->",
        "",
        f"CRITICAL terms in a substantive bullet: {len(crit_ok)}/{len(crit)}",
        f"Tracked terms (CRITICAL + IMPORTANT): {total}",
        "",
        "| Term | Count | Tier | Status | Note |",
        "|---|---|---|---|---|",
    ]
    rank = {s: i for i, s in enumerate(STATUS_ORDER)}
    for r in sorted(rows, key=lambda r: (rank[r["status"]], -r["count"])):
        lines.append(
            f"| {r['term']} | {r['count']} | {r['tier']} | {r['status']} | {r['note']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_coverage(text: str) -> dict[str, str]:
    """term -> status, from a previously written coverage file."""
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[3] not in STATUS_ORDER:
            continue
        out[cells[0]] = cells[3]
    return out


def coverage_regressions(previous: dict[str, str], rows: list[dict]) -> list[str]:
    """Terms that got weaker since the last build.

    This is the check that would have caught the SQL loss recorded in
    data-scientist_analysis.md, where a CRITICAL term was traded out of a bullet
    and cost 4 ATS points undetected for two iterations.
    """
    rank = {s: i for i, s in enumerate(STATUS_ORDER)}
    out = []
    for r in rows:
        was = previous.get(r["term"])
        if was is None or was not in rank:
            continue
        if rank[r["status"]] < rank[was]:
            out.append(
                f"{r['term']} ({r['tier']}, in {r['count']} listings) went "
                f"{was} -> {r['status']} since the last build"
            )
    return out


def run_coverage(slug: str) -> int:
    rows = compute_coverage(slug)
    path = coverage_path(slug)
    previous = parse_coverage(path.read_text(encoding="utf-8")) if path.exists() else {}

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_coverage(slug, rows), encoding="utf-8")

    for line in coverage_regressions(previous, rows):
        print(f"[warn] REGRESSION: {line}")
    weak = [r for r in rows if r["tier"] == "CRITICAL" and r["status"] != "IN-BULLET"]
    for r in weak:
        print(f"[warn] CRITICAL {r['term']!r} ({r['count']} listings): {r['status']}")
    print(f"[ok]   wrote {path.relative_to(ROOT)}")
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) < 2 or len(argv) > 3 or (len(argv) == 3 and argv[2] != "--coverage"):
        print(__doc__)
        return 2
    slug = argv[1]
    try:
        return run_coverage(slug) if len(argv) == 3 else write_table(slug)
    except KeywordError as exc:
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
