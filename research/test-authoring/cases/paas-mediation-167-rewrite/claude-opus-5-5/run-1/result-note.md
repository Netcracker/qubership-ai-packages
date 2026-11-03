I rewrote the tests in `service/internal/kubernetes/route_test.go` that your commit added. Only that file changed, and nothing is committed. The package passes in random order (`go test -shuffle=on`). I also made 8 deliberate breaks to `route.go` in a scratch copy of the repo, one per error-reporting branch (wrapping with `%v` instead of `%w`, or building the message from the full status). Every one fails at least one of the tests below.

Here is the message I'd leave for the author:

---

Going through the exported methods and checking error semantics with `errors.Is` and `ReasonForError` is the right direction. Most of the tests stay as you wrote them. I changed these things:

1. **Two inputs from the deleted tests were missing.**
   - `Test_dualModeRouteError_NoErrorDuplication` checked both partial failures, but only the case where the ingress fails was carried over. I added `Test_CreateRoute_DualMode_HTTPRouteCreateFailed_ReportsTheHTTPRouteErrorOnce` for the case where the HTTPRoute fails and the ingress is created. If the message summary is built from the full per-resource status, it now fails alongside the ingress test.
   - The old `..._AlreadyExistsAndInternalError_...` test covered an HTTPRoute AlreadyExists together with an ingress InternalError. Your `BothCreatesFailed` test had swapped that for Forbidden + AlreadyExists, so I put the original pair back. It still checks that both errors can be matched with `errors.Is` and that the "try using Update endpoint" hint is absent.

2. **`UpdateOrCreateRoute` had no error-semantics test,** although the commit message lists it. I added `Test_UpdateOrCreateRoute_DualMode_IngressUpdateConflict_ReturnsConflictWithUpdateHint`. It updates a route whose ingress update returns Conflict, and checks `ErrorIs`, the Conflict reason, and the hint.

3. **Assertions on one result now report together.** The checks after the call use `assert` instead of a `require.New(t)` that stops at the first failure. For example, a lost wrapper and a missing hint now both show up in one run. `require` stays only for the arrange step and for the `require.Error` guard that runs before `err.Error()` is called.

4. **One helper instead of two.** `newGatewayAPIOnlyKubeClient` built the same client as your new `newRouteKubeClient`, so it now calls `newRouteKubeClient(t, GatewayApiDefault)`. Its callers don't change. The only difference is `UseNetworkingV1Ingress = true`, and gateway-only mode never reaches the ingress code.

5. **Doc comments** no longer describe the old behavior ("used to report every failure as an internal error"). That history belongs in the commit message, where you already have it.

**Proposed, not done:**
- Many existing tests outside this commit still build the client inline, for example `Test_CreateRoute_DualMode_BothFailed_ReturnsFullStatusError`, `..._HTTPRouteFailed_IngressCreated_...`, and the `GatewayAPIOnly_*Error` tests. They could use `newRouteKubeClient` and `failingReactor`. I left them alone because the commit didn't touch them.
- When both resources fail with different reasons, `ReasonForError` returns the HTTPRoute's reason. That only holds because the HTTPRoute error is wrapped first. The old test relied on it, and no test asserts it now. If callers are meant to depend on that order, it should be documented and tested. If not, the current tests are enough.
- The single-mode table covers only create. Single-mode update and delete wrap the error the same way, but no test checks the reason they return.
