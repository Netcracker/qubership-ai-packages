# Case: review pgjdbc/pgjdbc#2572, a timeout the stream wrapper ignores

A case for `final-review` on the rule about two limits on one quantity (`research/final-review/coupled-limits.md`),
in code rather than configuration. The input is [pgjdbc/pgjdbc#2572][pr] at `7f63448463`, six commits on top of
`6e453aaead`, five files: the new `sslResponseTimeout` property (default 5000 ms), its docs, and
`ConnectionFactoryImpl.enableSSL`, which sets it with `getSocket().setSoTimeout(...)` around the read of the reply to
the SSL request. The prompt quotes the pull request description as the task statement.

The setting has no effect at the default `socketTimeout=0`. `VisibleBufferedInputStream` rethrows a
`SocketTimeoutException` only when `timeoutRequested` is set, and only `PGStream.setNetworkTimeout` sets it; the raw
`setSoTimeout` leaves it false, so the read retries every 5 s and the connection still hangs. The fix of the cancel
path for the same pattern, `QueryExecutorBase`'s call to `setNetworkTimeout`, is already in the repository.
[pgjdbc/pgjdbc#2683][issue] reported it, and [pgjdbc/pgjdbc#2687][fix] fixed it. The comment in the diff covers the
other pair, `socketTimeout` against the new setting, and does not hint at the wrapper.

## Checks

1. **The wrapper ignores the new timeout.** Pass: a substantive finding that the raw `setSoTimeout` bypasses
   `setNetworkTimeout`, so at the default `socketTimeout` the timeout is swallowed and the read does not end.

## Skill parts

- `final-review`: `SKILL.md` §2 item *Boundaries, partitions, and the negative control*, item *Siblings of the change*
- `test-authoring`: `SKILL.md` §4, §11
- `english-developer-style`: loaded, not checked

## Files

`repo`, `base`, `head`, `prompt.md`, and `<model>/<label>/…`, as in `authz-agent-122-review`. `main-<n>` ran the skills
at `1b34f27` (before this rule), `final-<n>` at `75f0709` (the committed rule).

## Results, 2026-10-23

| Model | Arm | Check 1 | Cost, USD |
| --- | --- | --- | --- |
| Opus | main | pass, pass | 0.68, 0.70 |
| Opus | final | pass, fail | 0.83, 0.50 |
| Haiku | main | fail, fail | 0.09, 0.06 |
| Haiku | final | fail, fail | 0.13, 0.10 |

Opus finds it without the rule, by reading `setNetworkTimeout` and the wrapper; `final-2` reports only missing tests.
Haiku misses it in both arms; with the rule it reports other pairs instead: `socketTimeout` capping the new setting,
which the diff states in a comment, and `loginTimeout` capping it, which the docs do not say.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/2572
[issue]: https://github.com/pgjdbc/pgjdbc/issues/2683
[fix]: https://github.com/pgjdbc/pgjdbc/pull/2687

## Results of the `series` arm, 2026-10-23

`series-<n>` ran every rule in the series that adds the questions of `research/final-review/change-reach.md` and the
question on a replaced mechanism, in the wording of 2026-10-23: before two sentences were cut from the paragraphs on
values users already pass and on parallel paths, and before the question on a replaced mechanism was shortened. Opus,
two runs, as a no-regression check against the arm named below.

| Check | `series-1` | `series-2` | `final` |
| --- | --- | --- | --- |
| 1 | pass | fail | pass, fail |

The same split as `final`. `series-2` files the bypass of `PGStream.setNetworkTimeout` as taste, and the question on a
replaced mechanism leads it to a false failure time: it says a silent peer now fails after 5 s, where at the default
`socketTimeout=0` `VisibleBufferedInputStream.readMore` swallows the timeout. Cost 0.61 and 0.77 USD against 0.83 and
0.50.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with the runner also supplying
`apm-authoring`. In this tree §2a takes the input for an added instruction from what the artifact names, labels it
before writing a row, and replaces an empty table with the line `Added instructions: <n>, no rows.` Graded by reading
`result.md`. Opus and Haiku, two runs each.

| Model | Run | Check 1 | Cost, USD | Words |
| --- | --- | --- | --- | --- |
| Opus | `instr-1` | fail | 0.84 | 1518 |
| Opus | `instr-2` | fail | 0.59 | 1811 |
| Haiku | `instr-1` | pass | 0.25 | 1339 |
| Haiku | `instr-2` | pass | 0.23 | 1606 |

Both Haiku runs find the bypass and file it as substantive. `instr-1` finding 1 (`result.md:67`): "The raw
`setSoTimeout` bypasses the `timeoutRequested` flag, so `readMore` swallows the `SocketTimeoutException` and
`ensureBytes` loops", with the request to use `pgStream.setNetworkTimeout(...)`. `instr-2` traces the same path in four
steps under item 3 and files it as S1, "Substantive (blocker)" (`result.md:96`): "The timeout is set on the raw socket,
so `timeoutRequested` stays false and `readMore` swallows the timeout, looping forever".

Opus `instr-1` never mentions `setNetworkTimeout` or the wrapper. It reports missing tests, `sslResponseTimeout=0`, a
negative value, the unstated default, GSS and the TLS handshake, and states "Users on `socketTimeout=0` (the default)
move from "wait forever" to 5 s" (`result.md:43`), which is false. Opus `instr-2` names the pattern but files it as
taste: "Bypasses `PGStream.get/setNetworkTimeout`" (`result.md:118`), with no word on the swallowed timeout, and it
states "**New:** about 5 s" for a silent server (`result.md:61`), which is false at the default `socketTimeout`.

Against tree `1b1ebc3e` one grade changed: Haiku `instr-2` rose from fail to pass, so Haiku now passes in both runs.
Opus is fail, fail in both trees, with the same pair of misses: `instr-1` silent on the wrapper, `instr-2` filing it as
taste. Opus cost 0.84, 0.59 against 0.73, 0.54, at 1518, 1811 words against 1765, 1867. Haiku cost 0.25, 0.23 against
0.28, 0.19, at 1339, 1606 words against 1562, 1171; the longer `instr-2` carries the four-step trace of the bypass and a
table of how the old and new code fail on each fault. The change is a Java diff, and no run writes a table of added
instructions or the `Added instructions:` line.
