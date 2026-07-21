#!/usr/bin/env python3
"""Assemble, render, extract and verify a role-targeted CV.

    python scripts/build_cv.py <role-slug>

Reads:
    config/frozen.yaml              immutable facts (never generated)
    config/cv-template.tex          LaTeX template with {{PLACEHOLDER}} slots
    build/<slug>/content.yaml       generated titles / bullets / projects / skills

Writes:
    <slug>.tex                      root, per project convention
    <slug>.pdf                      root, rendered by tectonic
    build/<slug>/<slug>.txt         pdftotext extraction — what the ATS grader reads

Exits non-zero if the render fails or if any frozen fact was altered. The
generator never emits frozen fields in the first place; this is the backstop
that proves it, and it checks the *rendered PDF text* rather than the source,
so it also catches a fact mangled by LaTeX itself.
"""

from __future__ import annotations

import re
import shutil
import statistics
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
BUILD = ROOT / "build"

# Windows consoles default to cp1252 and would crash on accented names in
# diagnostics; force UTF-8 so failures print instead of raising.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# A month-year range anywhere in the document. Any match not present in
# frozen.yaml:allowed_date_ranges is an invented or stretched duration.
# No leading \b: a date abutting other glyphs (a rendering artifact, or a
# deliberate attempt to smuggle one past the check) must still be caught.
DATE_RANGE = re.compile(
    r"([A-Z][a-z]{2}\.?\s+\d{4})\s*[-–—]\s*([A-Z][a-z]{2}\.?\s+\d{4}|Present|Current)"
)


class BuildError(Exception):
    """Fatal problem — reported to the caller and aborts the build."""


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise BuildError(f"missing required file: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_content(slug: str) -> dict:
    return load_yaml(BUILD / slug / "content.yaml")


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def check_latex_hazards(where: str, text: str) -> list[str]:
    """Flag characters that silently corrupt LaTeX output or abort the render."""
    problems = []
    # A bare % comments out the rest of the line — content vanishes with no error.
    if re.search(r"(?<!\\)%", text):
        problems.append(f"{where}: unescaped '%' (use \\%)")
    # A bare & is an alignment tab; inside our tabular* it aborts the render.
    if re.search(r"(?<!\\)&", text):
        problems.append(f"{where}: unescaped '&' (use \\&)")
    # A bare # is a macro parameter token.
    if re.search(r"(?<!\\)#", text):
        problems.append(f"{where}: unescaped '#' (use \\#)")
    # A bare _ outside math mode is a subscript token and aborts the render.
    if re.search(r"(?<!\\)_", text.replace("$", "")):
        problems.append(f"{where}: unescaped '_' (use \\_)")
    # In text mode < and > render as inverted punctuation, not angle brackets —
    # silent corruption that survives to the PDF and the ATS extraction.
    if re.search(r"[<>]", re.sub(r"\$[^$]*\$", "", text)):
        problems.append(f"{where}: bare '<' or '>' (use $<$ / $>$)")
    # An odd number of unescaped $ leaves math mode open — usually a currency
    # figure that should have been \$.
    if len(re.findall(r"(?<!\\)\$", text)) % 2:
        problems.append(f"{where}: unbalanced '$' (currency must be \\$)")
    # Em and en dashes are banned outright in CV content. Both the literal
    # characters and the LaTeX ligatures (-- and ---) that render as them.
    if "—" in text or "–" in text:
        problems.append(
            f"{where}: em/en dash is not allowed — rewrite the clause "
            "(use a comma, colon, or separate sentence)"
        )
    if re.search(r"--", text):
        problems.append(
            f"{where}: '--' renders as an en/em dash, which is not allowed"
        )
    return problems


def bullets_latex(bullets: list[str], indent: str = "      ") -> str:
    lines = [f"{indent}\\resumeItemListStart"]
    for b in bullets:
        lines.append(f"{indent}  \\resumeItem{{{b.strip()}}}")
    lines.append(f"{indent}\\resumeItemListEnd")
    return "\n".join(lines)


def build_experience(frozen: dict, content: dict) -> tuple[str, list[str]]:
    """Join frozen company/dates/location with generated title/bullets.

    The generated content supplies no frozen field, so drift is impossible by
    construction. Order and membership are pinned to frozen.yaml.
    """
    problems: list[str] = []
    frozen_jobs = frozen.get("experience", [])
    gen_jobs = content.get("experience", [])

    frozen_ids = [j["id"] for j in frozen_jobs]
    gen_ids = [j.get("id") for j in gen_jobs]
    if gen_ids != frozen_ids:
        raise BuildError(
            "experience entries must match frozen.yaml exactly, in order.\n"
            f"  expected: {frozen_ids}\n"
            f"  got:      {gen_ids}\n"
            "Jobs may not be added, dropped, or reordered."
        )

    blocks = []
    for fz, gen in zip(frozen_jobs, gen_jobs):
        title = (gen.get("title") or "").strip()
        bullets = gen.get("bullets") or []
        if not title:
            raise BuildError(f"experience '{fz['id']}' has no title")
        if not bullets:
            raise BuildError(f"experience '{fz['id']}' has no bullets")

        problems += check_latex_hazards(f"experience[{fz['id']}].title", title)
        for i, b in enumerate(bullets):
            problems += check_latex_hazards(f"experience[{fz['id']}].bullets[{i}]", b)

        blocks.append(
            "    \\resumeSubheading\n"
            f"      {{{fz['company']}}}{{{fz['dates']}}}\n"
            f"      {{{title}}}{{{fz['location']}}}\n"
            + bullets_latex(bullets)
        )
    return "\n\n".join(blocks), problems


def build_projects(content: dict) -> tuple[str, list[str]]:
    problems: list[str] = []
    blocks = []
    projects = content.get("projects") or []
    if not projects:
        raise BuildError("content.yaml has no projects")

    for i, p in enumerate(projects):
        name = (p.get("name") or "").strip()
        tech = (p.get("tech") or "").strip()
        bullets = p.get("bullets") or []
        if not name:
            raise BuildError(f"projects[{i}] has no name")
        if not bullets:
            raise BuildError(f"project '{name}' has no bullets")

        problems += check_latex_hazards(f"projects[{i}].name", name)
        problems += check_latex_hazards(f"projects[{i}].tech", tech)
        for j, b in enumerate(bullets):
            problems += check_latex_hazards(f"projects[{i}].bullets[{j}]", b)

        heading = f"\\textbf{{{name}}}" + (f" $|$ \\emph{{{tech}}}" if tech else "")
        blocks.append(
            f"    \\resumeProjectHeading\n      {{{heading}}}{{}}\n"
            + bullets_latex(bullets)
        )
    return "\n\n".join(blocks), problems


def build_skills(content: dict) -> tuple[str, list[str]]:
    problems: list[str] = []
    groups = content.get("skills") or []
    if not groups:
        raise BuildError("content.yaml has no skills")

    lines = []
    for i, g in enumerate(groups):
        label = (g.get("label") or "").strip()
        items = (g.get("items") or "").strip()
        if not label or not items:
            raise BuildError(f"skills[{i}] needs both 'label' and 'items'")
        problems += check_latex_hazards(f"skills[{i}].items", items)
        lines.append(f"\\textbf{{{label}}}{{: {items}}}")
    return " \\\\\n".join(lines), problems


def build_education(frozen: dict, content: dict) -> str:
    """Frozen subheading, plus the coursework bullet unless the role drops it.

    The bullet's wording is frozen; only its presence is the generator's call.
    `education_bullet: false` in content.yaml omits it. See SKILL.md.
    """
    block = frozen.get("education_latex", "").rstrip()

    if content.get("education_bullet", True) is False:
        return block

    bullet = (frozen.get("education_bullet") or "").strip()
    if not bullet:
        return block

    return (
        f"{block}\n"
        f"    \\resumeItemListStart\n"
        f"      \\resumeItem{{{bullet}}}\n"
        f"    \\resumeItemListEnd"
    )


def render_template(frozen: dict, content: dict) -> tuple[str, list[str]]:
    template = (CONFIG / "cv-template.tex").read_text(encoding="utf-8")

    experience, p1 = build_experience(frozen, content)
    projects, p2 = build_projects(content)
    skills, p3 = build_skills(content)

    contact = frozen.get("contact", {})
    slots = {
        "NAME": contact.get("name", ""),
        "CONTACT_LINE": contact.get("contact_line", ""),
        "EMAIL_URL": contact.get("email_url", ""),
        "EMAIL_DISPLAY": contact.get("email_display", ""),
        "LINKEDIN_URL": contact.get("linkedin_url", ""),
        "LINKEDIN_DISPLAY": contact.get("linkedin_display", ""),
        "GITHUB_URL": contact.get("github_url", ""),
        "GITHUB_DISPLAY": contact.get("github_display", ""),
        "EDUCATION": build_education(frozen, content),
        "EXPERIENCE": experience,
        "PROJECTS": projects,
        "SKILLS": skills,
    }
    for key, value in slots.items():
        template = template.replace("{{" + key + "}}", str(value))

    leftover = re.findall(r"\{\{([A-Z_]+)\}\}", template)
    if leftover:
        raise BuildError(f"template placeholders left unfilled: {sorted(set(leftover))}")

    return template, p1 + p2 + p3


# --------------------------------------------------------------------------
# render + extract
# --------------------------------------------------------------------------

def run_tectonic(tex_path: Path) -> None:
    if not shutil.which("tectonic"):
        raise BuildError("tectonic not found on PATH")
    proc = subprocess.run(
        ["tectonic", "--keep-logs", str(tex_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or proc.stdout).strip().splitlines()[-25:])
        raise BuildError(f"tectonic failed:\n{tail}")


def run_pdftotext(pdf_path: Path, txt_path: Path) -> str:
    if not shutil.which("pdftotext"):
        raise BuildError("pdftotext not found on PATH (install poppler-utils)")
    # -enc UTF-8 is required: this poppler build otherwise emits Latin-1, which
    # corrupts accented characters in the text an ATS would ingest.
    proc = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(txt_path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise BuildError(f"pdftotext failed:\n{proc.stderr}")
    return txt_path.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Collapse layout whitespace so frozen strings can be matched literally."""
    return re.sub(r"[ \t ]+", " ", text)


def verify_frozen(frozen: dict, extracted: str, content: dict | None = None) -> list[str]:
    content = content or {}
    """Confirm every frozen fact survived generation and rendering intact."""
    failures: list[str] = []
    flat = normalize(extracted)

    for job in frozen.get("experience", []):
        for field in ("company", "dates", "location"):
            if job[field] not in flat:
                failures.append(
                    f"frozen {field} missing from rendered PDF: "
                    f"'{job[field]}' (job '{job['id']}')"
                )

    # Education is injected verbatim; confirm its facts survived the render.
    edu = frozen.get("education_latex", "")
    for literal in re.findall(r"\{([^{}\\]{4,})\}", edu):
        probe = literal.replace("\\&", "&").strip()
        if probe and probe not in flat:
            failures.append(f"frozen education text missing from rendered PDF: '{probe}'")

    # The coursework bullet may be dropped, but if the role kept it, its wording
    # is frozen: verify it rendered verbatim rather than reworded.
    if content.get("education_bullet", True) is not False:
        probe = (frozen.get("education_bullet") or "").replace("\\&", "&").strip()
        if probe and probe not in flat:
            failures.append(
                f"frozen education bullet missing from rendered PDF: '{probe}'"
            )

    # Scan with newlines collapsed too: a date range wrapped across two lines by
    # the renderer would otherwise slip past the allowlist.
    allowed = set(frozen.get("allowed_date_ranges", []))
    unwrapped = re.sub(r"\s+", " ", extracted)
    for match in DATE_RANGE.finditer(unwrapped):
        found = normalize(match.group(0)).replace("–", "-").replace("—", "-").strip()
        if found not in allowed:
            failures.append(
                f"unrecognized date range in rendered PDF: '{found}' "
                "— durations may not be invented or altered"
            )
    return failures


def measure_fit(pdf_path: Path, config: dict) -> tuple[list[str], str]:
    """Measure how well the content fills the page budget.

    Returns (failures, human-readable report). The CV must occupy exactly
    `max_pages` and leave no more than `max_trailing_blank_lines` of empty space
    at the bottom of the final page — too short reads as thin, too long spills.
    """
    import fitz  # pymupdf

    layout = config.get("layout") or {}
    max_pages = layout.get("max_pages", 1)
    max_blank = layout.get("max_trailing_blank_lines", 3)
    text_bottom = layout.get("text_bottom_pt", 744.0)

    doc = fitz.open(pdf_path)
    pages = doc.page_count

    def line_bounds(page) -> list[tuple[float, float]]:
        out = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                out.append((line["bbox"][1], line["bbox"][3]))
        return sorted(out)

    all_pitches: list[float] = []
    for pno in range(pages):
        bounds = line_bounds(doc[pno])
        all_pitches += [
            bounds[i + 1][1] - bounds[i][1]
            for i in range(len(bounds) - 1)
            if 0 < bounds[i + 1][1] - bounds[i][1] < 40
        ]
    pitch = statistics.median(all_pitches) if all_pitches else 13.0

    last_bounds = line_bounds(doc[pages - 1])
    last_bottom = last_bounds[-1][1] if last_bounds else 0.0
    doc.close()

    failures: list[str] = []

    if pages > max_pages:
        # Estimate how much has to come out: everything on the overflow pages.
        overflow_lines = max(1, round((last_bottom - 19.0) / pitch))
        failures.append(
            f"CV is {pages} pages; budget is {max_pages}. "
            f"Cut roughly {overflow_lines} lines "
            f"({overflow_lines * pitch:.0f}pt) of content."
        )
        report = f"{pages} pages (over budget by {pages - max_pages})"
    elif pages < max_pages:
        failures.append(f"CV is {pages} pages; budget is {max_pages}.")
        report = f"{pages} pages (under budget)"
    else:
        blank_lines = max(0.0, (text_bottom - last_bottom) / pitch)
        report = (
            f"{pages} page, content ends at {last_bottom:.0f}pt of {text_bottom:.0f}pt "
            f"usable, ~{blank_lines:.1f} blank lines trailing"
        )
        if last_bottom > text_bottom:
            # LaTeX will overfull a vbox rather than break, so a page can "fit"
            # while spilling into the bottom margin. That reads as cramped and
            # can clip on print.
            over = (last_bottom - text_bottom) / pitch
            failures.append(
                f"content overruns the text area by {last_bottom - text_bottom:.0f}pt "
                f"(~{over:.1f} lines) into the bottom margin. Cut "
                f"{max(1, round(over))}-{max(1, round(over)) + 1} lines."
            )
        elif blank_lines > max_blank:
            need = blank_lines - max_blank
            failures.append(
                f"~{blank_lines:.1f} blank lines at the bottom of the page; "
                f"maximum is {max_blank}. Add roughly {need:.0f}-{need + 1:.0f} "
                "more lines of content (a bullet is 1-2 lines)."
            )
    return failures, report


def measure_bullets(pdf_path: Path, config: dict) -> tuple[list[str], list[str], str]:
    """Measure every rendered bullet's line count and how full its last line is.

    A bullet must occupy exactly the configured number of rendered lines — three
    lines is a wall of text, one line wastes the row. The last line should run
    close to the right margin; a bullet ending a third of the way across line two
    reads as padded.

    Returns (failures, warnings, report).
    """
    import fitz  # pymupdf

    layout = config.get("layout") or {}
    min_lines, max_lines = layout.get("bullet_lines", [2, 2])
    target_fill = layout.get("bullet_target_fill", 0.65)

    doc = fitz.open(pdf_path)
    lines = []
    for pno in range(doc.page_count):
        for block in doc[pno].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"])
                lines.append((pno, line["bbox"][1], line["bbox"][0], line["bbox"][2], text))
    doc.close()
    lines.sort(key=lambda r: (r[0], r[1]))

    right_edge = layout.get("text_right_pt") or max((r[3] for r in lines), default=0.0)

    # Group each bullet with its continuation lines. Bullets open with U+2022;
    # continuations are indented further than the bullet's own left edge.
    bullets: list[dict] = []
    for _, _, x0, x1, text in lines:
        if text.startswith("•"):
            bullets.append({"x0": x0, "lines": 1, "last_x1": x1,
                            "text": text.lstrip("• ").strip()})
        # A continuation sits in a narrow indent band just right of the bullet.
        # Bounding it above matters: right-aligned date and location lines start
        # far to the right and would otherwise be absorbed into the bullet.
        elif bullets and bullets[-1]["x0"] + 3 <= x0 <= bullets[-1]["x0"] + 25:
            bullets[-1]["lines"] += 1
            bullets[-1]["last_x1"] = x1

    # The education coursework line is frozen content, not a generated bullet.
    bullets = [b for b in bullets if not b["text"].startswith("Coursework:")]

    failures, warnings = [], []
    fills = []
    for b in bullets:
        snippet = b["text"][:60] + ("..." if len(b["text"]) > 60 else "")
        if b["lines"] > max_lines:
            failures.append(
                f"bullet runs {b['lines']} lines (max {max_lines}): \"{snippet}\" "
                "— shorten it"
            )
        elif b["lines"] < min_lines:
            failures.append(
                f"bullet runs {b['lines']} line (min {min_lines}): \"{snippet}\" "
                "— extend it toward the end of line 2"
            )
        else:
            denom = right_edge - (b["x0"] + 9.3)
            fill = (b["last_x1"] - (b["x0"] + 9.3)) / denom if denom > 0 else 1.0
            fills.append(fill)
            if fill < target_fill:
                warnings.append(
                    f"bullet's last line is only {fill:.0%} full "
                    f"(target {target_fill:.0%}): \"{snippet}\" — add detail"
                )

    avg = f"{statistics.mean(fills):.0%}" if fills else "n/a"
    report = f"{len(bullets)} bullets, mean last-line fill {avg}"
    return failures, warnings, report


def check_divergence(content: dict, master_path: Path) -> list[str]:
    """Warn where a generated bullet is nearly a copy of a master CV bullet.

    A role-targeted CV that reuses the master's phrasing has not actually been
    retargeted, and both graders will score it as generic.
    """
    if not master_path.exists():
        return []
    master_bullets = [
        line.lstrip("- ").strip()
        for line in master_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("- ")
    ]
    if not master_bullets:
        return []

    def strip_latex(s: str) -> str:
        s = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", s)
        s = re.sub(r"[\\${}]", "", s)
        return " ".join(s.lower().split())

    master_norm = [strip_latex(b) for b in master_bullets]
    warnings: list[str] = []
    for job in content.get("experience", []):
        for i, bullet in enumerate(job.get("bullets", [])):
            probe = strip_latex(bullet)
            best = max(
                (SequenceMatcher(None, probe, m).ratio() for m in master_norm),
                default=0.0,
            )
            if best >= 0.75:
                warnings.append(
                    f"experience[{job['id']}].bullets[{i}] is {best:.0%} identical "
                    "to a master CV bullet — retarget it for this role"
                )
    return warnings


# --------------------------------------------------------------------------
# XYZ structure
# --------------------------------------------------------------------------

# Past-tense achievement verbs that do not end in -ed. Anything ending in -ed is
# accepted without listing it, so this only has to cover the irregulars that
# actually open CV bullets.
IRREGULAR_VERBS = {
    "built", "cut", "led", "ran", "wrote", "drove", "grew", "won", "made",
    "found", "held", "set", "sped", "took", "brought", "caught", "taught",
    "sent", "kept", "split", "chose", "rose", "fell", "shrank", "beat", "met",
    "rebuilt", "shipped", "swept", "spun", "dealt", "put", "left", "began",
}

# Connectors that introduce the mechanism (Z). Deliberately permissive: the
# mechanism may be a gerund clause ("by building a pipeline") or a plain noun
# phrase ("with Optuna Bayesian search"), and distinguishing a real mechanism
# from a passing preposition is not something a regex can do honestly. This
# catches the bullet that states an outcome and stops.
MECHANISM = re.compile(
    r"\b(by|through|via|using|utilizing|leveraging|after|with|from)\b", re.I
)

# Y does not have to be a figure. The rule allows "a verifiable qualitative
# outcome ... never a vague intensifier", so these are the constructions that
# state an outcome a reader could check: a thing eliminated, prevented, ruled
# out, or confirmed. Matching one downgrades a missing figure to a warning.
#
# This exists because the diagnostic bullets that legitimately carry no
# percentage are the ones the recruiter rubric rewards as most credible, and a
# hard failure was pushing them toward manufactured metrics — which the same
# rubric then penalizes as uniform win magnitude.
QUALITATIVE_OUTCOME = re.compile(
    r"\b(to (eliminate|prevent|avoid|confirm|rule out|surface|catch|hold)"
    r"|without|before (release|anyone|it)|so (that|a|it)"
    r"|eliminating|preventing|ruling out|confirming)\b",
    re.I,
)


def check_xyz(content: dict) -> tuple[list[str], list[str]]:
    """Check every bullet for XYZ structure: accomplished X, measured by Y, doing Z.

    Returns (failures, warnings).

    Y and Z are hard failures because their absence is unambiguous — a bullet
    with no figure anywhere in it has no measure, and one with no mechanism
    connector never says how. X is a warning only: whether the opening word is
    a genuine achievement verb is a judgement the graders make better than a
    word list does.

    Known limitation: Y is satisfied by any digit, so an incidental number
    ("Day-7", "two-stage") passes. Deliberate — a false pass costs a grader
    comment, a false failure blocks a build on a correct bullet.
    """
    failures: list[str] = []
    warnings: list[str] = []

    def bullets() -> list[tuple[str, str]]:
        out = []
        for job in content.get("experience", []):
            for i, b in enumerate(job.get("bullets", [])):
                out.append((f"experience[{job.get('id')}].bullets[{i}]", b))
        for j, proj in enumerate(content.get("projects", [])):
            for i, b in enumerate(proj.get("bullets", [])):
                out.append((f"projects[{j}].bullets[{i}]", b))
        return out

    for where, bullet in bullets():
        # Strip \textbf{...} and stray LaTeX so markup neither hides a figure
        # nor supplies a false one.
        plain = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", bullet)
        plain = re.sub(r"[\\${}^]", "", plain).strip()
        excerpt = plain[:60] + ("..." if len(plain) > 60 else "")

        if not re.search(r"\d", plain):
            if QUALITATIVE_OUTCOME.search(plain):
                warnings.append(
                    f"{where}: no figure, carried by a qualitative outcome "
                    f"instead (Y): \"{excerpt}\"\n"
                    "      fine if no number genuinely exists; confirm it is "
                    "not a vague intensifier"
                )
            else:
                failures.append(
                    f"{where}: no quantified result (Y): \"{excerpt}\"\n"
                    "      add a metric, or a verifiable qualitative outcome"
                )
        if not MECHANISM.search(plain):
            failures.append(
                f"{where}: no mechanism clause (Z): \"{excerpt}\"\n"
                "      say how it was done (by/through/using ...)"
            )

        first = re.sub(r"[^a-z]", "", plain.split(" ")[0].lower()) if plain else ""
        if first and not first.endswith("ed") and first not in IRREGULAR_VERBS:
            warnings.append(
                f"{where}: does not open with a past-tense achievement verb "
                f"(X): \"{excerpt}\""
            )

    return failures, warnings


# --------------------------------------------------------------------------
# keyword coverage
# --------------------------------------------------------------------------

def report_keyword_coverage(slug: str) -> None:
    """Warn on weak or regressed keyword coverage. Never fails the build.

    Advisory by design. Coverage is a judgement about what the CV should spend
    its space on, and a term can be legitimately absent because claiming it
    would be a lie — that decision belongs to the generating agent and the
    grader, not to the renderer. What the build CAN do cheaply is notice when a
    high-frequency term silently got weaker between two iterations, which has
    happened here before and cost four ATS points undetected for two rounds.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import keyword_freq

    try:
        rows = keyword_freq.compute_coverage(slug)
    except keyword_freq.KeywordError as exc:
        # An old-format benchmark with no frequency table, or none at all. Not
        # a build problem; the skill rebuilds it on the next run of this role.
        print(f"[info] keyword coverage skipped: {exc}")
        return

    path = keyword_freq.coverage_path(slug)
    previous = (
        keyword_freq.parse_coverage(path.read_text(encoding="utf-8"))
        if path.exists() else {}
    )

    for line in keyword_freq.coverage_regressions(previous, rows):
        print(f"[warn] KEYWORD REGRESSION: {line}")

    weak = [r for r in rows if r["tier"] == "CRITICAL" and r["status"] != "IN-BULLET"]
    for r in weak:
        detail = f" — {r['note']}" if r["note"] else ""
        print(f"[warn] CRITICAL keyword {r['term']!r} ({r['count']} listings): "
              f"{r['status']}{detail}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(keyword_freq.render_coverage(slug, rows), encoding="utf-8")

    crit = [r for r in rows if r["tier"] == "CRITICAL"]
    covered = len(crit) - len(weak)
    print(f"[info] keyword coverage: {covered}/{len(crit)} CRITICAL terms in a "
          f"bullet — detail in {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    slug = argv[1]

    try:
        frozen = load_yaml(CONFIG / "frozen.yaml")
        config = load_yaml(CONFIG / "cv-config.yaml")
        content = load_content(slug)
        tex, hazards = render_template(frozen, content)
    except BuildError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if hazards:
        print("[FAIL] unescaped LaTeX characters in generated content:")
        for h in hazards:
            print(f"  - {h}")
        return 1

    # Checked before rendering: this is a content rule, so there is no reason to
    # spend a tectonic run proving a bullet that is already malformed.
    xyz_failures, xyz_warnings = check_xyz(content)
    for w in xyz_warnings:
        print(f"[warn] {w}")
    if xyz_failures:
        print("[FAIL] XYZ structure:")
        for f in xyz_failures:
            print(f"  - {f}")
        print("\nEvery bullet: accomplished X, as measured by Y, by doing Z.")
        return 1

    tex_path = ROOT / f"{slug}.tex"
    pdf_path = ROOT / f"{slug}.pdf"
    out_dir = BUILD / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / f"{slug}.txt"

    tex_path.write_text(tex, encoding="utf-8")
    print(f"[ok]   wrote {tex_path.name}")

    try:
        run_tectonic(tex_path)
        print(f"[ok]   rendered {pdf_path.name}")
        extracted = run_pdftotext(pdf_path, txt_path)
        print(f"[ok]   extracted {txt_path.relative_to(ROOT)} ({len(extracted)} chars)")
    except BuildError as exc:
        print(f"[FAIL] {exc}")
        return 1

    report_keyword_coverage(slug)

    failures = verify_frozen(frozen, extracted, content)
    if failures:
        print("[FAIL] frozen-fact verification failed:")
        for f in failures:
            print(f"  - {f}")
        print("\nFix content.yaml — do NOT edit config/frozen.yaml to make this pass.")
        return 1
    print("[ok]   frozen facts verified against rendered PDF text")

    for w in check_divergence(content, CONFIG / "master_cv.md"):
        print(f"[warn] {w}")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from measure_spacing import analyze as analyze_spacing

    spacing = analyze_spacing(pdf_path)
    spacing_failures = []
    if spacing.inter <= spacing.intra:
        spacing_failures.append(
            f"bullet line spacing is inverted: gaps inside a bullet "
            f"({spacing.intra:.1f}pt) are >= gaps between bullets "
            f"({spacing.inter:.1f}pt), so pdftotext splits every wrapped bullet "
            "into two paragraphs. Fix \\resumeItem in cv-template.tex."
        )
    for gap, txt in spacing.anomalies:
        spacing_failures.append(
            f"anomalous {gap:.1f}pt gap before {txt!r} — an empty line box, "
            "usually a stray space before \\vspace in the template"
        )

    bullet_failures, bullet_warnings, bullet_report = measure_bullets(pdf_path, config)
    print(f"[info] bullets: {bullet_report}")
    for w in bullet_warnings:
        print(f"[warn] {w}")

    fit_failures, fit_report = measure_fit(pdf_path, config)
    print(f"[info] page fit: {fit_report}")

    if spacing_failures:
        print("[FAIL] line spacing:")
        for f in spacing_failures:
            print(f"  - {f}")
    if bullet_failures:
        print("[FAIL] bullet length:")
        for f in bullet_failures:
            print(f"  - {f}")
    if fit_failures:
        print("[FAIL] page fit:")
        for f in fit_failures:
            print(f"  - {f}")
    if spacing_failures or bullet_failures or fit_failures:
        return 1
    print(f"[ok]   spacing (intra {spacing.intra:.1f}pt < inter "
          f"{spacing.inter:.1f}pt), bullet lengths, and page fit all within budget")

    print(f"\nBuild complete: {slug}.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
