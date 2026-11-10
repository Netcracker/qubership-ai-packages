I rewrote the tests the last commit added in `service/internal/kubernetes/route_test.go`. That is the only file changed, and nothing is committed. `go vet` and `go test ./...` in `service/` pass.

I also ran 13 mutations, one at a time, on a copy of `route.go` in the scratchpad. Each changes how one error is wrapped, reported or ordered, and each one now makes at least one test fail. Run against the commit's own tests, three of them pass:
- `%w` → `%v` in the single-resource delete path (`resolveSingleResourceDeleteResult`).
- Swapping the two errors when both creates fail in dual mode.
- `%v` in the ingress update path of `UpdateOrCreateRoute` gets past every test the commit added; only an older test catches it.

The skill also points to two companion skills for wording and doc comments (`english-developer-style`, `godoc-authoring`). Neither is installed here, so the wording follows the main skill alone.

---

**Message for the author of the pull request**

Thanks — going through the exported methods and checking error semantics instead of the text of `dualModeRouteError` is the right direction. I reworked the tests this commit added:

- **`UpdateOrCreateRoute` now has a test.** The commit message says the tests cover it, but none of the new tests call it. `Test_UpdateOrCreateRoute_ConflictingUpdate_ReturnsConflictInEveryGatewayMode` runs a rejected update in all three gateway modes and checks the reason is `Conflict`.
- **The single-resource delete path is now covered.** `Test_DeleteRoute_RefusedDelete_ReturnsForbiddenInEveryGatewayMode` runs in all three gateway modes, like the create table. Before, changing `%w` to `%v` in `resolveSingleResourceDeleteResult` passed every test.
- **The three tables share one list of gateway modes** (`routeGatewayModes`), so each table states only its own act and its own reason.
- **One input the rewrite dropped is back.** The earlier test `AlreadyExistsAndInternalError` had the HTTPRoute create return AlreadyExists while the ingress create failed with an internal error. Its replacement used Forbidden plus AlreadyExists and no longer checked which reason the caller sees. `Test_CreateRoute_DualMode_BothCreatesFailed_WrapsBothErrorsWithoutUpdateHint` uses the original input again. It checks that both errors can be matched with `errors.Is`, that the reason is `AlreadyExists`, and that the update hint is absent.
- **The duplicated-error check now runs in both directions**, as the old table did. `…_IngressCreateFailed_NamesTheIngressErrorOnce` and the new `…_HTTPRouteCreateFailed_NamesTheHTTPRouteErrorOnce` both fail if the full status replaces the summary.
- **All the checks in a test now report together.** The new tests used `require` for every check, so the first failure hid the rest. They now use `assert` for the checks and keep `require` only for setup and for the `require.Error` that guards `err.Error()`.
- **Comments removed.** The comments above the tests repeated the test name or described what the code used to do; that history belongs in the commit message. The comments on the helpers stay. `newRouteKubeClient`, `failingReactor` and the resource helpers are unchanged.

To check the new tests, I ran 13 mutations of `route.go` covering each wrap, the summary-vs-full status, the hint, and the order of the two errors. Each one makes at least one test fail.

Proposed, not done:
- **The test now fixes which error wins when both creates fail.** The reason is `AlreadyExists` only because the HTTPRoute error comes first in the chain; with the order swapped, callers would see `InternalError`. Please confirm that order is intended, or decide whether `AlreadyExists` should win whichever resource reports it. In that case the test and the code would both change.
- **The older dual-mode tests still check message fragments** (`"httproute: created"`, `"ingress: error"`) and build their client by hand. Moving them onto `newRouteKubeClient` and `failingReactor` would shorten them. I left them alone because this change is limited to the tests the commit added.
