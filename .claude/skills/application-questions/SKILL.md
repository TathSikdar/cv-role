---
name: application-questions
description: Answer the free-text screening questions on a job application ("Why do you want to work here?", "Describe a time you...", "What makes you a fit?") for one specific posting, grounded only in the rendered CV and the fetched listing. Takes a CV slug, a listing URL, and the questions. Use when asked to answer, draft, or revise application-form / screening questions for a posting.
---

# application-questions

Answers the free-text questions on **one specific application form** — the boxes
next to "Why this company?", "Tell us about a time...", "What makes you a good
fit?" — so they read as the same candidate the CV and cover letter describe.

The evidence base is exactly two documents: the **rendered CV for this role** and
the **fetched job listing**. Same grounding law as the cover letter. Nothing else.

There is **no build step**. These answers get pasted into a web form; there is no
PDF, no LaTeX, no page fit. The discipline below is what you enforce by hand.

## Invocation

- `/application-questions <slug> <listing-url>` — then the questions, pasted in
  the prompt (one per line, numbered or not).
- `/application-questions <slug> <letter-id-or-answers-id>` — revise an existing
  answer set.

Match the slug against `config/cv-config.yaml` the loose way `cv-role` does. If no
CV has been built for the slug, stop and say so — the answers cannot be grounded
or checked without one. If the questions are not in the prompt, ask for them; do
not invent the form's questions from the posting.

`answers-id` is derived from the company on first run: lowercase, hyphenated, no
legal suffix (`Acme Robotics Inc.` -> `acme-robotics`). Reuse the cover letter's
`letter-id` if one already exists for this company and slug.

## The evidence rule (identical to cover-letter)

- **Never read `config/master_cv.md`, `build/<slug>/content.yaml`, or
  `generation-notes.md`.** Read `build/<slug>/<slug>.txt` — what a reader with the
  PDF actually sees. Every claim about the candidate is bounded by it.
- **Every number in an answer appears on the rendered CV.** No CV figure, no
  answer figure. Inventing a metric here is the same failure as in the letter.
- **Every claim about the employer traces to text fetched this run.** Never invent
  a product, a scale, or a team.
- Read `.claude/skills/cover-letter/references/guidelines.md` for register:
  no em or en dashes (`—`, `–`, `--`, `---`), no marketing diction (seamless,
  robust, world-class, passionate, thrilled, leverage-as-verb), no hedging,
  active voice, plain sentences under ~30 words. First person is correct here.
- **Do not reuse the cover letter.** If `build/<slug>/cover-letters/<id>.txt`
  exists for this posting, read it and treat its prose as off limits: no shared
  run of seven or more consecutive words, and do not recycle its opening hook,
  its sentences, or its framing. The letter and the form answers are read by the
  same person; the same phrasing twice reads as boilerplate. They may cite the
  same CV results — the numbers are shared, the words are not.

## Step 1 — Fetch the listing

WebFetch the URL. Keep company, exact title, the quoted requirements and
responsibilities, and any named product, system, or pain point. If the fetch
returns boilerplate, WebSearch the company plus the title for another host; if
that also fails, ask the user to paste the listing. Do not answer "why us" from a
URL slug and a guess.

For any "why this company" question, also fetch the company's own site for two or
three concrete facts about how the business operates — the same research the
cover letter's rule 14 requires, and for the same reason: an answer that works
verbatim for a competitor is a non-answer.

## Step 2 — Read the CV

Read `build/<slug>/<slug>.txt`. Note the three or four results whose metrics best
match what the listing centrally asks for, each as its number. Those are the
proof you draw on. Draw from employment, not personal projects, unless a project
is genuinely the best evidence for something the role centrally needs.

## Step 3 — Answer, by question type

Answer the question that was actually asked. Match the form:

| Question type | Shape of a good answer |
|---|---|
| **Behavioral** ("describe a time you...") | One situation, in STAR order: situation, task, action, **result with its CV metric**. One story, not a survey. The result is the point; land on it. |
| **Motivation** ("why this company / role?") | Lead with a researched fact about how *this* employer operates (Step 1), tie it to one matching result of yours. Must be false of the obvious competitor. Never their own posting language back at them. |
| **Fit / strengths** ("what makes you a fit?") | Two or three results, each with a metric, each mapped to a stated requirement. Selection and relevance, not a CV re-read. |
| **Logistics** (authorization, notice, salary, start date) | Direct and factual. Work authorization comes from `config/frozen.yaml` (Canadian Citizen; USMCA/TN eligible for US roles). Do not embellish. |
| **Open / "anything else?"** | One thing the CV could not foreground that matters for this role. Optional; a short honest answer beats a padded one. |

**Honor the limit.** Application forms cap answers, often by character count. If a
limit is given, stay under it and say the count. If none is given, keep behavioral
answers ~120 to 180 words, motivation ~80 to 150, fit ~100 to 150. Shorter reads
as more confident.

## Step 4 — Self-check each answer

Rewrite any answer that fails:

- **A1 Grounding.** Every metric is on the rendered CV; every employer claim
  traces to fetched text. Name the trace or cut the claim.
- **A2 On question.** It answers *this* prompt, not the one you wanted. A
  behavioral prompt gets one story, not a list of strengths.
- **A3 Swap test** (motivation/fit answers). Replace the company with its obvious
  competitor. If the answer still reads perfectly, it is a template — add a claim
  true here and false there.
- **A4 Register.** No dashes, no marketing words, no hedging, active voice, plain
  English on one read. (guidelines.md)
- **A5 Limit.** Within the stated or default word/character budget.
- **A6 No fabrication of scope.** No degree, clearance, tool-year, or authorization
  the CV and `frozen.yaml` do not support.
- **A7 No cover-letter overlap.** If a letter exists for this posting, no answer
  shares seven consecutive words with it and none reuses its hook or framing.

## Step 5 — Write and report

Write the answers to `build/<slug>/application-answers/<answers-id>.md`: the
listing source line for traceability, then each question as a `##` heading with
its answer below and a `(N words)` or `(N chars)` tag. Plain markdown the user
copies straight into the form.

Report: the file path, company and title, then for **each** question reproduce
the verbatim question text followed by the full answer as written, so the user
reviews the actual deliverable in the response and not a summary of it. After
each pair, name in one line the result or company fact it leans on. Flag any
question the CV cannot honestly support — that is where the user must decide what
to say, not you.

## Output map

| Path | Contents |
|---|---|
| `build/<slug>/application-answers/<id>.md` | the answers, one `##` per question |
| `build/<slug>/<slug>.txt` | evidence base (read-only) |
| `.claude/skills/cover-letter/references/guidelines.md` | shared register + grounding rules |
