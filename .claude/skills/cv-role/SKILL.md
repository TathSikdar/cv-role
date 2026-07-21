---
name: cv-role
description: Generate a role-targeted CV from the master CV, render it to PDF with tectonic, then grade it through isolated ATS and recruiter review loops until it clears the configured thresholds. Use when asked to build, regenerate, or improve a CV for a specific role, or when asked what a perfect candidate for a role looks like.
---

# cv-role

Reverse-engineers the ideal candidate for a role family. Takes the master CV,
rewrites everything that is allowed to change, renders a real PDF, and pushes it
through two independent graders until it clears threshold or runs out of
iterations.

## Invocation

- `/cv-role` — every role in `config/cv-config.yaml`
- `/cv-role <slug>` — one role (`/cv-role backend-developer`)

## Before starting

Read `config/cv-config.yaml`. It supplies `level`, the role list, loop
thresholds, and layout budgets. Everything below is driven by it — do not
hardcode a threshold or an iteration count.

Process roles one at a time, start to finish. Do not interleave.

---

## What may and may not change

Non-negotiable, and enforced mechanically by `scripts/build_cv.py`:

| Element | Rule |
|---|---|
| Education | **Frozen.** Injected verbatim from `config/frozen.yaml`. Never touched. |
| Company names, dates, locations | **Frozen.** Injected from `config/frozen.yaml`. You never write them. |
| Number and order of jobs | **Frozen.** No adding, dropping, or reordering. |
| Position titles | Free — retarget to the role's vocabulary. |
| Experience bullets | Free — rewrite completely for the role. |
| Projects | Free rein. Reuse from the master CV, adapt, or invent something that would impress for this role. |
| Skills | Free rein, including technologies not on the master CV. |

Bullets must remain grounded in work that plausibly happened at that company in
that timeframe at that level. Reframing an agent-orchestration project as a
backend-systems project is the intent. Inventing a job that never happened is
not, and the recruiter rubric penalizes it hard under seniority credibility.

---

## Step 1 — Ensure the listings benchmark exists

Check `config/job-listings/<slug>.md`.

If it is missing (or `listings.refresh` is true), build it: use WebSearch with
the role's `search_terms` plus the configured `level`, gather `listings.per_role`
real postings, and write the file as one `##` section per listing containing
company, title, and the requirements and responsibilities text verbatim. Do not
paraphrase — the ATS grader extracts keywords from this text and paraphrasing
launders exactly the vocabulary being measured.

Warn and continue if you can only gather `listings.min_required`; below that,
stop and tell the user.

**These listings are cached and reused across every iteration and every rerun.**
That is what makes scores comparable between iterations — if the benchmark moved,
a score change would tell you nothing about the CV.

---

## Step 2 — Generate content

Read `config/master_cv.md` and the listings. Write `build/<slug>/content.yaml`
per the schema in `references/latex.md`.

**Treat the master CV as raw material, not as a draft to lightly edit.** The
single most common failure of this pipeline is copying master bullets across with
a few keywords swapped in. That produces a CV that reads as generic to the
recruiter grader and wastes iterations. The build enforces this: any bullet ≥75%
textually identical to a master bullet is flagged.

Work bullet by bullet:

1. From the listings, extract what this role is actually screened on — the
   responsibilities that recur, not just the technology nouns.
2. For each job, ask what that same work looks like *through this role's lens*.
   The Nestlé multi-agent system is an orchestration problem to an agent
   developer, a distributed-systems and API problem to a backend developer, a
   pipeline and evaluation problem to an ML engineer. Same underlying work, a
   different layer of it made the subject of the sentence.
3. Rewrite the bullet around that layer, with the mechanism a practitioner in
   this role would care about. Change the verb, the object, and the detail — not
   just the technology names.
4. Drop material that does not serve the role, and surface master-CV work that
   was buried. Bullet counts need not match the master.

### Every position must read as role-family experience

The most common way this pipeline produces weak output: recent jobs get
retargeted properly while an older, unrelated position is left nearly untouched,
so the CV carries a block of bullets that do nothing for the role.

**Retitle and rewrite every position, including ones whose real work sits
outside the role family.** Titles are free. If the master CV says "Mobile
Developer" and the target is agent development, the title becomes "AI Developer
Co-op" and the bullets describe the AI-adjacent work that plausibly existed in
that job: an in-app recommendation feature, an on-device inference path, an
LLM-backed support flow, a data pipeline feeding a model.

Apply this test to every bullet: **if it were deleted, would the CV be weaker
for this specific role?** If not, it does not belong. A bullet about Figma
handoff or design-token consistency is dead weight on an agent developer CV no
matter how well written it is.

The constraint that still holds: bullets must describe work that could plausibly
have happened at that company, in that timeframe, at that level. You choose
which layer of a real job to make the subject. You do not relocate a project
from one employer to another, and you do not invent a job that never happened.

### Cover the role's skill surface across the bullets

Treat the recurring listing requirements as a checklist. Across the positions
and projects, the bullets should collectively demonstrate most of them in
context rather than parked in the skills list. Anything central to the role
appearing only under Technical Skills is a gap that both rubrics penalize: the
ATS as SKILLS-ONLY coverage, the recruiter as unevidenced skills that will not
survive a phone screen.

Distribute coverage across positions rather than loading every keyword into the
most recent one. A candidate whose role-relevant work spans three employers
reads stronger than one with a single relevant job and two unrelated ones.

Also free: choose projects that reinforce the role story rather than showing
range, and group skills the way the listings group them.

### Write every bullet with the XYZ method

**"Accomplished X, as measured by Y, by doing Z."** Every experience and project
bullet follows this. Lead with the outcome, name the measure, then the mechanism.

> Cut competitor research turnaround from days to minutes and unlocked **$750K**
> in annual savings **[X, Y]** by building a production multi-agent system that
> coordinates six specialized agents across web and email sources **[Z]**.

Rules that follow from it:

- **X is a result, not a task.** "Built a pipeline" is a task. "Cut turnaround
  from days to minutes" is a result.
- **Y is concrete.** A percentage, dollar figure, latency, scale, or throughput.
  If a number genuinely does not exist, use a verifiable qualitative outcome
  ("without human escalation", "before release"), never a vague intensifier.
- **Z carries the technical substance** that makes the claim credible and holds
  the role's keywords. This is where the reader decides whether you did the work.
- Do not open every bullet with the same verb or force an identical
  X-Y-Z rhythm throughout. The recruiter rubric penalizes bullets that share one
  skeleton as machine-generated. Vary the construction while keeping all three
  elements present.

### Never use em dashes or en dashes

Not in bullets, titles, project names, or skills. No `—`, no `–`, and no `--` or
`---` (which LaTeX renders as dashes). Use a comma, a colon, parentheses, or
split the sentence. The build fails on any of them.

### Every bullet must render as exactly two lines

Measured from the PDF, not estimated from character count. Three lines is a wall
of text a recruiter skips; one line wastes the row. The sweet spot is a bullet
that runs close to the end of the second line, so aim to fill it past
`layout.bullet_target_fill`.

Roughly 200 to 230 characters lands on two full lines in this template, but bold
markup changes the width, so let the build tell you. Filling line two more fully
costs no vertical space, so a short second line should always be extended with
real detail rather than left padded with whitespace.

Calibrate scope language to `level` — see the seniority anchors in
`references/ats-rubric.md`. Overclaiming is penalized as hard as underclaiming.

Aim initially for the `layout` targets in `config/cv-config.yaml`; Step 3 will
tell you exactly how much to add or cut.

---

## Step 3 — Build

```bash
python scripts/build_cv.py <slug>
```

Produces `<slug>.tex`, `<slug>.pdf`, and `build/<slug>/<slug>.txt`.

**A non-zero exit is a hard stop.** Fix `content.yaml` and rebuild. Never edit
`config/frozen.yaml` to make verification pass, and never grade a CV that did not
build.

### Filling the page exactly

The build measures real PDF geometry and fails unless:

- the CV occupies exactly `max_pages`, with no more than
  `max_trailing_blank_lines` of empty space at the bottom and no overrun into the
  bottom margin
- every bullet renders as exactly two lines

It reports the gap in lines and tells you how many to add or cut, and it names
each bullet whose last line falls short of the fill target. Loop on Step 3 until
it passes — this is a sub-loop, not something to defer to the graders.

Note that bullet fill and page fit are independent: a bullet occupies two lines
whether its second line is 40% or 90% full, so extending a short bullet improves
density without costing page space.

A partially filled page is a failure, not an acceptable outcome. It reads as a
thin candidate regardless of content quality, and the recruiter rubric penalizes
it under the six-second scan.

**Too sparse — add, in this order:**
1. A bullet to the most role-relevant job (highest value; targets ATS keyword
   coverage at the same time)
2. An additional project
3. A bullet to an existing project
4. A further skills group

**Overflowing — cut, in this order:**
1. The weakest bullet from the oldest or least relevant job
2. The weakest project bullet
3. An entire lower-value project
4. Tighten wordy bullets to two rendered lines

Never adjust margins, font size, or `\vspace` to force a fit. Those changes are
invisible to the ATS rubric, hurt human readability, and invalidate the measured
`text_bottom_pt`.

A warning that a bullet is ≥75% identical to a master CV bullet is not
cosmetic — rewrite it per Step 2 before proceeding to grading.

---

## Step 4 — Grade, in isolation

Run both graders as **subagents with fresh context**. This is the most important
mechanic in the system: a grader that can see the master CV or your generation
reasoning grades your intent instead of the page, scores generously, and the loop
converges on nothing.

Launch both in one message so they run concurrently:

```
Agent(subagent_type="general-purpose", description="ATS grade <slug>", prompt="""
You are grading a CV. Read and follow .claude/skills/cv-role/references/ats-rubric.md
exactly, including its output format.

CV (extracted PDF text, the only representation you may score): build/<slug>/<slug>.txt
Job listings benchmark: config/job-listings/<slug>.md
Seniority level: <level from cv-config.yaml>

Do NOT read config/master_cv.md, build/<slug>/content.yaml, <slug>.tex, or any
*_analysis.md file. You are simulating an automated parser with no prior context.

Return only the rubric's output block.
""")
```

and the same shape for the recruiter, pointing at `recruiter-rubric.md` and
additionally allowing `<slug>.pdf` (a human recruiter sees the rendered page).

Do not summarize or soften what comes back. Their numbers are the numbers.

---

## Step 5 — Record

**Append** an iteration section to `<slug>_analysis.md` in the repo root. Never
overwrite: the trajectory across iterations is the point, and a change that made
things worse is only visible in the history.

```markdown
# <Role Name> — Analysis
<!-- created <date> | level: <level> | thresholds: ATS <n> / Recruiter <n> -->

## Iteration <n> — <date>

| Rubric | Score | Threshold | Status |
|---|---|---|---|
| ATS | 82/100 | 90 | BELOW |
| Recruiter | 79/100 | 85 | BELOW |

### ATS breakdown
<category table verbatim from the grader>

### Recruiter breakdown
<category table verbatim, plus screen decision and one-line impression>

### Binding constraints
<the 2-4 lowest-scoring weighted categories — where points actually are>

### Changes planned for iteration <n+1>
<specific edits, each naming the category it targets and points it should recover>

### Changes made since iteration <n-1>
<what you changed, and what it did to each category — the audit trail>
```

---

## Step 6 — Iterate or stop

**Stop when:** both scores meet their thresholds, or `loop.max_iterations` is
reached — whichever comes first.

**Abort when:** either score drops by more than `loop.regression_abort_delta`
versus the previous iteration. Report the regression, keep the better-scoring
iteration's `content.yaml`, and stop. Do not keep pushing a rubric off a cliff.

**Otherwise:** revise `content.yaml` targeting only the binding constraints —
the lowest-scoring categories weighted by their max points. A 12-point gap in a
30-point category outranks a perfect fix in a 10-point one. Then return to Step 3.

Note the tension between the rubrics and use it: stuffing keywords lifts ATS
category 1 while sinking recruiter category 2 (seniority credibility). When the
two graders pull against each other, the CV is near its real ceiling — favor the
recruiter, since a human makes the actual decision.

---

## Step 7 — Report

Per role: final scores, iteration count, stop reason, output paths.
Across roles when running the full set: a summary table, plus any role that hit
`max_iterations` without clearing — those need a human look.

---

## Output map

| Path | Contents |
|---|---|
| `<slug>.tex` | generated LaTeX |
| `<slug>.pdf` | rendered CV |
| `<slug>_analysis.md` | full iteration history |
| `build/<slug>/content.yaml` | generated content (the editable source) |
| `build/<slug>/<slug>.txt` | extracted text the ATS grader scores |
| `config/job-listings/<slug>.md` | cached benchmark listings |
