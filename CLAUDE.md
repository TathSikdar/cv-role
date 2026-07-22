# cv-role

Generates role-targeted CVs from a master CV, renders them with tectonic, and
grades them through ATS + recruiter review loops.

## Working here

- **To generate a CV, invoke the `cv-role` skill.** Do not improvise the
  pipeline — the skill carries the loop logic, thresholds, and grader isolation
  rules that make the output meaningful.
- **To write a cover letter, invoke the `cover-letter` skill.** It takes a CV
  slug and a listing URL, and writes against the *rendered CV plus the fetched
  listing only*. `config/master_cv.md` is out of scope there: the letter must
  argue for the story the accompanying CV actually tells.
- Never hand-edit `<slug>.tex`. It is generated. Edit `build/<slug>/content.yaml`
  and rerun `python scripts/build_cv.py <slug>`.
- **`config/frozen.yaml` is ground truth.** Education, company names, dates, and
  locations live there and are never rewritten to make a CV score better. If the
  build's frozen-fact verification fails, the generated content is wrong — not
  the frozen file.

## CV content rules (enforced by the build)

- **Experience bullets are designed from the keyword table, not retargeted from
  the master CV.** Each entry hosts one invented project that solves a problem
  the employer actually has; the bullets are that project's narrative. The
  project is invented, the anchors are not: `config/frozen.yaml` fixes each
  employer's real `domain`, the tenure, `level`, and the candidate's
  `technology_exposure`. See SKILL.md Step 2, tests T1 to T6.
- **Neither grader can detect fabrication.** Both are forbidden from reading the
  master CV or `content.yaml`, so an invented project with a plausible metric
  scores clean. Rising scores are not evidence the content is defensible.
- **No em or en dashes** anywhere in CV content. No `—`, `–`, `--`, or `---`.
- **Every bullet uses the XYZ method**: accomplished X, as measured by Y, by
  doing Z.
- **Every bullet renders as exactly two lines**, ideally running close to the end
  of the second. Measured from the PDF, not estimated.
- **The page must be full**: exactly one page, no bottom-margin overrun, no more
  than three blank lines trailing.
- **Bullets under one employer are written as a set**, not independently. Each
  entry's bullets must add up to one describable job.

## Cover letter rules (enforced by the build)

- **The letter never restates the CV.** A run of seven consecutive words shared
  with the rendered CV is a hard build failure; a sentence 60% similar to a CV
  line warns. The letter's content is the reasoning, motivation and fit that a
  bullet had no room for.
- **The CV is the evidence base and the ceiling.** The letter may explain
  anything on it and may claim nothing beyond it.
- **Never invent a fact about the employer.** Every claim about the company
  traces to text actually fetched this run.
- Same no-dash and LaTeX-escaping rules as the CV. First person is correct here.
- **The page is not required to be full**, unlike the CV. Only overrun fails.

## Keywords

Each role's benchmark carries a generated `## Keyword frequency` table: how many
listings demand each term, tiered CRITICAL / IMPORTANT / PERIPHERAL. Tier decides
what earns bullet space, and CRITICAL terms belong in bullets rather than the
skills list.

Regenerate it with `python scripts/keyword_freq.py <slug>` — never hand-edit the
table, and check both tiers before swapping one term for another.

## Layout

```
config/     master_cv.md, cv-template.tex, cover-letter-template.tex,
            cv-config.yaml, frozen.yaml, keyword-synonyms.yaml, job-listings/
scripts/    build_cv.py           — assemble, render, extract, verify
            build_cover_letter.py — same, for one listing's cover letter
            keyword_freq.py       — listing frequency table + CV coverage report
build/      per-role content.yaml, extracted PDF text, keyword-coverage.md,
            cover-letters/<id>.yaml
cover-letters/  rendered <slug>-<id>-cover-letter.tex / .pdf
./          <slug>.tex, <slug>.pdf, <slug>_analysis.md
```

`config/cv-config.yaml` is the file to edit between runs: seniority `level`,
which roles to generate, and loop thresholds.
