## Goal

A repository that calls `generic-go-build.yaml` by commit SHA wants the image build and publish step to be fixed by that SHA too. Today it is not. `generic-go-build.yaml` calls `docker-build.yaml` by a tag, so a repository such as `qubership-ratelimit` pins the outer workflow and still runs whatever `v2.5.2` points to when the job starts.

## Context

All observations below are from 2026-09-23.

`qubership-ratelimit` (`feat/ratelimit-operator` at `7701fd5`) pins the workflow by full SHA in `.github/workflows/go-build.yml`, line 43:

```text
uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
```

That commit is the one `v2.5.2` peels to. Inside it, every action is pinned by SHA except the last `uses:`, the `docker-build` job at line 392 (line 8 is a usage comment):

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

GitHub resolves that tag at run time. Run 35839496302 of `qubership-ratelimit` (workflow "Build", `pull_request`, created 2026-09-23T08:51:16Z) lists these referenced workflows:

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

The `docker-build` job of that run pushed `ghcr.io/netcracker/qubership-ratelimit-operator` to GHCR (job 107112852067, `packages: write`). The job log, trimmed to the first push line:

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

The tag is not protected. `v2.5.2` is a plain tag, not an immutable release. The GitHub API returned `[]` for `GET /repos/Netcracker/qubership-core-infra/rulesets` and for `.../releases`, and 404 for `.../releases/tags/v2.5.2` and for the legacy `tags/protection` endpoint.

No different logic has run. On the same day the tag still resolved to the pinned commit:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

The pattern is not limited to `v2.5.2`. `generic-go-build.yaml` has `docker-build.yaml@v2.6.0` in `v2.6.0` (line 392), and `docker-build.yaml@v2.6.1` in `v2.6.1` and on `main` (line 394). `generic-maven-build.yaml` on `main` has `docker-build.yaml@v2.6.1` at line 222.

## Why this repository

The nested reference is set inside `generic-go-build.yaml`, so a caller cannot change it from its own workflow file. Pinning `generic-go-build.yaml` fixes only that file.

The wording in the GitHub docs supports pinning here. "Reuse workflows" ("Calling a reusable workflow") says: "Using the commit SHA is the safest option for stability and security." "Secure use reference" says a tag "can be moved or deleted if a bad actor gains access to the repository storing the action." The second quote is about actions, and I did not find a statement about reusable workflows specifically.

The same workflow already pins its seven third-party and GitHub actions by SHA (listing above), and `docker-build.yaml` at `71206242` pins all of its own. The `docker-build` job is the one `uses:` left on a tag.

Known affected caller: `qubership-ratelimit`. Issue #367 says the workflow is used by 16 observability repositories. I did not check how they reference it.

## Prior proposals

Searched issues and pull requests in this repository, all states: `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, `mutable tag`.

The nearest hit is PR #321 (open, from Renovate, created 2026-07-27, updated 2026-09-16, no reviews). It changes `generic-go-build.yaml` line 394 and `generic-maven-build.yaml` line 222 from `docker-build.yaml@v2.6.1` to `docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`, and does the same for the `generic-maven-build.yaml@v2.6.1` references in `maven-deploy.yml` and `maven-verify.yml`. It pins to the `v2.6.1` commit, so the pin does not need the SHA of the release that contains it.

This issue differs from #321 in what it asks for after the merge. A change on `main` does not alter the released tags, and `qubership-ratelimit` calls `v2.5.2`. The pin reaches callers only in a new release that they then move to.

## Definition of done

- In a tagged release, every `uses:` of a workflow or action in `generic-go-build.yaml` and `generic-maven-build.yaml`, outside comments, ends in a full 40-character commit SHA with a trailing `# vX.Y.Z` comment.
- The `jq` command above, run against a `qubership-ratelimit` run that calls that release, prints a commit SHA after `docker-build.yaml@` and no tag name.

## Scope

In scope: the two reusable workflows above, and any other workflow in this repository that calls `docker-build.yaml` by a tag. I did not search for others beyond the files named here.

Out of scope: how callers reference `generic-go-build.yaml` (the usage comment at line 8 shows a tag), the choice of how to produce the pin, and the release schedule.

One level lower, `docker-action/action.yml` in `qubership-workflow-hub` at `6b356d28e46b2d4683cccb1d91f92643d7f0c513` uses `actions/upload-artifact@v4` at line 485, the only tag reference I found there. That belongs to `qubership-workflow-hub`, and I have not reported it.
