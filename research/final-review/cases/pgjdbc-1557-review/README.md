# Case: review pgjdbc/pgjdbc#1557, a validation timeout that replaces the caller's

A case for `final-review` on the rule about two limits on one quantity (`research/final-review/coupled-limits.md`),
in code rather than configuration. The input is [pgjdbc/pgjdbc#1557][pr] at `0e1f4829b7`, five commits (one a merge
of master) on top of `8495127fe0`, one file, `PgConnection.java`, +16 −10. The prompt quotes the pull request
description as the task statement.

`isValid(timeout)` saves the caller's network timeout, sets it to `timeout * 1000`, runs the check query with
`setQueryTimeout(timeout)`, and restores the saved value. Two defects of the class, both confirmed later:

1. **The caller's limit is replaced, not narrowed.** A connection opened with a 500 ms network timeout waits the full
   `isValid(2)`, and `isValid(0)` removes the bound. [pgjdbc/pgjdbc#2022][fix1] fixed it by taking the smaller value.
2. **Two limits of the same length on the same query.** The network timeout and the query timeout start together
   with the same value, so either may fire first: one closes the connection, the other sends a cancel over a new one.
   [pgjdbc/pgjdbc#1943][fix2] removed the `setQueryTimeout` call.

## Checks

1. **The caller's limit replaced.** Pass: a substantive finding that a smaller network timeout the caller set is
   raised or removed during the check, with the request to keep the smaller one. Partial: only the `isValid(0)` case.
2. **The two equal limits.** Pass: a substantive finding that the query timeout and the network timeout fire together,
   so which one wins decides between a cancel and a closed connection.

## Skill parts

- `final-review`: `SKILL.md` §2 item *Boundaries, partitions, and the negative control*
- `test-authoring`: `SKILL.md` §4, §11
- `english-developer-style`: loaded, not checked

## Files

`repo`, `base`, `head`, `prompt.md`, and `<model>/<label>/…`, as in `authz-agent-122-review`. `main-<n>` ran the skills
at `1b34f27` (before this rule), `final-<n>` at `75f0709` (the committed rule).

## Results, 2026-10-23

| Model | Arm | Check 1 | Check 2 | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | main | pass, pass | pass, pass | 0.43, 0.45 |
| Opus | final | pass, pass | fail, pass | 0.48, 0.45 |
| Haiku | main | fail, partial | fail, fail | 0.06, 0.03 |
| Haiku | final | pass, fail | fail, pass | 0.09, 0.12 |

Opus finds both defects without the rule. With it, `final-1` lists the query timeout as a second limit and judges that
it does not conflict, so it loses check 2; `final-2` files it, in the rule's words. Haiku gains one finding per run with
the rule, a different one in each: `final-1` the replaced limit, `final-2` the equal pair.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/1557
[fix1]: https://github.com/pgjdbc/pgjdbc/pull/2022
[fix2]: https://github.com/pgjdbc/pgjdbc/pull/1943

## Results of the `series` arm, 2026-10-23

`series-<n>` ran every rule in the series that adds the questions of `research/final-review/change-reach.md` and the
question on a replaced mechanism, in the wording of 2026-10-23: before two sentences were cut from the paragraphs on
values users already pass and on parallel paths, and before the question on a replaced mechanism was shortened. Opus,
two runs, as a no-regression check against the arm named below.

| Check | `series-1` | `series-2` | `final` |
| --- | --- | --- | --- |
| 1 | pass | pass | pass, pass |
| 2 | pass | pass | fail, pass |

No regression; both runs file the equal pair of check 2. Cost 0.42 and 0.36 USD against 0.48 and 0.45.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with the runner also supplying
`apm-authoring`. In this tree §2a takes the input for an added instruction from what the artifact names, labels it
before writing a row, and replaces an empty table with the line `Added instructions: <n>, no rows.` Graded by reading
`result.md`. Opus and Haiku, two runs each. The results stand for tree `8545c2eb` as well, without a new run: it differs
from `796a9b8d` by one sentence in step 2 of the §2a table of added instructions, and no run of this case writes that
table, because the change adds no instruction.

| Model | Check 1 | Check 2 | Cost, USD | Words |
| --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, pass | 0.52, 0.49 | 1600, 1537 |
| Haiku | fail, partial | fail, fail | 0.10, 0.10 | 1108, 1073 |

- **Opus.** Both runs file the replaced `socketTimeout` and ask to keep the smaller value (`instr-1`, `result.md:85`:
  "`isValid(0)` and large timeouts replace the user's `socketTimeout` with a longer one", with "Only lower the timeout";
  `instr-2`, `result.md:67-68`: "Use the smaller of the two non-zero limits" and "A `timeout` larger than the configured
  `socketTimeout` raises the limit for the call"). Both file the equal pair (`instr-1`, `result.md:86`: "Socket timeout
  equal to query timeout races the cancel; on a slow but healthy server the connection is aborted instead of cancelled";
  `instr-2`, `result.md:72`: "The read timeout equals the query timeout and races the cancel timer").
- **Haiku `instr-1`.** Both checks fail. No finding says the caller's `socketTimeout` is raised or removed; `isValid(0)`
  appears only as an untested claim, "`isValid(0)` leaves the network timeout unchanged. **No test.**" (`result.md:15`).
  The equal pair is noted under item 3 and left open: "The statement's query timeout is set to the same `timeout` in
  seconds" and "I did not verify whether that cancel runs off the calling thread" (`result.md:25`); no row files it.
- **Haiku `instr-2`.** Check 1 is partial. F3 (`result.md:52`) states both cases, "For `isValid(0)` SO_TIMEOUT becomes 0
  (infinite)" and "For `isValid(n)` with a longer `n` it lengthens the bound", but asks to keep the configured value
  only for `timeout == 0` and to "State the precedence" otherwise. Check 2 fails: item 3 says the query timeout "is set
  to the same value and does not unblock the caller's blocked read, so it does not bound the call" (`result.md:28`),
  which drops the race instead of filing it.

Against tree `1b1ebc3e` Opus is unchanged, 4 of 4 passes, at a cost of 0.52, 0.49 against 0.67, 0.51 and 1600, 1537
words against 1538, 1597. Haiku loses three of its passes: `instr-1` falls from pass, pass to fail, fail, and `instr-2`
from fail, pass to partial, fail, so the one gain is check 1 of `instr-2`, from fail to partial. Haiku cost 0.10, 0.10
against 0.12, 0.06, and its reports shrank from 1258, 1436 to 1108, 1073 words. The change is a Java diff, and no run
writes a table of added instructions or the `Added instructions:` line. Haiku `instr-2` has a `### Not findings` list
(`result.md:56`), but it names items 1, 4 and 5 that had nothing to review, not instructions.
