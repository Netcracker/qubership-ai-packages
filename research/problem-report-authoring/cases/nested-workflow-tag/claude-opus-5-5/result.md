## Goal

qubership-ratelimit pins `generic-go-build.yaml` by commit SHA, so that its CI cannot change without a commit in qubership-ratelimit. The `docker-build` job of that workflow still calls `docker-build.yaml` by the tag `v2.5.2`, and that job builds the service images and pushes them to GHCR with `packages: write`. We need a release of `generic-go-build.yaml` whose call to `docker-build.yaml` resolves to a fixed commit, so that a SHA pin on the outer workflow fixes everything it runs.

## Context

The caller is `.github/workflows/go-build.yml` in Netcracker/qubership-ratelimit (branch `feat/ratelimit-operator` at `7701fd5`), line 43:

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

In `generic-go-build.yaml` at that commit, every action reference is a full SHA, and line 392 calls `docker-build.yaml` by tag:

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

`docker-build.yaml` at the same commit pins every `uses:` by full SHA as well.

GitHub resolved the nested call through the tag in qubership-ratelimit run 35839496302 (event `pull_request`, head `ae667a4`, 2026-09-23T08:51:16Z):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

[Job 107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067) of that run pushed the operator image through this call (first of three push lines):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

On 2026-09-23, `v2.5.2` peeled to `71206242f5967ac6691337913593f8623863f711`, the commit the caller pins, so both calls ran the same code that day. The rulesets and releases endpoints of this repository returned `[]`, and `releases/tags/v2.5.2` returned 404, so `v2.5.2` is a plain tag and not an immutable release. GitHub's [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) page says: "Using the commit SHA is the safest option for stability and security."

The latest tag and `main` (`f7fba11`, read 2026-09-23 10:00 UTC) have the same pattern:

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`generic-maven-build.yaml` on `main` calls `docker-build.yaml@v2.6.1` at line 222. #367 states that `generic-go-build.yaml` is used by 16 observability repositories.

Renovate's #321, open since 2026-07-27 with no reviews, pins both lines on `main` to `8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. This issue asks for that change and for a release that carries it, because a caller pinned to a release commit keeps running the tag until it moves to a commit that contains the pin.

## Scope

- Pin the `docker-build.yaml` call in `generic-go-build.yaml` and `generic-maven-build.yaml`. #321 makes this change on `main`.
- Tag a release that contains it, so that callers can pin its commit.
- Out of scope: changing the existing tags `v2.5.2`, `v2.6.0`, and `v2.6.1`. Callers move to the new release.

A SHA pin is one possible shape. A file cannot name the commit it is in, so a pinned call reaches `docker-build.yaml` from an earlier commit, as #321 pins the `v2.6.1` one. How to keep the two files in step is the project's choice; what we need is that the call resolves to a fixed commit.

## Definition of done

- A tag exists on this repository whose `generic-go-build.yaml` and `generic-maven-build.yaml` contain the change.
- In a caller run that pins `generic-go-build.yaml` to that tag's commit, the `jq` command above prints the `docker-build.yaml` entry with a commit SHA in its path and `ref=-`.
