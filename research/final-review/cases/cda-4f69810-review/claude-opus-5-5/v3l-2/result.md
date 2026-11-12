# Final review: `d79c43d..4f69810`, "stop drafts from inventing symptoms and translating hunks"

**Inputs.** The change is one commit. It edits the `change-description-authoring` skill (SKILL.md and README.md) and bumps the version from 1.3.0 to 1.4.0 in three manifests. No task statement was handed over, so the claimed cases come from the commit message alone. There is no previous report, so there is no carry-over table.

This is a change with no code, so every item below uses the §2a analogue. The skills loaded were `english-developer-style` and `apm-authoring` (the repository's copy, under `agent-packages/apm-authoring`). I did not run the drift script: the change has only Markdown and YAML, and the script has no members to parse.

`S` below stands for `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
*Analogue: what each changed file says about another file, about a slot, or about the skill's own examples.*

- **The What-slot example still puts an outcome in prose (`S:353-354`).** The *After* example reads: "a caller that runs before startup completes fails at once instead of opening the pool on demand." Two things contradict it:
  - The explanation two lines below (`S:358-359`) sends that same outcome (the `IllegalStateException` from `Pool.acquire()`) to "User-visible changes".
  - `S:231` says "A fact stated in slot 3 is not restated in slot 2."

  The commit message also claims the example "no longer puts an outcome in prose", and the example still does. An agent copying the exemplar will state the outcome twice.
- **The open-question rule conflicts with §4 rule 5 (`S:199`, `S:458-463` against `S:608-611`).** The new rule keeps a question only a maintainer can settle "in the Scope slot as a question". Rule 5 applies when the merge setting copies the description into the commit body. That body has no Scope slot, and rule 5 says to "keep reviewer-only content out of it".
  - A maintainer-only question is reviewer-only content.
  - Under rule 5 the two rules ask for opposite things, and an agent following the new one puts an open question into `git log`.
- **The README is stricter than the skill (`README.md:29-31`).** It says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `S:98-101` explicitly allows a consequence derived from the code, once it is traced to what a caller sees and marked as derived. Someone choosing the package from the README gets the impression that derived consequences are banned.
- **The new qualifier and its example disagree (`S:94-95`, taste).** The slot now reads "no symptom *by construction*", but its example is still "a leak on an error path with nothing logged". A leak does have a symptom (memory grows), so the example leaves "by construction" undefined. That invites the stated-absence wording the rule was written to stop.
- No sentence narrates the change ("now", "no longer") in a way that misleads. The "now" in `S:288` and the examples quotes the bad drafts or the code in the example.

## Item 2: claimed cases covered
*Analogue: each claim in the commit message, against the section that handles it.*

| Claim in the commit message | Where the skill handles it |
| --- | --- |
| Slot 2: an audit-found defect names what found it and ends the sentence | `S:91-93`, the skip cell `S:81`, checklist `S:803-806` |
| A changelog entry for it names the condition alone | `S:475` |
| A derived consequence only when traced and marked as derived | `S:98-101`, checklist `S:804` |
| "Say so" kept only for no symptom by construction | `S:94-96` |
| What slot: a sentence recovered from one hunk is translation; a public identifier is named once | `S:342-347` |
| §7 points to the What-slot rule | `S:763-764` |
| §2 asks for "what changed that the diff does not show" | `S:288` |
| Rejected alternatives: the mechanism is a fact about the merged code | `S:370-373`, checklist `S:832-833` |
| Open questions: answered, kept in Scope, or dropped | `S:458-465`, `S:199`, checklist `S:834-837` |
| Bad and good examples for slot 2 and the What slot | `S:92-93`, `S:349-355` |
| The What example "no longer puts an outcome in prose" | **Not met** (Item 1) |
| "The examples avoid the pull request the drafts were written for" | Cannot check; the drafts are not in the repository |

- **Detection of each rule.** Each new rule has a checklist line. The Translation line does not check the rule it is attached to (see Item 5).
- **Commands.** None of the changed lines contains a command.
- **Hunks that no sentence claims:**
  - The three version bumps follow the repository's convention (`agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md:338`), as in the previous three commits. Not a finding.
  - The README paragraph is claimed by no sentence (taste): one clause in the message would cover it.

## Item 3: boundaries, partitions, and the negative control

**Partitions with no evidence.** The rules change three genres: the commit body (`S:81`, `S:91`), the PR description, and the changelog (`S:475`). The trial covered only "blind drafts of one pull request description", so the commit-body and changelog wordings have no run behind them.

**Pre-existing state.** The package installs over 1.3.0, and the instructions file is unchanged, so no earlier state is left behind for the change to meet. None.

**Added instructions: 9.** These cover `:81`/`:91`, `:98`, `:199`/`:458`, `:288`, `:342`, `:370`, `:475`, `:763` and the checklist lines that restate them. One gets a row:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `S:91` "name what found it and end the sentence there" (and `S:475` "the condition alone") | An audit-found defect that the new regression test reproduces, with an assertion or `TRAP:` line | "An audit of X found this." The literal R3 greps is dropped from the body and the changelog | "unless a test or a report has since shown the symptom; then quote it as slot 2 asks" |

Not findings:
- `S:98`: "stated as derived, not observed" already ends this one.
- `S:370`: the clause about the change removing the obstacle limits it.
- `S:342`: the identifier exception at `:345` ends it.
- `S:288`, `S:763`: these narrow the rules and add no instruction.
- `S:199`/`:458` under rule 5 is filed under Item 1 as a conflict.

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, and whether the repository's gate passes.*

- Each rule sits in the section of the slot it governs, and its checklist line is in §8.
- None of the sentences is generic tutorial content.
- `python3 scripts/check-skill-descriptions.py` printed `ok: all 27 skill descriptions are within 1020 characters`.
- I did not run `apm pack --check-versions`, because it needs `uvx` and the network. Both versions read 1.4.0 by inspection.

None.

## Item 4: names by content, not by position

None. The headings and cross-references use the skill's existing convention of numbered slots and section numbers. `S:357` "the first sentence" points to a two-sentence example right above it, which is harmless.

## Item 5: the failure report
*Analogue: whether each rule's detection reaches the rule, and detects that rule rather than a weaker property.*

**The Translation checklist line is weaker than its rule (`S:826-827`).** The line says: "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted." It fails the rule in both directions:
- It lets through the case the rule names. `S:343` says a sentence is translation "even under a lead-in that states a reason". The diff does not show that reason, so the *Before* example at `S:349-351` survives the test.
- It deletes what the rule keeps. A sentence that names an added or renamed public identifier is recoverable from the diff, but `S:345-347` says to name it once.

The Symptom, Alternatives and Discussion lines do reach their rules.

## Item 6: what the writer says it verified

The commit states counts from fifteen blind Opus drafts for each defect. It also says, in its own words, what those counts do not cover:
- The drafts ran against version 1.0.1, before the outcome slot and the length rules landed.
- The current open-question rule and the rewritten What example were not re-run.
- Hunk translation persists in about one draft in two.
- With the final symptom wording the sample is two drafts.

Missing from it:
- **No noise control.** There is no run on an input where the added items are noise, such as a defect with an observed symptom and no open question, and so no check that the output there did not grow.
- **The rewritten exemplar fails its own rule.** Applying the What rule to its own *After* example fails on the outcome in prose (Item 1).

## Item 7: siblings of the change

- **Surfaces that route to the skill.** The marketplace and `apm.yml` descriptions are unchanged, and that is correct because the scope did not widen. The instructions file only triggers loading, and `references/merge-model.md` mentions "symptom" only generically.
- **§7b list of finding names.** "unsupported claim" and "diff paraphrased" already cover the new failure kinds.
- **Sibling packages.** `problem-report-authoring` and `english-developer-style` state no rule about audit-found defects or stating an absent symptom.

None.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The What *After* states the outcome in prose, against `:231`, its own explanation, and the commit message's claim | Substantive | `S:353-354` | Rewrite the first sentence to give the reason (opening at startup) without the caller's failure, and leave that failure to the User-visible line |
| The Scope-slot open question conflicts with §4 rule 5's "keep reviewer-only content out" | Substantive | `S:199`, `S:458-463`, `S:608-611` | Say where a maintainer-only question goes when rule 5 applies (a PR comment, not the description) |
| The Translation checklist line passes the reason-led *Before* and deletes the public-identifier sentence | Substantive | `S:826-827` | Make the test "the sentence states an edit the diff shows, with or without a reason", except a public identifier |
| The audit rule drops a symptom that a regression test or a report has since shown | Substantive | `S:91`, `S:475` | Add the clause in the Item 3 table row |
| Commit-body and changelog wordings have no trial; no noise control was run | Substantive | `S:81`, `S:91`, `S:475` | Run drafts of a commit body and a changelog entry, and one input where the items are noise, and check that its length did not grow |
| The README bans derived consequences that the skill allows | Substantive | `README.md:29-31` | Add "unless traced and marked as derived", or drop "a predicted failure" |
| The "by construction" qualifier is paired with a leak example that has a symptom | Taste | `S:94-95` | An example with no symptom by construction (for example, a redundant guard) |
| The README hunk is claimed by no sentence in the commit message | Taste | `README.md:26-32` | One clause in the message |

I did not check the prose for style alone, did not run `apm pack` (it needs the network), and could not check the drafts and the pull request the commit message cites, because they are not in the repository.
