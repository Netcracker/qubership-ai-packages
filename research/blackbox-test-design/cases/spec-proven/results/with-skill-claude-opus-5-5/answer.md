# Is the spec "proven"?

**No.** All three numbers are real and worth having. But each one measures the spec against the spec itself, or
against answers that were chosen without trying to break it. None of them shows that the spec's *structure* matches
the legacy service. They only show it is consistent inside its own vocabulary. So don't stop asking the stand yet.
Change *what* you ask it.

(Note: the repository has no code yet, so this is based on what you described, not on reading the spec.)

## Why each number falls short

| Evidence | What it does show | What it cannot show |
| --- | --- | --- |
| 5,000/5,000 goldens match | On those inputs, the spec and the service agree *after the comparator normalizes both answers* | Anything about inputs nobody sent. Goldens recorded from ordinary traffic are mostly typical cases, and the corners are where ports break. Anything the comparator erases (order, null vs absent, error kind, message text) is not pinned at all |
| 98% mutation score over config knobs | Among the alternatives *someone wrote down*, the goldens rule out nearly all of them | Rules nobody wrote down. If the real service has a rule the spec lacks (evaluation order, short-circuiting, first-match vs last-match on duplicate ids, trimming), no mutant points at it, so nothing can "kill" it. The 2% survivors are open questions, not noise |
| Complete pairwise coverage over 14 dimensions | Every pair of values *of the spec's own concepts* appears in some golden | The 14 dimensions come from the spec. A feature the spec does not compute is not a dimension: a rule's position, sibling order, how a value is spelled, a dependency failing, state from an earlier request. A pair also counts as "covered" when *the spec says* an input reaches it, which assumes the spec is right |

In short, you have strong evidence that the spec has no wrong values among the choices it knows about. You have
almost no evidence that it isn't missing whole choices. For an authorization-like service, a missing choice is
exactly what turns into a wrong **allow**.

A quick check you can run yourself: look at the last 10–20 corrections the spec needed. Did each one flip an
existing knob, or add a *new* rule nobody had written down? If they were mostly new rules, the measures above
were blind to the errors that actually happened, and there is no reason to think those errors have run out.

## What's missing, and what I'd add

Ordered by roughly value per cost.

### 1. Make the decision list explicit, with provenance (cheap; do first)
For every place where the service could have behaved in more than one way, list:
- the choice the spec made;
- the golden that forced it, or "inferred" if none did.

Mark the decisions pinned by only one weak golden. Those are half-guesses, and the next round of questions starts
with them. Also record the legacy build or version with each golden batch. That way a later contradiction can be
told apart from a spec bug.

### 2. Audit the oracle and the comparator
- Feed the parity comparator pairs of answers that differ in exactly one way: list order, `null` vs absent, error
  code vs error text, extra fields, number format. Record which pairs it merges. Every spec decision whose
  alternatives differ only inside a merged class is unpinned, even with 5,000 green goldens.
- Separate outcomes that look the same in a final verdict: **deny because a rule said no**, **deny because no rule
  applied**, and **deny because evaluation failed**. Use a separating context, for example a fallback rule that
  allows only if evaluation reaches it, or a combining mode where these three outcomes produce different verdicts.
  Authorization systems usually treat these three differently, and specs often collapse them.
- Capture side channels with each answer: error messages (which rule fired), downstream call logs (what was
  evaluated, and in what order), and debug traces if the stand allows them.

### 3. Evaluation order and laziness (sentinels and poison)
For each position the *input format* allows, such as each rule in a policy, each condition in a rule, each attribute
lookup, or each external call:
- a **sentinel**, a dependency that logs that it was called and returns a neutral value;
- **poison**, a dependency that fails or references something missing.

These questions tell you whether the position is evaluated at all, in what order, which failure wins when two
fail, and whether the service short-circuits. Write the spec's prediction before sending each one. "The spec has no
opinion here" is itself a gap you've found.

### 4. Structural metamorphic relations
Here the relation itself is the oracle: you don't need to know the right answer, only that two answers must agree.
- **Permutation**: reorder rules, conditions, list items, config entries, JSON keys.
- **Irrelevant addition**: add a rule that never matches, before and after the existing ones.
- **Wrap/flatten**: a group of one vs the bare rule.
- **Split/merge**: `A or B` as one rule vs two rules.
- **Placement**: the same condition at policy level vs rule level.
- **Identity collisions**: two rules with the same id, the same role name in two scopes, `Admin` vs `admin`,
  ids with leading zeros or surrounding whitespace. Map-backed implementations silently keep the first or the last
  one, and your spec probably never had to decide which.
- **Cross-endpoint**: a batch check vs single checks; a "list what I can access" filter vs per-item checks.

Classify each pair. **Assumed** means the spec keeps the relation but nothing pins it; ask these first.
**Predicted** means the spec predicts a quirk; ask to confirm it. **Pinned** means both sides already have
goldens. Add a negative control: break the spec on purpose (for example, reverse its rule order) and confirm the
relation generator notices.

### 5. Exception lists are probably one mechanism
Inventory every hand-written list of special cases in the spec ("these operators behave differently", "these
resource types skip X"). Each list was fitted to the goldens one element at a time, and mutation testing only tries
adding or removing an element. Cluster the lists and propose a general rule for each cluster: a phase, an ordering,
or a value conversion. Then find the minimal question that tells the rule apart from the list.

### 6. Platform idioms as standing hypotheses
Find out what the legacy service is built on: its language, JSON library, database collation, and regex engine.
Each one has a short list of usual edge behaviors: trimming, case folding (including the Turkish dotless i),
number parsing (`"01"`, `"1.0"`, `"1e0"`, `"+1"`), empty vs blank checks, collection order, regex full-match
vs find. At every point where the spec handles such a value, keep the other common behaviors as live hypotheses.
Run them against the goldens, and turn the ones that survive into questions.

### 7. Boundaries on spelling, not meaning
Take input classes from the request schema or grammar, not from the spec's value rules. For every field, cover the
state matrix: absent, `null`, `""`, `" "`, each whitespace class (tab, NBSP, line separator), the value with
padding, the value as a number vs a string, and a one-element array. Ask in **opposite pairs**, two spellings of
the same value in one round. Then any difference between them is a finding, whatever the right answer turns out to
be.

### 8. Combinatorial coverage over raw features
Recompute coverage using factors read off the **input alone**, never through the spec: policy depth, rules per
policy, a rule's index among its siblings, the kinds of rules before and after it, which positions hold external
references, caller kind, tenant shape, and an order index. Cover pairs, plus triples that involve order or sibling
kind. Wherever the spec-derived measure says "covered" and the raw measure says "not covered", the spec is
treating different inputs as the same. That is where to ask.

### 9. An independent second model (most expensive, most valuable; start now in parallel)
Have someone (a person or a separate agent session) build a second model from the goldens, the input format, and
the docs only. They should not see the spec's code or its decision list. Give it a deliberately different
architecture: if the spec is a declarative rule table, write an imperative interpreter in the legacy platform's
style, or the other way round. Run both on every generator from steps 3, 4, 7 and 8, shrink each disagreement to a
minimal input, and cluster them. Each cluster no golden covers is a question for the stand.

### 10. Free questions to harvest first
- **The 2% surviving mutants.** Each one is an alternative no golden rules out. Its minimal distinguishing input is
  a ready-made question.
- **Send your pairwise suite to the stand**, not only to the spec.
- **Shadow traffic**, if you can mirror production or staging reads to both. Compare the raw answers, not the
  normalized ones. Mirror only reads, or isolate writes and stub their downstream effects.
- **Ask the legacy owners** about config flags, library versions, and known quirks. Treat what they say as a
  hypothesis until the stand confirms it.

## How to run the remaining questions

- **Score each candidate question by how many live alternatives its answer separates, weighted by the cost of being
  wrong.** A wrong *allow* outweighs a wrong error message, so questions near allow/deny boundaries, default-deny
  fallbacks, and error→verdict mapping go first.
- **Ask stateful sequences**, because single requests can't see state: grant → check → revoke → check;
  cache warm vs cold; first upload vs re-upload of a policy; retries.
- Give each round a fixed budget, must/should/may tiers so a budget cut drops the least useful questions, control
  replays of a few known goldens at the start and end (to detect drift on the stand), and an isolated tenant for
  config-changing questions.
- Classify each contradiction you find as a **flipped** decision (another value of an existing knob) or a **new**
  decision. New decisions show the old measures were blind there.
- Label each finding **observed** (a golden or answer shows it), **inferred** (it follows from observed answers
  under a stated assumption), or **hypothesis** (no answer has separated it yet). Change the spec only when an
  answer forces it.

## A stopping rule your lead can defend

Base the decision to stop on the questions and answers, not on a score of the spec against itself. Stop when all of
these hold:

1. The last round produced **no new decisions**: only flipped values, or nothing.
2. Every open hypothesis from steps 2–9 (surviving mutants, assumed relations, unasked spelling classes, raw
   combinations not yet covered, second-model disagreements) has been asked, or explicitly accepted as a risk.
3. `n` independent random requests drawn from a **stated** input distribution, compared raw, all agreed. That bounds
   the disagreement rate on *that distribution* at about `3/n` with 95% confidence. For example, 1,000 clean draws
   give about 0.3%. It says nothing about inputs outside the distribution, so state the distribution.

Until then, a fair way to put it: "the spec matches every recorded answer, and we have no known open questions *in
its current vocabulary*." That is a solid result. It is not "proven", and the gap matters most on the allow side
of an authorization service.
