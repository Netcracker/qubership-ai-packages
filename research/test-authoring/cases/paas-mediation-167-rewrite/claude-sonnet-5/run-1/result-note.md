Changes are left uncommitted, as requested.

---

**Message for the PR author:**

I went through the tests this commit added or changed against the test-authoring skill (Go `testing` + testify). Most of it already does exactly what the skill asks: goes through the exported methods instead of the private `dualModeRouteError`/`dualModeDeleteError` helpers, asserts error semantics (`errors.Is`, `ReasonForError`) instead of message text, and keeps each case readable as a scenario with its own name. Two things I changed:

1. **`Test_CreateRoute_ExistingRoute_ReturnsAlreadyExistsInEveryGatewayMode`** only checked `ReasonForError == AlreadyExists` in each mode, not that the *specific* injected error was the one that reached the caller. I added a `wantErrs []error` per table row and an `ErrorIs` check for each, so the test also catches a fix that preserves *some* `AlreadyExists` reason (e.g. by synthesizing a fresh status error) without actually wrapping the real one.

2. Its comment, and the one on `Test_DeleteRoute_DualMode_IngressDeleteRefused_ReturnsForbidden`, said "a dual-mode create/delete used to report every failure as an internal error of its own" and named `paasErrors.IsAlreadyExists`/`IsForbidden`, neither of which the test calls. That's also factually off for the create case: your own commit message pins the defect to the *single-mode* branches of `resolveRouteResult` (`%w` → `%v`), not the dual-mode branch, which already wraps correctly. I rewrote both comments to name the actual defect location and drop the stale function references.

I did not add a symmetric "HTTPRoute create fails, ingress succeeds" case for the no-duplication check (`ReportsTheIngressErrorOnce`): that path runs through the same `formatRouteResourceStatusSummary`, parameterized only by the resource name, so it's the same equivalence class and a second case would be redundant rather than stronger.

One thing I didn't do: verify red-on-the-base-commit for the strengthened `ErrorIs` checks (I didn't want to touch `route.go` even temporarily). If you want that evidence, reverting `%w`→`%v` in the two single-mode branches of `resolveRouteResult` and rerunning `Test_CreateRoute_ExistingRoute_ReturnsAlreadyExistsInEveryGatewayMode` should turn the "legacy ingress only" and "gateway api only" subtests red.

All tests in the package still build, vet clean, and pass (`go test ./service/internal/kubernetes/...`).
