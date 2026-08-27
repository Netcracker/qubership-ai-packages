# Fix central files and workflows

Fetch central sources from `Netcracker/.github` at one resolved `main` commit. Copy their contents without rendering or
substitution. Record the commit SHA and source URLs in the result. Do not run the organization broadcast workflow,
create an issue, or add a repository topic as part of remediation.

| Finding | Central source | Target |
| --- | --- | --- |
| `FILE-005` | `config/examples/grand-report.json` | `.qubership/grand-report.json` |
| `FILE-009` | `.editorconfig` | `.editorconfig` |
| `FILE-009` | `.gitattributes` | `.gitattributes` |
| `WF-001` | `workflow-templates/cla.yaml` | `.github/workflows/cla.yaml` |
| `WF-002` | `workflow-templates/pr-conventional-commits.yaml` | `.github/workflows/pr-conventional-commits.yaml` |
| `WF-008` | `workflow-templates/super-linter.yaml` | `.github/workflows/super-linter.yaml` |
| `WF-009` | `workflow-templates/automatic-pr-labeler.yaml` | `.github/workflows/automatic-pr-labeler.yaml` |
| `WF-009` | `config/examples/auto-labeler-config.yaml` | `.github/auto-labeler-config.yaml` |
| `WF-010` | `workflow-templates/pr-lint-title.yaml` | `.github/workflows/pr-lint-title.yaml` |
| `WF-011` | `workflow-templates/profanity-filter.yaml` | `.github/workflows/profanity-filter.yaml` |
| `WF-012` | `workflow-templates/link-checker.yaml` | `.github/workflows/link-checker.yaml` |
| `WF-013` | `workflow-templates/pr-assigner.yml` | `.github/workflows/pr-assigner.yml` |

Resolve the SHA with `gh`, then fetch each selected source at that SHA. Do not reconstruct files from memory.

Before writing, compare the source with the target. Add a missing file byte-for-byte. Preserve a working semantic
workflow equivalent and any intentional `.editorconfig`, `.gitattributes`, or Super-Linter customization. Show the
diff and require a new confirmation before replacing an existing file.

Validate changed JSON and YAML, inspect every workflow's required permissions and secrets, and run the repository's
relevant checks plus `git diff --check`. GitHub expressions such as `${{ github.repository }}` remain unchanged and are
evaluated by GitHub Actions in the target repository.

`FILE-006`, `FILE-007`, and `FILE-008` normally need no local file: GitHub inherits `CONTRIBUTING.md`, `SECURITY.md`,
and `CODE-OF-CONDUCT.md` from [`Netcracker/.github`](https://github.com/Netcracker/.github/tree/main/.github). Create a
local file only for confirmed repository-specific content.

The remaining catalog items have no byte-for-byte central file in this reference. Follow their routed fix instructions;
if the required repository-specific content or prerequisite cannot be determined, return `UNAVAILABLE` without opening
a ticket.

Sources: [central file map](https://github.com/Netcracker/.github/blob/main/.github/broadcast-files-config.yaml),
[workflow templates](https://github.com/Netcracker/.github/tree/main/workflow-templates), and
[broadcast workflow](https://github.com/Netcracker/.github/blob/main/.github/workflows/broadcast-files.yaml).
