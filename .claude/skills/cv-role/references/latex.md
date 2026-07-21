# LaTeX / build reference

You never write LaTeX by hand for a CV. You write `build/<slug>/content.yaml` and
run the build script, which assembles the `.tex` from the template and the frozen
facts. This file documents the contract.

## Build command

```bash
python scripts/build_cv.py <slug>
```

Produces `<slug>.tex` and `<slug>.pdf` in the repo root, and
`build/<slug>/<slug>.txt` (the pdftotext extraction the ATS grader reads).
Non-zero exit means the build failed — never grade or proceed past a failure.

## content.yaml schema

```yaml
# Optional. Omit or set true to keep the frozen coursework line under Education;
# set false to drop it. Its WORDING is never yours to change either way — only
# whether it appears. See SKILL.md, "The education coursework bullet may be
# dropped". Dropping it frees one rendered line that must be refilled.
education_bullet: false

experience:
  # Every id from config/frozen.yaml, same order, none added or removed.
  # You supply ONLY title and bullets. Company, dates and location come from
  # frozen.yaml and are not yours to write.
  - id: nestle
    title: "AI Agent Systems Developer"
    bullets:
      - "Engineered a multi-agent \\textbf{LangGraph} orchestration layer ..."
  - id: chase
    title: "..."
    bullets: ["..."]
  - id: fanique
    title: "..."
    bullets: ["..."]

projects:
  # Free rein: reuse any project from master_cv.md, adapt one, or invent one
  # that would impress for this role.
  - name: "Conformal-Cashflow"
    tech: "PyTorch, LangGraph, Docker, Conformal Prediction"
    bullets: ["..."]

skills:
  # Free rein, including technologies not on the master CV.
  # LABELS ARE ONE WORD (layout.skill_label_max_words). The label is a signpost
  # and carries no keyword weight its items do not already carry, so a compound
  # label wastes a third of the line and wraps the items. Split the group or
  # move its items rather than reaching for "Frameworks & Orchestration".
  - label: "Languages"
    items: "Python, TypeScript, Go, C++, SQL"
  - label: "Agents"
    items: "LangGraph, LangChain, MCP, AutoGen"
```

Bullet text is inserted into LaTeX **verbatim** — it is LaTeX source, not plain
text. That is deliberate: it lets you bold key terms, which materially helps the
recruiter's six-second scan.

## YAML quoting — read this before writing bullets

**Always use single-quoted YAML scalars for bullet text.** In a double-quoted
YAML string, `\t` is a tab and `\textbf{...}` silently becomes a tab followed by
`extbf{...}`. The backslash is gone before LaTeX ever sees it, and the damage
shows up as garbled text in the PDF rather than as an error.

```yaml
- 'Built a \textbf{LangGraph} orchestration layer ...'   # correct
- "Built a \textbf{LangGraph} orchestration layer ..."   # WRONG — \t eaten
```

In single-quoted YAML, a literal `'` is written `''`.

## Escaping

The build script hard-fails on unescaped hazards before invoking tectonic, so
these are caught early rather than as a cryptic TeX error:

| Character | Write it as | Why |
|---|---|---|
| `%` | `\%` | bare `%` comments out the rest of the line — content silently vanishes |
| `&` | `\&` | alignment tab; aborts the render inside `tabular*` |
| `#` | `\#` | macro parameter token |
| `_` | `\_` | subscript token outside math mode |
| `<` `>` | `$<$` `$>$` | in text mode these render as inverted punctuation, and the corruption survives into the PDF |

**Em and en dashes are banned outright**, not merely escaped. The build rejects
literal `—` and `–` as well as `--` and `---`, which LaTeX renders as dashes.
Rewrite the clause with a comma, colon, parentheses, or a sentence break.

Safe and encouraged: `\textbf{...}`, `\emph{...}`, `$R^2$`, `$|$`, and math mode
generally.

## Formatting conventions

- **Bold the terms that matter** — role-critical technologies and headline
  metrics. Bold nothing else; uniform bolding is the same as no bolding.
- Keep bullets to roughly two rendered lines. Longer ones fail the six-second scan.
- Lead with outcome or scale where it is genuinely the strongest part of the bullet,
  but do not force every bullet into the same verb-metric skeleton — the recruiter
  rubric penalizes that pattern as machine-generated.
- Respect the `layout` budgets in `config/cv-config.yaml`. The build warns if the
  PDF exceeds `max_pages`; treat that warning as a failure and cut content.

## Bullet length

The build measures each rendered bullet from the PDF and hard-fails any that does
not occupy exactly `layout.bullet_lines` (default two) rendered lines. It also
reports how full each bullet's final line is and warns below
`layout.bullet_target_fill`.

Roughly 200 to 230 characters produces two full lines in this template, though
bold markup shifts that. Extending a short second line costs no vertical space,
so respond to a fill warning by adding real detail, never by padding.

## Page fit

The build measures the rendered PDF with pymupdf and hard-fails on any of:

- more or fewer pages than `layout.max_pages`
- content overrunning `layout.text_bottom_pt` into the bottom margin (LaTeX will
  overfull a vbox rather than break, so a page can "fit" while spilling)
- more than `layout.max_trailing_blank_lines` of empty space at the bottom

It reports the gap in lines so you know exactly how much to add or cut. See
SKILL.md Step 3 for the ordered add/cut strategy.

`text_bottom_pt` is derived from the template's TeX geometry, not guessed. If you
change any margin in `cv-template.tex`, recompute it by compiling a probe with
the same preamble:

```latex
\typeout{PROBE topmargin=\the\topmargin}
\typeout{PROBE headheight=\the\headheight}
\typeout{PROBE headsep=\the\headsep}
\typeout{PROBE textheight=\the\textheight}
```

Then `text_bottom_bp = (72.27 + topmargin + headheight + headsep + textheight) / 72.27 * 72`
(TeX points to PDF big points). Run tectonic with `--keep-logs` and read the
values out of the `.log`.

Do not calibrate this by eyeballing where content stops on a full page — pages
often break early at a keep-together block, well short of the true margin.

## What the build verifies

After rendering, the script extracts the PDF text and checks:

1. Every frozen company, date range, and location appears verbatim
2. Every frozen education string appears verbatim
3. Every date range found anywhere in the PDF is on the `allowed_date_ranges`
   allowlist — this is what catches an invented or stretched duration
4. No unfilled `{{PLACEHOLDER}}` remains
5. Page fit — page count, margin overrun, and trailing blank space (hard failure)
6. Bullet divergence from the master CV (warning)

If verification fails, fix `content.yaml`. **Never edit `config/frozen.yaml` to
make a check pass** — that file is the ground truth the whole system rests on.

## Troubleshooting

- **`tectonic not found`** — install from https://tectonic-typesetting.github.io
- **First run is slow** — tectonic downloads its package bundle once, then caches it
- **Accented characters mangled in the extraction** (e.g. `Nestlé`) — a real ATS
  parse defect, not a cosmetic one. Fix it rather than working around the check.
- **Content overflows one page** — cut the weakest project bullet first, then the
  weakest experience bullet from the oldest role. Never shrink margins or font
  size; both hurt human readability and neither is measured by the ATS rubric.
