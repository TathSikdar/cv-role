# cv-role

Reverse-engineer the perfect candidate. An AI agent that morphs a baseline CV
into elite benchmarks for specific job descriptions.

Given a master CV, it generates a role-targeted variant, renders it to PDF, then
grades it through two independent reviewers — an ATS parser and a human
recruiter — looping until it clears threshold or hits the iteration cap.

## Usage

Edit `config/cv-config.yaml` to set the seniority `level` and pick roles, then in
Claude Code:

```
/cv-role                    # every role in the config
/cv-role backend-developer  # a single role
```

To rebuild a CV after hand-editing its content:

```bash
python scripts/build_cv.py <slug>
```

## Outputs

| Path | Contents |
|---|---|
| `<slug>.pdf` / `<slug>.tex` | the rendered CV and its generated source |
| `<slug>_analysis.md` | full ATS + recruiter iteration history |
| `build/<slug>/content.yaml` | generated content — the editable source |
| `config/job-listings/<slug>.md` | cached listings used as the fixed benchmark |

## How it stays honest

- **Frozen facts.** Education, company names, dates, and locations live in
  `config/frozen.yaml` and are injected directly into the LaTeX. The generator
  never emits them, so it cannot drift them — and the build re-verifies every one
  against the *rendered PDF text* afterward, including an allowlist check that
  catches any invented duration.
- **Isolated graders.** Both reviewers run as subagents with fresh context, given
  only the extracted CV text, the rubric, and the listings — never the master CV
  or the generation reasoning. A grader that can see your intent scores it
  instead of the page.
- **Extracted text, not source.** The ATS grader reads `pdftotext` output, which
  is what real applicant tracking systems parse. This catches column scrambling,
  encoding damage, and dropped glyphs that reading the LaTeX would miss.
- **Fixed benchmark.** Listings are cached per role and reused across iterations,
  so a score change reflects the CV changing and nothing else.
- **Measured page fit.** The build reads real PDF geometry and fails unless the
  CV fills exactly one page — too long, spilling into the bottom margin, or more
  than three blank lines at the bottom all block the build and report how many
  lines to add or cut.
- **Measured bullet length.** Every bullet must render as exactly two lines, and
  the build reports how full each second line is. No em or en dashes are allowed
  anywhere in CV content.
- **XYZ bullets.** Every bullet follows "accomplished X, as measured by Y, by
  doing Z", and both rubrics score against that structure.
- **Divergence check.** Any bullet that is ≥75% identical to a master CV bullet
  is flagged, so a "retargeted" CV cannot just be the master with keywords swapped.
- **Bounded loop.** Stops at threshold or `max_iterations`, and aborts on a
  regression larger than `regression_abort_delta`.

## Requirements

`tectonic`, `pdftotext`, Python 3 with `pyyaml` and `pymupdf`.
