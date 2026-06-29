# migrate-dbaas-crs

An APM package that helps coding agents migrate legacy DBaaS database
declarations and database policies to the dedicated `dbaas-operator` custom
resources:

- `DatabaseDeclaration` to `InternalDatabase`
- `DbPolicy` to `DatabaseAccessPolicy`

It handles legacy `deployments/dbaas-configuration.json` files and generic
DBaaS YAML resources used by Cloud Core components.

## Contents

- `.apm/skills/migrate-dbaas-crs/SKILL.md` - the migration workflow and
  validation contract.
- `.apm/skills/migrate-dbaas-crs/references/mapping.md` - field-by-field
  mappings and validation rules.
- `.apm/skills/migrate-dbaas-crs/references/examples.md` - representative
  before-and-after manifests.
- `.apm/skills/migrate-dbaas-crs/scripts/convert_dbaas_crs.py` - an optional
  bundled bulk converter for repetitive JSON and YAML inputs.

The converter is deliberately optional. Agents can migrate small inputs from
the mapping alone; the script is useful when a declaration list expands into
many Kubernetes resources and deterministic splitting reduces manual errors.
Its output remains a draft that must be compared with the source and validated
against the target CRDs.

## Install

```sh
apm install migrate-dbaas-crs@qubership-ai-packages
```

Then invoke the `migrate-dbaas-crs` skill by name or ask the agent to migrate
legacy DBaaS declarations or policies.

## Requirements

- Python 3 to use the optional converter.
- PyYAML when converting YAML input. JSON conversion works without it.
