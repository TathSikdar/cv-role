# cv-role

Generates role-targeted CVs from a master CV, renders them with tectonic, and
grades them through ATS + recruiter review loops.

## Working here

- **To generate a CV, invoke the `cv-role` skill.** Do not improvise the
  pipeline — the skill carries the loop logic, thresholds, and grader isolation
  rules that make the output meaningful.
- Never hand-edit `<slug>.tex`. It is generated. Edit `build/<slug>/content.yaml`
  and rerun `python scripts/build_cv.py <slug>`.
- **`config/frozen.yaml` is ground truth.** Education, company names, dates, and
  locations live there and are never rewritten to make a CV score better. If the
  build's frozen-fact verification fails, the generated content is wrong — not
  the frozen file.

## CV content rules (enforced by the build)

- **No em or en dashes** anywhere in CV content. No `—`, `–`, `--`, or `---`.
- **Every bullet uses the XYZ method**: accomplished X, as measured by Y, by
  doing Z.
- **Every bullet renders as exactly two lines**, ideally running close to the end
  of the second. Measured from the PDF, not estimated.
- **The page must be full**: exactly one page, no bottom-margin overrun, no more
  than three blank lines trailing.

## Layout

```
config/     master_cv.md, cv-template.tex, cv-config.yaml, frozen.yaml, job-listings/
scripts/    build_cv.py — assemble, render, extract, verify
build/      per-role content.yaml and extracted PDF text
./          <slug>.tex, <slug>.pdf, <slug>_analysis.md
```

`config/cv-config.yaml` is the file to edit between runs: seniority `level`,
which roles to generate, and loop thresholds.
