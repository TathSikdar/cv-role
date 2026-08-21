---
name: application-questions
description: Answer the free-text screening questions on a job application ("Why do you want to work here?", "Describe a time you...", "What makes you a fit?") for one specific posting. Answers are short, human-sounding, and never restate the CV. Takes a CV slug, a listing URL, and the questions. Use when asked to answer, draft, or revise application-form / screening questions for a posting.
---

# application-questions

Answers the free-text questions on **one specific application form** — the boxes
next to "Why this company?", "Tell us about a time...", "What makes you a good
fit?" — so they read as the same candidate the CV and cover letter describe.

Three things govern every answer here:

1. **Short.** A form answer is read in fifteen seconds by someone with forty more
   to get through. Say the thing and stop.
2. **Not the CV again.** They have the CV. An answer that walks back through it
   has spent the box and told them nothing new.
3. **Human.** It has to read like the candidate typed it, not like it was
   generated. See the human-voice rules in Step 4.

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

## The evidence rule (wider than cover-letter)

Unlike the cover letter, this skill **may read the candidate's full history**. A
form asks things a one-page CV had no room for, and answering "describe a time
you disagreed with a teammate" from a rendered PDF alone produces a non-answer.

**In scope:**

- `build/<slug>/<slug>.txt` — the rendered CV, what the reader has in front of
  them. Still the primary source and still the consistency baseline.
- `config/master_cv.md` — the candidate's real, fuller history. Use it for
  context, detail, and stories the CV had to cut.
- `build/<slug>/content.yaml` — the projects the CV was built from, including
  the invented ones. An answer may develop a project the CV names.
- **Directions inside the question itself.** If the question says "use the STAR
  method", "focus on a technical challenge", "keep it under 200 characters", or
  names a specific project, that instruction outranks the defaults in this file.

**Still out of scope:**

- **Never contradict the rendered CV.** It is the document they are holding. The
  master CV supplies depth beneath what the CV shows, never a different story on
  top of it. Where the two disagree about a title, an employer, a date, or a
  scope, the rendered CV wins and the master CV's version does not appear.
- **Every number in an answer appears on the rendered CV.** No CV figure, no
  answer figure. Inventing a metric here is the same failure as in the letter.
  Detail from the master CV is fine; a *metric* from it is not.
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

## Step 2 — Read the CV, then the history behind it

Read `build/<slug>/<slug>.txt` first. Note the three or four results whose metrics
best match what the listing centrally asks for, each as its number. Those are the
proof you draw on. Draw from employment, not personal projects, unless a project
is genuinely the best evidence for something the role centrally needs.

Then read `config/master_cv.md` and `build/<slug>/content.yaml` for what sits
**underneath** those bullets: the detail, the constraint, the thing that went
wrong, the reason a choice was made. That is the material a good form answer is
built from, because it is the part the reader cannot already see.

The split to hold in your head: the CV supplies the **numbers**, the history
supplies the **story**. An answer that takes its story from the CV is the
regurgitation this skill exists to prevent.

## Step 3 — Answer, by question type

Answer the question that was actually asked. Match the form:

| Question type | Shape of a good answer |
|---|---|
| **Behavioral** ("describe a time you...") | One situation, in STAR order: situation, task, action, **result with its CV metric**. One story, not a survey. The result is the point; land on it. |
| **Motivation** ("why this company / role?") | Lead with a researched fact about how *this* employer operates (Step 1), tie it to one matching result of yours. Must be false of the obvious competitor. Never their own posting language back at them. |
| **Fit / strengths** ("what makes you a fit?") | Two or three results, each with a metric, each mapped to a stated requirement. Selection and relevance, not a CV re-read. |
| **Logistics** (authorization, notice, salary, start date) | Direct and factual. Work authorization comes from `config/frozen.yaml` (Canadian Citizen; USMCA/TN eligible for US roles). Do not embellish. |
| **Open / "anything else?"** | One thing the CV could not foreground that matters for this role. Optional; a short honest answer beats a padded one. |

**Honor the limit, and default short.** Application forms cap answers, often by
character count. A stated limit is a ceiling, not a target: hitting 498 of 500
characters reads as padding. If a limit is given, stay comfortably under it and
report the count.

If none is given:

| Question type | Budget |
|---|---|
| Behavioral | 90 to 130 words |
| Motivation | 60 to 100 words |
| Fit / strengths | 70 to 110 words |
| Logistics | one or two sentences |
| Open / "anything else?" | under 60 words, or skip it |

These are deliberately tighter than a cover letter paragraph. If an answer will
not fit, the answer is trying to make two points; cut one. Never pad to reach a
budget. A 40-word answer that lands is finished.

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
- **A8 No CV regurgitation.** No answer shares seven consecutive words with
  `build/<slug>/<slug>.txt`, and no answer is a bullet with its verbs swapped.
  Read the answer next to the CV line it cites: if a reader who has both learns
  nothing from the answer, it fails. Cite the number, tell them something else.
- **A9 Human voice.** Read it aloud. It fails if it carries any of these:
  - em or en dashes (`—`, `–`), or `--` standing in for one. Use a comma, a full
    stop, or a colon. This one is absolute.
  - a three-item list where two items would do, especially adjectives
  - "not just X, but Y", "it's not about X, it's about Y", "what stood out",
    "that experience taught me", "I thrive in", "deeply", "truly", "genuinely"
  - a closing sentence that summarizes the answer just given. Stop at the last
    real point instead.
  - **advanced punctuation.** No semicolons, no colons, no parentheticals mid
    sentence. A form answer is plain sentences with full stops and the occasional
    comma. If a sentence needs a colon to hold together, split it in two.
  - **announcing instead of saying.** "The interesting part was X", "what I
    learned was Y", "the challenge here was Z". Cut the frame and state X.
    Same for motivation answers: no "that is why I applied", "that is what drew
    me". Give the reason and let it stand as the reason.
  - **run-on sentences.** One clause chain per sentence. Two short sentences beat
    one long one joined by "and" or a comma splice.
  - every sentence the same length. Real writing has a short one in it.
  - perfect parallel structure across sentences
  - opening by restating the question back
  A small amount of unevenness is correct. A specific, slightly odd detail is the
  strongest signal a person wrote it, and it is usually available in
  `config/master_cv.md`.

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
| `build/<slug>/<slug>.txt` | rendered CV: the numbers, and the consistency baseline (read-only) |
| `config/master_cv.md` | real history: the detail and stories behind the bullets (read-only) |
| `build/<slug>/content.yaml` | the projects the CV was built from (read-only) |
| `.claude/skills/cover-letter/references/guidelines.md` | shared register + grounding rules |
