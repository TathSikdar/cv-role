---
name: job-cv
description: Adapt an already-built role CV to one specific job posting, changing as little as possible so it covers every skill that posting requires but the CV is missing. Builds the perfect candidate for that posting by claiming every required skill. Takes a base CV slug and a listing URL, fetches the posting, computes the skill gap, makes the minimal edits to close it, and renders the result into the job-cv/ folder. Use when asked to tailor, target, or adapt a CV to a specific job description or posting URL.
---

# job-cv

Takes a CV that already exists for a role family and points it at **one specific
posting**. The goal is the perfect candidate *for that job*: every skill the
posting requires is covered, and nothing else about the CV moves.

This is the opposite discipline from `cv-role`. `cv-role` designs a CV outward
from a whole market's keyword frequencies and redesigns every bullet from
scratch. Here the base CV is already good; the job is a **surgical diff** against
one posting. Change the fewest bullets, add the fewest skills, keep everything
else byte-for-byte identical. The measure of a good run is how little changed.

The evidence base is exactly two things: the **rendered base CV**
(`build/<base>/<base>.txt`) and the **fetched posting**. Never read
`config/master_cv.md` here.

## Invocation

- `/job-cv <base-slug> <listing-url>` — tailor that CV to that posting
- `/job-cv <base-slug> <listing-url> us` — same, with the US header
- `/job-cv <base-slug> <job-id>` — rebuild or revise an existing job CV

**Parsing the argument.** An argument containing `://` or starting `www.` is the
listing URL; a bare `us` (or `ca`/`canada`) is the header region; anything else
is a `job-id` naming an existing job CV under `build/<base>-<job-id>/`. Match the
base slug loosely against `config/cv-config.yaml`, the same way `cv-role` does.

**The base CV must already be built.** This skill adapts `build/<base>/content.yaml`
and reads `build/<base>/<base>.txt`. If either is missing, stop and tell the user
to build it first with `/cv-role <base-slug>`. This skill never designs a CV from
nothing — that is `cv-role`'s job and its grading is what makes content
defensible.

`job-id` is derived from the company on first run: lowercase, hyphenated, no
legal suffix (`Acme Robotics Inc.` becomes `acme-robotics`). The job CV's slug is
`<base>-<job-id>` (e.g. `ai-ml-engineer-acme-robotics`). If that slug already
exists, append the role (`ai-ml-engineer-acme-robotics-ml`).

---

## What may and may not change

Everything `cv-role` freezes is still frozen — this skill inherits every rule
`scripts/build_cv.py` enforces (frozen facts, XYZ, two-line bullets, full page,
no dashes). On top of that, this skill adds its own restraint:

| Element | Rule |
|---|---|
| Employer names, dates, locations, order, education | **Frozen**, same as always. |
| Bullets the posting does not touch | **Left identical to the base CV.** Do not "improve" a bullet the gap analysis did not flag. |
| Skills list | Add missing required skills; never remove what is there. |
| Bullets covering a required-but-missing skill | Minimally edited to name it, or one term swapped in. Never rewritten wholesale, never given a new invented metric. |
| Projects, titles | Untouched unless a required skill has no other honest home. |

**Minimal change is the whole point.** A job CV that rewrote half the base CV is
a failed run even if it scores well: it means the diff was not surgical, and the
base CV's graded, defensible content was thrown away for no reason.

---

## Step 1 — Fetch the posting

Fetch the URL with WebFetch. Extract and keep:

- company, exact title, location
- **every concrete technology, framework, platform, protocol, method, and named
  tool the posting asks for** — the same kind of list `keyword_freq` parses, one
  comma-separated set. Pull these out even when buried in prose.
- which of those the posting signals as **central**: named in the title, listed
  under "required" / "must have", or repeated. These are the ones that earn a
  bullet edit; the rest can live in the skills list.

**If the fetch fails or returns boilerplate** (common on JS-heavy boards), try a
WebSearch for the company plus exact title on another host. If that also fails,
stop and ask the user to paste the posting. Never invent a requirement from the
URL slug — every skill you add must trace to text actually retrieved this run.

## Step 2 — Compute the gap

Read `build/<base>/<base>.txt` (the rendered CV — what a parser actually sees)
and `build/<base>/content.yaml` (to know which bullet carries what).

- **Covered** = every technology already named in a bullet or the skills list.
- **Required** = the posting's technology set from Step 1.
- **Gap** = Required minus Covered. This is the only thing that changes.

If the gap is empty, say so and stop — the base CV already covers this posting;
there is nothing to tailor. (Still render a copy into `job-cv/` if the user wants
the pair of files for this application; otherwise just point them at
`base-cv/<base>.pdf`.)

**Claim every gap term.** This skill builds the perfect candidate for the
posting, so any skill it requires gets claimed regardless of whether the base CV
ever held it. There is no exposure boundary to respect here.

`build_cv.py`'s `check_exposure` warns on any skill named in a bullet that is not
in `config/frozen.yaml: technology_exposure`. Those warnings are expected and
harmless — they do not fail the build. Leave `config/frozen.yaml` alone (it is
shared by every role CV; a claim for this posting belongs in this job CV only,
not written back into everyone's ground truth).

## Step 3 — Make the minimal edits

Copy `build/<base>/content.yaml` to `build/<base>-<job-id>/content.yaml`, then
change only what the gap requires, cheapest placement first:

1. **Skills list.** Every gap term goes into the right existing skills group as a
   single word. This alone covers most gaps and costs nothing.
2. **Bullet evidence, for central terms only.** For each gap term the posting
   signals as central (Step 1), the skills list is not enough — both a recruiter
   and the ATS want it evidenced. Name it in the **one** most plausible existing
   bullet: swap it in for a weaker term, or extend the bullet by one clause. Keep
   XYZ, keep two rendered lines, invent no new metric.
3. **New content only as a last resort.** Add a bullet or a project only if a
   central required skill has no honest home in any existing bullet. This is rare;
   prefer a term swap.

Touch nothing the gap did not name. Every edit should be traceable to one gap
term.

## Step 4 — Build

```bash
python scripts/build_cv.py <base>-<job-id>
```

Add `us` as a second argument for the US header. A non-zero exit is a hard stop:
fix `content.yaml` and rebuild. Adding skills can push a line and break page fit
or a bullet's two-line rule — this is the same Step 3 sub-loop as `cv-role`; loop
until it passes.

Expect two harmless notices: `check_exposure` warns on any newly claimed skill
not in `technology_exposure` (Step 2), and keyword coverage is skipped because a
single posting has no `config/job-listings/` benchmark. Neither is an error.

`build_cv.py` renders straight into `job-cv/`: any slug that is not a role in
`config/cv-config.yaml` is a job CV, and base CVs go to `base-cv/`. Nothing is
written to the repo root and nothing needs moving afterwards. For a US build the
files are `job-cv/<base>-<job-id>-us.tex` / `.pdf`.

## Step 5 — Change log

Write `job-cv/<base>-<job-id>-notes.md` so the diff against the base CV is
readable at a glance:

```markdown
# <base> → <Company> <Title> — tailoring notes
<!-- <date> | source: <fetched | pasted | found via search> | <url> -->

## Required by the posting
<comma-separated technology set pulled in Step 1>

## Already covered by the base CV
<the terms that needed no change>

## Added to close the gap
| Term | Central? | Placement |
|---|---|---|
| TensorFlow | yes | swapped into nestle bullet 1 |
| Terraform  | no  | skills: Platforms          |
```

## Step 6 — Report

Give the user: output path (`job-cv/<base>-<job-id>.pdf`), the company and title,
how many bullets changed (fewer is better), and the skills added. If the gap was
empty, say the base CV already fits and no tailoring was needed.

---

## Output map

| Path | Contents |
|---|---|
| `build/<base>-<job-id>/content.yaml` | tailored content (the editable source, a minimal diff of the base) |
| `build/<base>-<job-id>/<base>-<job-id>.txt` | extracted text |
| `job-cv/<base>-<job-id>.tex` | generated LaTeX |
| `job-cv/<base>-<job-id>.pdf` | rendered job-targeted CV |
| `job-cv/<base>-<job-id>-notes.md` | the gap analysis and change log |
