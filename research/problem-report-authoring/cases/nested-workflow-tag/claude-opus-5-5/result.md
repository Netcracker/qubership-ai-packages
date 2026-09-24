## Goal

qubership-ratelimit pins `generic-go-build.yaml` by commit SHA, and its images are still built and pushed by a `docker-build.yaml` that GitHub resolves through the tag `v2.5.2` at run time. I want a caller's SHA pin to fix every workflow in the chain, so that the job that pushes images with `packages: write` changes only when the caller changes its pin.

## Context

The caller, `.github/workflows/go-build.yml` on `feat/ratelimit-operator` at `7701fd5`, pins the reusable workflow by SHA and grants it `packages: write` (lines 39-43):

```yaml
    permissions:
      contents: read
      pull-requests: write
      packages: write
    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

Inside that commit, the `docker-build` job calls the next workflow by tag (`generic-go-build.yaml` line 392 at `71206242`):

```yaml
    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

GitHub resolved the two calls this way in a qubership-ratelimit run on 2026-09-23 ([run 35839496302](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302), event `pull_request`, head `ae667a4`):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The tag-resolved `docker-build.yaml` pushed the operator image in that run ([job 107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067), first of three manifest lines):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

Today `v2.5.2` peels to `71206242`, the pinned commit, so that run executed the code a SHA pin would have given it. The tag is a plain tag: the repository's rulesets API returned `[]` and it has no releases. GitHub's [reusable workflow docs](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) say "Using the commit SHA is the safest option for stability and security", and [secure use](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions) says a tag can be moved or deleted.

The call to `docker-build.yaml` is the only `uses:` in `generic-go-build.yaml` at `71206242` that is not a full SHA; its seven action references are, and so is every `uses:` in `docker-build.yaml`. The tag reference is still there in later versions, read on 2026-09-23 (`main` at `f7fba11`):

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

`generic-maven-build.yaml` on `main` has the same call at line 222. #367 says `generic-go-build.yaml` is used by 16 observability repositories; for every caller of v2.5.2, v2.6.1, or `main`, the nested call resolves through a tag whatever the caller pins.

The nearest existing item is Renovate's #321, open since 2026-07-27 with no review, which pins these two lines to `8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`. This issue asks for that outcome in a release, since callers pin released versions, and states why it matters.

## Scope

- The `docker-build.yaml` call in `generic-go-build.yaml`.
- The same call in `generic-maven-build.yaml`.

Out of scope: what `docker-build.yaml` does, and the action pins inside qubership-workflow-hub. Existing tags such as `v2.5.2` keep their tag reference whatever `main` does; whether to protect `v*` tags with a ruleset is a separate decision.

## Definition of done

- In a released version of core-infra, `grep -n 'docker-build.yaml@'` over `generic-go-build.yaml` and `generic-maven-build.yaml` shows a 40-character commit SHA, or the call uses another form that GitHub resolves to a fixed commit.
- For a caller pinned by SHA to that release, the run's `referenced_workflows` lists `docker-build.yaml` with no `refs/tags/` ref.

The mechanism is yours to choose. Two possible shapes, neither tried:

- A SHA pin, as in #321. A commit cannot contain its own SHA, so the pin names an earlier commit: #321 pins the `docker-build.yaml` of v2.6.1 into the file that ships in the next release. A change to `docker-build.yaml` would then reach `generic-go-build.yaml` callers one release later.
- A same-repository reference, `./.github/workflows/docker-build.yaml`. The reusable workflow docs say such a reference resolves to the caller's own commit, but they do not say how it resolves inside a workflow that another repository calls.
