## Goal

In qubership-ratelimit I call `generic-go-build.yaml` pinned by full commit SHA, so that a change to the build and publish logic needs a commit in my repository. The pin does not do that. The `docker-build` job inside the pinned file calls `docker-build.yaml` by the tag `v2.5.2`, and that job builds and pushes the images with `packages: write`. Moving the tag would change the publish logic that runs on the next push, and no commit in the caller would show it.

Nothing different runs today: on 2026-09-23 the tag resolved to the pinned commit. The request is to make the pin sufficient.

## Context

All observations are from 2026-09-23.

### The caller pins by SHA

`.github/workflows/go-build.yml` in Netcracker/qubership-ratelimit, branch `feat/ratelimit-operator` at `7701fd5`:

```yaml
    permissions:
      contents: read
      pull-requests: write
      packages: write
    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

### The pinned file calls `docker-build.yaml` by tag

```bash
curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/71206242f5967ac6691337913593f8623863f711/.github/workflows/generic-go-build.yaml | grep -n 'uses:'
```

```text
8:#       uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@v2.x.x
118:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
227:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
233:        uses: actions/setup-go@924ae3a1cded613372ab5595356fb5720e22ba16 # v6
300:        uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6
313:        uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
353:        uses: actions/download-artifact@634f93cb2916e3fdff6788551b99b062d0335ce0 # v5
376:        uses: SonarSource/sonarqube-scan-action@fd88b7d7ccbaefd23d8f36f73b59db7a3d246602 # v6
392:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

Line 392 is the only reference in the file that is not a full commit SHA. The `docker-build` job (lines 388-395) runs under the workflow-level `packages: write`.

### GitHub resolved it the same way in a real run

Run 35839496302 of qubership-ratelimit (workflow "Build", `pull_request`, head `ae667a4`):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The same run pushed an image to GHCR (job 107112852067; first of three `pushing manifest` lines):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

### The tag is a plain tag, and newer releases have the same pattern

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

- The tag resolves to the pinned commit `71206242`.
- `GET /repos/Netcracker/qubership-core-infra/rulesets` returned `[]`, `GET .../releases` returned `[]`, and `GET .../releases/tags/v2.5.2` returned 404. `v2.5.2` is not an immutable release.
- `generic-go-build.yaml` at `v2.6.1` (the newest tag, `8a233b03c5b5355d59c1585ffdaa1f45ea816405`) and on `main` calls `docker-build.yaml@v2.6.1`, at line 394. `generic-maven-build.yaml` on `main` does the same at line 222.

## What I expect, and what it rests on

A release of qubership-core-infra in which `generic-go-build.yaml` and `generic-maven-build.yaml` reference `docker-build.yaml` by full commit SHA. A caller pinned to the commit of either file then runs the same `docker-build.yaml` content on every push, and its `referenced_workflows` list shows a 40-character SHA for `docker-build.yaml`, not a tag. The requirement is that the pinned commit fixes the nested call. Pinning by SHA with a `# vX.Y.Z` comment, as in line 118, is one way to meet it.

This rests on two things:

- GitHub's reusable workflow documentation: "Using the commit SHA is the safest option for stability and security." (<https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows>)
- The files' own practice. `docker-build.yaml` at `7120624` pins every `uses:` by SHA, and the seven action references in `generic-go-build.yaml` above are pinned too.

I found no project document that states a pinning rule for nested reusable workflows.

## Related issues and PRs

I searched this tracker, issues and PRs in all states, for `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, and `mutable tag`.

The nearest hit is PR #321 (open, Renovate, created 2026-07-27): "chore(deps): pin netcracker/qubership-core-infra action to 8a233b0". It changes line 394 of `generic-go-build.yaml` and line 222 of `generic-maven-build.yaml` from `docker-build.yaml@v2.6.1` to `@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. This issue differs in the reach, not in the change: callers pinned to `v2.5.2` or earlier tags only get the pin from a release made after #321 merges.

Issue #367 states that the generic Go workflow "is used by 16 observability repositories". I did not check how those repositories pin it, so how many callers share this gap is not established.

## Scope

In scope: the nested `docker-build.yaml` references in the generic Go and Maven build workflows.

Not requested: rewriting or moving existing tags, or any change to the logic of `docker-build.yaml`.

## Definition of done

1. A tagged release of qubership-core-infra contains `generic-go-build.yaml` and `generic-maven-build.yaml` whose `docker-build.yaml` reference is a full commit SHA.
2. A caller pinned to that release's `generic-go-build.yaml` commit shows `docker-build.yaml@<40-character SHA>` in `referenced_workflows` for its run.
