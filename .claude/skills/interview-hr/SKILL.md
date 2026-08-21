---
name: interview-hr
description: Generate the behavioral / HR-screen interview questions a recruiter or HR partner would ask for one specific application, grounded in the rendered CV and the fetched listing. Takes a CV slug and a listing URL. Use when asked to predict, draft, or prep for the HR / behavioral / recruiter-screen round for a posting — the "what will they ask me" for the non-technical interview.
---

# interview-hr

Predicts the questions an **HR partner or recruiter** asks in the behavioral /
phone-screen round for **one specific application**: motivation, competency
stories, culture and logistics. The output is a prep sheet — the questions this
candidate will actually face, plus where the CV's story is thin, so the user can
rehearse before the call.

The evidence base is exactly two documents: the **rendered CV for this role** and
the **fetched job listing**. Same grounding law as the cover letter — nothing
else. The questions must be tailored to *this* application, not a generic HR list
you could find anywhere.

There is **no build step**. This is a markdown prep sheet the user reads.

## Invocation

- `/interview-hr <slug> <listing-url>` — generate the question set.
- `/interview-hr <slug> <id>` — revise an existing set.

Match the slug against `config/cv-config.yaml` the loose way `cv-role` does. If no
CV has been built for the slug, stop and say so — the questions cannot be grounded
without one. `id` is the company, lowercased and hyphenated, no legal suffix
(`Acme Robotics Inc.` -> `acme-robotics`); reuse the cover letter's `letter-id`
if one exists for this company and slug.

## The evidence rule (identical to cover-letter)

- **Never read `config/master_cv.md`, `build/<slug>/content.yaml`, or
  `generation-notes.md`.** Read `build/<slug>/<slug>.txt` — what a reader with the
  PDF actually sees. The interviewer only has the CV and the listing; so do you.
- **Every question traces to something real** — a claim on the CV, a requirement
  in the listing, or the gap between them. No generic filler ("what's your
  greatest weakness") unless you tie it to this candidate's actual profile.
- **Never invent a fact about the employer.** Every "why us" angle traces to text
  fetched this run.
- No em or en dashes (`—`, `–`, `--`, `---`) in the output. Plain English.

## Step 1 — Fetch the listing

WebFetch the URL. Keep company, exact title, the stated responsibilities, the
"about us" / values / culture language, team size, and any named product or
mission. If the fetch returns boilerplate, WebSearch the company plus title for
another host; if that fails, ask the user to paste it. For "why us" questions,
also grab two or three concrete facts about how the business operates from the
company's own site.

## Step 2 — Read the CV, mark the HR flags

Read `build/<slug>/<slug>.txt`. An HR screener reads for signals, not
architecture. Note:

- The headline results (each with its metric) — the "walk me through this" hooks.
- **Soft-signal flags**: short tenures, employment gaps, job hops, a career pivot,
  a title that is a stretch for the seniority band, being over- or under-qualified
  for this posting. These are exactly what a recruiter probes.
- The competencies the *listing* centrally names (ownership, collaboration,
  ambiguity, stakeholder management) — HR asks for a STAR story on each.

## Step 3 — Generate the question set

Produce questions across these buckets, weighted to what *this* pairing surfaces.
Not every bucket needs the same depth; skip a bucket the listing does not justify.

| Bucket | What to generate |
|---|---|
| **Motivation** | "Why this company / role?" phrased so a generic answer fails — anchor it in a fact from Step 1. One or two. |
| **Behavioral (STAR)** | One prompt per competency the listing names, each pointed at a *specific* CV result the candidate can build the story around. "Tell me about a time you..." |
| **Ownership / conflict / failure** | The standard recruiter probes, but tied to this candidate's actual scope. |
| **Flag probes** | One direct, fair question for each Step-2 soft-signal flag (the gap, the short stint, the pivot). This is the highest-value section — it is what they will actually push on. |
| **Culture / values** | Mapped to the employer's stated values from Step 1, not invented ones. |
| **Logistics** | Notice period, salary expectation, start date, work authorization (from `config/frozen.yaml`: Canadian Citizen; USMCA/TN eligible for US roles), relocation/remote. |

For each question, add a one-line **prep note**: which CV result to answer with, or
— for a flag probe — the honest framing that defuses it. This is the point of the
sheet; a question without its prep note is half the value.

## Step 4 — Self-check

- **H1 Tailored.** Each question could only be asked of *this* application. Cut any
  that would fit any candidate for any job.
- **H2 Grounded.** Prep notes cite only CV results and fetched employer facts.
- **H3 Flags covered.** Every soft-signal flag from Step 2 has a probe and a
  defusing note. Do not hide the awkward ones — those are the ones they ask.
- **H4 Fair.** Questions are ones a real recruiter would ask, not softballs and not
  interrogation. No dashes.

## Step 5 — Write and report

Write to `build/<slug>/interviews/<id>-hr.md`: the listing source line, then each
bucket as a `##` heading with its questions as a list, each question's prep note
indented beneath it. Report the file path, company and title, and reproduce the
full sheet in the response so the user prepares from the actual deliverable. Call
out the single question you expect to be hardest for this candidate.

## Output map

| Path | Contents |
|---|---|
| `build/<slug>/interviews/<id>-hr.md` | the HR question set + prep notes |
| `build/<slug>/<slug>.txt` | evidence base (read-only) |
