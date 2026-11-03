Title: `generic-go-build.yaml` calls `docker-build.yaml` by tag, so a caller's SHA pin does not cover the image build

## Goal

Netcracker/qubership-ratelimit pins `generic-go-build.yaml` by full commit SHA. The `docker-build` job inside it still
calls `docker-build.yaml` by the tag `v2.5.2`, and GitHub resolves that tag at run time. That job builds and pushes the
caller's images to GHCR with `packages: write`.

A caller that pins `generic-go-build.yaml` or `generic-maven-build.yaml` by SHA should run only workflow code that the SHA
fixes, including the job that pushes its images.

## Context

The caller, `.github/workflows/go-build.yml` in qubership-ratelimit (`feat/ratelimit-operator` at `7701fd5`):

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

Line 392 of `generic-go-build.yaml` at `71206242`:

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

Every other `uses:` in that file and in `docker-build.yaml` pins a full SHA.

GitHub records the two calls differently. Caller run
[35839496302](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302) (`pull_request`, 2026-09-23):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

In the same run, [job 107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067)
pushed `ghcr.io/netcracker/qubership-ratelimit-operator` (`sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b`).

On 2026-09-23, `v2.5.2` still peeled to the pinned commit, so that run executed the code the caller pinned:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

`v2.5.2` is a plain tag. The repository has no GitHub releases, and `GET /repos/Netcracker/qubership-core-infra/rulesets`
returned `[]`. GitHub's [secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions)
states that "a tag can be moved or deleted", and its
[Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) page says "Using the
commit SHA is the safest option for stability and security."

The latest tag and `main` (`f7fba11`, 2026-09-23) both still use a tag reference:

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`generic-maven-build.yaml` on `main` has the same reference at line 222.

Renovate PR #321 pins both lines to `8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. It has been open since
2026-07-27 with no review. This issue states the problem behind that PR and the release constraint below, which a
one-time pin does not settle.

## Scope

- `generic-go-build.yaml`, the `docker-build` job.
- `generic-maven-build.yaml`, the same `docker-build.yaml` call.

Each release names its own tag in this line: `v2.5.2` calls `@v2.5.2`, `v2.6.0` calls `@v2.6.0`, and `v2.6.1` calls
`@v2.6.1`. A commit cannot contain its own SHA, so a SHA pin always names an earlier commit, such as the `v2.6.1` commit
in #321. Which reference to use, and how a release updates it, is yours to choose. One possibility, which I have not
tested, is `./.github/workflows/docker-build.yaml`. The Reuse workflows page says such a reference uses "the same commit
as the caller workflow", but it does not say how the reference resolves inside a workflow that another repository calls.

## Definition of done

- In a run of a caller that pins `generic-go-build.yaml` by SHA, no qubership-core-infra entry in `referenced_workflows`
  has a `ref` of `refs/tags/…` or `refs/heads/…`. The `curl` command above shows this.
- The same holds for a caller that pins `generic-maven-build.yaml` by SHA.
- The change is in a tagged release that callers can pin.
