Title: Pinning generic-go-build.yaml by SHA leaves the docker-build job's workflow resolved by tag

## Goal

In qubership-ratelimit I pin `generic-go-build.yaml` by commit SHA, so that a commit in our repository decides which workflow code builds and pushes our images. For the `docker-build` job that does not hold: GitHub resolves the nested `docker-build.yaml` by the tag `v2.5.2`. I want the commit I pin to also decide which `docker-build.yaml` runs.

## Context

The caller is `.github/workflows/go-build.yml` in Netcracker/qubership-ratelimit (commit `7701fd5`, branch `feat/ratelimit-operator`), line 43:

```yaml
uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

In that commit, `generic-go-build.yaml` line 392 calls the next workflow by tag, while the seven `uses:` lines before it name a full commit SHA with a version comment:

```text
392:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2
```

I read the references of a real caller run (qubership-ratelimit run 35839496302, created 2026-09-23T08:51:16Z, `pull_request`, head `ae667a4`):

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

That job built and pushed images to GHCR, for example (job [107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067)):

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

Nothing different runs today. `git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}'` returns `71206242f5967ac6691337913593f8623863f711`, the pinned commit. But on 2026-09-23 the API returned no rulesets (`[]`), no releases, and a 404 for tag protection, so `v2.5.2` is a plain tag that nothing in the repository holds in place.

The reference is the same in later releases: on `v2.6.1` and on `main` (`f7fba11`, read 2026-09-23 10:00 UTC), line 394 is `docker-build.yaml@v2.6.1`. `generic-maven-build.yaml` on `main` (line 222) has the same pattern. Callers that use a tag, as the usage comment in line 8 shows, are not affected by this report; callers that pin by SHA are. Issue #367 says the Go workflow is used by 16 repositories. I did not check how they pin it.

GitHub's "Reuse workflows" page says "Using the commit SHA is the safest option for stability and security." This file already follows that for every other reference.

Nearest hit: open PR #321 (Renovate) changes line 394 of `generic-go-build.yaml` and line 222 of `generic-maven-build.yaml` on `main` to the SHA of `v2.6.1` (`8a233b03c5b5355d59c1585ffdaa1f45ea816405`). It does not change releases that already exist, such as `v2.5.2`. Because a commit cannot contain its own SHA, a SHA written in the file can name only an earlier commit, so each release would still run the `docker-build.yaml` of the release before it.

## Scope

The requirement is that, for a caller pinned to a commit of `generic-go-build.yaml`, the `docker-build.yaml` that runs is fixed by that commit. How to get there is the project's choice, given the self-reference limit above. One possible shape, untested: a relative call, `./.github/workflows/docker-build.yaml`. GitHub's page says a same-repository relative reference runs "the called workflow ... from the same commit as the caller workflow", but I did not establish whether that holds inside a nested workflow that a caller in another repository invokes.

Out of scope: actions that `docker-build.yaml` uses through qubership-workflow-hub. They belong to that repository.

## Definition of done

For a caller pinned by SHA to a `generic-go-build.yaml` release made after the change, the `referenced_workflows` command above lists no workflow of qubership-core-infra by tag name, and `docker-build.yaml` appears at a commit that the pinned release fixes.
