# qubership-essentials

Deprecated compatibility alias. The repository baseline now lives in
[`qubership-repo-essentials`](../qubership-repo-essentials/); installing
`qubership-essentials` resolves to it.

Two things changed with the rename:

- The name states the installation scope: `qubership-repo-essentials` is the
  per-repository baseline, and
  [`qubership-user-essentials`](../qubership-user-essentials/) is the global
  user-workspace superset.
- `codex-review` left the repository baseline. Depend on
  [`codex-review`](../codex-review/) directly if your repository still wants
  agent-run Codex reviews.

Depend on `qubership-repo-essentials` directly; pin this alias only when you
cannot change the name yet.
