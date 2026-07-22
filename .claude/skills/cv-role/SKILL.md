---
name: cv-role
description: Generate a role-targeted CV from the master CV, render it to PDF with tectonic, then grade it through isolated ATS and recruiter review loops until it clears the configured thresholds. Use when asked to build, regenerate, or improve a CV for a specific role, or when asked what a perfect candidate for a role looks like.
---

# cv-role

Reverse-engineers the ideal candidate for a role family. Reads the market's own
keyword frequencies, designs a project for each frozen employer that solves a
problem that business actually has, writes the entry's bullets as that project's
narrative, renders a real PDF, and pushes it through two independent graders until
it clears threshold or runs out of iterations.

## Invocation

- `/cv-role` — every role in `config/cv-config.yaml`
- `/cv-role <slug>` — one role (`/cv-role backend-developer`)
- `/cv-role <slug> <n>` — one role, capped at `n` iterations
  (`/cv-role embedded-developer 5`)
- `/cv-role <n>` — every role, each capped at `n` iterations

**Parsing the argument.** A trailing positive integer is the iteration cap;
everything before it names the role. Match the role loosely against the `slug`
and `name` fields in `config/cv-config.yaml` — `embedded developer`,
`Embedded Developer`, and `embedded-developer` all select the same role. If the
role does not match exactly one entry, ask rather than guess.

Reject a cap that is not a positive integer, and say what was wrong. `0` is not
a cap: it would generate a CV and never grade it, which is the one thing this
skill exists to prevent.

## Before starting

Read `config/cv-config.yaml`. It supplies `level`, the role list, loop
thresholds, and layout budgets. Everything below is driven by it — do not
hardcode a threshold or an iteration count.

**The one exception is the iteration cap.** An `n` passed at invocation
overrides `loop.max_iterations` for that run only. Never write it back to
`config/cv-config.yaml`: the argument is a property of one run, and persisting
it would silently change every later run that passed no argument. Thresholds and
`regression_abort_delta` are not overridable this way — a shorter run is still
graded against the same bar.

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
| Position titles | Free — retarget to the role's vocabulary, provided the entry's bullets make the title true. |
| Experience bullets | Free — **designed from the keyword table, not retargeted from the master CV.** See Step 2. |
| Projects | Free rein. Reuse from the master CV, adapt, or invent something that would impress for this role. |
| Skills | Free rein, but every role-central skill must be evidenced by a bullet. |

**The project inside a job is invented. The job is not.** Step 2 designs a project
that solves a problem the employer actually has, and writes the entry's bullets as
that project's narrative. What constrains the invention is `config/frozen.yaml`:
the employer's real `domain`, the tenure implied by the frozen dates, `level`, and
the candidate's `technology_exposure` set. Those five are never invented.

The failure this replaces is a bullet about work from a different domain with the
role's keywords bolted on. The failure it risks is a project the candidate cannot
speak to in a phone screen. T1 through T6 in Step 2 exist to prevent the second,
and they are the only thing preventing it — **neither grader can detect
fabrication.** Both are forbidden from reading `master_cv.md` or `content.yaml`,
so a confidently written invented project with a plausible metric scores clean on
both rubrics. Rising scores are not evidence that the content is defensible.

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

## Step 2 — Generate content from the keyword set

**The master CV is not the source of experience bullets.** It supplies exactly two
things, and both have already been distilled into `config/frozen.yaml`: each
employer's real business `domain`, and the candidate's `technology_exposure` set.
Never read `config/master_cv.md` when writing experience bullets. Projects may
still be adapted from it.

Experience bullets are *designed outward from the keyword table*. Retargeting
master bullets is what this step used to do and it is what produced weak entries:
a bullet about agent orchestration with `CAN` bolted onto it reads as a generalist
CV relabeled for the role, and both rubrics say so.

The order is: keywords, then allocation, then a real problem at that employer,
then the project that solves it, then the bullets.

### 2.1 Read the keyword set

From `config/job-listings/<slug>.md`, take the `## Keyword frequency` table.
Work with **CRITICAL and IMPORTANT rows only**, and keep their counts —
allocation is weighted by them. PERIPHERAL never drives a design decision.

### 2.2 Allocate keywords to entries

- **CRITICAL terms are shared.** Every one appears in a substantive bullet in the
  most recent entry, and in at least one other. Repeating a CRITICAL term costs
  nothing on the ATS rubric and reads as continuity to a recruiter. This is the
  only tier allowed to appear everywhere.
- **Each IMPORTANT term is assigned to exactly one entry**, chosen by which
  employer's real `domain` most plausibly generates it — not by which entry has
  room. A term with no plausible home goes to projects; failing that, to skills;
  failing that, it is recorded as unreachable in the analysis file. Never force
  one into an entry whose business would not produce it.
- **Caps.** At most `ceil(n_important / n_entries) + 1` primary IMPORTANT terms
  per entry, and **at most 3 tracked terms per bullet**. Past three the sentence
  becomes a technology list, which the recruiter rubric hits twice: once for
  buzzword density, once for a bullet that could appear on any candidate's CV.

Worked example, embedded-developer:

| Entry | Real domain | CRITICAL | IMPORTANT |
|---|---|---|---|
| Nestlé, 20 mo | food/CPG manufacturing: filling lines, plant-floor sensors, QA sampling | C, C++ | firmware, RTOS, CAN, embedded systems |
| Chase, 8 mo | auto parts retail: counter terminals, diagnostic readers | C, C++ | SPI, I2C, UART, Python |
| Fanique, 4 mo | Toronto consumer/media, real work mobile | C (light) | Git, Linux |

### 2.3 Find the problem, in the employer's own terms

For each entry, write **one sentence naming a problem that business actually has,
containing no term from the keyword table.** This is a working note, not CV text.

> Nestlé: "The plant's filling line has to be stopped and hand-checked at every
> SKU changeover, because nothing on the line reports fill weight continuously."

The no-keyword rule is the whole test. If the sentence needs "CAN bus" to make
sense, the problem was reverse-engineered from the keyword list and the entry will
read as invented no matter how well it is written.

### 2.4 Design the project that solves it

One project per entry. Two only for entries with 4+ bullets, and then they must be
phases of one effort, not two efforts. The project must:

- solve the 2.3 problem,
- be implementable with the allocated keywords,
- be sized to the entry's tenure and to `level`,
- be a different *shape* from every other entry's project.

### 2.5 Write the entry's bullets as one project narrative

Bullet count from `layout.bullets_per_experience`. Each bullet is a different
facet of the one project, drawn from a fixed set so they cannot collapse into each
other: **build → verify → harden → hand off.** A 2-bullet entry takes build plus
one other; a 3-bullet entry takes build, verify, harden.

Ordering, which is what "start with the keywords necessary for that section"
means concretely:

- **Bullet 1 is the anchor bullet.** It carries every CRITICAL term allocated to
  the entry plus that entry's highest-count IMPORTANT term, and its vocabulary
  must justify the entry's **title**. If the title says "Firmware Developer
  Co-op", bullet 1 is the bullet that makes that title true.
- **At least one allocated term lands in the first ~100 characters**, so it sits
  on rendered line one where a six-second scan reaches, not trailing off line two.
- Remaining bullets are ordered by descending listing-count of the terms they
  carry.
- No two bullets in an entry open with the same technology.

An anchor bullet built this way:

> `Cut SKU changeover validation on a filling line from \textbf{40} minutes of manual checks to under \textbf{9} by writing the \textbf{C} sampling and fault-reporting \textbf{firmware} for an inline load-cell node that streams weights to the line controller over \textbf{CAN}.`

Three tracked terms, inside a sentence whose subject is a problem Nestlé actually
has. Compare a retargeted master bullet, which is an orchestration sentence with
technology nouns swapped in.

### 2.6 The anchoring constraints

The project is invented. These are not:

| Invented (free) | Fixed (never invented) |
|---|---|
| The project, its problem, mechanism, and metrics | Employer name, dates, location, order |
| The position title | The employer's real `domain` |
| | The **duration**, and therefore the project's size |
| | `level`, and the scope of ownership language |
| | The candidate's `technology_exposure` set |

Apply all six tests to your own output before writing YAML. Rewrite what fails;
do not annotate it.

- **T1 Domain.** The 2.3 sentence names the employer's actual business and
  contains no keyword-table term.
- **T2 Exposure.** Every technology named in an experience bullet appears in
  `frozen.yaml: technology_exposure`. No adjacency arguments. A CRITICAL term
  outside the set stays out and is recorded as unreachable. `scripts/build_cv.py`
  warns on violations, but the check belongs here, before the build.
- **T3 Tenure and scope.** One deliverable per ~4 months of tenure. Permitted
  openers: wrote, built, implemented, ported, instrumented, tested, traced,
  brought up, characterized, reduced, cut, held, verified. **Forbidden anywhere in
  experience bullets:** architected, owned, led, established, drove, spearheaded,
  standardized across. Ownership verbs outrunning the role cost 4 recruiter points
  and have done so in this repo.
- **T4 Instrument.** Every metric names or plainly implies the instrument that
  produced it, and it is one a person at `level` could read: a logic-analyzer
  capture, a changeover log, a bench timing run, a bug count. **No dollar figures
  in any experience bullet.** When the project itself is invented, an unattributed
  dollar amount is the loudest possible fabrication tell.
- **T5 Interview defence.** For each entry, write three questions a hiring manager
  would ask about the project, and confirm the bullets contain enough to answer
  them without inventing facts outside `technology_exposure`. If an answer needs a
  fact the candidate could not supply, the project is over-specified: cut detail
  until it is defensible.
- **T6 Non-collision.** No invented employer project shares subject matter with a
  Personal Projects entry, and no two employers host the same project shape. Three
  CAN sensor nodes at three companies is a worse CV than the unfocused one it
  replaced.

### 2.7 The win-magnitude ladder

This method optimizes for keyword-dense impressive projects, and the recruiter
rubric deducts 4 points for "every bullet claiming a large win". Uniform heroism
is how an invented CV gives itself away. So:

1. **Exactly one bullet per entry** carries a headline outcome — a percentage, a
   time reduction, a throughput figure. It is the anchor bullet, so this rule
   reinforces the keyword ordering rather than fighting it.
2. Every other bullet is a supporting facet with **no improvement claim**:
   *verify* (a measurement with a named instrument), *harden* (a qualitative
   outcome), *hand off* (enablement).
3. Across the whole CV, **at most 3 experience bullets** carry a headline metric,
   and no two are the same kind.
4. **The earliest entry gets no headline at all.** A four-month intern who
   delivered a measured business win is the least believable line on a page.

Build constraint to write against: `check_xyz` hard-fails a bullet with no digit
anywhere unless it matches one of `without`, `to eliminate/prevent/avoid/confirm`,
`before release`, `so that`. So a non-headline bullet either carries an incidental
honest figure — channel count, board count, register count — or uses one of those
constructions.

### 2.8 Delegate the generation

Run the design above as a **subagent with a restricted context**. The graders are
isolated so they cannot see your intent; this agent is isolated for the opposite
reason — so it cannot see the master CV's *prose*, which is the failure mode the
whole step exists to escape. It gets the master CV's *facts* through
`frozen.yaml`.

```
Agent(subagent_type="general-purpose", description="Generate <slug> content", prompt="""
Design CV content for <role name> at level <level>. Return YAML only.

You may read: config/frozen.yaml, config/job-listings/<slug>.md,
config/cv-config.yaml, .claude/skills/cv-role/references/latex.md

Do NOT read: config/master_cv.md, any existing build/<slug>/content.yaml,
<slug>_analysis.md, build/<slug>/keyword-coverage.md, or either rubric in
.claude/skills/cv-role/references/. Writing directly at a rubric produces
rubric-shaped prose, which is exactly what the graders penalize as
machine-generated.

<paste sub-steps 2.2 through 2.7 verbatim, plus the CRITICAL/IMPORTANT rows with
counts, the frozen entries with domain and tenure, technology_exposure, the
layout budgets, and the LaTeX and dash rules from references/latex.md>

Return one YAML document:
  allocation:   term -> entry id
  entries:      [{id, title, project: {name, problem, mechanism, metric_source},
                  keywords_used, bullets}]
  projects:     [{name, tech, bullets}]
  skills:       [{label, items}]
  self_check:   {<entry id>: {T1..T6}, unreachable_terms, headline_metric_count}
""")
```

Route the result: `title`, `bullets`, `projects`, `skills` go into
`build/<slug>/content.yaml`; the `project`, `allocation` and `self_check` blocks
go into `build/<slug>/generation-notes.md`, which is **never shown to a grader**.

**Re-run T2, T4 and the headline count yourself against the returned bullets.** An
agent grading its own output passes.

**The generation agent runs once per role**, here at the top of Step 2. Step 6
revisions edit `content.yaml` directly, or re-invoke the agent scoped to a single
entry id when the recruiter's bullet-set review flags that entry. Regenerating the
whole CV every iteration makes the analysis trajectory meaningless and the loop
never converges.

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

**Retitle and rewrite every position, including ones whose real business sits
outside the role family.** Under Step 2 each entry hosts an invented project, so
the title follows the project rather than the employer's industry. A consumer
mobile shop targeted at agent development becomes "AI Developer Co-op" hosting an
LLM-backed support flow, because a consumer app company plausibly has that
problem.

**But the title must be earned by bullet 1.** A title claiming work the entry's
anchor bullet does not describe is the single most expensive error this pipeline
makes: it scored recruiter 40 in this repo, against 72 for the same CV with honest
titles. Retitle because the project justifies it, never to reach a keyword.

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

The constraint that still holds: the entry's invented project must solve a problem
inside that employer's real `domain`, be sized to that tenure and `level`, and be
built only from technologies in `technology_exposure`. You invent the project. You
do not invent the employer, the dates, the business it is in, or a technology the
candidate has never touched. See T1 through T6 in Step 2.

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
- **Keep one voice across the group.** Consistent tense, no first person.
- **And keep every bullet professional on its own.** Consistency is not enough:
  four uniformly casual bullets read as casual, not as coherent, and there is no
  register break to notice. Judge each bullet against plain professional English
  rather than against its neighbours. No shop-floor diction:
  "dumped it", "off the floor", "guessed at", "figured out", "spun up",
  "hooked up", "a ton of", "under the hood", "on the fly".
  And no marketing register in the other direction: "cutting-edge",
  "seamlessly", "robust solutions". Every "it",
  "this" and "them" must have exactly one possible antecedent inside its own
  bullet. Read each bullet once at speed, as a screener does: if a noun run
  parses wrong on that pass, rewrite it. The build fails on the named phrases.

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
costs no vertical space, so extend a short second line with a further *fact*:
another number, component, constraint, or consumer of the work.

Never extend it with a gloss that restates the outcome in casual words. "So that
a silent unit could be read back rather than guessed at" is padding wearing a
purpose clause, and it is where unprofessional wording comes from. If no further
fact exists, tighten the opening clause and let the bullet be shorter: the fill
target **warns, it does not fail**. A short bullet costs a warning; a padded one
costs register points under the recruiter rubric.

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
build/<slug>/keyword-coverage.md, build/<slug>/generation-notes.md, or any
*_analysis.md file. You are simulating an automated parser with no prior context.

Return only the rubric's output block.
""")
```

and the same shape for the recruiter, pointing at `recruiter-rubric.md` and
additionally allowing `<slug>.pdf` (a human recruiter sees the rendered page).
Carry the same "do NOT read" list.

`build/<slug>/generation-notes.md` is on that list for the strongest reason of
all: it contains the invented problem statement and mechanism behind every
experience entry. A grader that reads it is reading the scaffolding instead of the
page, and would score our intent rather than what a real screener sees.

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
<!-- cap this run: <n> (requested at invocation | loop.max_iterations) -->

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

Record the cap on each iteration section. A run that stops three iterations
short of clearing reads as a plateau a year later unless the file says the cap
was 3, and the whole point of appending rather than overwriting is that the
trajectory stays interpretable.

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

**Stop when:** both scores meet their thresholds, or the iteration cap is
reached — whichever comes first. The cap is the `n` passed at invocation if
there was one, otherwise `loop.max_iterations`.

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

This does not license unbounded fabrication. The ATS wins ties over *presentation*
choices (which term to use, which bullet carries a keyword, how a title is
worded), not over the anchoring constraints in Step 2. A keyword that would
require claiming a technology outside `technology_exposure`, or a project outside
the employer's real `domain`, stays out and gets recorded in the analysis file as
unreachable rather than closed.

Watch for this specifically when both scores are climbing. The graders cannot see
ground truth, so a CV drifting past its anchors shows up as *improvement* on both
rubrics right up until a phone screen. Rising scores never retire T1 through T6.

---

## Step 7 — Report

Per role: final scores, iteration count, stop reason, output paths.
Across roles when running the full set: a summary table, plus any role that hit
the iteration cap without clearing — those need a human look.

State the stop reason precisely, because the two cap cases carry different
meaning. A role that exhausted `loop.max_iterations` has plateaued and wants a
human. A role that stopped at a cap passed at invocation was cut short on
purpose and may simply need more iterations, so say so and name the number
that would continue it:

> Stopped at the requested cap of 5 iterations, not at a plateau. ATS 91,
> recruiter 88 (threshold 90) and still climbing. `/cv-role embedded-developer 10`
> to keep going.

Rerunning does not resume: each run starts from the current `content.yaml`,
which is the last iteration's output, so a second `/cv-role <slug> 5` continues
from where the first stopped and appends to the same analysis file.

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
| `build/<slug>/generation-notes.md` | each entry's invented problem, mechanism, metric source, keyword allocation, and T1-T6 self-check — **never shown to a grader** |
| `config/job-listings/<slug>.md` | cached benchmark: frequency table, compact listings, verbatim subset |
| `config/keyword-synonyms.yaml` | alias merges and stopterms, shared across roles |
