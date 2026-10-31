I rewrote the tests from the last commit in `service/internal/kubernetes/route_test.go`. Production code is unchanged and nothing is committed. `go vet` and the package's tests pass, including a run in random order (`-shuffle=on`). `gofmt -l` lists only `mock/clientset.go`, which I didn't touch.

To check the tests could fail, I changed each `%w` in `route.go` to `%v`, one at a time, ran the tests, then restored the file (the script is at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-K8oWPNcpRu-repo/ecf3237e-f2f3-49ee-8417-b54d0deeb35c/scratchpad/mutate.sh`). On the original commit, every change was caught except one: `%w`→`%v` in `resolveSingleResourceDeleteResult`, the single-mode delete. The suite stayed green there. After the rewrite, every change is caught.

---

**Message for the author of the pull request**

Moving these tests onto the exported methods and asserting error semantics instead of message text is the right call. I changed five things:

1. **The commit message promised more than the tests covered.** It says the tests show that `CreateRoute`, `UpdateOrCreateRoute` and `DeleteRoute` wrap the API error rather than replace it. But nothing went through `UpdateOrCreateRoute`. And if you change `%w` to `%v` in `resolveSingleResourceDeleteResult` (the single-mode delete), every test still passes. I added two tables shaped like your create table:
   - `Test_UpdateOrCreateRoute_ConflictingUpdate_ReturnsConflictInEveryGatewayMode`
   - `Test_DeleteRoute_RefusedDelete_ReturnsForbiddenInEveryGatewayMode`

   The three gateway modes are now one shared `routeGatewayModes` list instead of a local copy in each table.
2. **Grouped assertions now all report.** The new tests used `require.New(t)`, which stops at the first failure. So a broken `ErrorIs` hid whether the reason and the hint were still right. Assertions on the result now use `assert`, so one run reports every mismatch. `require` stays only for setup (`CreateRoute` → `require.NoError`) and as `require.Error(t, err)` before a line that calls `err.Error()`. Otherwise a nil error would panic instead of failing.
3. **One test name was missing an outcome.** `Test_CreateRoute_DualMode_BothCreatesFailed_WrapsBothErrors` also asserts the hint is absent, so it is now `..._WrapsBothErrorsWithoutUpdateHint`. Its comment names the test that shows the hint does appear when one resource was created, as the control for that absence.
4. **One test had no comment.** `Test_DeleteRoute_DualMode_HTTPRouteDeleteRefused_ReturnsForbidden` now has one, matching its ingress sibling. The ingress test's comment now says which branch it covers instead of recounting history.
5. **The rest is unchanged.** The helpers `newRouteKubeClient`, `failingReactor`, `httpRoutesResource` and `ingressesResource`, and the expectations of every test you added, are as you wrote them.

Two things I'm proposing but didn't do:

- **Dropped cases.** Two cases from the deleted tests aren't restored:
  - `Test_dualModeRouteError_NoErrorDuplication` checked duplication when only the HTTPRoute fails. Only the ingress side is checked now. Both sides build their message the same way, so changing that code for one side changes it for both, and the ingress test catches it.
  - `AlreadyExistsAndInternalError` pinned that a caller sees `AlreadyExists` when the HTTPRoute exists and the ingress fails with an internal error. That outcome comes only from which error is wrapped first, so I left it out. If callers rely on that order, it deserves a test of its own and a sentence in the description.
- **Older tests below the new ones.** They still assert error text only. These include `Test_CreateRoute_GatewayAPIOnly_HTTPRouteCreateError` and the `..._IngressDeleteError` and `..._UpdateError` tests, and some copy the client setup that `newRouteKubeClient` now provides. Moving them onto `newRouteKubeClient` and `ErrorIs` would be a separate cleanup; I didn't change them.
