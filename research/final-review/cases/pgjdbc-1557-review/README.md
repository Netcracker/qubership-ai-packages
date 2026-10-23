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
