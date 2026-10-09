# values-schema-generator

A skill that generates a strict `values.schema.json` for a Helm chart and validates it through `helm lint`. Field
names, types, and enum values come from the repository's own sources: `values.yaml`, Go API types, CRDs, templates,
the installation guide, and override files. The skill never assumes a field name or an enum value.

The skill is `values-schema-generator`. The user invokes it by name or asks to generate, update, or validate a values
schema; it does not fire on its own.

## What it does

1. Lists the charts in the repository and asks which one to process when the user has not named it.
1. Collects the sources, and each deployment's ordered stack of override files from CI jobs, scripts, `helmfile`
   releases, and Argo CD applications. It asks when the order cannot be found.
1. Merges Go structs that several `*_types.go` files define, so a short copy of a struct cannot drop fields.
1. Resolves each field's type in a fixed priority order: Go type, guide, `values.yaml` default, then a safe fallback.
   It asks only when every fallback would reject `values.yaml` itself.
1. Writes the schema, or edits only the changed nodes of an existing one.
1. Validates with `helm lint`: the chart defaults, valid and invalid edge cases, and every deployment's values stack in
   order. Helm's own merge decides what is checked, including `null` deleting a default key.
1. Fixes schema gaps in a loop and reports the fields it resolved with a fallback.

It processes one chart per invocation and offers to continue with the next.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/values-schema-generator
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/values-schema-generator@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the location your agent reads (`.claude/skills/`,
`.cursor/`, ...).

## Requirements

- `helm` on the `PATH`, for validation.
- `python3` with PyYAML, for the extraction scripts.
- `go`, only when Go types come from external modules that the skill reads from the module cache.

## Typical use

- "Generate a values schema for the chart in `charts/my-service`."
- "Update `values.schema.json` after the new `values.yaml` keys."
- "Validate our Helm values against the schema."

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.
