# Trial on the verifyReleaseDependencies failure message

The error-text rules tried on the change that motivated them: the failure message of the Gradle task
`verifyReleaseDependencies` in [apache/jmeter#6846](https://github.com/apache/jmeter/pull/6846), which compares the jars
of the binary release with a committed list and a total size limit. In the session that wrote that task, the writer
loaded this skill, judged it irrelevant because every rule spoke of hosts, operators, and alerts, and wrote a message
that listed the added and removed modules but said neither where the limit lives, nor how to find which dependency
brought a module in, nor what to tell the reviewer.

## Method

The fixture is JMeter at commit `5b08ff8cc7` of that pull request, without its git history, with the failure message
replaced by `throw GradleException("Release dependencies do not match")`. Each writer got the same prompt
(`prompt_ab-verify-release-deps.md`): replace that message with a proper one, without running Gradle. The prompt does
not name the skill; only the trigger in the project instructions and the skill's description can lead a writer to it.

| Arm | Skill installed in `.claude/skills/` | Trigger in the project instructions |
| --- | --- | --- |
| `old` | The skill before this change | The instruction before this change |
| `new` | The skill with tool mode | The instruction that names build, CLI, and CI failure messages |

Both arms also had `english-developer-style` installed. Each cell ran three times, on Haiku 5.5 and on Sonnet 5.5, with
`claude -p --setting-sources project`, on 2026-10-26. The `new` arm is the first version of the change, a "tool mode"
for build scripts, CLIs, and CI checks; before it was committed, its example was aligned with the pull request's current
message, and the accept row's detection and the review checklist were tightened. The revision below generalized it.

Round 1 leaked: `--setting-sources project` does not stop user-level `CLAUDE.md` files, and the user-level rules of the
machine carried the new trigger, so both arms saw it. Round 1 therefore compares only the skill body. Round 2 disabled
every `CLAUDE.md` with `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` and passed the project instructions through
`--append-system-prompt-file`; the session transcripts confirm that no user-level rule reached it. Round 2 is the
trial of trigger and body together.

Each of the 24 messages was rendered for one scenario (one module added, the size 1 MiB over the limit), shuffled under
a letter code, and scored by an Opus judge that saw no arm, model, or round, against a fact ledger built from what an
agent holding only the output needs, not from the skill text. Each rendered message was also handed to a fresh Haiku
with no repository and no tools, asked to explain the failure to the user; the judge scored those replies too. The six
round 2 writers of the `old` arm and the one `new` writer that skipped the skill were then resumed and asked why. A
stray fixture script recreated two run directories while their writers worked; the edit of one was recovered from the
recreated directory and the other run was repeated.

## Results

| Round | Model | Arm | Loaded the skill | Mean ledger score of 12 | All 12 rows | Broken accept command | Mean reader score of 4 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2 | Haiku | old | 0/3 | 6.3 | 0/3 | 1/3 | 2.8 |
| 2 | Haiku | new | 2/3 | 9.7 | 2/3 | 1/3 | 3.3 |
| 2 | Sonnet | old | 0/3 | 7.7 | 0/3 | 0/3 | 3.3 |
| 2 | Sonnet | new | 3/3 | 11.8 | 2/3 | 0/3 | 4.0 |
| 1 | Haiku | old | 1/3 | 5.7 | 0/3 | 2/3 | 2.8 |
| 1 | Haiku | new | 3/3 | 11.8 | 2/3 | 0/3 | 4.0 |
| 1 | Sonnet | old | 3/3 | 8.3 | 0/3 | 0/3 | 3.5 |
| 1 | Sonnet | new | 3/3 | 11.8 | 2/3 | 0/3 | 4.0 |

The per-run scores, the judge's notes, and the key are in `results_ab-verify-release-deps-judge.md`.

- **The old trigger loaded the skill for nobody.** In round 2, none of the six `old` writers loaded it. Asked why, all
  six quoted the same words: the trigger and the description speak of "a call to a logger, a metric, or a span", and a
  thrown `GradleException` is none of these. Four of the six also said they had not weighed the skill before skipping
  it, and three that the old trigger's "what a new failure … should emit" could have covered the task, so the quoted
  words explain the skip after the fact rather than record a decision. Several said they would have loaded it had it
  named build failures or exception messages.
- **The new trigger loaded it for five of six.** The Haiku writer that skipped it said the trigger "describes this task
  closely" and that it missed it; its message scored 5, the same as the weakest `old` messages.
- **Loading the old body does not help.** In round 1, where both arms saw the new trigger, the three Sonnet writers of
  the `old` arm loaded the old skill and still scored 8.3: without the error-text rules, the skill says nothing about
  this message.
- **Every run that loaded the new skill scored at least 11.5 of 12; every other run scored at most 9.** The rows the
  skill adds are the ones the `old` messages miss: why the check exists, where `total-size-limit` lives, a diagnose
  command, what to do when the change is not intended, and what to put in the pull request.
- **Without the skill, the accept command was wrong in four messages.** `./gradlew :src:dist -PupdateExpectedJars`
  names a project, not the task, and all four readers passed it on to the user. Readers of the weaker messages also
  invented the expected file's path and a false claim that the update leaves the size limit as it is.
- **The worked example is copied.** The example in the new skill is adapted from the message this fixture removed, and
  the rendered scenario uses the example's module and sizes. Ten of the eleven messages written with the new skill
  repeat its sentence on what the check catches, and one Sonnet message reproduces the example almost word for word. The
  trial therefore shows that the new arm reaches the example's message, not that the table alone yields one for another
  check. An example in the skill also has to be true of any message it is pasted into.
- **Two `new` messages kept a placeholder** (`--dependency <module>` in one, `<group:module>` in the other) although the
  module was known, which the table's detection names; one invented a value format for `total-size-limit`.

## Revision: rules for any error text

The first version framed the rules as a mode of build scripts, CLIs, and CI checks. The rules apply to any error text,
so the revision moved them into section 2, under what a message on the caller's channel carries, and made the table's
detections general. It dropped rows that all 12 `old` messages met without the skill: the expected file, the module
list, and the sizes. It kept the rows the `old` messages missed: why the check exists, the key together with its file, a
diagnose command with the values filled in, each way out runnable as printed, and what to report. All 12 `old` messages
also gave each branch its own text, but per-branch remedies are not common sense: arm `gen`, whose example had one
branch, lost them, so they stay a detection under each way out.

Revisions ran in the setup of round 2, three writers each on Haiku and Sonnet, all with the general trigger. Arm `gen`
cut the example to the added module; `gen2` put back the size branch and gave each branch its own remedy; `gen3` added a
library example with no override, made the detections general, and cut the paragraph that restated the reader model.
Three fresh blind judges scored them, each beside the previous arm (`results_ab-verify-release-deps-revision.md`): judge
2 scored `old`, `new`, and `gen`; judge 3 `new`, `gen`, and `gen2`; judge 4 `gen2` and `gen3`; judge 5 `gen3` and
`gen4`. Scores from different judges differ by up to a point for the same message, so each comparison below is within
one judge.

| Judge | Model | Arm | Loaded the skill | Mean ledger score of 12 | Key with its file | Which jars grew | Own remedy per branch | Mean reader score of 4 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | Haiku | new | 2/3 | 9.5 | 2/3 | 2/3 | 2/3 | 3.3 |
| 3 | Haiku | gen | 3/3 | 9.7 | 0/3 | 1/3 | 0/3 | 4.0 |
| 3 | Haiku | gen2 | 3/3 | 10.8 | 3/3 | 2/3 | 2/3 | 4.0 |
| 3 | Sonnet | new | 3/3 | 11.8 | 3/3 | 3/3 | 3/3 | 4.0 |
| 3 | Sonnet | gen | 3/3 | 11.0 | 1/3 | 2/3 | 1/3 | 4.0 |
| 3 | Sonnet | gen2 | 3/3 | 11.8 | 3/3 | 3/3 | 2/3 | 4.0 |
| 4 | Haiku | gen2 | 3/3 | 10.7 | 3/3 | 1/3 | 1/3 | 4.0 |
| 4 | Haiku | gen3 | 3/3 | 11.7 | 3/3 | 2/3 | 3/3 | 4.0 |
| 4 | Sonnet | gen2 | 3/3 | 11.8 | 3/3 | 3/3 | 2/3 | 4.0 |
| 4 | Sonnet | gen3 | 3/3 | 11.5 | 3/3 | 2/3 | 3/3 | 3.8 |
| 5 | Haiku | gen3 | 3/3 | 11.7 | | | | 4.0 |
| 5 | Haiku | gen4 | 3/3 | 12.0 | | | | 4.0 |
| 5 | Sonnet | gen3 | 3/3 | 11.2 | | | | 3.8 |
| 5 | Sonnet | gen4 | 3/3 | 11.8 | | | | 3.8 |

- **The general trigger loaded the skill for all 24 writers of the revisions.** It names an exception and an error
  response, and keeps a failed build, CLI command, or CI check as examples.
- **The writers follow the example more than the table.** With the size branch cut from the example, the messages lost
  the key's file and the list of grown jars, although a table row names the first as a defect. With the branch back,
  both returned.
- **The general version holds on this fixture.** `gen3`, with general detections and a library example first, scored as
  `gen2` did; `ab-max-result-buffer.md` tries it on a library exception.
- **A copied phrase can be false.** Two messages said "external jars", taken from the example, while the fixture's code
  sums the JMeter jars too; a sentence warning against reuse did not stop the second. The shipped example no longer says
  "external".

Arm `gen4` added what `ab-max-result-buffer.md` showed missing on a library exception: where a limit refused the
operation, the way-out row asks for the change to the request beside raising the limit, and a size-limit example
replaces the setting example. Judge 5 scored it beside `gen3` and found no loss on this fixture (12.0 and 11.8 against
11.7 and 11.2). The shipped skill is `gen4` plus two later edits tried only on the pgjdbc fixture: remedies must work as
the code stands, and an example value that would fail the same check is a defect.

## Not covered

The trials exercised one Gradle check that compares the tree with a committed list. The revision states the rules for
any error text, and `ab-max-result-buffer.md` tried them on a library exception; no run tried them on an error response
or a CLI command that rejects its input, nor on a lint, a pre-commit hook, a CI step outside the build tool, or a tool
outside the JVM. The removed-module branch was never rendered. No control run shows that the trigger stays off for a
task that only rewords a message. The writers whose messages missed rows were not asked why. Case 5.5 of
`phase2_result.md` §5, a library parser exception over a configured limit, now owes the rows of the caller's-channel
table; the pass that produced the six cases was not re-run for it.

## Files

```text
prompt_ab-verify-release-deps.md                 the writer prompt, both arms' instructions, the ledger, and the render, reader, and judge prompts
results_ab-verify-release-deps-judge.md          the judge's table, the key, and the aggregates
results_ab-verify-release-deps-messages.md       each rendered message with its reader reply and its diff
results_ab-verify-release-deps-interrogation.md  the seven writers that did not load the skill, asked why
results_ab-verify-release-deps-revision.md       the revision's arms, both later judges, and the revision's messages
```
