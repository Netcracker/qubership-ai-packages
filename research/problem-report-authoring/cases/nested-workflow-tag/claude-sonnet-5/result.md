## Describe the bug

A caller that pins `generic-go-build.yaml` (or `generic-maven-build.yaml`) to a full commit SHA still gets a Docker build-and-push step that is not pinned, because the `docker-build` job inside that pinned commit calls `docker-build.yaml` by a mutable tag rather than by SHA. On the commit `71206242f5967ac6691337913593f8623863f711` (tag `v2.5.2`), the call is `uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2`; on `main` (`f7fba11dddcc0614b6701ea76f780de14d41c609`) and on tags `v2.6.0`/`v2.6.1`, the call is `@v2.6.1`. Neither is a SHA. That job runs with `packages: write`, and the same pattern exists in `generic-maven-build.yaml`'s call to `docker-build.yaml`.

A real workflow run confirms GitHub resolves the two calls differently. Run 35839496302 (qubership-ratelimit, a caller pinned to commit `71206242...`) reports its `referenced_workflows` as `generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-` and `docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2`. The top-level call already names an exact commit and carries no `ref`; the nested call carries `ref=refs/tags/v2.5.2` and is resolved by that tag at run time, not frozen to whatever `docker-build.yaml` looked like when `v2.5.2` was cut.

If `v2.5.2` or `v2.6.1` is ever moved to a different commit, every caller pinned by SHA to a commit whose `docker-build` job still resolves `docker-build.yaml@v2.5.2` or `@v2.6.1` starts running whatever `docker-build.yaml` the tag then points to, with `packages: write`, with no SHA change on the caller's side for anyone to review. Today the tag still resolves to the pinned commit: `git ls-remote` on 2026-09-23 shows `refs/tags/v2.5.2^{}` at `71206242f5967ac6691337913593f8623863f711`, the same commit `generic-go-build.yaml@71206242...` is pinned to. No caller is running different code right now; this report is about the gap in the pinning guarantee, not an active incident.

The `docker-build.yaml` call is the only `uses:` in `generic-go-build.yaml` that is not pinned to a full 40-character SHA. Every third-party action the same file calls (`actions/checkout`, `actions/setup-go`, `actions/upload-artifact`, `actions/download-artifact`, `SonarSource/sonarqube-scan-action`, and the workflow-hub `metadata-action`/`docker-action`) is pinned by SHA with a `# vX.Y.Z` comment, and `docker-build.yaml` itself pins every action it calls the same way. Nothing in either file documents why the call between them is the exception.

GitHub's own guidance treats an unpinned reference to reusable code as a real gap, not a style preference: "Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release", and "a tag can be moved or deleted if a bad actor gains access to the repository storing the action" (Secure use reference, "Using third-party actions", https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions). The same reasoning applies to a reference to a reusable workflow. GitHub's "Reuse workflows" guide also documents a same-repository form: a call written as `./docker-build.yaml`, without `{owner}/{repo}` and `@{ref}`, "is from the same commit as the caller workflow" (https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows, "Calling a reusable workflow"). Whether that syntax works unchanged for this call (inputs, secrets, and `needs` all still have to apply) has not been tested here; pinning the existing `@v2.5.2`/`@v2.6.1` reference to a SHA, matching how `docker-build.yaml`'s own action calls are pinned, is the other option. Which shape to take is the project's choice; this report asks only that the nested call stop resolving through a mutable ref.

### Expected behavior

Once a caller pins `generic-go-build.yaml` or `generic-maven-build.yaml` to a commit SHA, every `uses:` reference inside that pinned commit that runs with `packages: write` (currently the `docker-build.yaml` call) should resolve to the same fixed content on every run, the guarantee the caller already gets from the actions in the same files that are pinned by SHA. Moving the `v2.5.2` or `v2.6.1` tag should not change what an already-pinned commit runs.

## To Reproduce

Reproduced in this session, on 2026-09-23.

1. Show that a caller pins `generic-go-build.yaml` by commit SHA:

```bash
git show origin/feat/ratelimit-operator:.github/workflows/go-build.yml | cat -n
```

Relevant line, from `Netcracker/qubership-ratelimit`, `.github/workflows/go-build.yml`:

```text
    43	    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

2. Show that the pinned commit's own `docker-build` job still calls `docker-build.yaml` by a tag, not a SHA, while every action call around it is SHA-pinned:

```bash
curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/71206242f5967ac6691337913593f8623863f711/.github/workflows/generic-go-build.yaml | grep -n 'uses:'
```

```text
118:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
227:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
233:        uses: actions/setup-go@924ae3a1cded613372ab5595356fb5720e22ba16 # v6
300:        uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6
313:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
353:        uses: actions/download-artifact@634f93cb2916e3fdff6788551b99b062d0335ce0 # v5
376:        uses: SonarSource/sonarqube-scan-action@fd88b7d7ccbaefd23d8f36f73b59db7a3d246602 # v6
392:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

3. Confirm the same pattern on the current default branch and the latest tags:

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`generic-maven-build.yaml` on `main`, line 222, has the same pattern: `docker-build.yaml@v2.6.1`.

4. Confirm that GitHub actually resolves the nested call through the tag at run time, using a completed run of the pinned caller:

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

Run: `Netcracker/qubership-ratelimit`, workflow "Build", event `pull_request`, branch `feat/migrate-to-v1`, head `ae667a4`, created 2026-09-23T08:51:16Z, conclusion success. The `docker-build` job it triggered pushed images to `ghcr.io/netcracker/qubership-ratelimit-operator` (see Logs).

5. Confirm the tag currently still points at the commit the caller pinned, so nothing different is running today:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

## Version

- `qubership-core-infra`, `main`: `f7fba11dddcc0614b6701ea76f780de14d41c609` (read 2026-09-23).
- `qubership-core-infra`, tag `v2.6.1`: tag object `fc321328f887a9e895fb7b22a12212ef7c568233`, peels to `8a233b03c5b5355d59c1585ffdaa1f45ea816405`.
- `qubership-core-infra`, tag `v2.6.0`: `e8322e6`.
- `qubership-core-infra`, tag `v2.5.2` (older, still the pinned target of the live caller shown above): tag object `504063c0cc240324254b46ad4fc855f14ccf2bf5`, peels to `71206242f5967ac6691337913593f8623863f711`.

The same pattern is present in every one of these: `main`, the newest tag (`v2.6.1`), and the older tag a live caller currently pins.

## Logs

Job `107112852067` ("Build and test / Build Docker image / Build Docker Images (qubership-ratelimit-operator, ./operator/Dockerfile, ., false)"), from run 35839496302, pushed:

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
2026-09-23T08:59:29.5768985Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-f7659c9@sha256:635897f0...
2026-09-23T08:59:30.1920286Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-snapshot@sha256:635897f0...
```

Job URL: https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067

## Additional information

The nearest existing report is PR #321 (open, opened 2026-07-27 by Renovate, updated 2026-09-16, listed in Dependency Dashboard #258 under `renovate/pin-dependencies`): "chore(deps): pin netcracker/qubership-core-infra action to 8a233b0". It changes `generic-go-build.yaml` line 394 and `generic-maven-build.yaml` line 222 from `docker-build.yaml@v2.6.1` to `docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`, and makes the matching change in `maven-deploy.yml` and `maven-verify.yml`. Merging it would close the gap this report describes for any caller that re-pins to a commit created after the merge; it cannot change what a commit already pinned today (such as `71206242...`) runs, because that commit's own content cannot change after the fact, so this report and PR #321 do not conflict.

`generic-go-build.yaml` is documented, in issue #367, as used by 16 observability repositories, which is the closest available statement of how many callers a change here reaches.

This report depends on nothing else filed in this tracker.
