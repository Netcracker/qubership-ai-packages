### Describe the bug

`generic-go-build.yaml`'s `docker-build` job calls the reusable workflow `docker-build.yaml` by the mutable tag `@v2.5.2` (line 392), not by a commit SHA, even at the commit `71206242f5967ac6691337913593f8623863f711` that a caller pins to by full SHA. `docker-build.yaml` runs with `permissions: packages: write` and builds and pushes the operator and service images to GHCR.

Concretely, `Netcracker/qubership-ratelimit`'s `.github/workflows/go-build.yml` (base branch `feat/ratelimit-operator`) calls:

```yaml
uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

Fetching `generic-go-build.yaml` at that exact commit shows its own `docker-build` job pinned by tag instead:

```
392:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

Because that inner reference is a tag, moving `v2.5.2` on `qubership-core-infra` after the fact would change which `docker-build.yaml` content every caller already pinned to commit `71206242...` runs on its next build, with no corresponding commit change on the caller's side — the caller's own SHA pin does not carry the guarantee it looks like it carries.

This is not specific to `v2.5.2`: the same pattern is present today. `generic-go-build.yaml` at `v2.6.0` (commit `e8322e6`) and at `v2.6.1`/current `main` (commit `8a233b03c5b5355d59c1585ffdaa1f45ea816405`, tip `f7fba11dddcc0614b6701ea76f780de14d41c609`) still calls `docker-build.yaml@v2.6.1` by tag at line 394. `generic-maven-build.yaml` on `main` has the identical pattern at line 222 (`docker-build.yaml@v2.6.1`). The file's own header usage comment (line 8) also documents callers pinning the outer workflow by tag (`generic-go-build.yaml@v2.x.x`), which does not raise this problem on its own, but nothing in the file's documented usage or in its own code signals that the inner call needs the stronger, SHA-based pin that the outer call is meant to get from a caller.

A run's own metadata confirms how GitHub resolves the two references differently. In `Netcracker/qubership-ratelimit` run `35839496302` (workflow "Build", event `pull_request`, branch `feat/migrate-to-v1`, conclusion `success`):

```
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The outer call resolves by commit (no `ref`); the inner call resolves `ref=refs/tags/v2.5.2` — a reference that can move.

As of 2026-09-23 10:00 UTC, `refs/tags/v2.5.2^{}` on `qubership-core-infra` still points to `71206242f5967ac6691337913593f8623863f711`, so nothing different runs today; this report is about the pin, not about an observed compromise.

**Related:** PR #321 (open since 2026-07-27, unmerged) already changes the `main` versions of this same line — `generic-go-build.yaml` line 394, `generic-maven-build.yaml` line 222, and the equivalent lines in `maven-deploy.yml` and `maven-verify.yml` — from `docker-build.yaml@v2.6.1` to `docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. That fixes the shape of this defect for whichever release is cut from `main` after it merges. It does not mention why the change matters (a caller's own SHA pin on the outer workflow does not hold without it), and it cannot reach commits already tagged and already in use, such as `71206242...`/`v2.5.2` and `e8322e6`/`v2.6.0` — those stay pinned-by-tag internally forever, because their commit content cannot change after the fact.

### To Reproduce

1. In any repository, add a caller workflow with `uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2` (or any other released SHA — the same pattern holds at `v2.6.0`/`v2.6.1`/`main`), with `packages: write`, and run it without `skip-docker: true`.
2. After the run, list its referenced workflows:
   ```
   gh api repos/<owner>/<repo>/actions/runs/<run-id> | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
   ```
3. Observed output, from `Netcracker/qubership-ratelimit` run `35839496302`:
   ```
   Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
   Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
   ```
   The `docker-build.yaml` reference carries a tag `ref`; the `generic-go-build.yaml` reference does not.
4. Confirm the source line directly:
   ```
   curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/71206242f5967ac6691337913593f8623863f711/.github/workflows/generic-go-build.yaml | sed -n '388,395p'
   ```
   Line 392: `uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2`.

### Expected behavior

At any commit a caller can pin `generic-go-build.yaml` to — including `71206242f5967ac6691337913593f8623863f711` (`v2.5.2`), `e8322e6` (`v2.6.0`), and `8a233b03c5b5355d59c1585ffdaa1f45ea816405` (`v2.6.1`, current `main`) — the `docker-build` job's `uses:` line names `docker-build.yaml` by its full 40-character commit SHA, the same way every other `uses:` line in that same file (`actions/checkout`, `actions/setup-go`, `actions/upload-artifact`, `actions/download-artifact`, `SonarSource/sonarqube-scan-action`) is already pinned; the trailing `# vX.Y.Z` comment is one reasonable rendering of that, not a requirement of its own. The same applies to the equivalent line in `generic-maven-build.yaml`. This closes the gap only for whichever release is cut after the fix lands — a commit and tag already published, such as `v2.5.2` and `v2.6.0`, keeps its internal tag reference forever, and a caller already pinned to one of those keeps the exposure described above regardless of this fix.

This is what GitHub's own documentation states about this exact mechanism:

- "Reuse workflows" (https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows), "Calling a reusable workflow": "the `{ref}` can be a SHA, a release tag, or a branch name"; "Using the commit SHA is the safest option for stability and security."
- "Secure use reference" (https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions): "Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release"; "a tag can be moved or deleted if a bad actor gains access to the repository storing the action." The same holds for a reusable workflow reference, which resolves the same way.

### Version

- Caller: `Netcracker/qubership-ratelimit`, `.github/workflows/go-build.yml` on branch `feat/ratelimit-operator` at `7701fd5`.
- Callee: `Netcracker/qubership-core-infra`, default branch `main`.
- Pinned commit exhibiting the defect: `71206242f5967ac6691337913593f8623863f711` (tag `v2.5.2`, tag object `504063c0cc240324254b46ad4fc855f14ccf2bf5`).
- Same pattern also present at: `v2.6.0` (`e8322e6`), `v2.6.1` and current `main` (`8a233b03c5b5355d59c1585ffdaa1f45ea816405`, tip `f7fba11dddcc0614b6701ea76f780de14d41c609`, read 2026-09-23 10:00 UTC).

### Logs

Not applicable — this is a workflow-pinning defect, not a failing run. The relevant evidence is the `referenced_workflows` output above from run https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302 (job https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067).

### Additional information

- Searched `Netcracker/qubership-core-infra` issues and PRs (all states) for `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, `mutable tag`. Nearest hit: PR #321, described under Related above. Other hits (#371, #367, #401) touch the same jobs for unrelated problems (forwarding build-arg toggles, fork-safety of gates, pinning the Go compiler) and are not duplicates.
- `qubership-core-infra` has no GitHub Security Advisories rulesets or release protection on tags (`GET /repos/Netcracker/qubership-core-infra/rulesets` → `[]`; `releases` → `[]`; `releases/tags/v2.5.2` → 404), so `v2.5.2` is a plain, movable tag rather than an immutable release.
- One level further down the same call chain, the workflow-hub action `docker-action` (a different repository, `netcracker/qubership-workflow-hub`, pinned here by SHA `6b356d28e46b2d4683cccb1d91f92643d7f0c513`) itself references `actions/upload-artifact@v4` by tag at its `action.yml` line 485. Left out of this report because it is a different owner's repository; noting it here in case it is worth its own issue there.
