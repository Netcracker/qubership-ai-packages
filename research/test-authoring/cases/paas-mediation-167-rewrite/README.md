# Case: rewrite the route error tests of paas-mediation-client#167

A regression case for `test-authoring`. The input is [Netcracker/qubership-core-lib-go-paas-mediation-client#167][pr]
as the reviewer saw it, commit `67c0e6a0`, applied to its parent `d0f4cbbd`. The pull request is open, has one commit,
and changes only `service/internal/kubernetes/route_test.go`. It replaces tests that called the unexported
`dualModeRouteError` and matched substrings of the message with tests that go through `CreateRoute` and `DeleteRoute`
over the fake clientsets of `client-go` and `gateway-api`, and assert `errors.Is` on the injected API error and the
reason `paasErrors.ReasonForError` reads.

The tests were written by Claude with an earlier `test-authoring`. The reviewer approved them and wrote that the
duplicated client constructors and the nearly identical tests were left to the author, and that the skill can be
improved there ([the comment][review]). In the submitted file:

- `newRouteKubeClient(t, gatewaySystemType)` is new, and `newDualModeKubeClient` now calls it, but the existing
  `newGatewayAPIOnlyKubeClient` keeps its own copy of the same builder chain, differing in the system type, in not
  setting `UseNetworkingV1Ingress`, and in not returning the Kubernetes fake.
- The three new delete tests repeat the same six lines (client, a successful create, an API error, a reactor, the
  delete) and differ in which fake fails and with which error. `IngressDeleteRefused` and `HTTPRouteDeleteRefused` run
  the same assertions.
- The tests use `require.New(t)` for several assertions on one error, as the file's neighbors do, so the first failed
  `ErrorIs` hides the second.

The reviewer also asked which reason the two tests that inject two errors with different reasons should pin. The
session is not told about the comment.

[pr]: https://github.com/Netcracker/qubership-core-lib-go-paas-mediation-client/pull/167
[review]: https://github.com/Netcracker/qubership-core-lib-go-paas-mediation-client/pull/167#issuecomment-5728517655

## What it exercises

This is the first case that is not a compiler-like harness: a Go service client, fakes of the services it calls, one
act per call, testify on `go test`, and cases that expect the same outcome.

- **The reader sees each input whole, and the difference between two cases on one line** (§7 principle 2). The client
  and the failure injection are the shared setup; which fake fails and with which error is the varying value. A
  helper that takes them, or the rows of a table, passes; copies of the six-line setup that a reader compares line by
  line fail.
- **A new helper beside one whose body differs in one line** (§7 principle 2, §9 *A new test uses the helpers the
  file already has*). `newGatewayAPIOnlyKubeClient` calls the helper that takes the system type, so that its callers
  stay as they are.
- **The form follows the assertions** (§7 principle 4, and `references/go/testing.md`). Cases that run the same
  assertions are rows of one table run through `t.Run`, or separate tests on one helper; a row field that selects the
  assertions fails; a `wantErr bool` cannot carry the error kind these tests assert.
- **Each case fails on its own, under a name of its own** (§7 principle 1), and **several assertions on one behavior
  report together** (§7, `references/go/testify.md`: `assert` continues, `require` stops).
- **A rewrite keeps every input** (§7 principle 3, §4), and **a new test takes the shape of its neighbors** unless the
  shape breaks §7 (§9). The neighbors build the client inline and use `require.New(t)`.
- **The stack line is proposed** (§0). The repository has no `AGENTS.md` or `CLAUDE.md`.

## Files

| File | What it is |
| --- | --- |
| `repo`, `base` | The repository and `d0f4cbbd82be924bf1bf83a0c9f8128ab96b831d`, the parent of the pull request's commit. |
| `change.patch` | `git diff d0f4cbbd 67c0e6a0`: the test file the reviewer saw. It applies to `base` cleanly. |
| `change-message.txt` | The message of `67c0e6a0`. |
| `production-paths` | The non-test files of `service/internal/kubernetes`, one per line. |
| `build.sh` | Runs `go test -json` over `service/internal/kubernetes` and every package whose `_test.go` files differ from `base`, and prints the count (a subtest counts) and the failed tests. |
| `mutants.sh` | Replaces each `%w` of `route.go` with `%v`, one at a time, and prints which top-level tests fail on each. |
| `prompt.md` | The task, with `<skill>` replaced by the path of the skill copy. |
| `<model>/…` | The outputs `run-case.sh` writes; its header lists them. |

Go 1.27.1 on darwin/arm64 was used; `go.mod` asks for 1.26.5. `build.sh` takes about 26 seconds in a fresh checkout
and 8 seconds warm, and runs 202 tests on the submitted file. `mutants.sh` takes about 2 minutes.

## How to run

From the repository root:

```bash
research/test-authoring/cases/run-case.sh research/test-authoring/cases/paas-mediation-167-rewrite <model> [<rev>]
```

`run-case.sh` prints the temporary directory it worked in; to grade check 2, run
`research/test-authoring/cases/paas-mediation-167-rewrite/mutants.sh <that directory>/repo`.

## Red on the base

The pull request changes no production code, so the run of `build.sh` on the base is the run on the fix, and both
must pass. The evidence the pull request offers in place of a red run is a mutation check, and `mutants.sh` repeats
it. On `route.go` of the base:

| Mutant (line:occurrence) | Site | Base tests | Submitted tests |
| --- | --- | --- | --- |
| 100:1 | `resolveRouteResult`, gateway API only | survives | killed |
| 106:1 | `resolveRouteResult`, legacy ingress only | survives | killed |
| 117:1 | `dualModeRouteError`, both failed, HTTPRoute error | killed | killed |
| 117:2 | `dualModeRouteError`, both failed, ingress error | survives | killed |
| 122:1 | `dualModeRouteError`, one failed | killed | killed |
| 462:1, 462:2 | `dualModeDeleteError`, both failed | survive | killed |
| 465:1 | `dualModeDeleteError`, HTTPRoute failed | killed | killed |
| 467:1 | `dualModeDeleteError`, ingress failed | killed | killed |
| 451:1 | `resolveSingleResourceDeleteResult` | survives | survives |
| 23:1, 283:1, 699:1 | the route cache | survive | survive |

The submitted tests kill 100 and 106 only through the gateway-API-only and legacy-only rows of
`Test_CreateRoute_ExistingRoute_ReturnsAlreadyExistsInEveryGatewayMode`, 117 only through
`Test_CreateRoute_DualMode_BothCreatesFailed_WrapsBothErrors`, and 462 only through
`Test_DeleteRoute_DualMode_BothDeletesRefused_WrapsBothErrors`.

## Checks

Read `result.diff`, `result-note.md`, and `result-build.txt` against all of them, and run `mutants.sh` for check 2.

1. **Every submitted input survives with its expectation** (§7 principle 3, §4). Nine inputs: `CreateRoute` on a route
   that exists in each of the three gateway modes, reason `AlreadyExists`; dual-mode create with the ingress
   `AlreadyExists`, the injected error in the chain, reason `AlreadyExists`, and the update hint; dual-mode create with
   the ingress failing with an internal error, whose text appears once; dual-mode create with the HTTPRoute `Forbidden`
   and the ingress `AlreadyExists`, both errors in the chain and no hint; dual-mode delete with the ingress, then the
   HTTPRoute, `Forbidden`, the error in the chain and reason `Forbidden`; dual-mode delete with the HTTPRoute
   `Forbidden` and the ingress `Conflict`, both in the chain. An input dropped, replaced by another input (such as the
   base's earlier version of the same scenario), or an assertion of it weakened (an `ErrorIs` replaced by `Error`),
   fails.
2. **No mutant the submitted tests kill survives** (§1). `mutants.sh` on the result reports 100:1, 106:1, 117:1, 117:2,
   122:1, 462:1, 462:2, 465:1, and 467:1 killed. A rewrite that kills 451:1 as well passes with credit.
3. **One client constructor** (§7 principle 2, §9). The submitted tests and `newGatewayAPIOnlyKubeClient` reach the
   builder chain through one helper that takes the gateway system type: the old helper calls the new one, or its callers
   call the new one. Two helpers that build the same client with a few settings or return values different fail, however
   many lines differ: `newGatewayAPIOnlyKubeClient` sets no `UseNetworkingV1Ingress` and returns two values, and the old
   helper may take those as arguments or keep a thin wrapper over the shared one. A closing message that proposes the
   merge and leaves both is partial.
4. **The failure setup is written once** (§7 principle 2). No two of the rewritten tests carry the same block of
   client, create, error, and reactor that a reader compares line by line to find which fake fails with which error;
   that block is in a helper that takes the varying values, or the cases are rows. No test of the rewrite calls
   `NewKubernetesClientBuilder` inline. The helper takes values (a system type, a resource, an error), not pieces of
   Go code.
5. **Cases that assert the same way share one form** (§7 principle 4). The two single-resource delete cases are rows
   of one table run through `t.Run`, or two tests on one helper. The three gateway modes stay rows with names by
   condition. Cases that assert differently (one error in the chain and a reason, against two errors in the chain)
   are not rows of one table unless every row runs the same assertions.
6. **No row field selects the assertions** (§7 principle 4, §6). No `if tt.wantHint`, `if tt.wantErr`, or nil check on
   a row field decides which assertion runs. A `wantErr bool` column, or a table that asserts only that some error came
   back, fails: these cases assert the error kind.
7. **The error kind is asserted** (§7 *Compare error semantics*). Every error case asserts `ErrorIs` on the injected
   error, or the reason (`ReasonForError`, `IsForbidden`), or both. A message substring stands only for what the
   message defines: the update hint and the count of the ingress error. Pinning the reason where the two injected
   errors differ, as the reviewer asked, passes with credit; it is not required.
8. **Several assertions on one error report together** (§7, `references/go/testify.md`). A test that asserts two facts
   about one error uses `assert`, or `require` only before a line that would dereference a nil. The rewrite may keep
   `require` where it says why, such as the neighbors' shape; then this check is partial, since §9 lets §7 win over
   the neighbors.
9. **Names state the scenario and the outcome** (§7). Test names keep the file's `Test_Method_Mode_Scenario_Outcome`
   shape; subtest names are conditions (`gateway api only`), unique, with no ordinal; no `And` joins the outcomes of
   two inputs. A message names the call and the input where the assertion cannot (`reason of the DeleteRoute error
   %v`).
10. **The production code is unchanged, and the tests pass** (§1). The production part of `result.diff` is empty, and
    `result-build.txt` shows no failure on either run. No `AGENTS.md` or `CLAUDE.md` is created; the closing message
    proposes a stack line (§0), such as Go `testing` with testify and the `client-go` fakes.
11. **The closing message names what moved and why.** It passes where it gives, for each move, the section of the
    skill behind it (`§7`, `§9`, or the rule's words), and says which neighbors' shape the rewrite departs from or
    leaves (the inline builder chains of the other tests, `require.New(t)`). A message that names what moved but
    neither of those is partial.
