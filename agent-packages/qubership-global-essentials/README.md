# qubership-global-essentials

Deprecated compatibility alias. The global user-workspace baseline now lives in
[`qubership-user-essentials`](../qubership-user-essentials/); installing
`qubership-global-essentials` resolves to it.

The new name pairs with
[`qubership-repo-essentials`](../qubership-repo-essentials/), the
per-repository baseline that `qubership-user-essentials` builds on. Install the
new package globally:

```sh
apm install qubership-user-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

Depend on `qubership-user-essentials` directly; pin this alias only when you
cannot change the name yet.
