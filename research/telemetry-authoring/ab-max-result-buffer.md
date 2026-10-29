# Trial on the maxResultBuffer exception of pgjdbc

The error-text rules tried on a library exception. The JDBC driver pgjdbc throws a `PSQLException` when a result set
grows past the `maxResultBuffer` connection property, and drops the connection before the throw. The trial asks whether
the rules written for a build check carry over, whether the first version, which framed them as a mode of build scripts,
CLIs, and CI checks, serves a library exception worse than the general version, and, in three further arms, how the
skill can make writers offer a change to the request beside raising the limit.

## Method

The fixture is pgjdbc at commit `874745258455be18708d91a24cc98a0ae5ae85a3`, without its git history, with the message in
`PGStream.increaseByteCounter` replaced by `GT.tr("Result set exceeded maxResultBuffer")`. Each writer got the same
prompt (`prompt_ab-max-result-buffer.md`): replace that message with a proper one, without running Gradle. The prompt
does not name the skill. The project instructions were the repository's `AGENTS.md`, which has its own section on error
messages, plus the arm's trigger, passed with every user-level `CLAUDE.md` disabled as in round 2 of
`ab-verify-release-deps.md`.

| Arm | Skill | Trigger |
| --- | --- | --- |
| `old` | The skill before this change | The instruction before this change |
| `new` | The build-tool mode of the first commit | Names build, CLI, and CI failure messages |
| `final` | The caller's-channel subsection of the second commit | Names the text of an exception or error |
| `final2` | `final`, whose way-out row also asks for the change to the request that brings it under a limit, with a size-limit example in place of the setting example | As `final` |
| `final3` | `final2`, whose way-out row asks for remedies that work as the code stands, with a value form in the example | As `final` |
| `final4` | `final3`, whose detection adds an example value that would fail the same check | As `final` |

Each arm ran three times on Haiku 5.5 and on Sonnet 5.5, on 2026-10-26. Each message was rendered for one scenario
(`maxResultBuffer=100M`, the running total at 100003200 bytes, en_US). A fresh Haiku with no source explained each
message to a user.

The first judges were told that fetch-size advice is unverified, because the running total seemed to reset only after a
simple-protocol query. A separate check against a live server showed otherwise: the Sync that ends each extended execute
and each fetch queues an entry that takes the same branch, so the total resets at every ReadyForQuery, and
`Statement.setFetchSize` with autocommit off keeps each fetch under the limit. The ledger was corrected, and one Opus
judge rescored all 36 messages under it, shuffled under letter codes, seeing no arm or model. The tables below are
that judge's; the per-run scores, its notes, the key, and every message with its reader reply and diff are in
`results_ab-max-result-buffer.md`.

## Results

| Model | Arm | Loaded the skill | Mean ledger score of 8 | Why the limit exists | Property named as a connection property | Value forms | Alternative to raising the limit | Nothing wrong or partial |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Haiku | old | 0/3 | 5.0 | 0/3 | 0/3 | 0/3 | 2/3 | 2/3 |
| Haiku | new | 0/3 | 5.8 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| Haiku | final | 3/3 | 7.2 | 2/3 | 2/3 | 2/3 | 1/3 | 3/3 |
| Haiku | final4 | 3/3 | 7.5 | 3/3 | 2/3 | 1/3 | 3/3 | 3/3 |
| Sonnet | old | 0/3 | 6.0 | 0/3 | 1/3 | 0/3 | 3/3 | 2/3 |
| Sonnet | new | 3/3 | 5.3 | 0/3 | 1/3 | 0/3 | 1/3 | 0/3 |
| Sonnet | final | 3/3 | 7.3 | 3/3 | 3/3 | 2/3 | 2/3 | 1/3 |
| Sonnet | final4 | 3/3 | 7.8 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |

`final2` scored 7.7 and 7.2, and `final3` 7.0 and 7.5; `results_ab-max-result-buffer.md` has their rows.

- **The build-tool framing did not reach a library exception.** Haiku did not load the first version for this message.
  Sonnet loaded it, and none of its three messages said why the limit exists; all three advised a fetch size without
  saying that autocommit must be off, and two offered no other way out.
- **The general version carried over.** Every `final` writer loaded the skill, and the messages added what the `old`
  and `new` messages lacked: why the limit exists (5 of 6, against 0 of 12), that `maxResultBuffer` is a connection
  property (5 of 6, against 2 of 12), and a value form such as `200M` or `10p` (4 of 6, against 0 of 12).
- **Asking for a change to the request needed a guard.** `final` offered an alternative to raising the limit in 3 of 6
  messages. Asking for the change to the request (`final2`) raised that to 6 of 6, but the size-limit example, which
  carried no value, cut the value forms to 1 of 6. Asking for remedies that work as the code stands, with a value in the
  example (`final3`), brought the value forms back to 6 of 6, and three messages then offered a "raised" limit no larger
  than the current one (`100M` against 100000000 bytes, `64M`), as two `final` messages had. Naming that case as a
  defect (`final4`) left no wrong or partial advice in six messages, with an alternative in all six.
- **The reader test did not separate the arms.** Readers scored 3.3 to 4.0 everywhere, because a reader that knows
  PostgreSQL JDBC fills the gaps from general knowledge. Three messages called the running total "a result set of N
  bytes", and readers of such messages took it for the size of the whole result and said a small increase would do;
  the total is where reading stopped. A number whose meaning the message does not state can mislead, but these runs are
  not enough to make that a rule.

## Not covered

One library exception, in one driver. No run covers an error response, a CLI command that rejects its input, or a
non-JVM library. The writers whose messages missed rows were not asked why.

## Files

```text
prompt_ab-max-result-buffer.md    the writer prompt, the arms' instructions and subsections, both ledgers, and the render, reader, and judge prompts
results_ab-max-result-buffer.md   the skills each writer invoked, the consolidated judge, the key, and every message with its reader reply and diff
```
