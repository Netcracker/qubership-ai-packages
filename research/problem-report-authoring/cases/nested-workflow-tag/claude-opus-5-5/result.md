### Describe the bug

In qubership-ratelimit, the `Build` workflow calls `generic-go-build.yaml` pinned by commit SHA (`@71206242f5967ac6691337913593f8623863f711 # v2.5.2`). In its run [35839496302](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302) on 2026-09-23, GitHub resolved the nested `docker-build.yaml` call by tag: `referenced_workflows` lists it as `docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2`. That job runs with `packages: write`, and in this run it pushed the `qubership-ratelimit-operator` image to GHCR. The caller's SHA pin fixes the code of `generic-go-build.yaml`, but the code that builds and pushes the images comes from whatever commit `v2.5.2` points to when the run starts.

The tag comes from `generic-go-build.yaml` itself, which calls `docker-build.yaml@v2.5.2` at line 392 of that commit. Every other `uses:` line in that file, and every `uses:` line in `docker-build.yaml`, is pinned by a full commit SHA. The same tag reference is in every later version I checked: `@v2.6.0` in v2.6.0 (line 392), and `@v2.6.1` in v2.6.1 and on `main` at `f7fba11` (line 394). `generic-maven-build.yaml` on `main` has the same reference at line 222. Because the reference is inside the called file, every caller gets it, however the caller pins `generic-go-build.yaml`.

On 2026-09-23, `v2.5.2` still peels to `71206242`, the commit the caller pins, so the code that runs today is the code the caller pinned.

#### Expected behavior

1. In a release of `generic-go-build.yaml` and `generic-maven-build.yaml`, the `uses:` line for `docker-build.yaml` names a full 40-character commit SHA. A check: `grep -nE 'docker-build\.yaml@[0-9a-f]{40}'` matches one line in each file, and in a caller run pinned to that release, the `referenced_workflows` entry for `docker-build.yaml` carries a commit SHA and no `refs/tags/` ref. The form is yours to choose; a SHA with a `# vX.Y.Z` comment, as #321 writes it, is one. I have not tested whether a same-repository `./.github/workflows/docker-build.yaml` reference inside a called workflow resolves to the called workflow's commit; GitHub's documentation states this for a top-level caller only.
2. A release tag that a released workflow file references, at least `v2.5.2`, `v2.6.0`, and `v2.6.1`, cannot be moved or deleted. Callers pinned to an already released commit such as `71206242` keep the tag reference in the file they run, so expected behavior 1 does not reach them until they upgrade. A check: a push that moves or deletes `v2.5.2` is rejected. A tag ruleset is one way to do this; the mechanism is yours to choose. On 2026-09-23, `GET /repos/Netcracker/qubership-core-infra/rulesets` returned `[]`, and `GET /repos/Netcracker/qubership-core-infra/releases/tags/v2.5.2` returned 404.

The two are independent: each can be done without the other.

What these rest on. For 1: this repository pins every other action and workflow in these files by full SHA, and Renovate, running with this repository's `renovate.json`, opened #321 to make exactly this change. GitHub's [reusable workflows documentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows#calling-a-reusable-workflow) says the ref "can be a SHA, a release tag, or a branch name" and that "Using the commit SHA is the safest option for stability and security." For 2: I found no statement from this project that its tags are immutable. This rests on GitHub's [security reference](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions), which says "a tag can be moved or deleted if a bad actor gains access to the repository storing the action", and on the absence of rulesets shown above.

### To Reproduce

I ran each command below on 2026-09-23.

1. The caller pins `generic-go-build.yaml` by SHA. From qubership-ratelimit, branch `feat/ratelimit-operator` at `7701fd5`:

   ```bash
   git show origin/feat/ratelimit-operator:.github/workflows/go-build.yml | cat -n
   ```

   Lines excerpted from the output:

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
   ```

2. At that commit, `generic-go-build.yaml` calls `docker-build.yaml` by tag and pins everything else by SHA:

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

   The `docker-build` job at lines 388-395 runs unless `skip-docker` is set or the event is a pull request from a fork. The workflow grants `packages: write` at lines 101-104, and `docker-build.yaml` grants it again at lines 30-32.

3. The latest release and `main` carry the same reference:

   ```bash
   for ref in v2.6.1 main; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
   ```

   ```text
   v2.6.1: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
   main: 394:    uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.6.1
   ```

4. How GitHub resolved both calls in a real caller run. Run 35839496302 is qubership-ratelimit's `Build` workflow, event `pull_request`, branch `feat/migrate-to-v1`, head `ae667a4`, created 2026-09-23T08:51:16Z, conclusion success. That repository's CI started the run; I queried it afterwards:

   ```bash
   curl -s https://api.github.com/repos/Netcracker/qubership-ratelimit/actions/runs/35839496302 | jq -r '.referenced_workflows[] | "\(.path) ref=\(.ref // "-")"'
   ```

   ```text
   Netcracker/qubership-core-infra/.github/workflows/generic-go-build.yaml@71206242f5967ac6691337913593f8623863f711 ref=-
   Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@v2.5.2 ref=refs/tags/v2.5.2
   ```

   Through `gh api`, the `sha` field of the same entries was `71206242f5967ac6691337913593f8623863f711` for the first and `504063c0cc240324254b46ad4fc855f14ccf2bf5`, the annotated tag object of `v2.5.2`, for the second.

5. Where the tag points today:

   ```bash
   git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
   ```

   ```text
   f7fba11dddcc0614b6701ea76f780de14d41c609	refs/heads/main
   71206242f5967ac6691337913593f8623863f711	refs/tags/v2.5.2^{}
   ```

### Version

| What | Value |
| --- | --- |
| `generic-go-build.yaml` the caller pins | `v2.5.2`, commit `71206242f5967ac6691337913593f8623863f711` (tag object `504063c0cc240324254b46ad4fc855f14ccf2bf5`) |
| Also checked | `v2.6.0` (`e8322e6`), `v2.6.1` (`8a233b03c5b5355d59c1585ffdaa1f45ea816405`), `main` at `f7fba11dddcc0614b6701ea76f780de14d41c609`, read 2026-09-23 10:00 UTC |
| Caller | Netcracker/qubership-ratelimit, `go-build.yml` on `feat/ratelimit-operator` at `7701fd5`; run 35839496302 on `feat/migrate-to-v1` at `ae667a4` |
| Runner | GitHub-hosted GitHub Actions |

### Logs

From job [107112852067](https://github.com/Netcracker/qubership-ratelimit/actions/runs/35839496302/job/107112852067), "Build and test / Build Docker image / Build Docker Images (qubership-ratelimit-operator, ./operator/Dockerfile, ., false)", in the run above. The same job pushed the same manifest under two more tags, `feat-migrate-to-v1-f7659c9` and `feat-migrate-to-v1-snapshot`.

```text
2026-09-23T08:59:28.8293149Z #20 pushing manifest for ghcr.io/netcracker/qubership-ratelimit-operator:feat-migrate-to-v1-20260923085731-193@sha256:635897f02cb0667c1da85c712e85cc30843eaabb3fca8cdc2688d8756e17251b
```

### Additional information

- Open PR #321 (Renovate, opened 2026-07-27, no reviews) makes the change of expected behavior 1 on `main`: it pins `docker-build.yaml@v2.6.1` to `@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1` in `generic-go-build.yaml` and `generic-maven-build.yaml`. Merging it and cutting a release would satisfy 1. It does not cover expected behavior 2, the callers already pinned to a released commit.
- Other open issues on the same job describe different problems: #371 (forwarding the `setup-qemu` and `setup-buildx` toggles) and #367 (fork-safe required CI gates). #367 says `generic-go-build.yaml` "is used by 16 observability repositories". I did not check how they pin it; as step 2 shows, the tag reference reaches them whichever way they do.
- I searched issues and pull requests in this repository, open and closed, for `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, and `mutable tag`. #321 was the only hit about this reference.
- A caller could set `skip-docker: true` and call `docker-build.yaml` by SHA from its own workflow. I have not tried this.
