---
name: blackbox-test-design
description: >-
  Load before deciding what to ask a system whose behavior you must learn by querying it, not by reading its code: a
  legacy service you are porting or rewriting, a vendor jar or third-party API without source, another team's
  undocumented service, a stand that answers a parity or golden suite, an executable spec checked against recorded
  answers. Also load when a parity suite or dual run is green before cutover and someone asks what it could still
  miss; when a recorded answer contradicts the model; when planning the next round of probes or deciding to stop
  asking; when building a comparator, shadow-traffic diff, metamorphic or fuzzing campaign against a reference; when a
  suite that matched the reference missed a production difference; and when asked whether the model's mutation score
  or coverage proves it matches the reference. Not for tests of your own code whose expected values you can state
  (test-authoring); load both when a suite compares your code with a reference.
---

# Designing questions for a black box

Use this skill when the behavior you need is owned by something you cannot read: a legacy service, a vendor binary, a
reference implementation behind a network boundary, a stand you can only send requests to. You hold a **model** of it
(an executable spec, a port, a mock, a mental model in a design document) and a pile of **recorded answers**
(goldens, snapshots, logs). Every answer costs something: a stand run, a person's time, a release cycle. The job is
to spend those answers on the questions most likely to show that the model is wrong.

This differs from ordinary test authoring in one way that changes everything: **the expected value is unknown.** You
cannot assert it, so a test here is a *question*, and its value is how many wrong models its answer rules out. A
question whose answer every live model predicts the same way is wasted, however thorough it looks.

This skill decides which questions to ask. Turning a question into a test, with its level, its assertion, and its
failure message, is `test-authoring`'s subject, and so is a harness or comparator once its behavior is decided; load
that skill too before writing any of them. Where the expected value can be stated, from a specification or from code
you can read, the task is ordinary test authoring and `test-authoring` alone applies.

The sections below are techniques, ordered roughly by cost. Most projects need several of them, because each one is
blind in a place another one sees.

## 0. Before anything: state the model and its provenance

Write down, or find, the model's decisions as a list: each place where the reference could have behaved in more than
one way, the choice the model made, and the recorded answer that forced it (or "inferred" when none did). This list
is what every technique below attacks. A decision with no answer behind it is a guess, and guesses are where the
model is most likely wrong.

Settle the goal first: **parity** (reproduce the reference, quirks included) or **intended behavior** (reproduce
what the reference was meant to do, and list the quirks as deliberate differences). The same answer is a bug to copy
under one goal and a bug to fix under the other, and the questions worth asking differ.

Two rules keep the process honest:

- **Change the model only when an answer forces it.** A technique produces questions and hypotheses, not facts. Do not
  "fix" the model from a hunch about how the reference probably works; turn the hunch into a question.
- **Record which version of the reference answered.** An answer from last year's build may contradict this year's. Store
  the version (an `/api-version` call, a build id, a log banner) with every batch of answers, so a later contradiction
  can be told apart from a model error.

## 1. The self-measurement trap

Every adequacy measure has dimensions: mutants have alternatives, coverage has lines or branches, combinatorial
coverage has factors and levels, a fuzzer's saturation has signature classes. **Ask where each measure's dimensions
came from.** If they came from the model under test, the measure can only find errors the model can already express:

| Measure | Blind spot when derived from the model |
| --- | --- |
| Mutation score on the model | Mutants are alternatives someone listed. The reference's real rule is often not among them, so no answer could kill anything pointing at it |
| Line or branch coverage of the model | Behavior the model lacks has no lines, so it is never "uncovered" |
| Pairwise coverage over the model's concepts | A pair counts as covered when the model *says* a case reaches it. Features the model does not compute (position, order, a sibling's outcome) are not factors |
| Fuzzer saturation by signature | If two inputs share a signature class because the model treats them alike, the second one is never generated, even when the reference treats them differently |
| Metamorphic relations the model predicts hold | A relation picked because it is true *in the model* tests the model's own symmetries |

None of these is useless: they find errors *inside* the model's vocabulary. But a high score on them is not evidence
that the model's *structure* is right. For each measure in use, name an independent source for its dimensions: the
input format, the grammar, the documentation, the platform the reference is built on, a second model. §6 to §9 are
those sources.

A quick audit: list the last ten corrections the model needed. If most of them were *new* decisions (a rule nobody had
written down) rather than *flipped* decisions (another value of an existing choice), the measures in use are measuring
the model against itself.

## 2. Oracle strength: what can an answer tell apart?

A recorded answer pins a decision only as far as the answer shows it. Before designing more questions, find out what
the current ones cannot see.

- **List the outcomes that must be told apart** at each decision point, not just the final verdict. Typical
  collapses: "the check failed" versus "the check did not apply" versus "the check returned false"; "absent" versus
  `null` versus empty; "refused at input" versus "accepted and ignored". If two outcomes produce the same visible
  answer in a probe, the probe pins neither. Fix it with a **context that separates them**: a sibling, a fallback, a
  second request, a combining rule under which the two outcomes lead to different verdicts. Build one helper that wraps
  any probe in the minimal separating context, and route every new question through it.
- **Audit the comparator.** Snapshot and parity suites normalize answers: sort lists, drop nulls, canonicalize
  numbers, ignore key order or whitespace. Whatever the normalizer erases, no answer can pin. Find its equivalence
  classes empirically, without reading its code if you have to: feed it pairs of answers that differ in exactly one
  aspect and record which pairs it merges. Then list the model decisions whose alternatives differ only inside a merged
  class; they need a raw comparison or a probe where the difference changes the verdict.
- **Audit which answers pin which decisions.** For each decision in the §0 list, find the recorded answers that
  would change if the decision changed, and check whether any of them separates the outcomes the decision claims.
  A decision pinned by one weak answer is *weakly pinned*; treat it as half a guess.
- **Use every channel the reference exposes.** Error messages name the rule that fired. Call logs of mocks the
  reference talks to show what it evaluated and in what order. Debug or trace logs, if the environment lets you turn
  them on, show the decision itself. Response headers, timing, and side effects in a database are answers too. Store
  them with the verdict; they are often the only way to pin *how* a verdict was reached.

## 3. Sentinels and poison: mapping evaluation order and laziness

A verdict hides *when* the reference read something, which of two failures won, and whether a value was computed and
thrown away. Models usually get these wrong, because they are invisible in ordinary answers and models are written
in whatever order felt natural.

- A **sentinel** is an input whose evaluation is visible without changing the verdict: a dependency that logs the call
  and returns a neutral value.
- A **poison** is an input whose evaluation changes the verdict recognizably: a dependency that fails, a reference to
  something absent, a value that makes an operator throw, a template placeholder that cannot resolve.

Enumerate **positions** from the input format, not from the model: each operand of each operator, each element of
each list, each child of each node, each stage of a pipeline (parse, validate, evaluate, render), each item of a batch,
each reference from one configured object to another. At each position, and its neighbors, ask:

1. Is this position evaluated at all, under each mode and each outcome of the earlier siblings?
2. In what order relative to its siblings (read the call log)?
3. If two positions both fail, which failure decides the answer?
4. Is a value computed and then discarded?

Write the model's prediction for each probe *before* sending it, including "the model has no opinion here". A
position where the model has no opinion is a gap in the model, not a question about the reference.

For alternatives to test against the answers, the useful family for each pair of things the model evaluates is: "the
other one first", "both always", "the second only when needed", "the first failure wins", "the last failure wins".

## 4. Metamorphic relations over structure

A metamorphic relation pairs two inputs whose answers must agree (or must differ in a known way). Its strength is
that **the relation is the oracle**: the reference answers `x` and `T(x)`, and a pair that breaks the relation is a
finding whatever each answer is. You do not need to know the right answer.

Relations over single values (swap operands, negate, move a value to another carrier) are the common ones. The ones
that catch structural errors in a model are relations over the **shape** of the input:

| Relation | Transformation |
| --- | --- |
| Irrelevant addition | Add a part whose own outcome should not matter (a rule that never applies, a node with each possible outcome, a no-op stage), before and after the existing parts |
| Permutation | Reorder siblings at every level: list items, rules, configuration entries, keys in a document, uploads, batch items |
| Wrapping and flattening | Put one part inside a container of one; flatten a container of one into its parent |
| Duplication | Duplicate a part, with and without a new identity |
| Splitting and merging | Split one part with a disjunction into two parts; merge two parts into one |
| Placement | Move a condition, a setting or a check to another level where the documentation says it means the same |
| Round trip | Apply a change and its inverse; apply two independent changes in either order; export then import |
| Cross-endpoint consistency | Ask two endpoints that must agree (a batch versus single calls, a filter versus individual checks, a preview versus the real call) |

**Identity deserves its own pass.** Whatever the input names or identifies (rule names, ids, keys, file names, tenant
codes), ask what happens on a collision: two parts with the same identity in one input, an identity reused across
scopes or uploads, two spellings of one identity (case, whitespace, leading zeros). Implementations keyed by a map
silently keep the first or the last; implementations keyed by a list keep both. The model usually never had to decide,
because nobody sent a collision.

For each pair, record the model's prediction in three classes:

- **assumed**: the model keeps the relation, and no recorded answer pins one side. The model took the equivalence for
  granted; ask first.
- **predicted**: the model breaks the relation, and one side is unpinned. The model predicts a quirk; ask to confirm.
- **pinned**: both sides have answers. Nothing to ask.

A negative control matters here more than anywhere: break the model's composition on purpose (reverse one order,
drop one child) and check that the relation generator reports it. A generator that cannot see a planted defect will
not see a real one.

## 5. Exception lists are footprints of one mechanism

When a recorded answer disagrees with the model, the cheapest fix is the narrowest one: a special case, a list of
states or operators where an exception applies. Each such patch is right for the answers behind it, so nothing in the
correction loop pushes towards the general rule. Mutants try only alternatives of the same narrow shape (one more or
one fewer list element), never the general rule.

Treat every hand-written exception list in the model as a symptom:

1. **Inventory** every decision whose value is a list, set or table of cases rather than one choice, and every
   condition that tests membership in a hand-written tuple. Note the answers behind each element.
2. **Cluster** lists that look like the footprint of one mechanism: same operations, same positions, same phase of
   processing.
3. **Propose general rules.** A mechanism is usually about *when* something happens (order, phase, laziness), *what
   form* a value has at that moment (converted, split, trimmed, wrapped in a collection), or *which* of two competing
   outcomes is kept. Write several candidates per cluster, including ones that predict more exceptions than the list.
4. **Score** each candidate against the recorded answers. A candidate that fits all of them and differs from the list
   somewhere is a live hypothesis: find its minimal distinguishing question.

## 6. Implementation idioms as standing alternatives

If you know what the reference is built on (its language, framework, serialization library, database), you know a
great deal about its edge behavior without reading a line of it: whatever the library calls it most likely uses do at
each boundary. Trimming, splitting, emptiness checks, number parsing and printing, case comparison, collection order,
pattern matching, templating, JSON binding, error-to-status mapping: each has a short list of common behaviors per
platform.

1. Find every **handling point** in the model where a value crosses one of these boundaries.
2. Tag each with the idioms that apply and the alternative the model uses now.
3. Make each other common alternative a **standing hypothesis** at that point. Run it against the recorded answers;
   survivors need a distinguishing question.
4. Add a check that fails when a new handling point appears without a tag, so the catalogue keeps up with the model.

`references/idioms.md` lists the common alternatives per area and per platform (JVM, .NET, Python, Go, JavaScript,
and the usual JSON and SQL layers). Read the section for the reference's platform; if the platform is unknown, the
idioms of two or three plausible platforms are still a better hypothesis space than the one choice the model made.

## 7. Boundaries on representation, not on meaning

Generators and coverage tools usually classify inputs by what they *mean* to the model, and then cover each class
once. If the reference treats two spellings of the same value differently, both land in one class and the difference
is never asked. **Take spelling classes from the input format** (the grammar, the schema, the protocol), never from
the model's value rules.

- **Spellings of one value.** For each token kind of the input grammar: every way the format accepts the same value
  and the nearest texts it refuses. Numbers: leading and trailing zeros, sign, exponent, integer versus decimal form,
  long digit strings, limits of the common integer and floating types. Strings: empty, one space, other whitespace
  classes (tab, form feed, vertical tab, non-breaking space, line separators), quotes, the format's own separators,
  non-ASCII letters with case mappings.
- **The same values on the data side**: as a JSON number, a JSON string, a number inside a string, a one-element list.
- **A state matrix for every field**: absent, `null`, `""`, blank (each whitespace class), the value with leading and
  trailing whitespace of each class, the value in another JSON type.
- **Ask in opposite pairs**: two spellings of one value at the same position in one question, so a difference between
  them is a finding whatever each answer is.

Measure coverage by spelling class per position and report the classes no recorded answer has ever sent.

## 8. Combinations over raw input features

Combinatorial coverage is only as good as its factors. Factors computed by the model (its own outcome of a node, its
own classification of neighbors) are subject to §1. Define factors that can be read off the **input alone**,
by a function that never calls the model:

- shape: depth, number of parts at each level, parts per container;
- for each part: its index among its siblings, and the kinds of siblings before and after it;
- modes and settings at each level;
- which positions hold external references, and of which declared kind;
- request kind, caller kind, tenant or context shape;
- an **order index**: which permutation of the uploaded parts this is, relative to a canonical order.

Cover pairs by default and triples for any triple that includes order or sibling kind. Then compare with the
model-derived coverage: combinations the model counts as covered but the raw measure does not are where the model's
classification merges inputs that differ in raw features. Each needs a question or a reason grounded in the
documentation, not in the model's code.

## 9. An independent second model

The strongest way to see outside one model is a second model built without looking at the first, with a
deliberately different architecture, that also fits the recorded answers. Where the two disagree on inputs no answer
covers, at least one of them is wrong, and the input is worth a question.

- **Isolation.** The author of the second model (a person or an agent in a separate session) reads only the recorded
  answers, the input format and grammar, and the documentation. Not the first model's code, its decision list, or its
  reports. Write down what was read.
- **A different architecture**, chosen to fail differently: if the first model is a declarative table of cases, write
  the second as an imperative interpreter in the style of the reference's platform (mutable context, explicit reads,
  exceptions caught at chosen levels, values held as the platform's runtime types). If the first is imperative, make
  the second declarative. Where the answers leave a choice open, the second model takes the option most natural for
  its architecture and records it.
- **The differential harness** runs both models on every generator from §3, §4, §7, and §8, shrinks each
  disagreement to a minimal input, and clusters by the shrunk shape. A cluster pinned by an answer means one model is
  wrong; fix it from the answer, in that model only. An open cluster is a question.
- **Keep them independent** afterwards: each model is fixed only from answers, never from reading the other.

This costs the most and pays the most. Start it early, in parallel, because it needs no other technique to begin, and
wire the harness in last, when the generators exist.

## 10. Questions you already have, and answers you can get for free

Before generating new questions, harvest the cheap ones:

- **Surviving mutants and live hypotheses are questions.** Each survivor of the model's own mutation run is an
  alternative no answer has ruled out. Its minimal distinguishing input is a ready-made question; the mutation run is
  blind to *missing* rules (§1), but it is a good source of questions about the rules the model does have.
- **Run the model's own suites against the reference.** A combinatorial or property suite generated for the model
  measures the model; sent to the reference, the same inputs become questions. Where sending all of them is too
  expensive, send the ones the model's predictions are least certain about.
- **Shadow traffic.** If production or staging traffic can be mirrored to both the reference and the model, every
  request becomes an answer at no question cost. Compare raw, not only through the parity normalizer (§2), and
  record which inputs disagreed. Mirror a request that writes only after its effects are isolated: the shadow side
  gets its own storage and stubs its downstream calls (payments, messages, emails, other services), or only reads
  are mirrored. A mirrored write that reaches shared state duplicates an order or a payment for real.
- **Ask people.** The reference's owners, its users and its operations runbooks answer some questions faster than a
  round: configuration flags, library versions, known quirks. Treat what they say as a hypothesis until an answer
  confirms it.

## 11. Choosing and budgeting the questions

Each technique produces more candidate questions than any round can afford. Select them like this:

- **Score a question by what its answer separates**: the number of live hypotheses, alternatives, relation pairs,
  spelling classes and raw combinations it distinguishes. Greedy cover over that score picks a small round with high
  yield. **Weight it by the cost of being wrong**: a wrong "allow" in an access check, a wrong amount in billing, or a
  silently dropped record costs more than a wrong error message, so questions near those outcomes go first.
- **Ask in sequences where the reference keeps state.** Caches, sessions, revocations, retries, counters and
  "first upload versus re-upload" are invisible to single requests. A question can be a short sequence (set, read,
  change, read again) with each step's answer recorded.
- **Give each question its separating context** (§2) and, where the outcome is a failure, a twin that tells the
  kind of failure apart.
- **Prefer questions whose answer is a finding either way**: opposite pairs, metamorphic pairs, and questions on
  weakly pinned decisions.
- **Put a fixed budget on each round** and say what the next round would add. A round that only confirms what the
  model predicts everywhere is a signal that the generators, not the model, have saturated.
- **Before sending, check that the questions are valid inputs** to the reference (a rejected upload answers nothing
  about evaluation), and that a fresh environment can run them in any order; a question that depends on a previous
  one's side effects is two questions. When several probes share one input to save budget, make sure every candidate
  rule would accept that input, so one rejection cannot hide the other probes.
- **Give the round a drop order.** Budgets get cut after planning; tier the questions (must, should, may) so the cut
  removes the least separating ones, not whatever came last.
- **Bracket the round with controls.** Replay a few already-answered questions at the start and at the end. A changed
  answer means the reference or its environment drifted during the round, and the round's other answers need a second
  look.
- **Keep shared environments safe.** Questions that change configuration go to an isolated namespace (a test tenant,
  jurisdiction, account) when one exists. Never overwrite configuration that other recorded answers depend on; if
  you must, export it first and restore it after.
- **Know when to stop asking.** A stopping rule is a statement about the questions, not about a score on the model:
  for example, the last round produced no *new* decisions (only flipped values, or nothing), every open hypothesis
  has been asked, and `n` independent random questions drawn from a stated input distribution all agreed, which
  bounds the disagreement rate on that distribution at about `3/n` with 95% confidence and says nothing about inputs
  outside it.
- **After the answers arrive**, every answer that contradicts the model goes back through §0 and §5: which
  decision changes, and is the change a new value of an existing decision or a new decision? New decisions are the
  sign that a technique found something the old measures could not.

## 12. Reporting what you found

A finding about a black box is a claim about something nobody on the team can read, so state its evidence:

- **observed**: a recorded answer shows it; cite the question and the answer;
- **inferred**: it follows from observed answers under a stated assumption; name the assumption;
- **hypothesis**: a live alternative no answer has separated yet; give the question that would.

Keep the observation and the mechanism apart. "A month of `"08"` is rejected" is observed; "it parses numbers with a
leading zero as octal" is a mechanism, and so is "it accepts only months that match a pattern". Before writing a
mechanism down, ask the one question that tells it from its nearest alternative (here, `"07"`: an octal reading
accepts it); otherwise report the observation and list both mechanisms as hypotheses. A reimplementation built on
the wrong mechanism passes the observed cases and fails the next ones.

Give each finding its minimal input, the reference version that answered, and the model decision it changes. Do not
present a hypothesis as behavior, and do not change the model on one.

## Checklist

- [ ] The model's decisions are listed with the answer behind each, and guesses are marked.
- [ ] Each adequacy measure in use has a named source for its dimensions that is not the model.
- [ ] Every probe separates the outcomes its decision claims; the comparator's merged classes are known.
- [ ] Evaluation order and laziness are asked with sentinels and poison, read through side channels.
- [ ] Structural metamorphic relations, including permutation, exist, with a negative control.
- [ ] Hand-written exception lists have candidate general rules.
- [ ] Handling points carry the platform's idiom alternatives.
- [ ] Spelling classes and field state matrices come from the format, and are asked in opposite pairs.
- [ ] Combinatorial coverage includes raw features and order.
- [ ] A second, isolated model exists or is planned, with a differential harness.
- [ ] Identity collisions (duplicate names and ids, reuse across scopes) are asked.
- [ ] Surviving mutants, the model's own suites, shadow traffic and the reference's owners have been harvested; mirrored
  writes reach no shared storage or downstream system.
- [ ] Each round is budgeted, greedily selected, tiered for cuts, bracketed by control replays, safe for shared
  environments, and every question is valid and independent.
- [ ] There is a stopping rule stated in terms of questions and answers, not of a score on the model.
- [ ] Findings are labeled observed, inferred, or hypothesis, with the reference version, and mechanisms are separated
  from observations.

## Worked example: a shipping-fee rules engine

A team is porting a shipping-fee service. They have a model of it and 3,000 recorded answers, and the model matches
all of them. Its mutation score is 97% and its pairwise coverage over "zone × carrier × weight band × promotion" is
complete.

- **§1.** Every factor of the pairwise measure is a concept the model computes ("weight band" is the model's own
  banding). The mutants are the alternatives the authors listed. Neither measure could notice a rule the authors did
  not think of.
- **§2.** The parity suite sorts fee lines before comparing, so the order of fee lines is unpinned. "Rule did not
  apply" and "rule errored" both produce the base fee; no answer separates them. A wrapper adds a second rule that adds
  a known surcharge only when evaluation reaches it.
- **§3.** Each rule calls a rate service; its mock logs calls. Poisoning the rate service at each rule position
  shows whether later rules are evaluated after an earlier one already decided the fee.
- **§4.** Reordering the rules in the configuration, adding a rule that never matches, and splitting a rule with
  "zone A or zone B" into two rules are all asked. The model predicts all three keep the fee.
- **§6.** The service is on the JVM, so weights pass through a number parser: `"1.0"`, `"1"`, `"1e0"` and `"+1"`
  become a standing hypothesis at the weight handling point, and so do trimmed versus untrimmed carrier codes.
- **§7.** The weight field gets its state matrix (absent, `null`, `""`, `" "`, `"\t1\t"`, `1` as a number,
  `"1"` as a string), asked in opposite pairs.
- **§11.** 120 candidate questions are scored; the 40 with the highest separation form the round. Each answer
  that contradicts the model is classified as a flipped decision or a new one.
