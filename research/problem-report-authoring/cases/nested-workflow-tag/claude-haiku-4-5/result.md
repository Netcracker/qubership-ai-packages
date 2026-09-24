## Describe the bug

`generic-go-build.yaml` calls `docker-build.yaml` by a mutable tag (`@v2.5.2` or `@v2.6.1`) rather than by commit SHA. When a caller pins `generic-go-build.yaml` by SHA—like qubership-ratelimit does—the pinned SHA does not constrain which version of `docker-build.yaml` runs.

If the tag were moved to a different commit, the next run of any caller would execute the new build and publish logic inside the moved tag, with no change to the caller's repository. The caller's commit SHA would not change, but the build steps and image output would.

## To Reproduce

1. Inspect the current `generic-go-build.yaml` on main:
   ```bash
   curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-go-build.yaml | grep 'docker-build.yaml@'
   ```
   Output (as of 2026-09-23):
   ```
   uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
   ```

2. Verify that the tag is not immutable:
   ```bash
   git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.6.1^{}'
   ```
   The tag resolves to a commit but carries no release object or immutable marker (e.g., the GitHub `GET /repos/.../releases/tags/v2.6.1` endpoint returns 404).

3. A caller repository that pins `generic-go-build.yaml` by SHA will resolve the `docker-build.yaml` tag at runtime:
   ```bash
   git show origin/feat/ratelimit-operator:.github/workflows/go-build.yml | grep 'generic-go-build'
   ```
   Output:
   ```
   uses: Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 # v2.5.2
   ```
   Here, the caller's pinned SHA does not constrain `docker-build.yaml`.

## Expected behavior

All reusable workflow calls inside `generic-go-build.yaml` and `generic-maven-build.yaml` should be pinned by full 40-character commit SHA, not by tag. This matches the org's documented pinning convention (qubership-ai-packages `.agents/skills/qubership-workflow-conventions/SKILL.md`, line 93: "Pin every action — Qubership and third-party — as a full 40-character commit SHA with a trailing `# vX.Y.Z` comment"). It also matches GitHub's own guidance: "Using the commit SHA is the safest option for stability and security" (GitHub Actions documentation, "Reuse workflows").

Two independent expected outcomes:
1. `generic-go-build.yaml` should call `docker-build.yaml` by commit SHA, not tag.
2. `generic-maven-build.yaml` should call `docker-build.yaml` by commit SHA, not tag.

These are distinct issues because a maintainer of this repository could fix one without touching the other (same file, same problem, but two callsites).

## Version

- Observed on `v2.5.2` (commit `71206242f5967ac6691337913593f8623863f711`)
- Same pattern confirmed on `v2.6.1` (tag object `fc321328f887a9e895fb7b22a12212ef7c568233`, peels to `8a233b03c5b5355d59c1585ffdaa1f45ea816405`)
- Same pattern observed on `main` as of 2026-09-23

## Additional context

**Tracker search:** Queries "docker-build.yaml in:title,body", "pin SHA in:title", "unpinned", "docker-build.yaml@", "pinned by SHA", "mutable tag" returned: PR #321 (open, Renovate, proposed pin of `docker-build.yaml@v2.6.1` -> SHA in `generic-go-build.yaml` and `generic-maven-build.yaml`, and also `maven-deploy.yml` and `maven-verify.yml`), and several unrelated issues (#371, #367, #401). No duplicate issue for this problem was found.

**Partial workaround:** PR #321 pins the workflow but requires merging. The caller cannot work around this because the tag resolution happens inside the callee; the caller cannot force a commit SHA from outside.

**Analysis (lower confidence):** The problem originates in these workflows because they do not follow the documented pinning convention. GitHub resolves a tag reference at workflow run time, and the `references_workflows` API endpoint returns both the pinned `generic-go-build.yaml@71206242...` and the resolved `docker-build.yaml@v2.5.2` (tag object SHA `504063c0cc...`). This behavior is consistent with GitHub's documented design for reusable workflows, where nested workflow references are resolved independently of their caller's pin. No defect in the CI platform itself was identified.
