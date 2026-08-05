---
name: us-version
description: Render a US-header variant of an already-built role CV. Takes a CV slug, reuses that role's existing content unchanged, and re-renders it with the US contact line (Buffalo NY, Canadian Citizen, USMCA/TN eligible) to base-cv/<slug>-us.pdf. Use when asked for a US version of a CV, a US CV, or an American-header CV.
---

# us-version

Produces the **US variant** of a CV that already exists. The US CV is the same
document as the Canadian one with a different line under the name: it swaps
`contact_line` for `contact_line_us` in `config/frozen.yaml` and renders to a
separate `base-cv/<slug>-us.pdf`. Nothing in the body changes.

This is deliberately not part of `cv-role`. The content is designed, graded, and
frozen there; here we only re-render an existing, approved CV under a second
header. If the CV has never been built, there is nothing to make a US version of.

## Invocation

- `/us-version <slug>` — render the US variant of that role's CV

**Parsing the argument.** Match the slug loosely against the `slug` and `name`
fields in `config/cv-config.yaml`, the same way `cv-role` does: `data scientist`,
`Data Scientist`, and `data-scientist` all select the same role. If it does not
match exactly one entry, ask rather than guess.

## Step 1 — Confirm the CV exists

The US variant re-renders `build/<slug>/content.yaml`, so that file must exist —
it is written by a `cv-role` run. If it is missing, stop and tell the user to
build the CV first with `/cv-role <slug>`. Do not generate content here; that is
`cv-role`'s job and its grading rules are what make the content defensible.

## Step 2 — Build

```bash
python scripts/build_cv.py <slug> us
```

This reads the same content the Canadian CV uses, injects the US header, and runs
the full render-and-verify pipeline. It writes:

| Path | Contents |
|---|---|
| `base-cv/<slug>-us.tex` | generated LaTeX (US header) |
| `base-cv/<slug>-us.pdf` | rendered US CV, alongside the Canadian `base-cv/<slug>.pdf` |
| `build/<slug>/<slug>-us.txt` | pdftotext extraction |

Because the body is identical to the Canadian build, keyword-coverage is not
recomputed for the US variant — it would only re-read the Canadian extract.

**A non-zero exit is a hard stop.** It almost always means the Canadian CV needs
a rebuild first (`/cv-role <slug>` or `python scripts/build_cv.py <slug>`), since
the two share the same content and fail or pass together.

## Step 3 — Report

Give the user the output path (`base-cv/<slug>-us.pdf`) and confirm the only difference
from the Canadian CV is the header: **Buffalo, NY $|$ Canadian Citizen $|$
USMCA/TN Eligible**. If they also need a US cover letter, that is a separate
input to the `cover-letter` skill (`region: us`), not part of this skill.
