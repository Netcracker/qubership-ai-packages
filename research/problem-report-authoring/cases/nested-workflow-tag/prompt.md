# What the session established

You spent a session investigating a CI finding in qubership-ratelimit. These are your notes; nothing here has been
written up for anyone else. All observations are from 2026-09-23.

## Starting point

The person filing pasted a review finding (DEP-01, written in Russian, from an earlier deep review of qubership-ratelimit),
roughly: `go-build.yml` pins `generic-go-build.yaml` by commit SHA, but inside that commit the `docker-build` job
calls `docker-build.yaml` by the mutable tag `v2.5.2`; that job builds and pushes the operator and service images with
`packages: write`; if `v2.5.2` were moved, the next push would run different build/publish logic with no commit in
qubership-ratelimit. Suggested fixes in the finding: ask qubership-core-infra to pin `docker-build.yaml` by SHA inside
`generic-go-build.yaml`, or call `docker-build.yaml` directly by SHA from `go-build.yml`.

The person filing asked for the issue text in English (their standing rule for ticket texts: English, no production policy
content, no wiki links). Target tracker chosen: Netcracker/qubership-core-infra.

## Repositories and SHAs

| What | Value |
| --- | --- |
| Caller repo | Netcracker/qubership-ratelimit, base branch `feat/ratelimit-operator` at `7701fd5` ("feat: Alert rules shipped with the chart (#48)") |
| Callee repo | Netcracker/qubership-core-infra (public, default branch `main`, not archived) |
| Tag `v2.5.2` | annotated tag object `504063c0cc240324254b46ad4fc855f14ccf2bf5`, peels to commit `71206242f5967ac6691337913593f8623863f711` |
| Tag `v2.6.1` | tag object `fc321328f887a9e895fb7b22a12212ef7c568233`, peels to `8a233b03c5b5355d59c1585ffdaa1f45ea816405` |
| Other tags | v2.6.0 e8322e6, v2.5.1 9d3a072, v2.5.0 8668020, v2.4.3 afe9035 ... |
| `main` of core-infra | `f7fba11dddcc0614b6701ea76f780de14d41c609` (read 2026-09-23 10:00 UTC) |
| workflow-hub actions used by docker-build.yaml | `netcracker/qubership-workflow-hub/actions/{metadata-action,docker-action}@6b356d28e46b2d4683cccb1d91f92643d7f0c513 # v2.0.11` |

## Caller workflow: qubership-ratelimit `.github/workflows/go-build.yml` (on `origin/feat/ratelimit-operator`)

```bash
git show origin/feat/ratelimit-operator:.github/workflows/go-build.yml | cat -n
```

Relevant lines:

```text
    20	permissions:
    21	  contents: read
    23	on:
    24	  push:
    25	    branches:
    26	      - main
    27	      - 'lts/**'
    28	  pull_request:
    29	    types: [opened, synchronize, reopened]
    32	  build:
    39	    permissions:
    40	      contents: read
    41	      pull-requests: write
    42	      packages: write
    43	    uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
    66	      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Callee: `generic-go-build.yaml` at 71206242 (v2.5.2), 396 lines

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

- Workflow-level `permissions:` (lines 101-104): `contents: read`, `pull-requests: write`, `packages: write`.
- `docker-build` job (lines 388-395): `needs: [test]`,
  `if: ${{ !inputs.skip-docker && !(github.event_name == 'pull_request' && github.event.pull_request.head.repo.fork) }}`,
  `uses: .../docker-build.yaml@v2.5.2`, `with: ref, dry-run, config-filename`.
- Inputs: `dry-run` (boolean, default false, "Run docker build in dry-run mode (no push)"), `skip-docker` (boolean,
  default false), `ref` (string).
- Header usage comment (line 8) shows callers using `generic-go-build.yaml@v2.x.x` (a tag), with `secrets: inherit`.

## `docker-build.yaml` at 7120624, 179 lines

- `permissions:` line 30-32: `contents: read`, `packages: write`.
- Every `uses:` is SHA-pinned: `actions/checkout@d23441a4... # v6`, workflow-hub `metadata-action` and `docker-action`
  `@6b356d28... # v2.0.11`.
- One level lower, workflow-hub `docker-action/action.yml` at 6b356d2 pins every action by SHA except line 485:
  `uses: actions/upload-artifact@v4` (tag). Different owner (qubership-workflow-hub); not pursued.

## Same reference in later releases and on main

```bash
for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
```

```text
v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

Also v2.6.0 line 392 `@v2.6.0`. `generic-maven-build.yaml` on `main` line 222 has the same pattern
(`docker-build.yaml@v2.6.1`).

## How GitHub resolved the calls in a real caller run

Run 35839496302 (qubership-ratelimit, workflow "Build", event `pull_request`, branch `feat/migrate-to-v1`, head `ae667a4`,
created 2026-09-23T08:51:16Z, conclusion success).

```bash
curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
```

```text
Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
```

(With `gh api`, the `sha` field was `71206242...` for the first and `504063c0...`, the tag object, for the second.)

Job 107112852067 ("Build and test / Build Docker image / Build Docker Images (qubership-ratelimit-operator,
./operator/Dockerfile, ., false)") pushed to GHCR:

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
2026-09-23T08:59:29.5768985Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-f7659c9@sha256:635897f0...
2026-09-23T08:59:30.1920286Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-snapshot@sha256:635897f0...
```

Job URL: https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067

## Today's state of the tag and its protection

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
```

```text
f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
```

- So the tag currently resolves to exactly the pinned commit: nothing different runs today.
- `GET /repos/Netcracker/qubership-core-infra/rulesets` returned `[]`; `GET .../releases` returned `[]`;
  `GET .../releases/tags/v2.5.2` 404; legacy `tags/protection` 404. `v2.5.2` is a plain tag, not an immutable release.
- Private vulnerability reporting on core-infra: `false`.

## Tracker search (Netcracker/qubership-core-infra, issues and PRs, all states)

Queries: `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`,
`mutable tag`. Hits:

- #321 (open PR, by Renovate, created 2026-07-27, updated 2026-09-16, mergeable, 0 reviews, 1 comment from
  sonarqubecloud): "chore(deps): pin netcracker/qubership-core-infra action to 8a233b0". Changes one line each in
  `generic-go-build.yaml` (line 394: `docker-build.yaml@v2.6.1` -> `@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1`),
  `generic-maven-build.yaml` (line 222, same), `maven-deploy.yml` and `maven-verify.yml` (their
  `generic-maven-build.yaml@v2.6.1` -> `@8a233b0... # v2.6.1`). Listed in Dependency Dashboard #258 under
  `renovate/pin-dependencies`.
- #371 (open, 2026-08-20): generic-go-build / docker-build: forward docker-action's setup-qemu and
  setup-buildx toggles. Different problem, same job.
- #367 (open, 2026-08-19): Make generic Go build fork-safe for required CI gates. States the workflow
  "is used by 16 observability repositories". #368 is its closed PR.
- #401 (merged, 2026-09-09): chore(ci): pin the Go compiler in the generic build workflow.
- Older: #196, #216, #102, #33 (unrelated).

## Channel

- No `.github/ISSUE_TEMPLATE` in core-infra; the org repo `Netcracker/.github` has `.github/ISSUE_TEMPLATE/bug_report.yml`
  (fields: Describe the bug [required], To Reproduce [required], Version, Logs, Additional information; title prefix
  `[Bug]: `, label `bug`) and `feature_request.yml`.
- Org SECURITY.md: "report any security issue to `opensourcegroup@netcracker.com`". Org CONTRIBUTING.md: only CLA and
  Code of Conduct; no AI policy found (repo or org).
- Recent issues by the person filing in this tracker use no `[Bug]:` prefix; bug issues carry label `bug` and a
  `26.4_scope` label. Their structure: `## Goal`, `## Context`, `## Scope`, `## Definition of done`.
- core-infra `renovate.json` extends `github>Netcracker/qubership-core-infra:renovate-frameworks-config`.

## Pinning conventions and documentation

- Org workflow conventions (Netcracker/qubership-ai-packages, `.agents/skills/qubership-workflow-conventions/SKILL.md`,
  last changed 0ce6088 2026-07-02), line 93 "Pin every action — Qubership and third-party — as a full 40-character
  commit SHA with a trailing `# vX.Y.Z` comment", line 107: "Forbidden: `@main`, short SHAs, bare tags (`@v6`,
  `@v1.2.3`). Always full SHA." Written for actions; says nothing specific about reusable workflows.
- GitHub docs, "Reuse workflows" (https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows),
  section "Calling a reusable workflow": "the `{ref}` can be a SHA, a release tag, or a branch name"; "Using the commit
  SHA is the safest option for stability and security."; "When you reference a reusable workflow in the same repository
  using `$/` or `./` (without `{owner}/{repo}` and `@{ref}`), the called workflow is from the same commit as the caller
  workflow." Section "Nesting reusable workflows": "Nested reusable workflows require all workflows in the chain to be
  accessible to the caller." The fetch said the page does not explicitly address how a `./` reference inside a nested
  called workflow resolves.
- GitHub docs, "Secure use reference", section "Using third-party actions"
  (https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions): "Pinning an action to a
  full-length commit SHA is currently the only way to use an action as an immutable release."; "a tag can be moved or
  deleted if a bad actor gains access to the repository storing the action."

## Not checked before drafting

- How the 16 repositories from #367 pin `generic-go-build.yaml`.
- The `skip-docker: true` + direct `docker-build.yaml@<sha>` workaround was not tried.

## The task

Draft the GitHub issue for Netcracker/qubership-core-infra that reports this. Write the issue body as Markdown to the
output file named in your instructions, and the hand-over note to the person filing (anything that is not part of
the issue body) to the second output file. Do not open a browser, do not use the network, and do not file anything:
everything established is in these notes.
