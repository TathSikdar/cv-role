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
- **To tailor a built CV to one specific posting, invoke the `job-cv` skill.** It
  takes a base CV slug and a listing URL, computes the skill gap against that
  posting, makes the *minimal* edits to close it, and renders into `job-cv/`.
  Unlike `cv-role` it redesigns nothing: fewest bullets changed wins. It builds
  the perfect candidate for the posting, claiming every skill it requires; those
  claims live in the job CV only, never written back to `config/frozen.yaml`.
- **To prep for an interview on a built CV, invoke `interview-hr` (behavioral /
  recruiter screen) or `interview-technical` (technical screen).** Each takes a CV
  slug and a listing URL and generates the questions *that* application will face,
  each with a prep note. Same grounding law as the cover letter: rendered CV plus
  fetched listing only, never the master CV. `interview-technical` doubles as a
  defensibility audit — it flags where the invented projects will crack under
  probing.
- **Every CV and cover letter has a Canadian (default) and a US header.** The
  only difference is the line under the name — `contact_line` vs
  `contact_line_us` in `config/frozen.yaml`; the body is identical. Make the US
  CV with the `us-version` skill (`python scripts/build_cv.py <slug> us`, output
  `<slug>-us.pdf`); pick the US cover-letter header with the `region: us` input.
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

- **Nine rules govern the prose**, in `references/guidelines.md`, most of them
  enforced by `check_rules`. The load-bearing ones: lead with hard metrics, never
  lecture, never state a gap, never criticize how the business operates, never
  close by proposing to review their processes.
- **The letter never restates the CV.** A run of seven consecutive words shared
  with the rendered CV is a hard build failure. What the letter adds is
  *selection and relevance* (which results matter here), never methodology.
- **The CV is the evidence base and the ceiling.** Every figure in the letter
  must appear on the rendered CV. Never invent a metric.
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
            analysis.md, cover-letters/<id>.yaml
base-cv/    rendered <slug>.tex / .pdf for each role in cv-config.yaml
job-cv/     rendered <base>-<job-id>.tex / .pdf / -notes.md per posting
cover-letters/  rendered <slug>-<id>-cover-letter.tex / .pdf
```

**Nothing is generated in the repo root.** `build_cv.py` routes by slug: a slug
listed under `roles:` in `config/cv-config.yaml` renders into `base-cv/`,
anything else into `job-cv/`. All four generated directories are gitignored, as
are `config/frozen.yaml` and `config/master_cv.md` — both personal, both with a
tracked `.example` beside them.

`config/cv-config.yaml` is the file to edit between runs: seniority `level`,
which roles to generate, and loop thresholds.
