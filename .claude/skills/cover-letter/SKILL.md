---
name: cover-letter
description: Write a cover letter for one specific job listing, rendered in the same LaTeX template as the role-targeted CV so the two documents match. Takes a CV slug and a listing URL, fetches the listing, and writes the letter against the rendered CV. Use when asked to write, generate, or revise a cover letter for a posting.
---

# cover-letter

Writes a cover letter for **one specific posting**, rendered from the same
header, font and margins as `base-cv/<slug>.pdf` so the pair reads as one application.

The letter's evidence base is exactly two documents: the **rendered CV for this
role** and the **fetched job listing**. Nothing else.

## Invocation

- `/cover-letter <slug> <listing-url>` — write a letter for that posting
- `/cover-letter <slug> <listing-url> us` — the same, with the US header
- `/cover-letter <slug> <letter-id>` — rebuild or revise an existing letter

**Parsing the argument.** An argument containing `://` or starting `www.` is the
listing URL; a bare `us` (or `ca`/`canada`) is the header region; anything else
is a `letter-id` naming an existing letter under `build/<slug>/cover-letters/`.
Match the slug against `config/cv-config.yaml` the same loose way `cv-role` does.
If no CV has been built for the slug, stop and say so — the letter cannot be
written or checked without one.

**The region is optional and defaults to Canadian.** Pass `us` to render the
Buffalo, NY / Canadian Citizen / USMCA-TN header instead. It selects only the
line under the name — nothing about the argument or the prose changes — and is
persisted as `region: us` in the letter YAML, so a later revision keeps it. Only
the body content is graded; the region is header selection.

`letter-id` is derived from the company on first run: lowercase, hyphenated,
no legal suffix. `Acme Robotics Inc.` becomes `acme-robotics`. If that id already
exists for this slug, append the role: `acme-robotics-embedded`.

---

## What may and may not change

| Element | Rule |
|---|---|
| Contact block (name, email, links, location) | **Frozen.** Injected from `config/frozen.yaml`, same as the CV. The `region` input picks which frozen location line is used (Canadian default, or `us`); it selects nothing else. |
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

Identify, as working notes, **the three or four results whose metrics best match
what the listing centrally asks for.** Write each one down as its number: the
percentage, the volume, the hours, the user count.

Those numbers are the letter. Rule 4 requires at least two of them in the body,
and `check_rules` fails the build below that.

**Draw from employment, not personal projects** (rule 8). A project belongs in
the letter only when it is genuinely the best evidence for something the role
centrally needs, never as a stand-in for enterprise scale.

**Do not write down the methodology.** How the result was achieved is rule 2, and
it is what sank the first letter this pipeline produced.

Also read `config/job-listings/<slug>.md` if it exists, for the role's keyword
tiers. Useful for knowing which of the listing's requirements the market treats
as central. **Do not write to the keyword table.** A cover letter read as
keyword-optimized is worse than one that misses a term; the ATS gate is the CV's
job, and this document is read by a person or not at all.

## Step 3 — Read the guidelines

Read `references/guidelines.md` in full before writing. It carries the seven
principles (with every numbered rule grouped under one of them), the paragraph
structure, the register rules, and the failure table.

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
  # Retrieved posting language, kept for grounding. check_rules also uses it to
  # enforce rule 1: paragraph 1 may not hand any of this back to the reader.
  quotes:
    - "verbatim requirement or responsibility from the posting"
  # What paragraph 1 actually leads with: your strongest matching result, with
  # its number. Never a quote from the listing.
  opening_result: "34 percent reduction in bring-up time (Nestle)"
  # Requirements the CV cannot evidence. Recorded here, NOT stated in the letter:
  # rule 6 forbids annotating your own gaps.
  gaps:
    - "..."

# Omit `date` to use today's.
date: "July 22, 2026"

# Header region. Omit (or "canada") for the default header; "us" renders the
# Buffalo, NY / Canadian Citizen / USMCA-TN line. Header only — no effect on prose.
region: us

recipient:
  - "Hiring Team"
  - "Acme Robotics"
  - "Toronto, ON"

salutation: "Dear Hiring Team,"

body:
  # Single-quoted YAML scalars: in a double-quoted string \t is a tab and
  # \textbf silently becomes one. Same rule as the CV.
  - 'Opening: your strongest matching result, with its number, in sentence one or two. Name the role and company once.'
  - 'Middle: two or three more results, each with a metric, each chosen because the posting asks for that thing. One short clause of relevance per result.'
  - 'Close: a standard call to action about the value you would deliver.'

closing: "Sincerely,"
```

Name a person in `salutation` only if the listing names one. Inventing a hiring
manager's name is the same failure as inventing a fact about the company, with a
worse outcome when it is wrong.

Apply these five tests to your own draft before building. Rewrite what fails.

- **C1 Metrics.** Every substantive claim carries a number, and every number
  appears on the rendered CV. Count them. Fewer than two and the build fails;
  one that is not on the CV is a fabrication and comes out (rule 4).
- **C2 Opening.** Hook, then the role, then proof. Sentence one is a researched
  insight into how this employer's business works, framed as a problem and false
  of its competitor. Sentence two names the role. Then the strongest matching
  result with its number. No "I am applying for" (rule 16), no bare statistic
  (rule 11), no describing their business back to them (rule 1).
- **C3 Plain English.** Read each sentence once at speed. Any that needs a second
  pass gets split or deleted. Nothing over about 30 words (rule 3).
- **C4 Grounding.** Every claim about the employer traces to retrieved text.
  Every claim about the candidate traces to the rendered CV. List the traces; if
  one cannot be named, the claim comes out.
- **C5 Posture.** No stated gaps, no asserted authority, no criticism of how the
  business operates, no closing that proposes to review their processes. Read the
  letter as the hiring manager: does this person sound useful, or clever
  (rules 5, 6, 7, 9)?

- **C6 The swap test.** Replace the company name throughout with its most obvious
  competitor. If the letter still reads perfectly, it is a template and it fails
  (rule 14). At least one claim must become false. `check_rules` verifies a
  researched fact reached the page, but only C6 judges whether it is doing real
  work.
- **C7 Robot resume.** Reorder the sentences inside each middle paragraph. If
  nothing is lost, you wrote a list, not a letter (rule 10). Each metric must sit
  in a sentence that says why it matters to this employer, and no metric may be
  followed by a general lesson about analytics (rule 13).
- **C8 Voice and cadence.** Read it aloud. Count the sentences opening on "I": if
  it is most of them, or three in a row, move the subject onto the project or the
  result without going passive (rules 27, 20). Then listen for three sentences of
  the same length in a row and break one (rule 31).

C5 and C6 decide whether the letter gets a reply. A letter can pass every
mechanical check and still read as someone who will argue with their manager
about baselines in week one, or as a template with the names swapped.

### Research the company before writing (rule 14)

C6 cannot be satisfied from the posting alone: the posting describes the job, and
every competitor's posting describes it the same way. Fetch the company's own
site, find two or three concrete facts about how the business actually operates,
and record them with a source in `listing.company_facts`. The build hard-fails on
an empty list and on facts that never reach the body.

Use only what was retrieved. A fabricated company fact is the worst failure
available here, worse than a generic letter.

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
| Fewer than 2 distinct figures in the body (rule 4) | hard fail |
| Paragraph 1 echoing 6 words of the posting (rule 1) | hard fail |
| Banned phrase: stated gaps, asserted authority, insulting the business, audit close (rules 5, 6, 7, 9) | hard fail |
| Academic jargon: "majority class", "held-out", "hyperparameter" (rule 12) | hard fail |
| A lesson tacked after a metric: "is usually what turns..." (rule 13) | hard fail |
| `listing.company_facts` empty, or none of it reaching the body (rule 14) | hard fail |
| Paragraph 1 opening "I am applying for" (rule 16) | hard fail |
| Literary approximation: "legible", "digestible" (rule 18) | hard fail |
| Telling them how to reach you (rule 19) | hard fail |
| A sub-8-word fragment outside the close (rule 17) | warn |
| A sentence ending on a preposition (rule 21) | hard fail |
| Over-explaining a baseline; opinion-as-law (rules 23, 25) | hard fail |
| A hedged close: "could contribute" (rule 26) | hard fail |
| Spatial approximation for data: "underneath a forecast" (rule 30) | hard fail |
| 3 sentences in a row opening "I" (rule 27) | hard fail |
| Passive voice (rule 20) | warn |
| Over half of body sentences opening "I" (rule 27) | warn |
| Time saved as an object handed back (rule 29) | warn |
| 3 consecutive sentences of equal length (rule 31) | warn |
| A sentence over 45 words (rule 3) | hard fail |
| A sentence over 32 words (rule 3) | warn |
| Leaning on a personal project (rule 8) | warn |
| Sentence 60%+ similar to a CV line | warn — usually a bullet with its verbs swapped |
| Body outside 220 to 400 words | warn |
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
| `cover-letters/<slug>-<id>-cover-letter.pdf` | rendered letter, to send alongside `base-cv/<slug>.pdf` |
| `config/cover-letter-template.tex` | template — preamble mirrors `cv-template.tex` |
