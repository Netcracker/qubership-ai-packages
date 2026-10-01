# values-schema-generator

Generate a strict, validated `values.schema.json` for Helm charts. This skill discovers field names, types, and enum
values from your repository's own sources (values.yaml, Go types, installation guides, templates) and creates a
comprehensive JSON schema for values validation.

This skill is **user-invoked** — it runs when you explicitly request schema generation. It does NOT run automatically.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/values-schema-generator
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/values-schema-generator@v1.0.0
```

Then run `apm install` and `apm compile`.

## What you get

A skill that generates strict Helm chart schemas by:

1. **Discovering** all available charts in your repository
2. **Reading** sources: values.yaml, Go types, CRDs, installation guides, override files
3. **Inferring** field types from defaults, usage, and type definitions
4. **Generating** a complete values.schema.json with descriptions, types, and constraints
5. **Validating** the schema against all known values files
6. **Fixing** any validation errors in an iterative loop

## Typical use

Ask your agent:

- "Generate schema for my Helm chart"
- "Create values.schema.json"
- "Validate helm values"
- "Schema for the chart in ./charts/my-service"

If multiple charts exist, the skill presents a selection menu. It processes one chart per invocation and can continue to
the next chart when complete.

## Features

- **Fully generic** — discovers everything from your repo, never assumes specific field names or enum values
- **Multi-source discovery** — reads values.yaml, Go structs, CRDs, docs, and override files
- **Type inference** — determines types from defaults, template usage, and Go type definitions
- **Enum detection** — extracts valid values from Go constants, comments, and existing usage
- **Validation loop** — tests schema against all override files and fixes errors automatically
- **External overrides** — can process values from external directories (pipeline/infra repos)

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades.
