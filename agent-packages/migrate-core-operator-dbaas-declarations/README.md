# migrate-core-operator-dbaas-declarations

An APM package that helps coding agents migrate legacy Core Operator DBaaS database
declarations and database policies to the dedicated `dbaas-operator` custom
resources:

- `DatabaseDeclaration` to `InternalDatabase`
- `DbPolicy` to `DatabaseAccessPolicy`

It handles legacy DBaaS JSON and YAML resources regardless of directory layout,
including `deployments/`, `<service-name>-deployments/`, and Helm chart folders.

## Contents

- `.apm/skills/migrate-core-operator-dbaas-declarations/SKILL.md` - the migration workflow and
  validation contract.
- `.apm/skills/migrate-core-operator-dbaas-declarations/references/mapping.md` - field-by-field
  mappings and validation rules.
- `.apm/skills/migrate-core-operator-dbaas-declarations/references/examples.md` - representative
  before-and-after manifests.
- `.apm/skills/migrate-core-operator-dbaas-declarations/scripts/convert_dbaas_crs.py` - an optional
  bundled bulk converter for repetitive JSON and YAML inputs.

The converter is deliberately optional. Agents can migrate small inputs from
the mapping alone; the script is useful when a declaration list expands into
many Kubernetes resources and deterministic splitting reduces manual errors.
Its output remains a draft that must be compared with the source and validated
against the target CRDs.

## Install

```sh
apm install migrate-core-operator-dbaas-declarations@qubership-ai-packages
```

Then invoke the `migrate-core-operator-dbaas-declarations` skill by name and optionally provide one or
more manifest file or directory paths to define the migration scope.

## Requirements

- Python 3 to use the optional converter.
- PyYAML when converting YAML input. JSON conversion works without it.
