I rewrote the tests that commit added in `service/internal/kubernetes/route_test.go`. Production code is unchanged and nothing is committed. `go vet` passes, and the package's tests pass with `-shuffle=on`.

To check the tests can actually fail, I temporarily edited `route.go` nine ways and ran the tests against each edit, then restored the file. Every edit was caught:

| Change to `route.go` | Test that fails |
| --- | --- |
| `%w`→`%v`, ingress-only branch of `resolveRouteResult` | `ExistingRoute…/legacy_ingress_only` |
| `%w`→`%v`, gateway-API-only branch | `ExistingRoute…/gateway_api_only` |
| `%w`→`%v` on either error in the "both creates failed" message | `BothCreatesFailed_WrapsBothErrorsWithoutUpdateHint` |
| One create fails and its error is replaced by an internal error of its own | `IngressAlreadyExists_…WithUpdateHint` and `UpdateOrCreateRoute_…IngressUpdateConflict_ReturnsConflict` |
| The full per-resource status instead of the summary in the message | both `…ReportsThe…ErrorOnce` tests |
| `%v` on the ingress error in the "both deletes failed" message | `BothDeletesRefused_WrapsBothErrors` |
| A one-sided delete error replaced by an internal error | the matching `…DeleteRefused_ReturnsForbidden` test (plus an existing neighbor) |

**Message for the PR author**

> I reworked the error-semantics tests in `route_test.go`. All of them are small tests that go through the exported methods, against the fake Kubernetes and gateway API clientsets.
>
> - **The checks on the error now report together.** The new tests used `require.New(t)`, which stops at the first failed check, so a broken reason hid whether the error chain or the hint was also wrong. Setup now uses `require` (`require.NoError` on the create in the delete tests, `require.Error` before `err.Error()` is called), and the checks on the returned error use `assert`.
> - **The duplicated-text check now covers both directions.** The removed `Test_dualModeRouteError_NoErrorDuplication` table had a "HTTPRoute failed, ingress created" row that the rewrite dropped. I added `Test_CreateRoute_DualMode_HTTPRouteCreateFailed_ReportsTheHTTPRouteErrorOnce` beside the ingress one.
> - **`UpdateOrCreateRoute` now has a test.** The commit message names it, but no new test called it. I added `Test_UpdateOrCreateRoute_DualMode_IngressUpdateConflict_ReturnsConflict`, which checks `errors.Is` and the `Conflict` reason. It injects a non-internal error on purpose: the existing update-error test injects an internal error, so it keeps passing even if the code replaces the API error with an internal error of its own.
> - **One client builder instead of two.** The new `newRouteKubeClient` repeated the body of `newGatewayAPIOnlyKubeClient`. That helper now calls `newRouteKubeClient(t, GatewayApiDefault)` and resets `UseNetworkingV1Ingress` to false, so its existing callers behave as before.
> - **Smaller edits.** I renamed `BothCreatesFailed_WrapsBothErrors` to `…WithoutUpdateHint`, since it also checks the hint is absent. The test comments now say why each case fails (why each gateway mode is its own row, and why Forbidden or Conflict rather than an internal error) instead of how the code used to behave. One comment now points to the existing test that checks the HTTPRoute is left in place after a partial create.
>
> **Proposed, not done:**
> - **Recording the test libraries.** The repository has no `AGENTS.md` or `CLAUDE.md`. I'd add one with the line `Tests: Go testing engine, testify assertions (assert for checks on a result, require only where continuing is meaningless)`. That's your call, so I haven't created the file.
> - **Single-mode `UpdateOrCreateRoute` failures.** When a get or update fails with only one resource configured, the existing tests (`…GatewayAPIOnly_HTTPRouteUpdateError`, `…HTTPRouteGetError`) only check the message text, not the error chain. An `errors.Is` check there would cover the `upsert*` paths.
> - **Older neighboring tests.** `Test_CreateRoute_DualMode_BothFailed_ReturnsFullStatusError`, `…HTTPRouteFailed_IngressCreated…`, and several single-mode error tests still build the client inline instead of using `newRouteKubeClient`. They also check message text where `errors.Is` would do. I left them alone because this commit didn't touch them.
