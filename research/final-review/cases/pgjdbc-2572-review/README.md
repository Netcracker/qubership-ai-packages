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
