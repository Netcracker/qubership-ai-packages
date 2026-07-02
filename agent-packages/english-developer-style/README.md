# english-developer-style

Compatibility alias for the original package name. Installing
`english-developer-style` now pulls in
[`english-us-developer-style`](../english-us-developer-style/), so the
bare name defaults to American English.

This package carries no skill of its own. Its only job is to keep the old
name resolvable and point it at a concrete dialect.

## Which package do I want?

- New American-English projects: depend on
  [`english-us-developer-style`](../english-us-developer-style/) directly.
- British-English projects: depend on
  [`english-uk-developer-style`](../english-uk-developer-style/).
- Already pinning `english-developer-style` and unable to rename the
  dependency: keep this alias. You now get the American-English default.

A direct dialect dependency states intent and skips one hop of
resolution, so pin the alias only when you cannot change the name.

## History

`english-developer-style` used to be a British-English-first skill. The
skill now ships as two dialect packages —
[`english-uk-developer-style`](../english-uk-developer-style/) and
[`english-us-developer-style`](../english-us-developer-style/) — and this
name is kept only for backward compatibility. The default dialect moved
from British to American with the split, which is why the alias is a 2.0
release.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/english-developer-style
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/english-developer-style@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to
pin, for example `v1.0.0`.

`apm install` then resolves `english-us-developer-style` transitively and
deploys its skill and generated instruction outputs.
