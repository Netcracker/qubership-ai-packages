# A/B trial: the skill on three Go pull requests

Run on 2026-09-07 against two Netcracker Go repositories, with the skill in the role-split layout and the trigger
sentence that makes the reference files be read. Three pull requests, chosen for what their tests have to establish:

- mediation-client [#125](https://github.com/Netcracker/qubership-core-lib-go-paas-mediation-client/pull/125): in
  dual mode (`legacy-ingress,gateway-api-default`) `CreateRoute` and `DeleteRoute` wrapped the API server's error in
  `NewInternalError(fmt.Errorf("%s", status))`, so an `AlreadyExists` reached the caller as `Internal` with the text
  repeated. The fix wraps with `%w`. The test space is the matrix HTTPRoute × Ingress × {ok, AlreadyExists, Internal}
  and the property that the error kind survives; the pull request's own tests call the unexported
  `dualModeRouteError` directly and assert substrings.
- facade-operator [#256](https://github.com/Netcracker/qubership-core-facade-operator/pull/256): new almost pure
  functions in `pkg/templates`: a GEP-2257 duration check on `HTTP_ROUTE_REQUEST_IDLE_TIMEOUT`, a fallback to the
  larger of two nginx timeout annotations, custom HTTPRoute filters parsed from JSON in an environment variable.
  Partitions and boundaries.
- mediation-client [#137](https://github.com/Netcracker/qubership-core-lib-go-paas-mediation-client/pull/137): a
  goroutine that decorates a watch channel. The pull request's tests carry a `time.Sleep` and a `select` whose timeout
  branch is empty, so the last test passes against any code. A negative benchmark: the task is to rewrite them.

## Setup

Nine headless `claude -p` sessions with `--setting-sources project`, each in a detached worktree at the pull
request's base commit with the pull request's non-test Go files applied as one commit and a `CLAUDE.md` line naming
the stack (Go `testing`, testify `require`, fake clients with `PrependReactor`). The *skill* arm has
`test-authoring`, `godoc-authoring`, and `english-developer-style` under `.claude/` with their trigger paragraphs;
the *no skill* arm has the same minus `test-authoring`. The *write* prompt gives the pull request's title and body,
the diff, and "write the tests this change needs, and update the existing tests the change made wrong"; the
*rewrite* prompt puts the worktree at the pull request's head, names the tests it added, and asks for them to be
rewritten so that they establish what the change did. No skill and no test is named in the prompt. One run per cell.
Scripts, prompts, transcripts, and the metrics extractor are in
`claude-skills-research/experiments/20260907-test-authoring-go-ab/`; total cost $40.22.

Two oracles, run here after the sessions: the tests with the main files reverted to the base commit (*red on base*),
and hand-made mutants applied to the fixed code, each a one-line change a reviewer would call a bug, run against every
cell and against the pull request's own tests (*o125*, *o137*, *o256*). Red on base is a build failure where a test
calls a function the change introduced, and says nothing then; the mutants are the oracle for those cells.

## #125: the error matrix

| Cell | Arm | Model | Tests added or rewritten | Reaches the code through | Error assertions | Red on base | Mutants killed (of 4) | Cost | Min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| o125 | the pull request | | 6 | `dualModeRouteError` called directly in 3 tests | 14 `Contains(err.Error())`, 4 `IsAlreadyExists`/`IsInternalError` | | 3 | | |
| g01 | skill | Opus | 12 | `CreateRoute`, `UpdateOrCreateRoute`, `DeleteRoute` only | 14 `ErrorIs`, 11 `EqualError`, 6 kind checks, 3 `Contains` | 16 of 178 | 4 | $5.72 | 8.7 |
| g02 | skill | Sonnet | 2 new, 10 existing rewritten | public API only | 12 `ErrorIs`, 1 `Contains` | 12 of 173 | 4 | $2.56 | 10.7 |
| g03 | no skill | Opus | 11 | one test calls `dualModeRouteError` directly | 19 `ErrorIs`, 20 `EqualError`, 4 `Contains` | does not compile | 4 | $4.05 | 8.9 |
| g04 | no skill | Sonnet | 5 | public API only | 12 `Contains`, 3 kind checks | 9 of 176 | 3 | $2.40 | 6.8 |
| g09 | skill, rewrite | Opus | 6 removed, 7 added | public API only; the 3 direct calls removed | 7 `ErrorIs`, 2 `Contains`; a `t.Run` table over the three gateway modes | 6 of 183 | 4 | $3.24 | 7.0 |

The mutant that separates the sets replaces `%w` with `%v` on the single-mode ingress error, so the kind is lost
where the message is unchanged. The pull request's tests and the no-skill Sonnet cell miss it, because both assert
substrings of the message; every set that asserts `ErrorIs` or the kind catches it. The other three mutants (the
dual-mode wrap lost, the hint added on every failure, the delete error taken from the wrong resource) are caught by
all six sets, the pull request's included: on this change the pull request's tests are not weak, they are bound to
the wrong thing. That binding is the finding of the trial: both skill cells and the rewrite reach the change only
through the public methods, the no-skill Opus cell calls the unexported helper once and its tests cannot be compiled
against the base commit, and the pull request calls it three times. §6's rule is the one that moved.

`EqualError` on the whole message in g01 and g03 is §7's change detector for wording, in both arms; the skill did not
stop Opus from pinning the text, only from pinning it *instead of* the kind.

## #256: partitions and boundaries

| Cell | Arm | Model | Test functions / subtests | Direct calls of unexported functions | Environment | Mutants killed (of 5) | Cost | Min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| o256 | the pull request | | 15 / 0 | 4 (`buildHTTPRouteCustomFilters`) | `t.Setenv` | 4 | | |
| g05 | skill | Opus | 9 / 22 | 3 | `t.Setenv` 15 | 5 | $6.71 | 12.5 |
| g06 | skill | Sonnet | 12 / 25 | 17 | `t.Setenv` 19, **`os.Setenv` 4** | 5 | $4.11 | 13.8 |
| g07 | no skill | Opus | 15 / 8 | 2 | `t.Setenv` 12 | 5 | $6.77 | 14.5 |

The mutant that separates the sets removes the duration check in `ValidateGatewayAPIConfig`; the pull request's tests
survive it because they test the same check one layer down, in `resolveStreamIdleTimeout`, and every cell catches it
because every cell tested the public method the operator calls at startup. The other four mutants (the fallback in
milliseconds, the smaller timeout chosen instead of the larger, filter validation skipped, the gRPC policy dropped)
are caught by all four sets. So the cells are one property ahead of the pull request, and the arms do not differ on
what the tests catch. They differ on shape: Sonnet with the skill reached the pure functions directly seventeen
times and set two variables with `os.Setenv`, which outlives the test and is §8's shared-state row, while Opus in
both arms went through `NewIngressTemplateBuilder` and `BuildHTTPRouteTemplate` and kept the environment in
`t.Setenv`. Opus without the skill produced the most test functions and the fewest subtests; the skill cell named
each case in a `t.Run` string (`HTTP_ROUTE_REQUEST_IDLE_TIMEOUT wins over the legacy proxy timeouts`).

## #137: the negative benchmark

| Set | `time.Sleep` | Empty timeout branch | Tests | Mutants killed (of 3) |
| --- | --- | --- | --- | --- |
| o137, the pull request | 1 | 1 (the third test passes whether or not the channel closes) | 3 on the decorator, 1 changed on `WatchRoutes` | 3 |
| g08, skill, Opus, $4.66, 21 min | 0 | 0 | 6 on the decorator, 2 on `WatchRoutes` through the fake watcher | 3 |

The rewrite removed the sleep and the empty branch, added an ordering test over three events, a test that a
non-HTTPRoute object passes through unchanged, and separate tests for the channel closing on source close and on
`StopWatching`, ran the package under `-race`, and did not add `goleak`. The three mutants (no conversion, stop not
forwarded, output never closed) are caught by both sets, so the pull request's tests were not blind to these; what
the rewrite bought is a set whose third test can fail, and whose failure names the event that did not arrive.

## What the trial says about the skill

- The rule that moved on Go is §6, test through the public API: every skill cell reached the change through the
  exported methods, the pull request's tests and the no-skill Opus cell reached the unexported helper. That is what
  makes a test survive the next refactoring and compile against the base commit.
- Error semantics over message strings (§7) moved for Sonnet, which is where it was missing: 12 `ErrorIs` against 12
  `Contains` between the two Sonnet cells on #125, and one mutant caught because of it. Opus asserted error identity
  in both arms.
- Where the pull request's tests were already sound (#256, #137 on the mutants), the skill changed shape rather than
  strength: named subtests, no sleep, no empty timeout branch, no `os.Setenv` in the Opus cell.
- Sonnet with the skill still calls unexported functions directly (17 times on #256) and leaked environment through
  `os.Setenv`; §6 and §8 are stated, and Sonnet did not apply them to a pure function it could reach by name. It did
  read the reference files in two of its three cells.
- The rewrite task is the cheaper way to use the skill on an existing pull request: $3.24 and seven minutes turned
  the #125 tests from helper-bound substring checks into public-API kind checks, and the result is the set that
  catches every mutant here.

The rewritten sets are on branches `ab/pr125-tests-rewritten` (g09) and `ab/pr137-tests-rewritten` (g08) in the
experiment's worktrees, with bundles under the experiment directory, for a follow-up pull request.
