## Goal

Reusable workflows in qubership-core-infra should pin all called workflows to immutable commit SHAs, not mutable tags, to ensure reproducible and auditable builds.

## Context

Callers of `generic-go-build.yaml` often pin it by commit SHA to guarantee reproducibility (e.g., qubership-ratelimit pins it at 71206242 / v2.5.2). However, inside `generic-go-build.yaml` (line 392), the `docker-build` job calls `docker-build.yaml` by the mutable tag `@v2.5.2` instead of a SHA. If that tag is moved, recreated, or deleted, the next build run would execute different build and publish logic with no entry in the caller's repository recording the change.

This is a security and reproducibility risk because:
1. The `docker-build` job carries `packages: write` permissions and pushes container images to a registry.
2. A mutable tag can be moved by anyone with write access to the repository.
3. Callers who pin `generic-go-build.yaml` by SHA expect all nested references to be equally fixed.
4. GitHub's own security documentation states: "Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release."

The same pattern appears in `generic-maven-build.yaml` (line 222: `docker-build.yaml@v2.6.1`), affecting multiple callers and releases.

## Scope

**Current state** (as of 2026-09-23):
- `generic-go-build.yaml` line 392: `uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2`
- `generic-maven-build.yaml` line 222: `uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1`
- Same issue exists on branch `main` (docker-build.yaml@v2.6.1)
- Tag `v2.5.2` currently resolves to commit 71206242f5967ac6691337913593f8623863f711; the tag itself is a plain annotated tag, not an immutable release.

**Affected callers**: Any repository that pins `generic-go-build.yaml` or `generic-maven-build.yaml` by SHA, expecting nested references to also be fixed (e.g., qubership-ratelimit).

## Expected Behavior

References to `docker-build.yaml` in reusable workflows should be pinned by full commit SHA with an optional trailing comment naming the tag version for readability, following Netcracker's own workflow conventions (line 93 of qubership-ai-packages workflow-conventions skill: "Pin every action — Qubership and third-party — as a full 40-character commit SHA with a trailing `# vX.Y.Z` comment").

Example:
```yaml
uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1
```

This makes nested references immutable and auditable, matching the intent of callers who pin `generic-go-build.yaml` itself by SHA.

## Definition of Done

1. `generic-go-build.yaml` line 392 references `docker-build.yaml` by full commit SHA.
2. `generic-maven-build.yaml` line 222 references `docker-build.yaml` by full commit SHA.
3. Both references include a trailing comment with the tag version.
4. The change is consistent with the organization's workflow pinning conventions.

## Reproducer

Verify the current tag references:
```bash
curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-go-build.yaml | grep -n 'docker-build.yaml@'
# Output (line 394): uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1

curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-maven-build.yaml | grep -n 'docker-build.yaml@'
# Output (line 222): uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
```

Both use mutable tags instead of commit SHAs.

## Related

PR #321 "chore(deps): pin netcracker/qubership-core-infra action to 8a233b0" already addresses this for `generic-go-build.yaml` and `generic-maven-build.yaml`, pinning both to SHA 8a233b03c5b5355d59c1585ffdaa1f45ea816405. This issue can be resolved by merging that PR or applying the same pinning approach.

## Evidence

All workflow file references were fetched directly from the repository at the specified commits:
- `generic-go-build.yaml` at v2.5.2 (71206242): line 392 uses `docker-build.yaml@v2.5.2`
- `generic-maven-build.yaml` at v2.5.2: line 222 uses `docker-build.yaml@v2.6.1`
- Same pattern on branch `main` and release v2.6.1
- Tag `v2.5.2` is not an immutable release; it is a plain annotated tag without protection rules

The organization's workflow conventions document (qubership-ai-packages SKILL.md) explicitly requires SHA pinning with tag comments, consistent with GitHub's security best practices as documented in https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions.
