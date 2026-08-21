---
name: interview-technical
description: Generate the technical-screen interview questions a technical recruiter or engineer would ask for one specific application, grounded in the rendered CV and the fetched listing. Takes a CV slug and a listing URL. Use when asked to predict, draft, or prep for the technical round for a posting — the "what will they grill me on" for the stack, the projects, and the headline metrics.
---

# interview-technical

Predicts the questions a **technical interviewer** asks in the technical screen for
**one specific application**: depth on the claimed stack, "how did you actually
build this" on the CV's projects, and system-design prompts matching the role. The
output is a prep sheet — and because the CVs in this repo host *invented* projects
(see CLAUDE.md), it doubles as a defensibility audit: it tells the user exactly
where their story will be pressure-tested and where it is thin.

The evidence base is exactly two documents: the **rendered CV for this role** and
the **fetched job listing**. Same grounding law as the cover letter — nothing else.

There is **no build step**. This is a markdown prep sheet the user reads.

## Invocation

- `/interview-technical <slug> <listing-url>` — generate the question set.
- `/interview-technical <slug> <id>` — revise an existing set.

Match the slug against `config/cv-config.yaml` the loose way `cv-role` does. If no
CV has been built for the slug, stop and say so. `id` is the company, lowercased
and hyphenated, no legal suffix; reuse the cover letter's `letter-id` if one
exists for this company and slug.

## The evidence rule (identical to cover-letter)

- **Never read `config/master_cv.md`, `build/<slug>/content.yaml`, or
  `generation-notes.md`.** Read `build/<slug>/<slug>.txt`. The interviewer has the
  CV and the listing; so do you. This isolation is what makes the defensibility
  audit honest — you probe only what a reader can see, exactly as they will.
- **Every question traces to a real anchor** — a technology or metric on the CV, a
  requirement in the listing, or the gap between the two.
- The role's **CRITICAL keywords** (`build/<slug>/keyword-coverage.md`, if present)
  are the terms most listings demand; depth questions belong on those first.
- No em or en dashes (`—`, `–`, `--`, `---`) in the output. Plain English.

## Step 1 — Fetch the listing

WebFetch the URL. Keep company, exact title, the required and preferred tech stack,
the stated responsibilities, and any named system, scale, or engineering problem.
If the fetch returns boilerplate, WebSearch for another host; if that fails, ask
the user to paste it. The listing tells you which of the CV's claims this employer
will actually care about — question those hardest.

## Step 2 — Read the CV, map the attack surface

Read `build/<slug>/<slug>.txt`. For a technical screen, mark:

- **Every headline metric on a project** — "you cut latency 40%, how did you
  measure it, what was the bottleneck, what did you try first?" Each metric is a
  question.
- **Every technology claimed** — the interviewer probes depth on the ones the
  listing requires. Note where the CV claims a tool the listing centres on.
- **The thin spots**: a bold result with no mechanism a reader can infer, a tool
  named once with no supporting detail, a scale claim (throughput, users, data
  size) that invites "walk me through the architecture." These are where an
  invented project cracks — flag them plainly, that is the audit.

## Step 3 — Generate the question set

Weight to what *this* pairing surfaces; skip a bucket the role does not justify.

| Bucket | What to generate |
|---|---|
| **Project deep-dive** | For each headline result: how you built it, how you measured it, what the bottleneck was, what you rejected and why, how it failed. The core of the round. |
| **Stack depth** | Pointed depth questions on the CRITICAL / listing-required technologies the CV claims — not trivia, the "explain the tradeoff" kind a real engineer asks. |
| **System design** | One or two prompts matching the role's actual domain and scale (from the listing), that a candidate with this CV should be able to drive. |
| **Debugging / practical** | A scenario from the role's day-to-day: "prod is doing X, walk me through it." |
| **Gap probes** | Where the listing requires something the CV under-supports: a fair question that exposes it, so the user prepares an honest answer instead of freezing. |

For each question, add a one-line **prep note**: the CV anchor to answer from, or —
for a thin-spot / gap probe — exactly what detail the user must have ready to make
the invented project hold up. That prep note is the deliverable's real value.

## Step 4 — Self-check

- **T1 Tailored.** Each question targets a real CV claim or listing requirement.
  Cut generic leetcode filler unrelated to this stack and role.
- **T2 Grounded.** Prep notes cite only what is on the rendered CV and in the
  listing. No invented metrics.
- **T3 Thin spots surfaced.** Every attack-surface weakness from Step 2 has a
  question and a note on what would make it defensible. Do not soften these — an
  unflagged thin spot is where the interview goes wrong.
- **T4 Real depth.** Questions match how an engineer actually probes: tradeoffs,
  failure modes, measurement. No dashes.

## Step 5 — Write and report

Write to `build/<slug>/interviews/<id>-technical.md`: the listing source line, then
each bucket as a `##` heading with its questions as a list, each prep note indented
beneath. Report the file path, company and title, reproduce the full sheet, and
name the **single weakest point** — the question most likely to break this
candidate's story — so the user knows where to spend prep time.

## Output map

| Path | Contents |
|---|---|
| `build/<slug>/interviews/<id>-technical.md` | the technical question set + prep notes |
| `build/<slug>/<slug>.txt` | evidence base (read-only) |
| `build/<slug>/keyword-coverage.md` | CRITICAL terms to prioritise (if present) |
