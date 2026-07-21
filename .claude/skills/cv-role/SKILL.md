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
| Education (institution, degree, dates, location) | **Frozen.** Injected verbatim from `config/frozen.yaml`. Never touched. |
| Education coursework bullet | **Wording frozen, presence optional.** Never reworded. May be dropped whole — see below. |
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

Check `config/job-listings/<slug>.md`. **Rebuild it if any of these is true:**

- the file is missing, or `listings.refresh` is true
- it has no `## Keyword frequency` section
- its recorded benchmark version is below `listings.benchmark_version`

The last two are the migration path. A benchmark built under the old format
carries around 20 listings and no frequency table, which is too thin to tell a
term demanded by half the market from one demanded by a tenth of it. Rebuilding
resets score comparability — say so in the analysis file, the same way the
earlier 6-to-11-listing change was recorded.

To build it: use WebSearch with the role's `search_terms` plus the configured
`level` and gather `listings.per_role` real postings.

**Gather in waves, not one query.** A hundred results from a single search are a
hundred results from one job board's ranking, and their vocabulary is that
board's house style rather than the market's. Vary the query across the role's
`search_terms`, individual technologies, and title variants inside the band
(`new grad`, `university grad`, `entry level`, `junior`, `I`). Deduplicate on
company plus title — the same posting syndicated to four boards must count once,
or it quietly quadruples its own vocabulary's weight.

`listings.per_role` is the target. Warn and continue below `listings.min_required`;
stop and tell the user below `listings.hard_floor`. `scripts/keyword_freq.py`
enforces the floor independently.

### Eligibility filter — apply before writing anything

The benchmark must contain only jobs this candidate could actually get. Scoring
against unreachable postings drags keyword coverage toward vocabulary that
cannot legitimately be claimed, and makes seniority calibration meaningless.

Drop a posting if any of these is true, per `listings.eligibility` in the config:

| Test | Default | Reason |
|---|---|---|
| Requires a degree above `max_degree` | above Bachelor's | Education is frozen in `config/frozen.yaml`. A degree requirement is the one thing CV rewriting can never satisfy. |
| Demands more than `max_years_experience` | more than 3 years | A posting asking for "5+ years" or "12+ years" is not reachable from a co-op record, whatever the CV says. |
| Title contains an `exclude_title_terms` entry | senior, staff, principal, architect, lead, director, head of, manager | The title places the role above the band regardless of stated requirements. |

A posting that states no degree or no experience floor is **eligible** — silence
is not disqualifying.

**The three tests above are the whole filter. Do not invent additional ones.**
In particular, these are *not* grounds for exclusion:

| Not a reason to exclude | Why |
|---|---|
| Security clearance required | The benchmark measures what the market asks for, not what the candidate can be hired into tomorrow. A cleared posting's skill vocabulary is as valid a signal as any other. |
| Citizenship or work authorization | Same. Visa and residency status are not CV-editable and not keyword-bearing. |
| Country, city, or onsite/remote | Location narrows where you apply, not what the role is screened on. |
| Industry or domain the candidate has not worked in | This is the *point* of a benchmark. An unfamiliar domain surfaces vocabulary gaps rather than disqualifying the posting. |

The filter exists for one reason: education and years-of-experience floors are
the requirements a CV rewrite can never satisfy, so scoring against them drags
keyword coverage toward vocabulary that cannot legitimately be claimed. Nothing
else in a posting has that property. When in doubt, keep the posting — a benchmark
that is too permissive costs a few points of measured coverage, while one that is
too strict silently narrows the vocabulary the whole pipeline optimizes toward.

`Engineer I`, `Level I`, `Tier I`, junior, and associate titles are **in band**
for `new-grad` and must not be excluded. See the `level` note in the config.

If the filter leaves you below `listings.per_role`, search again with different
terms rather than lowering the bar.

Record every exclusion in an `## Excluded postings` section at the bottom of the
file with the company, title, and the specific reason, so a later refresh does
not silently re-add it and so the filter's behaviour is auditable.

### File structure

Four sections, in this order:

```markdown
# <Role Name> — Job Listings Benchmark

<!-- built <date> | level: <level> | benchmark_version: 2
     <n> listings retained, <n> excluded -->

## Keyword frequency
<!-- generated by scripts/keyword_freq.py — do not hand-edit -->

## Compact listings
<every posting, one entry each>

## Verbatim listings
<the first `listings.verbatim_subset` postings, in full>

## Excluded postings
<table: company | title | reason>
```

**Compact entry** — this is the bulk of the file, and every one of them feeds the
frequency count:

```markdown
### 37. Stripe — Data Scientist, New Grad
United States (Remote) | Full-time | New grad, no years floor

`Technologies required:` Python, SQL, experimentation, A/B testing, ...
```

The `Technologies required:` line is an explicit comma-separated list of every
concrete technology, framework, platform, protocol, method, and named tool the
posting asks for. Pull these out even when the posting buries them in prose —
`scripts/keyword_freq.py` parses exactly this line and nothing else, so a term
left inside a paragraph is a term that does not count.

Spell terms the way the posting spells them. The script merges known synonyms
via `config/keyword-synonyms.yaml`; if you meet a spelling it does not know
(`k8s`, `NodeJS`), add it there rather than silently normalizing by hand, so the
merge applies to every future role too.

**Verbatim entry** — for the first `listings.verbatim_subset` postings only, keep
today's fuller format underneath the compact fields: requirements and
responsibilities quoted **verbatim**, not paraphrased. The recruiter grader reads
these to calibrate seniority and the market's own phrasing, and paraphrasing
launders exactly what is being measured. A hundred of these would not fit in a
grader's context, which is why only a subset keeps them.

**Omit degree and education requirements from the quoted text entirely.**
"Bachelor's degree in computer science or related field" is not actionable
content for this pipeline, because education is frozen and cannot be tuned toward
it. Keep years-of-experience lines, since those inform seniority calibration even
though they are also not directly editable.

### Generate the frequency table

After writing the file:

```
python scripts/keyword_freq.py <slug>
```

It counts how many listings demand each term (once per listing, however many
times that listing repeats it), merges synonyms, drops the `stopterms`, and
writes the `## Keyword frequency` table in place. Rerunning is safe and
idempotent.

The table is the priority signal for everything downstream. Never hand-edit it —
a hand-tuned count is a thumb on the scale for whatever the CV happens to
already say.

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

### The education coursework bullet may be dropped

`config/frozen.yaml` carries the coursework line as `education_bullet`. Its
**wording is frozen** — never reword it, never retarget it at the role, never
swap in courses the degree did not contain. That would misrepresent a
credential, which is the one thing this pipeline must never do.

Its **presence is not frozen.** Set `education_bullet: false` in
`build/<slug>/content.yaml` to drop it. Omitting a true fact is an editorial
choice every candidate makes; rewriting it is fabrication. Only the second is
off limits.

**The test: does the bullet earn its line?** Keep it only if it raises the ATS
or the recruiter score. It fails that test whenever the coursework points away
from the target role, which is common — a degree that was excellent preparation
for one role family often lists nothing a different family screens on, and the
line then sits in the highest-value real estate on the page arguing for a job
the candidate is not applying to. Both rubrics punish this: the recruiter under
six-second scan and role-narrative coherence, the ATS indirectly, because the
line consumes space that role-relevant content would otherwise fill.

When it is genuinely mixed, prefer keeping it. A CV with no coursework line is
unremarkable; the decision only matters when the line is actively working
against the role.

**Dropping it frees one rendered line**, so Step 3 will report the page as
short. Fill it with role-relevant content per the ordered add strategy, not by
reflowing. That swap is the entire point: a line of coursework arguing for the
wrong role becomes a line of evidence for the right one.

Judge this from grader feedback rather than in advance. If a rubric names the
coursework line as a deduction across iterations, that is the signal to drop it.

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

**No two positions may carry the same title.** Retargeting every entry toward one
role makes it tempting to give all three the same name, and three identical
titles is a worse outcome than the unfocused CV it was meant to fix. It reads as
find-and-replace, it flattens three years into one undifferentiated block, and
the ATS rubric deducts under category 2 because identical titles carry no
progression signal.

Titles should be **near-neighbours, not synonyms**: same family, visibly
different, and ordered so the earliest entry is the most junior. For a data
scientist target:

| | Good | Bad |
|---|---|---|
| Most recent | Data Scientist Co-op | Data Scientist Co-op |
| Middle | Associate Data Scientist Co-op | Data Scientist Co-op |
| Earliest | Data Science Intern | Data Scientist Co-op |

Ways to differentiate without leaving the family: the seniority word (`Intern`,
`Co-op`, `Associate`), the discipline noun (`Data Science` vs `Data Scientist` vs
`Data Analytics`), or a scope qualifier drawn from what that job actually did
(`Product Data Analyst`, `Data Operations Developer`, `ML Platform Co-op`).

Two constraints on the variation:

- **Every title still has to hit the role's vocabulary.** Differentiating by
  wandering to "Software Developer" on the oldest entry forfeits the ATS points
  the retitling existed to win. Keep the family noun in all of them.
- **The progression must be plausible for `level`.** Under `new-grad`, vary
  within the band (intern to co-op to associate). Do not manufacture a ladder
  that peaks above it, and do not imply a promotion between two different
  employers.

Apply this test to every bullet: **if it were deleted, would the CV be weaker
for this specific role?** If not, it does not belong. A bullet about Figma
handoff or design-token consistency is dead weight on an agent developer CV no
matter how well written it is.

The constraint that still holds: bullets must describe work that could plausibly
have happened at that company, in that timeframe, at that level. You choose
which layer of a real job to make the subject. You do not relocate a project
from one employer to another, and you do not invent a job that never happened.

### Cover the role's skill surface across the bullets

The `## Keyword frequency` table in the benchmark tells you what the market
actually asks for and how often. Spend the CV's space in that order:

| Tier | Where it must appear | Notes |
|---|---|---|
| **CRITICAL** (≥50% of listings) | in a substantive bullet | Every one that can be honestly claimed. This is where the ATS points are. |
| **IMPORTANT** (25–49%) | a bullet, or the skills list | Skills list is a legitimate home. |
| **PERIPHERAL** (<25%) | only if the space is genuinely free | Earns nothing. Never displace a higher tier for one. |

Use the table's spelling verbatim. Parsers match strings: `CPP` does not cover
`C++`, and `ML` does not cover `machine learning`. The table already prints the
form the market uses most.

**Before swapping any term out of a bullet, look up both terms' tiers.** Trading
a CRITICAL term for an IMPORTANT one to improve a sentence is a measurable loss
that reads like an improvement — it has happened in this repo and cost four ATS
points undetected for two iterations. `scripts/build_cv.py` now warns when a term
weakens between builds, but the warning arrives after the edit; the tier check
belongs before it.

Anything central to the role appearing only under Technical Skills is a gap that
both rubrics penalize: the ATS as SKILLS-ONLY coverage, the recruiter as
unevidenced skills that will not survive a phone screen.

None of this licenses fabrication. Tier priority decides *which honest claims
earn the space*, never whether to claim a technology the candidate never used. A
CRITICAL term with no grounding stays out and gets recorded as unreachable.

Distribute coverage across positions rather than loading every keyword into the
most recent one. A candidate whose role-relevant work spans three employers
reads stronger than one with a single relevant job and two unrelated ones.

Also free: choose projects that reinforce the role story rather than showing
range, and group skills the way the listings group them.

**Skill group labels are one word, maximum.** `Languages`, `Modeling`,
`Statistics`, `Platforms`, `Tools`, `Data`. A label like
"Machine Learning, Statistics \& Experimentation" burns a third of the line on a
heading that carries no keyword weight the items below it do not already carry,
and it pushes the items themselves onto a second wrapped line. The label is a
signpost, not content. If a group genuinely needs a compound label to make sense,
that is a sign it should be two groups or that its items belong elsewhere.

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

### Write each entry's bullets as a set, not a list

The XYZ rules above govern one bullet at a time, and a CV written only to them
comes out as four defensible sentences that describe no recognizable job. The
recruiter rubric scores this directly under bullet-set coherence, so write each
position and each project as a group from the start.

For every entry, before moving on:

- **State in one sentence what this person did there.** If the honest summary is
  a list joined by "and also", the bullets are fragments. Rewrite until one
  sentence covers them.
- **Give the bullets different jobs.** Build, then measure, then fix, then hand
  off. Different facets of one role, not four interchangeable wins.
- **Check for duplicate claims.** Two latency percentages under one employer read
  as one accomplishment split in half to fill space. So do two bullets opening
  with the same technology.
- **Keep one voice.** Consistent tense across the group, no marketing register
  ("cutting-edge", "seamlessly", "robust"), no first person.

Coherence is not sameness. Bullets that cohere because they all say the same
thing fail the redundancy check instead. What you want is range inside one story.

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

Produces `<slug>.tex`, `<slug>.pdf`, `build/<slug>/<slug>.txt`, and
`build/<slug>/keyword-coverage.md`.

**A non-zero exit is a hard stop.** Fix `content.yaml` and rebuild. Never edit
`config/frozen.yaml` to make verification pass, and never grade a CV that did not
build.

### Keyword warnings

The build classifies every CRITICAL and IMPORTANT term against the rendered text
and warns without failing:

```
[warn] KEYWORD REGRESSION: SQL (CRITICAL, in 61 listings) went IN-BULLET -> SKILLS-ONLY since the last build
[warn] CRITICAL keyword 'C++' (58 listings): ALIAS-ONLY — CV says 'CPP' (bullet); listings say 'C++'
```

Advisory by design: a term can be legitimately absent because claiming it would
be a lie, and that call is yours, not the renderer's. But **a REGRESSION warning
is almost never intentional.** It means an edit aimed at something else quietly
weakened a term the market asks for, which is a loss that reads like an
improvement. Read it before grading, not after.

`ALIAS-ONLY` is the cheapest fix on the board — the claim is already there and
only the spelling is wrong.

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

Score keyword coverage against the benchmark's `## Keyword frequency` table.
Use its counts and tiers as given; do not recount across the listings.

Do NOT read config/master_cv.md, build/<slug>/content.yaml, <slug>.tex,
build/<slug>/keyword-coverage.md, or any *_analysis.md file. You are simulating
an automated parser with no prior context.

Return only the rubric's output block.
""")
```

and the same shape for the recruiter, pointing at `recruiter-rubric.md` and
additionally allowing `<slug>.pdf` (a human recruiter sees the rendered page).
Carry the same "do NOT read" list.

`build/<slug>/keyword-coverage.md` is on that list for a reason. The build script
writes it by matching the frequency table against the rendered CV — it is our own
answer key, and a grader that reads it scores our analysis instead of the page.
It exists for you during Step 6, not for them.

Do not summarize or soften what comes back. Their numbers are the numbers.

---

## Step 5 — Record

**Append** an iteration section to `<slug>_analysis.md` in the repo root. Never
overwrite: the trajectory across iterations is the point, and a change that made
things worse is only visible in the history.

```markdown
# <Role Name> — Analysis
<!-- created <date> | level: <level> | thresholds: ATS <n> / Recruiter <n> -->
<!-- benchmark: <n> listings, version <n> -->

## Iteration <n> — <date>

| Rubric | Score | Threshold | Status |
|---|---|---|---|
| ATS | 82/100 | 90 | BELOW |
| Recruiter | 79/100 | 90 | BELOW |

### ATS breakdown
<category table verbatim from the grader, plus its coverage summary>

### Recruiter breakdown
<six-category table verbatim, plus screen decision and one-line impression>
<and the bullet-set review table, which names the specific entries to rewrite>

### Binding constraints
<the 2-4 lowest-scoring weighted categories — where points actually are>

### Changes planned for iteration <n+1>
<specific edits, each naming the category it targets and points it should recover>

### Changes made since iteration <n-1>
<what you changed, and what it did to each category — the audit trail>
```

**If the benchmark was rebuilt this run, say so before the first iteration
section** and state plainly that earlier scores are not comparable:

```markdown
<!-- BENCHMARK REBUILT <date>: 11 listings (v1, no frequency table) -> 103
     listings (v2). Scores below are NOT comparable with iterations 1-15. -->
```

The same applies to the recruiter rebalance: any iteration graded before
bullet-set coherence existed used a different 100 points, and a flat comparison
across that boundary is meaningless.

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

Two working files make the revision concrete, and both are yours alone — never
show either to a grader:

- `build/<slug>/keyword-coverage.md` — which CRITICAL terms are missing,
  skills-only, or merely misspelled, ranked by how many listings want them. When
  the ATS names a keyword gap, this says exactly what to add and what it is
  worth.
- The recruiter's **bullet-set review** table — it names the entries whose
  bullets do not cohere, so that category is repaired per entry rather than per
  bullet. Rewriting a flagged entry means rewriting its bullets *together*; a
  fragment fixed in isolation usually just becomes a better fragment.

Note the tension between the rubrics and use it: stuffing keywords lifts ATS
category 1 while sinking recruiter category 2 (seniority credibility). When the
two graders pull against each other, the CV is near its real ceiling — **favor
the ATS.** The parser runs first and it is a gate, not a judgement: a CV a
recruiter would have liked never reaches the recruiter if keyword coverage drops
it from the pile. Recruiter points are worth having, but only on a CV that gets
read.

This does not license fabrication. The ATS wins ties over *presentation* choices
(which term to use, which bullet carries a keyword, how a title is worded), not
over the grounding rule in Step 2. A keyword that would require inventing a
platform, employer, or domain the candidate never worked in stays out, and the
gap gets recorded in the analysis file as unreachable rather than closed.

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
| `build/<slug>/keyword-coverage.md` | which terms landed and which slipped — **never shown to a grader** |
| `config/job-listings/<slug>.md` | cached benchmark: frequency table, compact listings, verbatim subset |
| `config/keyword-synonyms.yaml` | alias merges and stopterms, shared across roles |
