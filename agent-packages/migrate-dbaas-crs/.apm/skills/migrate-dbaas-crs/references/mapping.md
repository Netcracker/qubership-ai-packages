# DBaaS CR Migration Mapping

Use this reference to convert old DBaaS declarative formats to the dedicated dbaas-operator CRDs.

## Source Formats

Legacy JSON:

- file: `deployments/dbaas-configuration.json`
- database declarations: `{"apiVersion":"nc.core.dbaas/v3","kind":"DatabaseDeclaration","declarations":[...]}`
- policies: `{"apiVersion":"nc.core.dbaas/v3","kind":"DbPolicy"}` or `{"kind":"dbPolicy"}`
- files may also contain a top-level JSON array mixing both declaration types

Old generic YAML CR:

- `apiVersion: core.netcracker.com/v1`
- `kind: DBaaS`
- `subKind: DatabaseDeclaration` or `subKind: DbPolicy`
- declaration body under `spec`
- Helm-template YAML may not parse as raw YAML because of unquoted `{{ ... }}` expressions or include lines under labels. Quote template scalar values or use the converter's Helm fallback, then review the output.

Target CRDs:

- `apiVersion: dbaas.netcracker.com/v1`
- `kind: InternalDatabase`
- `kind: DatabaseAccessPolicy`

## DatabaseDeclaration To InternalDatabase

Each old database declaration becomes one `InternalDatabase`.

| Old field | New field | Notes |
|---|---|---|
| `declarations[]` | one CR per item | JSON list must be split into separate Kubernetes manifests |
| `kind: DatabaseDeclaration` | `kind: InternalDatabase` | remove old `kind` and `subKind` |
| `spec.classifierConfig.classifier` or `classifierConfig.classifier` | `spec.classifier` | unwrap `classifierConfig` |
| `classifier.microserviceName` | `spec.classifier.microserviceName` | preserve Helm templates |
| `classifier.scope` | `spec.classifier.scope` | required |
| `classifier.namespace` | `spec.classifier.namespace` | usually omit; if present it must match metadata.namespace |
| `classifier.tenantId` | `spec.classifier.tenantId` | keep only when source uses tenant scope |
| `classifier.customKeys` | `spec.classifier.customKeys` | preserve nested JSON/YAML values |
| other top-level classifier keys | `spec.classifier.extraKeys` | use for legacy open classifier keys such as `transactional` |
| `type` | `spec.type` | required |
| `lazy` | `spec.lazy` | optional; do not combine with clone initial instantiation |
| `settings` | `spec.settings` | verify target schema; flag non-string values if CRD requires string values |
| `namePrefix` | `spec.namePrefix` | optional |
| `versioningConfig` | `spec.versioningConfig` | marks configuration/versioned database |
| `initialInstantiation` | `spec.initialInstantiation` | optional |
| `initialInstantiation.sourceClassifier` | `spec.initialInstantiation.sourceClassifier` | convert reserved/extra keys by the same classifier rule |

Do not keep old `spec.classifierConfig`. The dbaas-operator controller re-wraps `spec.classifier` into the aggregator wire shape.

## DbPolicy To DatabaseAccessPolicy

Each old DB policy becomes one `DatabaseAccessPolicy`.

| Old field | New field | Notes |
|---|---|---|
| `kind: DbPolicy` or `kind: dbPolicy` | `kind: DatabaseAccessPolicy` | remove old `kind` and `subKind` |
| `services` | `spec.services` | preserve list order |
| `policy` | `spec.policy` | preserve roles and database types |
| `disableGlobalPermissions` | `spec.disableGlobalPermissions` | coerce string `"false"`/`"true"` to boolean when safe |
| owning service name | `spec.microserviceName` | required by new CRD; derive from service context or ask |

Preferred derivation order for `spec.microserviceName`:

1. explicit user-provided service name
2. existing `spec.microserviceName` if the source already has it
3. Helm label `metadata.labels.app.kubernetes.io/instance`
4. Helm expression `{{ .Values.SERVICE_NAME }}` for chart-local declarations
5. service/chart folder name, if clearly the owning service

## Metadata

Use `metadata.name` values that are stable and DNS-label compatible. Examples:

- `db-declaration-1` -> `internaldatabase-1` or a domain-specific name such as `service-db`
- `db-policy-1` -> `database-access-policy` or `fiber-admin-role`

Use `metadata.namespace` from the old generic CR if present. For Helm charts, preserve:

```yaml
namespace: "{{ .Values.NAMESPACE }}"
```

Do not copy status blocks. Do not copy old generic CR labels unless the target deployment tooling still requires them.

## Validation Checklist

- Ensure no output manifest has `kind: DBaaS`.
- Ensure no `InternalDatabase` has `spec.classifierConfig`.
- Ensure every `InternalDatabase` has `spec.classifier.microserviceName`, `spec.classifier.scope`, and `spec.type`.
- Ensure every `DatabaseAccessPolicy` has `spec.microserviceName` and at least one of `spec.services` or `spec.policy`.
- Flag `lazy: true` combined with `initialInstantiation.approach: clone`.
- Flag `initialInstantiation.approach: clone` without `sourceClassifier`.
- Flag `settings` values that are not strings when the target CRD schema is `map[string]string`.
- Preserve `versioningConfig.approach: clone` or `new`; this is what marks configuration/versioned databases.
