I rewrote the tests that commit 7e656b3 added in `service/internal/kubernetes/route_test.go`. Production code is untouched and nothing is committed. The package passes in shuffled order (`go test -shuffle=on`). I also broke the error wrapping in `route.go` 11 ways, one at a time (mostly `%w` → `%v`), and restored it after each run. Every break failed at least one of the new or changed tests.

---

**For the PR author**

Your tests now go through `CreateRoute`, `UpdateOrCreateRoute` and `DeleteRoute` and check which error comes back, not its wording. That's the right direction. I changed seven things:

1. **The single-resource delete path wasn't tested.** The commit message says the delete path now has a test for each branch, but only the dual-mode ones had one. In single mode, `resolveSingleResourceDeleteResult` could switch `%w` to `%v` and every test still passed. I replaced the two one-sided dual tests with `Test_DeleteRoute_RefusedDelete_ReturnsForbiddenInEveryGatewayMode`. It's a table over the three gateway modes, like your create table. The two one-sided dual cases stay as their own tests, renamed to say which resource was deleted and which was refused.
2. **`UpdateOrCreateRoute` had no test.** The commit message names it, but none of the new tests called it. I added `Test_UpdateOrCreateRoute_ConflictingUpdate_ReturnsConflictInEveryGatewayMode`. The single-mode rows fail when either single-mode wrap in `resolveRouteResult` loses `%w`.
3. **Two dropped inputs are back.**
   - The deleted `Test_dualModeRouteError_NoErrorDuplication` also checked the reverse case: the HTTPRoute create fails and the ingress create succeeds. That case is back as `Test_CreateRoute_DualMode_HTTPRouteCreateFailed_ReportsTheHTTPRouteErrorOnce`.
   - The deleted test with "HTTPRoute already exists, ingress internal error" is back as the input of `..._BothCreatesFailed_WrapsBothErrors`. It now checks that both errors are still in the chain (`ErrorIs` on each), which is a stronger check than reading the reason.
4. **Failures now report together.** Tests with several checks used `require.New`, which stops at the first failure. They now use `assert.New`, so one run shows every mismatch. `require.Error` stays in front of any line that calls `err.Error()`, so a nil error can't crash the test. This means the new tests don't match their neighbours, which all use `require.New`. I think a better failure report is worth that.
5. **One helper instead of two.** Your new `newRouteKubeClient` built the same client as the existing `newGatewayAPIOnlyKubeClient`. That helper now just calls `newRouteKubeClient(t, GatewayApiDefault)`, and its nine callers are unchanged.
6. **New helper for existing routes.** `newRouteKubeClientWithExistingRoute` creates the route before the update or delete under test. The update table and every new delete test use it.
7. **The comment on the duplication test is shorter.** I removed the claim about what a caller "used to read".

**Proposed, not done:**
- **Stack line:** the repository has no `AGENTS.md` or `CLAUDE.md` that says which test libraries to use. I propose adding this line: `Tests: Go testing engine, testify assertions (assert for grouped checks, require for preconditions); client-go and gateway-api fake clientsets for the API server.` Should I add it in a new `AGENTS.md`?
- **Older tests:** some older tests in the file, like `Test_CreateRoute_GatewayAPIOnly_HTTPRouteCreateError` and `Test_DeleteRoute_LegacyIngress_*_IngressDeleteError`, still check message text with `Contains`, and several build their client by hand. I left them alone because this task only covered the commit's tests. They're worth a follow-up.
