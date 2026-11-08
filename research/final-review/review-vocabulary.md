# Terms, callees, and dense sentences in a doc-comment review

Evidence for four rules of `final-review` *Item 1: comments consistent with the code and with each other* (the
doc-comment checklist run over every added comment, the sentence a reader has to parse twice, the inline comment read
against its callee, and the terms the change introduces), and for three rules of `javadoc-authoring`, which its four
sibling doc-comment skills carry under the same section numbers: *A scope is not a definition* in §1, *No definition
through other members* in §3, and *A phrase fixed once is fixed everywhere* in §7a.

## Where they come from

[uber/NullAway#2069][pr] adds the JSpecify `NO_CHANGE` nullness for `? extends T` and for enhanced-for reads of `T`. The
author's session wrote it with `final-review` and `javadoc-authoring` installed. The maintainer's review of commit
`fc9b07b30` left fifteen comments on the documentation and the names in four main files, and four more on code. The
fifteen are the ground truth below.

| ID | Location at `fc9b07b30` | What the maintainer asked for |
| --- | --- | --- |
| G1 | `Nullness.java:89` | Say how `NULL_NO_CHANGE` at a holder differs from `NO_CHANGE` at an assignment |
| G2 | `Nullness.java:124` | Rename `isAtMost` to `isLessThanOrEqualTo` |
| G3 | `GenericsChecks.java:4758` | "A location that receives a value" should be "a location that can be assigned a value" |
| G4 | `GenericsChecks.java:4759` | A cast is not like the other locations in the list |
| G5 | `GenericsChecks.java:4764` | A stacked relative clause, "that the type arguments of the supertypes it is inherited through supply" |
| G6 | `GenericsChecks.java:4766` | "The method whose return receives the value" should be "the method that returns the value" |
| G7 | `GenericsChecks.java:4809` | Define the value through the specification, "a subtype of `T` that reaches `T` through upper bounds" |
| G8 | `GenericsChecks.java:4813` | "Every sink, and dataflow wherever a value moves to another holder" should be "at every pseudo-assignment" |
| G9 | `GenericsChecks.java:4861` | The phrase of G5, repeated |
| G10 | `GenericsChecks.java:4997` | An inline comment that restates what the callee already handles |
| G11 | `TypeSubstitutionUtils.java:100` | No comment on why `types.capture(types.skipTypeVars(t, true))` is used |
| G12 | `GenericsChecks.java:4573` | An `@return` the called overload cannot produce |
| G13 | `AccessPathNullnessPropagation.java:1294` | A summary defined through two private neighbors rather than through its result |
| G14 | `AccessPathNullnessPropagation.java:1295` | Rename `valueHeldByPath` |
| G15 | `AccessPathNullnessPropagation.java:1319` | Rename `valueHeldAs`, and rewrite its comment as in G13 |

[pr]: https://github.com/uber/NullAway/pull/2069

Six of the fifteen (G1, G3, G6, G8, G14, G15) turn on one vocabulary the change coined: holder, held, sink, moves,
receives. None of these words has a source in JSpecify, in the JLS, or in NullAway before the change.

## What was run

Every run used Opus in a fresh subagent with no access to GitHub or to the pull request, on a repository with no history
past the change's base. A blind judge in another subagent graded each set of reports.

| Experiment | Arms | Runs | What was graded |
| --- | --- | --- | --- |
| 1. Review of the change at `fc9b07b30` | installed skills; the rules of this note; the rules of this note plus a *Member names* rule | 3 per arm per round, 3 rounds | G1 to G15 hit, partial, or miss; every other finding valid, code, or noise |
| 2. Comments stripped and written again | installed skills; the rules of this note | 3 per arm | 13 items, G1, G3 to G13, and G15 restated for the member each names, plus coined terms |
| 3. Six member names replaced by placeholders and chosen again | installed skills; the rules of this note | 3 per arm | Each name good, fair, or poor; each first sentence pass or fail |

## Findings

Experiment 1, mean of three runs per arm, hits out of fifteen and findings the judge graded noise. Each round had its
own judge, so compare arms within a round.

| Round | Installed skills | First draft of the rules | Rules with *Member names* | Ported rules, plus two parts |
| --- | --- | --- | --- | --- |
| 1 | 0.7 hits, 1.0 noise, 214k to 223k tokens | 4.0 hits, 2.3 noise, 227k to 238k tokens | | |
| 2 | 1.0 hits, 1.0 noise | 4.0 hits, 2.0 noise | 4.3 hits, 3.3 noise | |
| 3 | | | 4.3 hits, 3.3 noise | 4.3 hits, 2.0 noise |

The ported text is the *Ported rules, plus two parts* column's minus those two parts: the paragraph in `final-review`
that compared each new member name with what a caller gets back, and a paragraph in `english-developer-style` on when a
word becomes a term. Both were present in every run of that column. Round 3 has no installed-skills arm, and its
reviewer could also fetch the JSpecify specification, so every comparison with the installed skills below is within
round 1 or round 2. Token counts were recorded in round 1 only. The per-run reports and verdicts of every round are in
the experiment directory, outside this repository; the grades per comment of round 1 are below, as hit (h), partial (p),
or miss (m), with A for the installed skills and B for the first draft of the rules.

| Run | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | G11 | G12 | G13 | G14 | G15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | m | m | m | m | m | m | m | m | m | m | m | p | m | m | m |
| A2 | p | m | p | p | p | m | p | h | p | m | p | p | p | p | p |
| A3 | p | m | p | m | m | m | p | h | m | m | m | p | p | m | p |
| B1 | p | m | p | m | h | m | p | h | h | m | p | p | h | p | p |
| B2 | p | m | p | m | h | m | p | h | h | m | p | p | h | m | m |
| B3 | p | m | m | m | h | m | p | h | h | m | p | p | h | m | m |

1. **A review with these rules finds more of the maintainer's comments.** In round 2, the two arms with the rules hit
   4.0 and 4.3 of fifteen against 1.0 for the installed skills; in round 1, 4.0 against 0.7, at about 7.5% more tokens
   (means of 217k and 233k per run) and 1.3 more findings graded noise per run. In round 1, G5, G9, and G13 are hit in
   every run with the rules and in none with the installed skills, which reach them at most as a partial hit that names
   a different word in the same sentence. In the six runs of the two later drafts (rounds 2 and 3), G13 is hit in five.
2. **Some comments no rule found.** G1 and G2 in no run; G14 and G15 only as part of the rename the term finding asks
   for; G10 in no run of round 1, and in three of the six runs of the two later drafts, which added the callee check.
3. **A rule for member names added noise and no hits.** A *Member names* section in `javadoc-authoring` and its check
   in `final-review` did not change G2, G14, or G15, and its clause on loosely named predicates produced the extra
   noise of the *Rules with Member names* column. It is not part of this change.
4. **Written from scratch, the comments avoid most defects with either skill set.** In experiment 2 the original passes
   5 of 13 items; rewrites pass 10.7 with the installed skills and 10.3 with these rules. In experiment 3 the original
   has 1 good name of 8; rewrites have 4.3 and 5.3. The defects came from the context the change was written in: the
   pull request description, the test comments, and the names chosen along the way.
5. **A word the model reaches for on its own survives the writing rules.** "A location that receives a value" appeared
   in three of six rewrites in experiment 2, with either skill set and with no source in the code shown to the writer.
   The term check of `final-review` reports it at review time; a row in the repository's own list of words to avoid
   would stop it at writing time.

## Threats

Three runs per arm. One judge per round, and two judges disagreed on partial hits by up to four. The rubric of
experiments 2 and 3 is drawn from the original's defects, so the original fails it by construction. One model family
writes, reviews, and judges. The last round of experiment 1 changed the rule and allowed the reviewer to fetch the
JSpecify specification at once. Every hit counted here comes from one Java change about a type system; the regression
cases below reviewed changes in Go, Python, and workflow YAML, but they check for noise and lost findings, not for hits.
The text was revised after review and not measured again on this change. Some revisions report less: the term check
accepts a word that the field defines, or that the code or its documentation already uses for the same concept, and a
parameter's name; the callee check keeps a comment that gives a reason specific to its call site. Others report more: a
summary defined through any other member, not only a private one, fails; the callee check reads every call in the code a
comment sits on, not only the next statement; and a dense sentence is any shape from the developer-style skill's table
that a reader has to parse twice, not three named shapes.

## Regression cases

The shipped text, final-review tree `ca8233fb` with the doc-comment skills at 1.4.0, ran on the regression cases whose
skill parts it touches, two runs per model, graded by reading; each case README has the grades under the `vocab` arm or
1.4.0. The other cases say in their README why they did not run.

- `textkit-page-count-review`, the noise control: the change adds no comment, and no run files anything under the
  comments item. All four runs fail the 800-word limit (Opus 835 and 817, where `cond` wrote 796 and 774); the Opus
  answer to the comments item is shorter than in `cond`, and the extra words are in other items. One Sonnet run lists
  the new questions with empty answers, 167 words against 124 and 97.
- `pgjdbc-1557-review`: 3 of 4 grades pass (two checks, two runs), against 4 of 4 in `instr`. One run turns the
  uncommented-expression question into a request for a comment on the second timeout and files the race as taste; the
  `final` arm split the same way before these rules.
- `pgjdbc-2572-review`: 1 of 2 runs passes, against 0 of 2 in `instr`; the passing run reaches the bypass from the
  uncommented-expression question as well. The dense-sentence findings are on a real comma splice.
- `camunda-44166-review`: 4 of 4 pass. One Opus run calls "SaaS Monorepo" a coined term although the polled workflow's
  file name carries it.
- `authz-agent-122-review`: Opus passes every check but one partial; Sonnet `vocab-2` fails three checks that both
  Sonnet `cond` runs passed, with a short comments item, which reads as variance. The new rules found two dense
  sentences and a wrong reason in a comment. Two term findings are weak: "part" where the helper's parameter is
  `component`, and "stand", where the run asks to rename the chart.
- The `members` case of each doc-comment skill: 20 of 20 runs pass every check. The scope rule has no specification to
  act on; the rule against a definition through other members reached the eviction-time method and jsdoc's `load`, and
  every run states the result.

The 36 runs cost about 21 USD: 14.4 for final-review, 6.7 for the doc-comment skills.
