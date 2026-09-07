# Trial: a checklist review in a fresh subagent, against the reviews two pull requests received

Run on 2026-09-06. The question: when the agent that wrote a change cannot see what it left out, does a second agent
with a clean context and a fixed form find it, and at what cost? The form is the `final-review` skill: six items
(comments consistent with the code and each other; every claimed case covered by a named test; boundaries and the
negative control; names by content rather than position; the failure report; the evidence that the tests can fail),
each answered in writing, "none" allowed, findings labelled substantive, taste, or churn. A script lists the members
whose code or doc comment moved, so that a comment nobody edited above changed code is on the list.

## Setup

Six headless sessions, each reviewing one change with the skill, `test-authoring`, `javadoc-authoring`, and
`english-developer-style` installed, given the task statement and told not to edit or run the suite. Four targets:
the head of [PR #4405](https://github.com/pgjdbc/pgjdbc/pull/4405) and of
[PR #4404](https://github.com/pgjdbc/pgjdbc/pull/4404) as their author pushed them, before review, where the
maintainer's LLM-assisted review is the ground truth; and the two weakest outputs of the earlier trials (Sonnet with a
plan, on each fix), where my own reading is the ground truth. Sonnet on all four; Opus on the two pull-request heads.

## Results

| Run | Cost | Minutes | Substantive findings | Taste |
| --- | --- | --- | --- | --- |
| Sonnet, PR 4405 head | $1.26 | 6.2 | `assertTrue(a == b)`; "A last one"; the reported-versus-actual case claimed and untested; no red-run evidence | – |
| Opus, PR 4405 head | $3.70 | 7.7 | the above, plus "used to send" attributes the change to the server; the class comment promises every inlined parameter while the hex `bytea` path is broken (the neighbouring defect, found and demonstrated on the server); a unit test on `toString` for the unreproducible case; no empty value | trailing backslash; `quoteAndCast` summary; case ids |
| Sonnet, PR 4404 head | $1.34 | 6.5 | `assertTrue(a == b)`; no warning assertion, with the argument that the rival fix would pass every test; the `DATA` comment's UTF-8 claim, with `0xe6` checked against a decoder | abbreviated literal; duplicated rationale |
| Opus, PR 4404 head | $2.05 | 5.5 | `assertTrue(a == b)`; no warning assertion, plus the note that the rival form is already used in `quoteAndCast`; the deprecated overload's stated reason is now incomplete; the `DATA` comment promises escaping checks the hex path never exercises | `toPGLiteral` summary shows one form; class summary; case ids; whitespace pair |
| Sonnet, generated 4404 (Sonnet-with-plan) | $1.29 | 8.2 | a sentence in the new helper's Javadoc that exempts the backslash-first case from corruption, which the task statement contradicts | on-controls for two branches; `0x7f`; "above" in a message |
| Sonnet, generated 4405 (Sonnet-with-plan) | $1.38 | 7.2 | `quoteAndCast` summary names one form; "keeps the value right where" reads as a place | extended-mode control; empty value |

Against the two reviews the pull requests received, on the findings that concern tests and comments:

| Review finding | Sonnet | Opus |
| --- | --- | --- |
| `assertTrue(a == b)` hides the operands (both PRs) | found, both | found, both |
| No warning assertion; the design's stated reason is untested (4404) | found | found |
| "A last one" (4405) | found | found, as a membership list |
| The `DATA` comment merges two UTF-8 cases (4404) | found, exactly | a different real flaw in the same comment |
| "used to send" puts the change in the server (4405) | missed, and endorsed the sentence | found |
| Nothing pins the literal text; no unit test (4405) | missed | reached, by a different route |
| The deprecated overload is silent (4404) | missed | found |
| `toPGLiteral` summary unconditional; input list incomplete (4404) | missed | summary as taste; list missed |
| "shape"; the helper's name; CHANGELOG length; three copies of one explanation | missed | missed |

On the two generated outputs, whose defects I knew: the review found a real comment error in each, and missed the
two largest test defects of the 4404 output (no warning assertion, no version guard) and the placement defect of the
4405 output (a second unit class with the fixture copied). Those three are not items on the form as first written:
the form asks whether claimed cases are covered and whether the negative control exists, and the writer's task
statement did not claim the warning; it has no item for the level, for placement, or for an environment guard.

## Reading

The pass earns its cost. At about $1.30 and seven minutes, Sonnet finds every mechanical item on the form (the
boolean assertion, the ordinal, the missing warning assertion where the design reason is stated, a factually wrong
comment) with evidence, and every report answers every item and ends with what it did not check. Opus, at two to
three times the cost, finds the findings that need the code read against the claim rather than the form: the
neighbouring defect, the deprecated sibling, the false subject of a history sentence, the promise in a comment that
the test data cannot keep. Neither model reports churn; the taste findings are labelled as such and read as
declinable.

Three gaps were in the form, not in the models, and the form now carries them: the level (a test that runs in every
job, through the public API, named when only a server-bound test exists), placement beside the unit's existing tests
with a shared fixture, and a skip rather than an error where the environment cannot provide a setting or a version;
plus, under the failure report, a bare boolean assertion with no message. One gap stays with the model: Sonnet praised
"used to send" as the permitted history form without checking whose behavior changed, which is the comparison the
doc-comment skill asks for and a form cannot force.

Recommendation: run it with Sonnet by default, at the end of every coding task that added or changed tests, and with
Opus when the change touches a public contract or a deprecated sibling.

## Addendum: the siblings item

After the trial the form gained item 7, siblings of the change: for each helper the fix touched, its other call
sites (`sb callers` where the tool is installed, `git grep` otherwise), each judged for the same defect. One Sonnet
run on the PR #4405 head with the extended form, $1.63 and 8.6 minutes: it listed every caller of
`Utils.escapeLiteral`, excluded the public `PgConnection.escapeLiteral` (the caller supplies the quotes) and
`PasswordUtil` (hardcodes the setting on) with the right reasons, and named `setSchema`, `setClientInfo`'s
`application_name`, and the startup `application_name` in `ConnectionFactoryImpl` as carrying the same defect, which
are the three sites the pull request's review had named. It also noted that the commit message mentions the four
sites only to explain why the helper took no prefix parameter, not to say whether the warning still fires there. The
same run, now carrying item 3a, asked for the in-process unit test on `SimpleParameterList.toString` that the earlier
Sonnet run had missed.
