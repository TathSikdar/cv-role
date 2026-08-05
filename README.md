# cv-role

Reverse-engineer the perfect candidate. An AI agent that morphs a baseline CV
into elite benchmarks for specific job descriptions.

Given a master CV, it generates a role-targeted variant, renders it to PDF, then
grades it through two independent reviewers — an ATS parser and a human
recruiter — looping until it clears threshold or hits the iteration cap. Around
that sit the skills for everything downstream of a CV: tailoring it to one
posting, the cover letter, the application form, and interview prep.

## Setup

**Requirements:** `tectonic`, `pdftotext` (poppler-utils), Python 3 with `pyyaml`
and `pymupdf`.

Three files to create before the first run. Two are personal and gitignored, each
with a tracked `.example` beside it:

```bash
cp config/frozen.yaml.example config/frozen.yaml
cp config/master_cv.md.example config/master_cv.md
```

| File | What to put in it |
|---|---|
| `config/frozen.yaml` | **Ground truth.** Contact details, education, and each employer's real name, dates, location, and `domain`. Also `technology_exposure` — the closed set of technologies you may be described as having used — and `allowed_date_ranges`. Nothing here is ever rewritten to make a CV score better. |
| `config/master_cv.md` | Your real CV: work history, projects, skills. The source pool for projects and for deriving `technology_exposure`. Raw notes are fine. |
| `config/cv-config.yaml` | Already tracked — edit it. Set the seniority `level`, list the roles to generate, and tune the loop thresholds and layout budget. |

Everything else is generated. `config/job-listings/` fills itself on the first
`/cv-role` run.

## Skills

Invoke these in Claude Code. `<slug>` is a role from `config/cv-config.yaml`,
matched loosely (`data scientist`, `Data Scientist`, `data-scientist` all work).

| Skill | Invocation | What it does |
|---|---|---|
| `cv-role` | `/cv-role`<br>`/cv-role <slug>`<br>`/cv-role <slug> <n>` | Builds the role CV: designs bullets from the market's keyword frequencies, renders, and loops through the ATS and recruiter graders until both clear threshold. No argument builds every role; a trailing integer caps iterations for that run. |
| `us-version` | `/us-version <slug>` | Re-renders an existing role CV with the US contact line. Body identical, header only. |
| `job-cv` | `/job-cv <slug> <url>`<br>`/job-cv <slug> <url> us`<br>`/job-cv <slug> <job-id>` | Tailors a built CV to **one posting**: computes the skill gap against it and makes the minimal edits to close it. Fewest bullets changed wins. Claims every skill the posting requires — those claims live in the job CV only. |
| `cover-letter` | `/cover-letter <slug> <url>`<br>`/cover-letter <slug> <url> us`<br>`/cover-letter <slug> <letter-id>` | Writes and renders a letter in the CV's own template. Grounded in the rendered CV plus the fetched listing only; every figure in it must appear on the CV. |
| `application-questions` | `/application-questions <slug> <url>`<br>+ the questions, pasted | Answers a form's free-text screening questions ("why us", "tell us about a time") in the same voice, without reusing the cover letter's prose. No build step; markdown out. |
| `interview-hr` | `/interview-hr <slug> <url>` | Predicts the behavioral / recruiter-screen questions *this* application will draw, each with a prep note. Flags the soft signals a screener will pick at. |
| `interview-technical` | `/interview-technical <slug> <url>` | Predicts the technical-screen questions, and doubles as a defensibility audit: it says where the CV's story will crack under probing. |

Order of use: `/cv-role <slug>` once per role family, then per posting
`/job-cv` → `/cover-letter` → `/application-questions` → `/interview-hr` and
`/interview-technical`. Everything after `cv-role` needs that role's CV to exist
already.

To rebuild a CV after hand-editing `build/<slug>/content.yaml`:

```bash
python scripts/build_cv.py <slug>        # add `us` for the US header
```

Never hand-edit the generated `.tex`.

## Outputs

| Path | Contents |
|---|---|
| `base-cv/<slug>.pdf` / `.tex` | the rendered role CV and its generated source |
| `job-cv/<base>-<job-id>.pdf` | CVs tailored to one posting, plus `-notes.md` |
| `cover-letters/<slug>-<id>-cover-letter.pdf` | rendered letters |
| `build/<slug>/content.yaml` | generated content — the editable source |
| `build/<slug>/analysis.md` | full ATS + recruiter iteration history |
| `build/<slug>/keyword-coverage.md` | which benchmark terms landed and which slipped |
| `build/<slug>/interviews/<id>-hr.md` / `-technical.md` | interview prep sheets |
| `build/<slug>/application-answers/<id>.md` | application form answers |
| `config/job-listings/<slug>.md` | cached listings used as the fixed benchmark |

Every one of those directories is generated and gitignored; nothing is ever
written to the repo root. `build_cv.py` routes by slug — a role listed in
`config/cv-config.yaml` renders into `base-cv/`, anything else into `job-cv/`.
