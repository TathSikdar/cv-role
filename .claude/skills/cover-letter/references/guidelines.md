# What makes a good cover letter

A cover letter proves you can solve this employer's problems and be an effective
person to work with. That is its whole job. It is not a summary of the CV, and it
is not a demonstration of how well you think.

**The reader has the CV and wrote the posting.** They know what the job is and
they can see your history. What they cannot see is which of your results matter
for their business and what those results would be worth on their team. That
judgement is the letter's entire content.

---

## The seven principles

Every rule this pipeline has accumulated groups under one of seven principles.
Each rule still carries its original number in **(parentheses)** because the
build script reports failures by that number; the numbers are stable tags, not an
order to read in. Where two rules said the same thing at different scope, they are
stated once here.

### I. Say something the CV cannot (1, 2, 4, 5, 10, 13, 25)

The reader has the CV. The letter earns its page only by adding what a bullet had
no room for: which of your results matter to *this* employer, and why.

- **Do not regurgitate the posting (1).** They wrote it. Summarizing the role
  back to them wastes the letter.
- **Do not lecture (2).** No paragraphs on the merits of one method over another.
  Expertise shows through achievements, not argument.
- **Lead with hard metrics (4).** Every substantive claim carries a number: a
  percentage, a volume, hours, scale. A letter with no numbers is incomplete.
- **Sell value, not intellect (5).** Prove you solve their problems, not that you
  are the cleverest person in the room.
- **No robot resume (10).** Not five bullets with the icons deleted. Each metric
  lives inside a sentence about why it matters here. If you can reorder a
  paragraph's sentences with no loss, it is a list, not a letter.
- **Let evidence speak; do not preach (13, 25).** Put a period after a good number
  and move on. Do not tack on a lesson about what "turns an analysis into a
  decision" (13, a trailing clause), and do not state your opinion as a law of
  business, "a portfolio stays manageable only when the reporting is self-serve"
  (25, the same fault at whole-claim scale). A clause about *their business* is
  tailoring and belongs; a clause about *analytics in general* is preaching and
  goes.

**The tension inside this principle:** rule 4 demands numbers, rule 10 forbids a
pile of them. Both hold because a cited metric wrapped in *why it matters to this
employer* is not a bullet. The connective tissue is relevance (which is also what
principle II's research supplies), never methodology.

### II. Stay grounded and honest (6, 7, 8, 14)

Every claim traces to a source. Nothing is invented to fill a gap.

- **Do not confess a gap and assert authority together (6).** Never pair "no
  direct experience" with "a fairly specific view". It reads as unmanageable. The
  CV states your experience; the letter does not annotate what is missing.
- **Do not insult the business (7).** Calling a normal practice "a question
  nobody asked" reads as detached from how companies operate.
- **Employment evidence over personal projects (8).** Do not bridge an
  enterprise-scale gap with a personal project. One belongs only when it is
  genuinely the best evidence for something the role centrally needs.
- **No form letter (14).** If the letter still reads perfectly with a
  competitor's name swapped in, bin it. At least one claim must be true of this
  employer and false of the obvious alternative, which means researching the
  *company*, not the posting. Record what you find in `listing.company_facts`
  with a source. See "Never invent a fact about the company" below.
- **Never invent a metric.** Every figure appears on the rendered CV. If the CV
  has no dollar figure, the letter has none (mirrors `SKILL.md` T4).

### III. The opening (1, 11, 16)

Three rules landed on the first sentence; the law is their intersection.

| Rule | Bans in the opening |
|---|---|
| 1 | handing the posting's description of the job back |
| 11 | a bare statistic with no human lead-in |
| 16 | "I am applying for", which is filler |

What survives all three is a **tailored hook**: one researched insight into how
this employer's business actually works, framed as a problem, false of a
competitor. Then name the role and company in the second sentence, where it costs
nothing, and transition into your strongest result.

> "An independent bottler supplying every province through 50 distribution
> centres carries a forecasting problem a single-site manufacturer never has to
> solve." Correct: researched, a problem, false of a competitor.
>
> "I am applying for the Data Scientist position at Coke Canada Bottling."
> Filler (16).
>
> "Coke Canada is a leading beverage company seeking a data scientist." Their own
> words back at them (1).
>
> "I cut projected stockouts by 18 percent." A bare statistic (11).

### IV. The close (9, 19, 26)

- **Assert, do not hedge (26).** Not "how I could contribute" but "how my
  background will directly contribute to your operations."
- **Do not propose an audit (9).** "I would welcome a conversation about where
  the forecasting work sits today" is a consultant reviewing their processes.
  Close with a call to action about the value you deliver.
- **Do not restate contact details (19).** No "I can be reached at". The header
  carries email, phone and LinkedIn; repeating them wastes a line and implies the
  reader could not find them. (This supersedes the withdrawn rule 15, which had
  asked for the opposite.)

### V. Active voice, varied subject (20, 27)

The pair most likely to fight, so hold both at once.

- **Active voice (20).** The subject performs the verb. Not "that problem is where
  my co-op terms have been spent" but "I spent my co-op terms solving it".
- **Vary the subject off "I" (27).** A column of "I built / I consolidated / I
  owned" is monotonous and self-centred.

The resolution is a **varied active subject**: the project, the model, or the
result does the work, and still acts.

> "I built dashboards. I moved reporting to self-serve. I saved six hours." Active,
> but three I-openers (27).
>
> "Dashboards I built now serve 500 users, saving the analysts six hours a week."
> The subject is the dashboards, and they act. Passes both.

Never resolve 27 by going passive. A passive sentence fails 20 no matter whose
name is absent from it.

### VI. One clean read (3, 12, 22, 23, 24, 28)

Every sentence lands on the first pass. This is a single standard; the rules below
are the specific ways letters have failed it.

- **No word salad (3).** If a sentence needs a second read, cut it. "What a single
  line cannot show is the choice I would actually bring, which was the baseline"
  is the original offender.
- **Plain business English, but do not patronize (12, 23).** Translate academic
  jargon, "majority class baseline", "held-out set", "hyperparameter" (12). But do
  not over-correct into explaining a baseline to someone who screens on them (23):
  "94 percent against a 71 percent baseline" is right; "simply guessing the most
  common category got 71" talks down to the reader.
- **Clean phrasing, especially for numbers (22, 28).** If a phrase is awkward,
  kill it (22): "cost 9 percent of it" becomes "caused a 9 percent drop". A metric
  must land in one read (28): "removed 23 percent of records as duplicates that
  had overstated price moves" becomes "eliminated a 23 percent duplication rate
  that was inflating price moves".
- **Proofread for missing words (24).** "Removing 23 percent duplicate records"
  reads as a typo. A data scientist who drops words reads as one who drops lines
  of code.

### VII. Prose that flows (17, 18, 21, 29, 30, 31)

Grammatical is not enough; the letter has to read well aloud.

- **Real transitions, not noir fragments (17).** "Pricing came with the same job."
  / "Cataloguing was the other half of it." Weave accomplishments together.
- **Precise vocabulary, not literary approximation (18).** A font is legible; a
  portfolio is *manageable* or *scalable*. Do not reach for a word that almost
  fits.
- **Do not end a sentence on a preposition (21).** "The rule the business had been
  running on" becomes "the business's legacy reorder rule".
- **Time saved is an achievement, not an object (29).** Not "returned six hours to
  the analysts" but "saved the analysts six hours each week".
- **Analytical verbs, not spatial ones (30).** Data *drives*, *feeds* or
  *supports* a forecast; it does not sit "underneath" one.
- **Vary the rhythm (31).** Three sentences of the same length in a row put the
  reader to sleep. Break one deliberately.

---

## Citing the CV is not restating it

The build hard-fails on a run of seven consecutive words shared with the rendered
CV (`check_no_cv_copy`), yet principle I demands the CV's own metrics. These do
not conflict: the CV *lists* what happened, the letter *selects* the two or three
results that fit this posting and says why they matter here. Name the number
(required); do not reproduce the bullet's sentence, and do not explain how you got
it (that is lecturing, principle I). When the copy check fires, the sentence was
restating rather than selecting; rewrite it toward relevance, not around the
seven-word window.

---

## Structure

Three or four paragraphs, 220 to 400 words of body. Shorter is usually better;
`build_cover_letter.py` warns outside the band and hard-fails past one page.

**Opening (3 to 4 sentences).** Open on the tailored hook: one researched thing
about how this employer's business works, framed as a problem, that would be
false of its competitor. Name the role and company in the second sentence. Then
transition into your strongest matching result, with its number.

That order matters. Insight, then the role, then proof. No "I am applying for"
(rule 16), no bare statistic (rule 11), no describing their business back to them
(rule 1).

**Middle (one or two paragraphs, 4 to 6 sentences).** Two or three more results,
each with its metric, each inside a sentence that says why it matters to this
employer. Not a list. If you can reorder the sentences freely with no loss, you
have written a robot resume (rule 10).

End each metric on the metric. No trailing lesson (rule 13).

**Close (2 sentences).** A standard call to action framed around the value you
would deliver. Thank them once. Stop. Do not restate your contact details
(rule 19) and do not propose to review their processes (rule 9).

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

Grouped by principle. The rule number in the middle column is what the build
reports.

| Failure | Rule | Fix |
|---|---|---|
| **I. Say something the CV cannot** | | |
| First paragraph summarizes the posting | 1 | Tailored hook, then the metric |
| A paragraph comparing modeling approaches | 2 | Replace with an outcome |
| A claim with no number attached | 4 | Add the metric or cut the claim |
| Adjective stacking: passionate, driven, detail-oriented | 5 | Replace with a result |
| Paragraph reads as reordered resume bullets | 10 | Each metric inside a why-it-matters-here sentence |
| A lesson tacked after a good number | 13 | Period after the metric. Move on |
| "stays manageable only when..." | 25 | State what you did, not the general law |
| **II. Stay grounded and honest** | | |
| "no direct experience, but I have a specific view" | 6 | Delete both halves |
| Calling a normal business practice wrong | 7 | Delete |
| A personal project standing in for enterprise scale | 8 | Use employment evidence |
| Works verbatim for a competitor | 14 | Add a claim true of this employer, false of the other |
| A number not on the CV | 4 | Remove it. Never invent a figure |
| **III. The opening** | | |
| Opening on a bare statistic, no lead-in | 11 | Tailored hook sentence first |
| "I am applying for the position of..." | 16 | Cut it; open on the researched hook |
| Explaining the company's business back to them | 1 | Cut it |
| **IV. The close** | | |
| Closing by proposing to review their processes | 9 | Standard call to action |
| "I can be reached at..." | 19 | Cut it. The header has it |
| "how I could contribute" | 26 | "how my background will directly contribute" |
| **V. Active voice, varied subject** | | |
| "where my co-op terms have been spent" | 20 | "I spent my co-op terms..." |
| Three sentences in a row opening "I..." | 27 | Move the subject to the project or result |
| **VI. One clean read** | | |
| A sentence needing two reads | 3 | Split it or delete it |
| "majority class baseline", "held-out set" | 12 | Plain English, without talking down |
| "cost 9 percent of it" | 22 | "caused a 9 percent drop in accuracy" |
| "simply guessing the most common category" | 23 | "against a 71 percent baseline" |
| "removing 23 percent duplicate records" | 24 | "removing 23 percent of records as duplicates" |
| "removed 23 percent of records as duplicates that..." | 28 | "eliminated a 23 percent duplication rate that..." |
| **VII. Prose that flows** | | |
| "Pricing came with the same job." | 17 | Real transitions, not fragments |
| "the portfolio stays legible" | 18 | "manageable", "scalable" — the standard term |
| Sentence ending "...had been running on" | 21 | "the business's legacy reorder rule" |
| "returned six hours a week to the analysts" | 29 | "saved the analysts six hours each week" |
| "the data underneath those forecasts" | 30 | "the data that feeds those forecasts" |
| Three consecutive sentences of equal length | 31 | Vary one deliberately |

---

## Never invent a fact about the company

Every claim about the employer, its products, its team, its scale, or its
problems must be traceable to the fetched listing page or another source actually
retrieved this run. If the listing is thin, say something true and narrow about
the role rather than reaching for a fact about the company.

A slightly plainer opening costs far less than one confident sentence about a
product they do not sell.
