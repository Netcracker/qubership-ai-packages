# Fix repository files

## `FILE-001`: README

Read manifests, build files, workflows, existing docs, and entry points. Draft only supported purpose, setup, build,
test, and usage facts. Show the proposed text and ask for missing product facts before editing; do not insert
placeholders or replace unrelated maintained content. If product intent is unavailable, keep the fix `UNAVAILABLE`.
Run the repository's Markdown checks and `git diff --check`.

Source: [GitHub README guidance](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).

## `FILE-002`: Apache License 2.0

Show the detected license and ask whether a legal exception applies. A general Apply does not authorize replacing a
different license. For a missing file, fetch the exact
[Apache License 2.0 text](https://www.apache.org/licenses/LICENSE-2.0.txt), save it as root `LICENSE`, and compare the
saved bytes with the source. Do not add headers or copyright text. Replace a different or modified license only after
explicit approval. Run `git diff --check`.

## `FILE-003`: CODEOWNERS

Use `.github/CODEOWNERS` for a new file. Infer path coverage from repository structure, but require confirmation for
every proposed GitHub user or team; commits do not prove ownership. Verify syntax and owner visibility when the API
permits, then run `git diff --check`.

Source: [GitHub CODEOWNERS](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

## `FILE-004`: Qubership repository Essentials

Install `qubership-repo-essentials`, not deprecated `qubership-essentials`. Inspect root `apm.yml`, lockfile, targets,
generated assets, `.gitattributes`, and Super-Linter configuration. Require `apm` on `PATH`; initialize only when no APM
project exists, and show target changes before ensuring `claude`, `codex`, and `cursor`.

```bash
apm install Netcracker/qubership-ai-packages/agent-packages/qubership-repo-essentials
apm targets
apm audit --ci --no-policy
git diff --check
```

Keep the complete lockfile and generated assets for every target; never hand-edit generated primitives. If
`.gitattributes` is missing, route it through `FILE-009` instead of creating it here. Otherwise add only needed
generated markers. Preserve custom Super-Linter configuration and exclude only generated outputs. Completion requires
the direct dependency, lock entry, generated assets, and successful audit; report audit limitations without deleting
transitive lock entries.
