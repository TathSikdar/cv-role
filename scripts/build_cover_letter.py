#!/usr/bin/env python3
"""Assemble, render, extract and verify a cover letter for one job listing.

    python scripts/build_cover_letter.py <role-slug> <letter-id>

Reads:
    config/frozen.yaml                          contact block (never generated)
    config/cover-letter-template.tex            LaTeX template with {{PLACEHOLDER}} slots
    config/cv-config.yaml                       layout geometry + letter budgets
    build/<slug>/cover-letters/<id>.yaml        the generated letter
    build/<slug>/<slug>.txt                     the CV this letter accompanies

Writes:
    cover-letters/<slug>-<id>-cover-letter.tex  rendered output
    cover-letters/<slug>-<id>-cover-letter.pdf  rendered output
    build/<slug>/cover-letters/<id>.txt         pdftotext extraction

Exits non-zero on a LaTeX hazard, a page-fit failure, or -- the check this
script exists for -- prose lifted out of the CV. A cover letter that restates
the CV wastes the one page a candidate gets to say something the CV cannot say,
so the overlap check is a hard failure rather than a warning.

The master CV is never read here, by design. The letter's evidence base is the
rendered CV for this role and the job listing, nothing else.
"""

from __future__ import annotations

import re
import statistics
import sys
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_cv import (  # noqa: E402  (path shim must run first)
    BUILD,
    CONFIG,
    DATE_RANGE,
    ROOT,
    BuildError,
    check_latex_hazards,
    contact_line_for,
    load_yaml,
    normalize,
    parse_region,
    run_pdftotext,
    run_tectonic,
)

# Where rendered letters land. Not the repo root: one CV backs many letters.
RENDERED = ROOT / "cover-letters"

# Length of the shared word run that counts as copying. Seven consecutive words
# reproduced from the CV is not coincidence: it is a bullet pasted into a
# sentence. Names, companies and single technical phrases stay well under it.
SHINGLE = 7

# Sentence-level similarity that earns a warning rather than a failure. A
# paraphrase this close is usually a bullet with its verbs swapped.
PARAPHRASE_RATIO = 0.60

# A cover letter is not a page to fill. These bound the body word count; the
# page-fit check separately forbids spilling onto a second page.
WORDS_MIN = 220
WORDS_MAX = 400


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def letter_dir(slug: str) -> Path:
    return BUILD / slug / "cover-letters"


def load_letter(slug: str, letter_id: str) -> dict:
    return load_yaml(letter_dir(slug) / f"{letter_id}.yaml")


def body_latex(paragraphs: list[str]) -> str:
    """Blank line between paragraphs; \\parskip in the template does the spacing."""
    return "\n\n".join(p.strip() for p in paragraphs if p and p.strip())


def recipient_latex(recipient) -> str:
    """Address block. A list, or a string with newlines, becomes one LaTeX line each."""
    if isinstance(recipient, str):
        lines = [ln.strip() for ln in recipient.splitlines()]
    else:
        lines = [str(ln).strip() for ln in (recipient or [])]
    lines = [ln for ln in lines if ln]
    return " \\\\\n".join(lines)


def render_template(frozen: dict, letter: dict) -> tuple[str, list[str]]:
    template = (CONFIG / "cover-letter-template.tex").read_text(encoding="utf-8")

    paragraphs = letter.get("body") or []
    if not paragraphs:
        raise BuildError("cover letter has no `body` paragraphs")
    if isinstance(paragraphs, str):
        raise BuildError("`body` must be a list of paragraphs, not a single string")

    problems: list[str] = []
    for i, para in enumerate(paragraphs, 1):
        problems += check_latex_hazards(f"body paragraph {i}", para)
    for field in ("salutation", "closing", "date"):
        if letter.get(field):
            problems += check_latex_hazards(field, str(letter[field]))
    problems += check_latex_hazards("recipient", recipient_latex(letter.get("recipient")))

    # The letter selects its header region the same way the CV does. Absent or
    # unrecognized `region` in the letter YAML defaults to the Canadian header.
    region = parse_region(str(letter.get("region", "canada"))) or "canada"

    contact = frozen.get("contact", {})
    slots = {
        "NAME": contact.get("name", ""),
        "CONTACT_LINE": contact_line_for(contact, region),
        "EMAIL_URL": contact.get("email_url", ""),
        "EMAIL_DISPLAY": contact.get("email_display", ""),
        "LINKEDIN_URL": contact.get("linkedin_url", ""),
        "LINKEDIN_DISPLAY": contact.get("linkedin_display", ""),
        "GITHUB_URL": contact.get("github_url", ""),
        "GITHUB_DISPLAY": contact.get("github_display", ""),
        # %-d is glibc-only and this repo runs on Windows; build the day by hand.
        "DATE": letter.get("date") or f"{date.today():%B} {date.today().day}, {date.today():%Y}",
        "RECIPIENT": recipient_latex(letter.get("recipient")),
        "SALUTATION": letter.get("salutation", "Dear Hiring Team,"),
        "BODY": body_latex(paragraphs),
        "CLOSING": letter.get("closing", "Sincerely,"),
    }
    for key, value in slots.items():
        template = template.replace("{{" + key + "}}", str(value))

    leftover = re.findall(r"\{\{([A-Z_]+)\}\}", template)
    if leftover:
        raise BuildError(f"template placeholders left unfilled: {sorted(set(leftover))}")

    return template, problems


# --------------------------------------------------------------------------
# the copy check
# --------------------------------------------------------------------------

def _words(text: str) -> list[str]:
    """Lowercased word stream with LaTeX markup and punctuation removed."""
    text = re.sub(r"\\[a-zA-Z]+\s*", " ", text)      # \textbf, \emph, ...
    text = re.sub(r"[{}$\\]", " ", text)
    text = re.sub(r"[^a-z0-9+#]+", " ", text.lower())
    return text.split()


def _shingles(words: list[str], n: int = SHINGLE) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.split()) >= 6]


def check_no_cv_copy(letter: dict, cv_text: str) -> tuple[list[str], list[str]]:
    """Hard-fail on prose lifted from the CV; warn on close paraphrase.

    The CV is a list of proof and the letter is an argument about it. Repeating
    a bullet spends the letter's only page saying something the reader has
    already read, and it is the single most common way a cover letter adds
    nothing. Two tests, because copying degrades gracefully into paraphrase:

      1. A shared run of SHINGLE consecutive words is a paste. Hard failure.
      2. A sentence with >= PARAPHRASE_RATIO similarity to a CV line is a bullet
         with its verbs swapped. A warning, because at that threshold a
         legitimate reference to shared subject matter is still possible.

    Naming a technology, a project, or an employer that appears on the CV is
    expected and neither test fires on it. What must not survive is the CV's
    own sentences.
    """
    failures: list[str] = []
    warnings: list[str] = []

    cv_lines = [ln.strip() for ln in cv_text.splitlines() if len(ln.split()) >= 6]
    cv_shingles = _shingles(_words(cv_text))

    for i, para in enumerate(letter.get("body") or [], 1):
        para_words = _words(para)
        shared = _shingles(para_words) & cv_shingles
        for run in sorted(shared)[:3]:
            failures.append(
                f"body paragraph {i} reproduces {SHINGLE} consecutive words from "
                f"the CV: \"{' '.join(run)}...\". Rewrite the sentence to make an "
                "argument the CV does not already make."
            )
        if shared:
            continue  # already failing; do not also warn about the same text

        for sentence in _sentences(re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", para)):
            for line in cv_lines:
                ratio = SequenceMatcher(None, sentence.lower(), line.lower()).ratio()
                if ratio >= PARAPHRASE_RATIO:
                    warnings.append(
                        f"body paragraph {i} is {ratio:.0%} similar to a CV line: "
                        f"\"{sentence[:70]}...\" vs \"{line[:70]}...\""
                    )
                    break
    return failures, warnings


# Phrases that sink a letter regardless of surrounding context. Every one of
# these is drawn from a letter this pipeline actually produced, so they are
# regressions to guard rather than hypotheticals. See references/guidelines.md.
RULE_BANS: list[tuple[str, str]] = [
    (r"\bno (?:direct|relevant|formal|hands.on|prior) experience\b",
     "rule 6: never state what you lack. The CV states your experience; the "
     "letter does not annotate what is missing from it"),
    (r"\b(?:a |fairly |quite )*specific view\b|\bstrong opinions?\b",
     "rule 6: asserting authority reads as unmanageable, and doubly so next to "
     "a confessed gap"),
    (r"\bnobody asked\b|\bquestion nobody\b|\bwrong question\b",
     "rule 7: do not tell the business its normal practice is wrong"),
    (r"\bwhere .{0,60}\bsits today\b|\bhow .{0,40}\bcurrently (?:works|operates)\b",
     "rule 9: closing by proposing to review their processes is an audit "
     "proposal, not a call to action"),
    (r"\bcannot show\b|\bwhat a single (?:line|bullet)\b",
     "rule 3: convoluted phrasing. Say the thing plainly"),
    (r"\bsmartest\b|\bthe realities of\b",
     "rule 5: sell value, not intellect"),
    # Rule 12: academic register stops a business reader cold.
    (r"\bmajority.class\b|\bheld.out\b|\bholdout\b|\bhyper.?parameter\b"
     r"|\bcross.validation\b|\bconfusion matrix\b|\bp.value\b|\bfeature space\b"
     r"|\bground truth\b|\bout.of.sample\b",
     "rule 12: academic jargon. Translate it into plain business English"),
    # Rule 13: the unsolicited lesson tacked onto a good number.
    (r"\bis usually what\b|\bis what (?:turns|decides|makes|separates)\b"
     r"|\bat the end of the day\b|\bmore often than not\b"
     r"|\bthe difference between .{0,40}\bis\b",
     "rule 13: let the metric stand. Put a period after it and move on"),
    # Rule 19: the header carries email, phone and LinkedIn. Saying it again
    # wastes a line and implies the reader could not find it.
    (r"\b(?:can be reached|reach me|contact me|get in touch with me)\b"
     r"|\bfeel free to (?:contact|reach|email)\b"
     r"|\bdo not hesitate to (?:contact|reach|call)\b"
     r"|\bmy (?:email|phone|number) is\b",
     "rule 19: do not tell them how to reach you. The header already does"),
    # Rule 23: over-explaining a baseline to someone who screens on baselines.
    (r"\bsimply guessing\b|\bjust guessing\b|\bwhich is basically\b"
     r"|\bin other words\b|\bthink of it as\b",
     "rule 23: do not explain a baseline to a data scientist. Tighten the "
     "comparison: \"against a 71 percent baseline\""),
    # Rule 25: a personal opinion stated as a general law of business.
    (r"\bonly (?:stays|works|holds|remains|becomes)\b|\bstays \w+ only when\b"
     r"|\bthe only way to\b|\balways comes down to\b",
     "rule 25: state what you did, not how you have decided the universe works"),
    # Rule 30: casual spatial words for an analytical relationship. Data feeds a
    # forecast, it does not sit beneath one.
    (r"\b(?:underneath|beneath|sits under|sitting under|sit under|under the)\b",
     "rule 30: spatial approximation. Data drives, feeds or supports a forecast, "
     "it does not sit under one"),
    # Rule 18: words that almost fit, reached for to sound original.
    (r"\blegible\b|\bdigestible\b|\bpalatable\b|\bnavigable\b|\bsurmountable\b",
     "rule 18: literary approximation. Use the standard business term "
     "(manageable, scalable, actionable)"),
    (r"\bpassionate\b|\bthrilled\b|\bexcited to\b|\bcutting.edge\b|\bseamlessly\b"
     r"|\bworld.class\b|\bsynerg",
     "marketing register"),
    (r"\bi believe i (?:may|might|could) be\b|\bi feel i would be\b",
     "hedging reads as low confidence. State it plainly"),
]

# Rule 21. A sentence trailing off on one of these reads as conversational.
# Conservative set: no "to" (infinitive), no "up/off/out" (phrasal verbs), so a
# match is almost always a genuine dangling preposition rather than a false hit.
END_PREPOSITIONS = {
    "on", "in", "at", "of", "for", "with", "from", "by", "into", "onto",
    "about", "through", "over", "under", "against", "toward", "towards",
    "within", "upon", "than",
}

# Rule 20. Passive constructions to flag. An explicit participle list rather than
# a blanket "be + \w+ed", because "was accurate" and "is relevant" are adjectival
# and not passive. Everything here is a real past participle a letter might slip
# into the passive with.
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?"
    r"(?:spent|built|driven|written|made|held|caught|shown|taken|given|drawn|"
    r"run|consolidated|removed|monitored|recovered|delivered|handled|achieved|"
    r"reduced|conducted|performed|completed|developed|deployed|implemented)\b",
    re.I,
)

# Rule 29. Time saved is an achievement, not an object handed back. Warn-level:
# the phrasing is sometimes fine, but "returned/gave N hours back" rarely is.
TIME_AS_OBJECT = re.compile(
    r"\b(?:returned|gave|handed|gives|hands|giving|handing)\b[^.]{0,40}"
    r"\bhours?\b[^.]{0,25}\b(?:back|to)\b"
    r"|\bhours?\b[^.]{0,15}\bback\b",
    re.I,
)

# Rule 27. Beyond this fraction of body sentences opening on "I", the letter reads
# as self-centred. A run of this many consecutive "I" openers is the sharper tell.
I_OPENER_RATIO = 0.55
I_OPENER_RUN = 3

# Rule 31. Three consecutive sentences whose word counts fall within this spread
# share a cadence the reader stops hearing.
RHYTHM_RUN = 3
RHYTHM_SPREAD = 3

# Rule 26. Hedge verbs in the closing pitch read as timid.
CLOSE_HEDGE = re.compile(
    r"\bcould (?:contribute|help|bring|add|be of)\b|\bmight (?:contribute|help)\b"
    r"|\bhope to (?:contribute|help|bring)\b|\bwould love to\b"
    r"|\bi (?:think|believe|feel) i\b",
    re.I,
)

# Rule 8. A personal project cannot stand in for enterprise scale, but it is
# legitimate when it is genuinely the best evidence for something central, so
# this warns rather than fails.
PERSONAL_PROJECT = re.compile(r"\bpersonal (?:project|forecasting|side)\b|\bside project\b", re.I)

# Rule 14. Vocabulary that appears in any company's description and therefore
# proves no tailoring. A fact matching only on these words is not a fact that
# distinguishes this employer from its competitor.
GENERIC_FACT_WORDS = {
    "portfolio", "brands", "brand", "company", "companies", "business",
    "employees", "product", "products", "sales", "distribution", "operations",
    "national", "local", "market", "markets", "industry", "teams", "team",
    "customers", "canada", "canadian", "north", "america", "american",
    "through", "across", "every", "their", "there", "other", "these", "those",
    "which", "where", "while", "about", "large", "leading", "global",
}

# Rule 3. Past this a sentence usually needs a second read.
SENTENCE_WARN_WORDS = 32
SENTENCE_FAIL_WORDS = 45

# Rule 4. A letter with no measurable outcome is incomplete.
METRICS_REQUIRED = 2


def check_rules(letter: dict) -> tuple[list[str], list[str]]:
    """Enforce the guidelines' rules, as far as flat text allows.

    Many rules (2, 5, 8, 10, 14's honesty, 17's rhythm) are judgement calls no
    regex settles; what is caught here are the loudest tells. A letter passing
    this function is not thereby a good letter, only one free of the specific
    failures seen before. The C-tests in SKILL.md Step 4 carry the rest.
    """
    failures: list[str] = []
    warnings: list[str] = []
    body = letter.get("body") or []

    for i, para in enumerate(body, 1):
        plain = re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", para)
        for pattern, why in RULE_BANS:
            hit = re.search(pattern, plain, re.I)
            if hit:
                failures.append(f"body paragraph {i}: \"{hit.group(0)}\" — {why}")
        if PERSONAL_PROJECT.search(plain):
            warnings.append(
                f"body paragraph {i} leans on a personal project (rule 8). Use "
                "employment evidence unless this is genuinely the best evidence "
                "for something the role centrally needs."
            )
        for sentence in _sentences(plain):
            n = len(sentence.split())
            if n > SENTENCE_FAIL_WORDS:
                failures.append(
                    f"body paragraph {i}: a {n}-word sentence (rule 3). Split it: "
                    f"\"{sentence[:60]}...\""
                )
            elif n > SENTENCE_WARN_WORDS:
                warnings.append(
                    f"body paragraph {i}: a {n}-word sentence reads long (rule 3)"
                )
            # Rule 21: a sentence dangling on a preposition.
            last = re.sub(r"[^a-z]+$", "", sentence.strip().split()[-1].lower()) \
                if sentence.strip() else ""
            if last in END_PREPOSITIONS:
                failures.append(
                    f"body paragraph {i}: a sentence ends on \"{last}\" (rule 21). "
                    f"Recast it: \"{sentence.strip()[:55]}...\""
                )
            # Rule 20: passive voice. A warning — the participle list is tight, but
            # only a human tells a dull passive from a defensible one.
            pv = PASSIVE.search(sentence)
            if pv:
                warnings.append(
                    f"body paragraph {i}: possible passive voice, \"{pv.group(0)}\" "
                    "(rule 20). Make the subject do the work."
                )
            # Rule 29: time saved written as an object handed back.
            if TIME_AS_OBJECT.search(sentence):
                warnings.append(
                    f"body paragraph {i}: time saved reads as an object handed "
                    "back (rule 29). Active: \"saved the analysts six hours a week\"."
                )

    # Rules 27 and 31 look across the whole body, so gather every sentence with
    # its opener and length first. The opening paragraph's first sentence is the
    # researched hook (rule 16 forbids an "I" opener there anyway), so these
    # cadence checks are about the flow of the evidence, not the hook.
    sents: list[str] = []
    for para in body:
        plain = re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", para)
        sents += [s.strip() for s in _sentences(plain)]

    # Rule 27: the I-disease. A run of consecutive "I ..." openers is the sharp
    # tell; an overall ratio above threshold is the diffuse one.
    opens_i = [bool(re.match(r"\s*I\b", s)) for s in sents]
    run = best_run = 0
    for flag in opens_i:
        run = run + 1 if flag else 0
        best_run = max(best_run, run)
    if best_run >= I_OPENER_RUN:
        failures.append(
            f"{best_run} sentences in a row open with \"I\" (rule 27). Move the "
            "subject onto the project, the model, or the result for some of them. "
            "Vary the subject, not the voice: keep it active (rule 20)."
        )
    if sents and sum(opens_i) / len(sents) > I_OPENER_RATIO:
        warnings.append(
            f"{sum(opens_i)} of {len(sents)} body sentences open with \"I\" "
            f"(rule 27). Aim under {I_OPENER_RATIO:.0%}."
        )

    # Rule 31: three consecutive sentences of near-equal length share a cadence
    # the reader stops hearing.
    lengths = [len(s.split()) for s in sents]
    for j in range(len(lengths) - RHYTHM_RUN + 1):
        window = lengths[j:j + RHYTHM_RUN]
        if max(window) - min(window) <= RHYTHM_SPREAD:
            warnings.append(
                f"{RHYTHM_RUN} consecutive sentences run {min(window)}-{max(window)} "
                "words with the same cadence (rule 31). Vary one deliberately."
            )
            break

    # Rule 26. The closing pitch must assert, not hedge. Checked on the last
    # paragraph only: "could" is fine mid-letter, timid in the final sentence.
    if body:
        close_plain = re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", body[-1])
        hedge = CLOSE_HEDGE.search(close_plain)
        if hedge:
            failures.append(
                f"the close hedges: \"{hedge.group(0)}\" (rule 26). Assert the "
                "value: \"how my background will directly contribute to your "
                "operations\"."
            )

    # Rule 4. Count distinct figures, so "18 percent" repeated is not two metrics.
    figures = set()
    for para in body:
        figures |= set(re.findall(r"\b\d[\d,]*(?:\.\d+)?\b", para))
    if len(figures) < METRICS_REQUIRED:
        failures.append(
            f"the letter carries {len(figures)} measurable result(s); rule 4 "
            f"requires at least {METRICS_REQUIRED}. Lead with outcomes that have "
            "numbers attached, taken from the rendered CV. Never invent a figure."
        )

    # Rule 16. The opening sentence is the most valuable line in the letter and
    # must not be spent announcing the application. Checked only on paragraph 1:
    # "I am applying" is unremarkable mid-letter, and fatal as the first words.
    if body:
        opener = re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", body[0]).lstrip()
        if re.match(
            r"\s*(?:i am (?:writing|applying)|i would like to apply"
            r"|please accept my application|i wish to apply"
            r"|i am submitting my)",
            opener, re.I,
        ):
            failures.append(
                "body paragraph 1 opens by announcing the application (rule 16). "
                "The reader knows what they clicked. Open on a researched hook "
                "about how their business works, and name the role in sentence two."
            )

    # Rule 17. Fragments strung together read as noir, not business prose. A
    # warning rather than a failure: a short sentence is sometimes the right
    # beat, and only the reader can tell a rhythm change from a jolt.
    #
    # The closing paragraph is exempt. Rule 17 is about weaving accomplishments
    # together, and a close is formulaic by design -- "Thank you for your time
    # and consideration" is a courtesy, not a hard-boiled fragment.
    for i, para in enumerate(body[:-1], 1):
        plain = re.sub(r"\\[a-zA-Z]+|[{}\\]", " ", para)
        for sentence in re.split(r"(?<=[.!?])\s+", plain.strip()):
            n = len(sentence.split())
            if 0 < n < 8 and sentence.strip():
                warnings.append(
                    f"body paragraph {i}: \"{sentence.strip()}\" is a {n}-word "
                    "fragment (rule 17). Join it to a neighbour with a real "
                    "transition unless the short beat is deliberate."
                )

    # Rule 14. The swap test, as far as text can check it: the body must carry a
    # researched fact about THIS employer. Without one, the letter reads the same
    # with a competitor's name substituted, which is the definition of a form
    # letter. company_facts is author-supplied and source-attributed, so this
    # verifies the fact reached the page, not that the research was honest.
    facts = letter.get("listing", {}).get("company_facts") or []
    body_words = set(_words(" ".join(body)))
    if not facts:
        failures.append(
            "listing.company_facts is empty (rule 14). Research the employer, "
            "record what you found with a source, and put at least one such fact "
            "in the letter. A letter that works for their competitor is a template."
        )
    else:
        # Content words only, and never the company's own name: a letter that
        # merely names the employer is the form letter this rule exists to catch.
        name_words = set(_words(str(letter.get("listing", {}).get("company", ""))))
        landed = False
        for fact in facts:
            terms = {
                w for w in _words(str(fact))
                if len(w) >= 5 and w not in GENERIC_FACT_WORDS
            } - name_words
            if terms & body_words:
                landed = True
                break
        if not landed:
            failures.append(
                "none of the researched company_facts appear in the body "
                "(rule 14). The letter currently reads the same with a "
                "competitor's name substituted."
            )

    # Rule 1. The opening must not hand the posting's own words back.
    quotes = [str(letter.get("listing", {}).get("hook") or "")]
    quotes += [str(q) for q in (letter.get("listing", {}).get("quotes") or [])]
    listing_shingles = set()
    for q in quotes:
        listing_shingles |= _shingles(_words(q), 6)
    if body and listing_shingles:
        echoed = _shingles(_words(body[0]), 6) & listing_shingles
        for run in sorted(echoed)[:2]:
            failures.append(
                f"body paragraph 1 echoes the posting: \"{' '.join(run)}...\" "
                "(rule 1). The hook belongs to your strongest result, not to "
                "their own description of the job."
            )
    return failures, warnings


def check_grounding(letter: dict, frozen: dict, extracted: str) -> list[str]:
    """Backstop against a letter inventing a tenure the CV does not claim."""
    failures: list[str] = []
    allowed = set(frozen.get("allowed_date_ranges", []))
    unwrapped = re.sub(r"\s+", " ", extracted)
    for match in DATE_RANGE.finditer(unwrapped):
        found = normalize(match.group(0)).replace("–", "-").replace("—", "-").strip()
        if found not in allowed:
            failures.append(
                f"unrecognized date range in rendered letter: '{found}' "
                "— durations may not be invented or altered"
            )

    contact = frozen.get("contact", {}) or {}
    name = contact.get("name", "")
    if name and name not in normalize(extracted):
        failures.append(f"contact name missing from rendered letter: '{name}'")

    # The contact block is frozen, so verify it survived the render, exactly as
    # the CV pipeline verifies its own frozen facts. This is not rule 15 (which
    # rule 19 withdrew): the requirement is that the HEADER carries the details,
    # never that the body mentions them.
    flat = normalize(extracted)
    for field, label in (("email_display", "email"), ("linkedin_display", "LinkedIn")):
        value = contact.get(field, "")
        if value and value not in flat:
            failures.append(f"{label} missing from rendered letter: '{value}'")

    # If a phone is configured it must survive to the page. A number that exists
    # in frozen.yaml but not in the PDF is the exact failure rule 15 describes.
    configured = re.search(
        r"\d{3}[.\-\s]?\d{3}[.\-\s]?\d{4}",
        " ".join(str(v) for v in contact.values()),
    )
    if configured and configured.group(0) not in flat:
        failures.append(
            f"phone number missing from rendered letter: '{configured.group(0)}'"
        )
    return failures


# --------------------------------------------------------------------------
# fit
# --------------------------------------------------------------------------

def measure_fit(pdf_path: Path, config: dict) -> tuple[list[str], str]:
    """One page, no spill into the bottom margin.

    Deliberately NOT the CV's fit rule. A CV must fill its page or it reads as a
    thin candidate; a cover letter that fills the page reads as one nobody will
    finish. Trailing whitespace here is correct, so only overrun fails.
    """
    import fitz  # pymupdf

    layout = config.get("layout") or {}
    text_bottom = layout.get("text_bottom_pt", 770.4)

    doc = fitz.open(pdf_path)
    pages = doc.page_count
    bounds = sorted(
        (line["bbox"][1], line["bbox"][3])
        for block in doc[pages - 1].get_text("dict")["blocks"]
        for line in block.get("lines", [])
    )
    pitch_samples = [
        bounds[i + 1][1] - bounds[i][1]
        for i in range(len(bounds) - 1)
        if 0 < bounds[i + 1][1] - bounds[i][1] < 40
    ]
    pitch = statistics.median(pitch_samples) if pitch_samples else 13.0
    last_bottom = bounds[-1][1] if bounds else 0.0
    doc.close()

    failures: list[str] = []
    if pages != 1:
        over = max(1, round((last_bottom - 19.0) / pitch))
        failures.append(
            f"cover letter is {pages} pages; it must be exactly 1. "
            f"Cut roughly {over} lines. Cut the weakest middle paragraph before "
            "trimming the opening or the close."
        )
    elif last_bottom > text_bottom:
        over = (last_bottom - text_bottom) / pitch
        failures.append(
            f"content overruns the text area by {last_bottom - text_bottom:.0f}pt "
            f"(~{over:.1f} lines) into the bottom margin. Cut "
            f"{max(1, round(over))}-{max(1, round(over)) + 1} lines."
        )
    report = (
        f"{pages} page, content ends at {last_bottom:.0f}pt of {text_bottom:.0f}pt usable"
    )
    return failures, report


def check_length(letter: dict) -> list[str]:
    words = sum(len(_words(p)) for p in letter.get("body") or [])
    warnings = []
    if words < WORDS_MIN:
        warnings.append(
            f"body is {words} words; under {WORDS_MIN} rarely makes a full argument"
        )
    elif words > WORDS_MAX:
        warnings.append(
            f"body is {words} words; over {WORDS_MAX} and a screener skims it. "
            "Cut the paragraph that restates rather than argues."
        )
    for i, para in enumerate(letter.get("body") or [], 1):
        n = len(_sentences(para)) or 1
        if n > 6:
            warnings.append(f"body paragraph {i} runs {n} sentences; 3 to 5 reads better")
    return warnings


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    slug, letter_id = argv[1], argv[2]

    try:
        frozen = load_yaml(CONFIG / "frozen.yaml")
        config = load_yaml(CONFIG / "cv-config.yaml")
        letter = load_letter(slug, letter_id)
        tex, hazards = render_template(frozen, letter)
    except BuildError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if hazards:
        print("[FAIL] unescaped LaTeX characters in generated content:")
        for h in hazards:
            print(f"  - {h}")
        return 1

    cv_txt = BUILD / slug / f"{slug}.txt"
    if not cv_txt.exists():
        print(
            f"[FAIL] missing {cv_txt.relative_to(ROOT)} — build the CV first with "
            f"`python scripts/build_cv.py {slug}`. The letter is written against "
            "the rendered CV, so it cannot be checked without one."
        )
        return 1
    cv_text = cv_txt.read_text(encoding="utf-8", errors="replace")

    copy_failures, copy_warnings = check_no_cv_copy(letter, cv_text)
    for w in copy_warnings:
        print(f"[warn] {w}")
    if copy_failures:
        print("[FAIL] the letter copies the CV:")
        for f in copy_failures:
            print(f"  - {f}")
        print(
            "\nThe CV already lists what was done. The letter's job is the reasoning, "
            "\nthe motivation, and the fit that a bullet had no room for."
        )
        return 1

    rule_failures, rule_warnings = check_rules(letter)
    for w in rule_warnings:
        print(f"[warn] {w}")
    if rule_failures:
        print("[FAIL] cover letter rules:")
        for f in rule_failures:
            print(f"  - {f}")
        print(
            "\nSee .claude/skills/cover-letter/references/guidelines.md. Sell the "
            "value,\nlead with the metric, and do not lecture the reader."
        )
        return 1

    for w in check_length(letter):
        print(f"[warn] {w}")

    out_dir = letter_dir(slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    RENDERED.mkdir(parents=True, exist_ok=True)
    stem = f"{slug}-{letter_id}-cover-letter"
    # Rendered letters live in cover-letters/ rather than the repo root: one CV
    # can back many letters, and at root they would swamp the <slug>.pdf files.
    # tectonic writes its output beside the .tex, so pointing the .tex here is
    # enough to move the .pdf and the .log with it.
    tex_path = RENDERED / f"{stem}.tex"
    pdf_path = RENDERED / f"{stem}.pdf"
    txt_path = out_dir / f"{letter_id}.txt"

    tex_path.write_text(tex, encoding="utf-8")
    print(f"[ok]   wrote {tex_path.name}")

    try:
        run_tectonic(tex_path)
        print(f"[ok]   rendered {pdf_path.name}")
        extracted = run_pdftotext(pdf_path, txt_path)
        print(f"[ok]   extracted {txt_path.relative_to(ROOT)} ({len(extracted)} chars)")
    except BuildError as exc:
        print(f"[FAIL] {exc}")
        return 1

    grounding = check_grounding(letter, frozen, extracted)
    if grounding:
        print("[FAIL] grounding:")
        for f in grounding:
            print(f"  - {f}")
        return 1
    print("[ok]   contact block and durations verified against rendered PDF text")

    fit_failures, fit_report = measure_fit(pdf_path, config)
    print(f"[info] page fit: {fit_report}")
    if fit_failures:
        print("[FAIL] page fit:")
        for f in fit_failures:
            print(f"  - {f}")
        return 1

    listing = letter.get("listing") or {}
    print(
        f"[ok]   {stem}.pdf — {listing.get('title', '?')} at "
        f"{listing.get('company', '?')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
