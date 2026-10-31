Title: generic-go-build.yaml calls docker-build.yaml by tag, so a caller's SHA pin does not fix the publish logic

## Goal

qubership-ratelimit pins `generic-go-build.yaml` by full commit SHA, so that a commit we reviewed decides which build and publish logic runs on a push. A real caller run shows that only the first level is pinned: inside that commit, the `docker-build` job calls `docker-build.yaml` by the tag `v2.5.2`, and that job pushes the images to GHCR with `packages: write`.

We want the `docker-build.yaml` that runs to be fixed by the SHA the caller pinned.

## Context

All observations are from 2026-09-23.

**Caller.** `.github/workflows/go-build.yml` in Netcracker/qubership-ratelimit, branch `feat/ratelimit-operator` at `7701fd5`, line 43. The job has `contents: read`, `pull-requests: write`, and `packages: write`.

```text
uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

**Callee.** `generic-go-build.yaml` at `71206242f5967ac6691337913593f8623863f711` (tag `v2.5.2`):

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

Seven action references in the file are pinned by full SHA with a version comment. Line 392 is the only reference that uses a tag. The `docker-build.yaml` it calls (179 lines at that commit) pins every action it uses by SHA, so the reference at line 392 is the only unpinned hop I found between the caller and the images.

**What GitHub resolved.** Run 35839496302 of the caller (workflow "Build", `pull_request`, head `ae667a4`, created 2026-09-23T08:51:16Z):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

Job 107112852067 of that run ([log](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067)) pushed images to GHCR (listing trimmed to the first push):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

**The tag today.** At the time of reading, `v2.5.2` resolved to the same commit the caller pins, so nothing different ran:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

`GET /repos/Netcracker/qubership-core-infra/rulesets` returned `[]`, and `GET .../releases/tags/v2.5.2` returned 404, so `v2.5.2` is a plain tag, not an immutable release.

**Later releases.** The same reference is in `v2.6.0` (line 392, `@v2.6.0`), `v2.6.1` (line 394, `@v2.6.1`), and on `main` (line 394, `@v2.6.1`). `generic-maven-build.yaml` on `main` has it at line 222 (`docker-build.yaml@v2.6.1`).

**Related items.** The nearest hit is the open Renovate PR #321, "chore(deps): pin netcracker/qubership-core-infra action to 8a233b0" (created 2026-07-27, no reviews). It changes line 394 of `generic-go-build.yaml` and line 222 of `generic-maven-build.yaml` on `main` to `@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. My case differs in one respect: a PR on `main` does not change the tags that already exist, so a caller pinned to `v2.5.2`, `v2.6.0`, or `v2.6.1` still gets the tag reference until the pin ships in a new release and the caller moves to it. Issue #367 says the Go workflow is used by 16 observability repositories, so each of them takes this reference from the workflow.

GitHub's documentation on [reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) says: "Using the commit SHA is the safest option for stability and security."

## Scope

Both `generic-go-build.yaml` and `generic-maven-build.yaml`, since they share the reference. How the pin is applied (a SHA, a different call form) and how the release is cut are for the project to choose. #321 is one way to apply the pin; I have not tested it.

## Definition of done

In a run of a caller that pins `generic-go-build.yaml` by full commit SHA at a released version, the `referenced_workflows` command above prints no line with `ref=refs/tags/`.
