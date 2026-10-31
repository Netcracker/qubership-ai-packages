## Goal

qubership-ratelimit calls `generic-go-build.yaml` by a full commit SHA, so that a change in qubership-core-infra does not change its build without a commit in qubership-ratelimit. That holds for every job in the called workflow except `docker-build`, the job that builds and pushes the images. Inside the pinned commit, that job calls `docker-build.yaml` by the tag `v2.5.2`, and GitHub resolves the tag when the caller runs.

A caller that pins a core-infra workflow by SHA needs the image build and push to come from a fixed commit as well.

## Context

The caller, qubership-ratelimit `.github/workflows/go-build.yml` on `feat/ratelimit-operator` at `7701fd5`, line 43:

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

`generic-go-build.yaml` at that commit, line 392, in the `docker-build` job. The workflow grants `packages: write` (lines 101-104), and so does `docker-build.yaml` (lines 30-32):

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

Every other `uses:` line in both files names a full SHA. No comment in `generic-go-build.yaml` gives a reason for the exception.

GitHub resolved the two calls this way in qubership-ratelimit run [35839496302](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302) (`pull_request`, created 2026-09-23T08:51:16Z):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The [`docker-build` job of that run](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067) pushed the operator image to GHCR (first of three manifest lines):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

On 2026-09-23 the tag still pointed at the pinned commit, so the code that ran was the code the caller pinned:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

On the same day the repository API returned `[]` for `rulesets` and for `releases`, and 404 for the legacy tag protection endpoint. Nothing visible through the API prevents the tag from being moved. GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions) says that "a tag can be moved or deleted if a bad actor gains access to the repository storing the action", and its page on [reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) says that "Using the commit SHA is the safest option for stability and security."

Later releases and `main` (`f7fba11`, read 2026-09-23 10:00 UTC) carry the same pattern:

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`v2.6.0` has `docker-build.yaml@v2.6.0` at line 392, and `generic-maven-build.yaml` on `main` has `docker-build.yaml@v2.6.1` at line 222. According to #367, the generic Go build "is used by 16 observability repositories".

Renovate, which this repository runs, opened #321 on 2026-07-27. It pins these references on `main` to `8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1` in `generic-go-build.yaml`, `generic-maven-build.yaml`, `maven-deploy.yml`, and `maven-verify.yml`. On 2026-09-23 it was open with no review. This issue asks for that change to reach a release, and it covers what #321 does not: callers that stay on releases already published.

## Scope

- On `main`, every `uses:` line that calls a reusable workflow in `Netcracker/qubership-core-infra` names a full 40-character commit SHA. Merging #321 covers the four files it touches.
- A release that contains these pins, so that callers can move their SHA to it.
- Releases already published, such as `v2.5.2`, cannot be edited, and callers pinned to them keep the tag lookup until they upgrade. One possible shape for them, not tested here, is a tag ruleset that blocks updates and deletions of release tags. Whether to add one is the maintainers' choice.
- Out of scope: what `docker-build.yaml` does. This issue is only about how it is referenced.

A commit cannot contain its own SHA, so a pinned reference names an earlier commit, and the `docker-build.yaml` that runs from a release is the one at the pinned commit. Where the two have to match, a same-repository reference (`./.github/workflows/docker-build.yaml`) is one possible shape. GitHub's page on reusable workflows says such a reference uses "the same commit as the caller workflow", but it does not say how the reference resolves inside a workflow that another repository calls, and this was not tested.

## Definition of done

- In the new release, every `uses:` line that calls a workflow in `Netcracker/qubership-core-infra` ends in a 40-character commit SHA. The commented usage example on line 8 does not count.
- For a caller run that uses the new release, the `referenced_workflows` command above lists `docker-build.yaml@<40-character SHA>` with `ref=-`, and no entry with `ref=refs/tags/...`.
