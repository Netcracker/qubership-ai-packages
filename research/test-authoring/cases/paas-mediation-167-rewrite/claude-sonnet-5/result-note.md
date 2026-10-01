Only the test file changed, production code is untouched, and the build/tests pass.

---

**Message for the PR author:**

I read `test-authoring` and reviewed every test and helper the commit added or changed against it (`newRouteKubeClient`, `failingReactor`, `httpRoutesResource`/`ingressesResource`, the `ExistingRoute_...InEveryGatewayMode` table, the two rewritten create-partial-failure tests, `BothCreatesFailed_WrapsBothErrors`, and the three new delete-branch tests).

**What I changed:** one line. `Test_CreateRoute_ExistingRoute_ReturnsAlreadyExistsInEveryGatewayMode`'s subtest used bare `require.Equal(t, ...)` instead of the `assertions := require.New(t)` pattern every other test in the file uses — a neighbor-shape inconsistency (skill §9). Fixed to match.

**What I verified and left alone, because it already follows the skill:**
- Every rewritten/new test goes through the exported `CreateRoute`/`UpdateOrCreateRoute`/`DeleteRoute` methods, asserts error semantics (`errors.Is`, `paasErrors.ReasonForError`) rather than message strings, and reads injected errors back through the unit's interface rather than asserting on test-local state.
- I didn't just trust the commit message's claim that these catch the wrapping regression — I reproduced it: temporarily changed `%w`→`%v` in both single-mode branches of `resolveRouteResult` and in all three branches of `dualModeDeleteError`, and separately reproduced the old "double-reported error" bug in `formatDualModeRouteStatusSummary`. Each mutation turned exactly the test(s) that should catch it red, then I restored the production file. So the red-on-base-commit oracle actually holds, not just as an assertion in the message.
- The new helpers (`newRouteKubeClient`, `failingReactor`, the two `*Resource()` builders) are infrastructure, not mystery guests — they don't hide any value the expectations depend on, and `newDualModeKubeClient` was correctly thinned to a wrapper rather than duplicated.
- The three new delete tests correctly cover each of `dualModeDeleteError`'s three branches, matching the commit message's claim one-for-one.

**One thing I noticed but did not touch, since it's production code and out of scope here:** `dualModeRouteError`'s first branch (`if httpRouteRes.err == nil && ingressRes.err == nil { return nil }`) looks unreachable — `resolveRouteResult` only calls `dualModeRouteError` when it has already established that at least one of the two errors is non-nil. The old test that called the unexported helper directly to cover that branch was correctly deleted (it exercised dead code via a path no caller takes), but the dead branch itself is still sitting in `route.go`. Worth a follow-up if you want to confirm it's truly unreachable and remove it, independent of this test change.

No repository instructions file (`AGENTS.md`/`CLAUDE.md`) names the test stack, so per the skill I'm proposing the line here rather than writing it myself: `Tests: Go testing engine; testify (require) for assertions.`
