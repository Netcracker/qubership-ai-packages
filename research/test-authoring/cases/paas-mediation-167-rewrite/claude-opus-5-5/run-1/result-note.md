I rewrote the tests and helpers from the last commit in `service/internal/kubernetes/route_test.go`. That is the only file changed; `route.go` is untouched and nothing is committed.

The whole module passes under `go test ./... -shuffle=on`, and `go vet` is clean. History before #125 isn't in the repository, so I couldn't run the tests against the old code to see them fail. Instead, in a scratch copy of the repo, I made 11 small breaking changes to `route.go`, one at a time, and confirmed at least one new test fails for each:
- each `%w` changed to `%v` in the create, update and delete error branches, single and dual mode;
- the partial-create message built from the full per-resource status instead of the summary;
- the "try using Update endpoint" hint removed.

---

**Message for the PR author**

Thanks for moving these tests onto the exported methods. That's the right boundary. I reshaped them as follows:

- **Two tests per resource became tables.** The `IngressDeleteRefused` / `HTTPRouteDeleteRefused` pair had the same act and the same assertions, so it is now `Test_DeleteRoute_DualMode_OneDeleteRefused_WrapsItsError`, with one row per resource. On the create side, `IngressAlreadyExists…WithUpdateHint` and `IngressCreateFailed_ReportsTheIngressErrorOnce` became `Test_CreateRoute_DualMode_OneCreateRefused_ReportsTheRefusalOnceWithUpdateHint`, with rows `ingress` and `httproute`.
- **One dropped case is back.** The old `NoErrorDuplication` table also checked that the error isn't printed twice when the HTTPRoute is the one that fails. The rewrite had dropped that; it's now the `httproute` row. The count uses the injected error's own text, so it no longer depends on a hand-copied string.
- **Two tests added, so every method the commit names is tested.**
  - `Test_UpdateOrCreateRoute_RefusedUpdate_ReturnsConflictInEveryGatewayMode`: no test of the change went through `UpdateOrCreateRoute`.
  - `Test_DeleteRoute_RefusedDelete_ReturnsForbiddenInEveryGatewayMode`: nothing could tell a wrapped error from a replaced one in single-mode delete. The existing single-mode delete tests only use `Contains`.
- **New helper `refuse(t, k8s, gw, verb, resource, err)`.** It installs `failingReactor` on whichever fake serves the resource, so a table row only has to name the resource.
- **Assertions.** Final checks use `assert`, so every failed assertion shows up in one run. `require.Error` stays only where `err.Error()` comes next. I removed `ReasonForError` where `ErrorIs` on the single injected error already implies it.
- **Comments.** The comments above the tests are gone: they repeated the test name or described what the code used to do. The one useful reason, why the hint is absent when both creates fail, is now the `NotContains` message.

What I propose but didn't do:
- **Which reason wins when both resources fail.** The deleted `AlreadyExistsAndInternalError` test pinned that `ReasonForError` returns the HTTPRoute's reason in that case. Nothing pins it now. If callers depend on it, it deserves its own test; if not, it's fine to leave it open.
- **Older single-mode error tests.** Tests like `Test_CreateRoute_GatewayAPIOnly_HTTPRouteCreateError` and the `*_IngressCreateError` / `*_IngressDeleteError` tests still check only message text. They predate this commit, so I left them alone. They could switch to `ErrorIs` and be folded into the new tables.
