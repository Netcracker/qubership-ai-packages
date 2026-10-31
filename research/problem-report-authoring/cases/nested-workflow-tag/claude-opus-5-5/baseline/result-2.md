## Goal

qubership-ratelimit pins `generic-go-build.yaml` by full commit SHA so that the logic that builds and pushes its images changes only with a commit in qubership-ratelimit. The pin does not cover the `docker-build` job. Inside the pinned commit, `generic-go-build.yaml` calls `docker-build.yaml` by the tag `v2.5.2`, and GitHub resolves that tag when the run starts.

I'd like `generic-go-build.yaml` and `generic-maven-build.yaml` to call `docker-build.yaml` by a reference that resolves to a fixed commit, so that a SHA pin on the outer workflow covers the whole chain.

## Context

All observations are from 2026-09-23.

The caller, qubership-ratelimit `.github/workflows/go-build.yml` at `7701fd5`:

```text
    39	    permissions:
    40	      contents: read
    41	      pull-requests: write
    42	      packages: write
    43	    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

Every `uses:` in `generic-go-build.yaml` at that commit:

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

Line 392 is the only executed reference not pinned by SHA (line 8 is a usage comment). `docker-build.yaml` requests `packages: write` (lines 30–32) and pins all of its own actions by SHA.

GitHub resolved the two calls differently in qubership-ratelimit run [35839496302](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302) (`pull_request`, created 2026-09-23T08:51:16Z):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The tag-resolved job in that run, [107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067), pushed the operator image (first of three manifest lines):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

On that day `v2.5.2` still pointed at the pinned commit, so the run executed the `docker-build.yaml` the pin names:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}'
```

```text
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

Nothing in the repository keeps it there: `GET /repos/Netcracker/qubership-core-infra/rulesets` returned `[]`, and `GET .../releases` returned `[]`, so `v2.5.2` is a plain tag.

Later releases and `main` (`f7fba11`) have the same pattern:

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`v2.6.0` has `@v2.6.0` at line 392, and `generic-maven-build.yaml` on `main` has `docker-build.yaml@v2.6.1` at line 222. #367 states that `generic-go-build.yaml` is used by 16 observability repositories.

GitHub's [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) page, section "Calling a reusable workflow", says the `{ref}` "can be a SHA, a release tag, or a branch name" and that "Using the commit SHA is the safest option for stability and security."

#321, opened by Renovate on 2026-07-27, makes this change on `main` for both files (`docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`). It is open with no reviews, so no release carries the pin yet.

## Scope

- The `docker-build.yaml` references in `generic-go-build.yaml` and `generic-maven-build.yaml`, and a release that carries the change.
- Out of scope: existing tags, and `actions/upload-artifact@v4` in qubership-workflow-hub `actions/docker-action/action.yml` (line 485 at `6b356d2`), which belongs to that repository.

The mechanism is yours to choose. A SHA pin as in #321 is one option; it always points at a commit earlier than the release that contains it, because a commit cannot contain its own SHA. Another option, which I haven't tried, is `./.github/workflows/docker-build.yaml`. GitHub documents that a `./` reference "is from the same commit as the caller workflow", but only for a call within the same repository.

## Definition of done

- A qubership-core-infra release in which `generic-go-build.yaml` and `generic-maven-build.yaml` reference `docker-build.yaml` by a full 40-character commit SHA, or by another reference that resolves to a fixed commit.
- For a qubership-ratelimit run that pins `generic-go-build.yaml` to that release by SHA, the `jq` command above prints `ref=-` for `docker-build.yaml`, as it does for `generic-go-build.yaml` today.
