# What makes a good cover letter

A cover letter proves you can solve this employer's problems and be an effective
person to work with. That is its whole job. It is not a summary of the CV, and it
is not a demonstration of how well you think.

**The reader has the CV and wrote the posting.** They know what the job is and
they can see your history. What they cannot see is which of your results matter
for their business and what those results would be worth on their team. That
judgement is the letter's entire content.

---

## The nine rules

These override anything else in this file. Each one exists because a letter this
pipeline produced broke it.

**1. Never regurgitate the job description.** The hiring manager wrote the
posting. Do not spend the first paragraph, your only hook, summarizing the role
back to them. Open with the value you bring.

**2. Do not lecture the hiring manager.** This is a job application, not a talk.
Do not spend paragraphs on the philosophical merits of one modeling approach over
another. Show expertise through achievements, not through argument.

**3. No pseudo-intellectual word salad.** If a sentence needs a second read,
delete it. Convoluted phrasing does not read as intelligent, it reads as a bad
communicator. The offending original:

> "What a single line cannot show is the choice I would actually bring to your
> team, which was the baseline."

**4. Hard metrics over methodology.** Nobody cares how elegant the model was
without the outcome. Every substantive claim carries a measurable business
result: the percentage, the volume, the hours, the scale. A letter with no
numbers is incomplete.

**5. Sell your value, not your intellect.** Prove you can solve their problems
and be a helpful employee, not that you are the smartest person in the room.

**6. Never confess ignorance and assert authority in the same breath.** Never
write that you have "no direct experience" in something and then declare you have
"a fairly specific view" on how it should be done. It reads as someone who will
be impossible to manage. If a gap exists, either let a relevant result speak to
it or leave it alone. The CV states your experience; the letter does not need to
annotate what is missing from it.

**7. Do not insult the business or its stakeholders.** Calling a standard
business practice, such as asking for a single expected value, "a question nobody
asked" insults the people who run the company and reads as detached from how
businesses actually operate.

**8. Match the scale of your examples to the role.** Do not bridge a gap in
enterprise experience with a personal project. Comparing a personal forecasting
exercise to the trade spend of a national bottler reads as naive, not adaptable.
**Draw evidence from employment first.** A personal project belongs in a letter
only when it is the best evidence for something the role centrally needs, never
as a substitute for enterprise scale.

**9. Earn the interview, do not demand an audit.** Do not close as a consultant
arriving to review their processes: "I would welcome a conversation about where
the forecasting work sits today" is an audit proposal. Close with a standard
professional call to action about the value you would deliver.

---

## What the letter adds, given it cannot restate the CV

Two constraints now sit next to each other, and reconciling them is the hard part
of writing one of these:

- The letter must not repeat the CV. `check_no_cv_copy` hard-fails on a run of
  seven consecutive words shared with the rendered CV.
- The letter must lead with hard metrics, and those metrics are on the CV.

**These do not conflict, because citing a result is not restating a bullet.** The
CV lists what happened. The letter says which of those results matters here and
what it would be worth to this employer. So:

| The CV does this | The letter does this |
|---|---|
| Lists every result, role by role | Picks the two or three that fit this posting |
| States the outcome | States why that outcome is relevant to this business |
| Complete history | An argument for one job |

The added value is **selection and relevance**, not methodology. Naming the
number is required. Explaining how you got it is rule 2.

**Never invent a metric.** Every figure in the letter must appear on the rendered
CV. The CV pipeline bans unattributed dollar amounts for the same reason
(`SKILL.md` T4): a figure nobody can source is the loudest fabrication tell there
is. If the CV has no dollar figure, the letter has no dollar figure.

---

## Structure

Three paragraphs, 220 to 400 words of body. Shorter is usually better under these
rules; `build_cover_letter.py` warns outside the band and hard-fails past one
page.

**Opening (3 to 4 sentences).** Lead with your single strongest result that maps
to what this role centrally does. The number goes in the first or second
sentence. Name the role and company once, briefly, so the letter is filed
correctly. Nothing else.

Do not open with "I am writing to apply for the position of". Do not open by
describing what the company or the team does.

**Middle (4 to 6 sentences).** Two or three more results, each with its metric,
each chosen because the posting asks for that thing. One short clause per result
connecting it to their business is enough. Resist the second clause: that is
where lecturing starts.

**Close (2 to 3 sentences).** A standard call to action framed around the value
you would deliver. Thank them once. Stop.

---

## Register

- **First person, plain sentences.** "I" is correct in a letter. Short
  declaratives. If a sentence runs past about 30 words, split it.
- **No em or en dashes.** No `—`, `–`, `--`, or `---`. The build rejects all
  four.
- **No marketing register:** cutting-edge, seamlessly, robust, dynamic,
  world-class, leverage as a verb, passionate, thrilled, excited to.
- **No shop-floor diction:** spun up, hooked up, a ton of, figured out.
- **No hedging:** "I believe I may be able to contribute" reads as low
  confidence. State it plainly.
- **Escape LaTeX hazards:** `\%`, `\&`, `\#`, `\_`, `$<$`, `$>$`. Body text is
  inserted verbatim as LaTeX source. Use single-quoted YAML scalars.
- **Do not bold inside prose.** The CV bolds because it is scanned. A letter is
  read.

Writing out percentages as words ("18 percent") avoids escaping `\%` and reads
more naturally in prose than in a bullet. Either form is acceptable.

---

## Failure table

| Failure | Rule | Fix |
|---|---|---|
| First paragraph summarizes the posting | 1 | Open with your strongest metric |
| "I am writing to apply for the position of..." | 1 | Cut it; lead with the result |
| A paragraph comparing modeling approaches | 2 | Replace with an outcome |
| A sentence needing two reads | 3 | Split it or delete it |
| A claim with no number attached | 4 | Add the metric or cut the claim |
| A number not on the CV | 4 | Remove it. Never invent a figure |
| "no direct experience, but I have a specific view" | 6 | Delete both halves |
| Calling a normal business practice wrong | 7 | Delete |
| A personal project standing in for enterprise scale | 8 | Use employment evidence |
| Closing by proposing to review their processes | 9 | Standard call to action |
| Adjective stacking: passionate, driven, detail-oriented | 5 | Replace with a result |
| Explaining the company's business back to them | 1 | Cut it |

---

## Never invent a fact about the company

Every claim about the employer, its products, its team, its scale, or its
problems must be traceable to the fetched listing page or another source actually
retrieved this run. If the listing is thin, say something true and narrow about
the role rather than reaching for a fact about the company.

A slightly plainer opening costs far less than one confident sentence about a
product they do not sell.
