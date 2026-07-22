---
name: cover-letter
description: Write a cover letter for one specific job listing, rendered in the same LaTeX template as the role-targeted CV so the two documents match. Takes a CV slug and a listing URL, fetches the listing, and writes the letter against the rendered CV. Use when asked to write, generate, or revise a cover letter for a posting.
---

# cover-letter

Writes a cover letter for **one specific posting**, rendered from the same
header, font and margins as `<slug>.pdf` so the pair reads as one application.

The letter's evidence base is exactly two documents: the **rendered CV for this
role** and the **fetched job listing**. Nothing else.

## Invocation

- `/cover-letter <slug> <listing-url>` — write a letter for that posting
- `/cover-letter <slug> <letter-id>` — rebuild or revise an existing letter

**Parsing the argument.** An argument containing `://` or starting `www.` is the
listing URL; anything else is a `letter-id` naming an existing letter under
`build/<slug>/cover-letters/`. Match the slug against `config/cv-config.yaml` the
same loose way `cv-role` does. If no CV has been built for the slug, stop and say
so — the letter cannot be written or checked without one.

`letter-id` is derived from the company on first run: lowercase, hyphenated,
no legal suffix. `Acme Robotics Inc.` becomes `acme-robotics`. If that id already
exists for this slug, append the role: `acme-robotics-embedded`.

---

## What may and may not change

| Element | Rule |
|---|---|
| Contact block (name, email, links, location) | **Frozen.** Injected from `config/frozen.yaml`, same as the CV. |
| Template geometry, font, header rule | **Frozen.** `config/cover-letter-template.tex` mirrors the CV's preamble. Never edit one without the other. |
| Claims about the candidate's work | **Bounded by the rendered CV.** The letter explains and motivates what the CV shows. It never claims beyond it. |
| Claims about the employer | **Bounded by the fetched listing.** See the grounding rule below. |
| The argument, structure, and prose | Free, within `references/guidelines.md`. |

**Never read `config/master_cv.md` during this skill.** Not for facts, not for
phrasing, not for background. The CV for this role was generated under
`cv-role`'s anchoring rules and is the candidate's story for this application; the
master CV carries a different and broader one. Pulling from it produces a letter
that argues for work the accompanying CV does not show, which is the fastest way
to make a coherent application incoherent.

`build/<slug>/content.yaml` and `build/<slug>/generation-notes.md` are also off
limits. Read `build/<slug>/<slug>.txt`, which is what a reader with the PDF
actually sees.

---

## Step 1 — Fetch the listing

Fetch the URL with WebFetch. Extract and keep:

- company, exact job title, location, and posting date if shown
- the requirements and responsibilities, **quoted**, not paraphrased
- any named product, system, team, or technical problem the posting describes
- anything that reads as a pain point rather than a checkbox

That last item is what the letter's middle paragraph is built on. A posting that
says "our ingestion pipeline currently reprocesses the full day on every run" has
handed over the letter's subject; one that lists "Python, SQL, 2+ years" has not.

**If the fetch fails or returns a wall of boilerplate** (common on
JavaScript-heavy boards), try a WebSearch for the company plus the exact title to
find the same posting on another host. If that also fails, stop and ask the user
to paste the listing text. Do not write the letter from the URL slug and a guess
about the company: every specific claim in the letter has to be traceable to text
actually retrieved.

Record what was retrieved and from where in the letter's `listing` block.

## Step 2 — Read the CV

Read `build/<slug>/<slug>.txt`.

Identify, as working notes:

- the two or three pieces of work most relevant to what the listing emphasizes
- for each, **the reasoning the bullet had no room for** — the constraint that
  made it hard, the alternative rejected, what the result implied

The second column is the letter. The first is only the pointer into it.

Also read `config/job-listings/<slug>.md` if it exists, for the role's keyword
tiers. Useful for knowing which of the listing's requirements the market treats
as central. **Do not write to the keyword table.** A cover letter read as
keyword-optimized is worse than one that misses a term; the ATS gate is the CV's
job, and this document is read by a person or not at all.

## Step 3 — Read the guidelines

Read `references/guidelines.md` in full before writing. It carries the three
questions, the paragraph structure, the register rules, and the failure table.

## Step 4 — Write the letter

Write `build/<slug>/cover-letters/<letter-id>.yaml`:

```yaml
listing:
  url: "https://..."
  company: "Acme Robotics"
  title: "Embedded Software Engineer, New Grad"
  location: "Toronto, ON"
  retrieved: "2026-07-22"
  source: "fetched from the posting page"   # or: pasted by user, found via search
  # The specific hook the opening paragraph is built on, quoted from the listing.
  # If this is empty, the opening will be generic. Go back to Step 1.
  hook: "\"...the fleet's nodes still fall out of time sync after a cold start\""

# Omit `date` to use today's.
date: "July 22, 2026"

recipient:
  - "Hiring Team"
  - "Acme Robotics"
  - "Toronto, ON"

salutation: "Dear Hiring Team,"

body:
  # Single-quoted YAML scalars: in a double-quoted string \t is a tab and
  # \textbf silently becomes one. Same rule as the CV.
  - 'Opening: the role, and the specific reason this posting.'
  - 'Middle: one thread, argued. The pointer to the CV is one clause; the rest is the reasoning behind it.'
  - 'Close: what is wanted, briefly.'

closing: "Sincerely,"
```

Name a person in `salutation` only if the listing names one. Inventing a hiring
manager's name is the same failure as inventing a fact about the company, with a
worse outcome when it is wrong.

Apply these four tests to your own draft before building. Rewrite what fails.

- **C1 Portability.** Read every sentence and ask whether it could appear in a
  letter to a different company. Each one that could is either cut or made
  specific. The opening paragraph must fail this test hardest.
- **C2 Addition.** For each middle paragraph, name what it tells the reader that
  the CV does not. If the answer is a rephrasing of a bullet, the paragraph is
  restating and must be rewritten into the reasoning behind that bullet.
- **C3 Grounding.** Every claim about the employer traces to retrieved text.
  Every claim about the candidate traces to the rendered CV. List the traces; if
  one cannot be named, the claim comes out.
- **C4 Register.** No em or en dashes. No banned phrase from the guidelines'
  failure table. First person, complete sentences, no bolding inside prose.

C2 is the one that decides whether the letter is worth sending. The build's copy
check catches pasted text, but a paragraph can restate a bullet in entirely
different words and pass every mechanical test while adding nothing.

## Step 5 — Build

```bash
python scripts/build_cover_letter.py <slug> <letter-id>
```

Produces `<slug>-<letter-id>-cover-letter.tex` and `.pdf` under `cover-letters/`,
plus `build/<slug>/cover-letters/<letter-id>.txt`.

**A non-zero exit is a hard stop.** Fix the YAML and rebuild.

| Check | Behaviour |
|---|---|
| LaTeX hazards, em and en dashes | hard fail |
| 7 consecutive words shared with the CV | hard fail |
| Sentence 60%+ similar to a CV line | warn — usually a bullet with its verbs swapped |
| Body outside 220 to 420 words | warn |
| Paragraph over 6 sentences | warn |
| More than one page, or overrun into the bottom margin | hard fail |
| A date range not in `frozen.yaml: allowed_date_ranges` | hard fail |

When the copy check fires, do not re-word around it. It is reporting that the
sentence was restating rather than arguing. Replace it with the reasoning behind
the claim, which is what C2 asks for anyway.

**Unlike the CV, the page is not required to be full.** Trailing whitespace on a
cover letter is correct; a letter that fills the page is one nobody finishes. The
fit check only fails on overrun.

## Step 6 — Report

Give the user: output path, company and title, body word count, and the specific
hook the opening was built on. Then state plainly what the letter argues, in one
sentence, so a mismatch with their own read of the role is visible immediately.

Flag anything that had to be left out for lack of grounding: a requirement in the
listing the CV cannot speak to, or a company detail that could not be verified.
Those are the two places a human should look before sending.

---

## Output map

| Path | Contents |
|---|---|
| `build/<slug>/cover-letters/<id>.yaml` | the letter (the editable source) |
| `build/<slug>/cover-letters/<id>.txt` | extracted text of the rendered letter |
| `cover-letters/<slug>-<id>-cover-letter.tex` | generated LaTeX |
| `cover-letters/<slug>-<id>-cover-letter.pdf` | rendered letter, to send alongside `<slug>.pdf` |
| `config/cover-letter-template.tex` | template — preamble mirrors `cv-template.tex` |
