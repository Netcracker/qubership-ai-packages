---
name: migrate-dbaas-crs
description: "Migrate legacy DBaaS declarative configuration to dbaas-operator CRDs. Use when converting deployments/dbaas-configuration.json or generic DBaaS YAML resources with subKind DatabaseDeclaration or DbPolicy into dbaas.netcracker.com/v1 InternalDatabase and DatabaseAccessPolicy manifests, including Cloud Core components with JSON, YAML, or JSON-to-CR migration artifacts."
---

# Migrate DBaaS CRs

Convert legacy DBaaS declarations into dedicated Kubernetes resources:

- `DatabaseDeclaration` to `apiVersion: dbaas.netcracker.com/v1`, `kind: InternalDatabase`
- `DbPolicy` or `dbPolicy` to `apiVersion: dbaas.netcracker.com/v1`, `kind: DatabaseAccessPolicy`

## Workflow

1. Find legacy declarations in `deployments/dbaas-configuration.json`, `helm-templates/<service>/declarations/*.yaml`, and generic resources with `kind: DBaaS` plus `subKind: DatabaseDeclaration` or `subKind: DbPolicy`.
2. Inspect the target repository's current `InternalDatabase` and `DatabaseAccessPolicy` CRD schemas.
3. Read [references/mapping.md](references/mapping.md) before editing manifests.
4. Resolve [scripts/convert_dbaas_crs.py](scripts/convert_dbaas_crs.py) relative to this `SKILL.md`. For bulk migration, optionally run it on a copy of the source, review every warning, and adjust the draft manually. Convert one or two resources directly when the script adds no value.
5. Read [references/examples.md](references/examples.md) when an exact before-and-after shape is useful.
6. Compare every generated field with the source and validate the output against the target CRDs.

## Required output

Produce standard Kubernetes manifests. Do not retain:

- `kind: DBaaS`
- `subKind: DatabaseDeclaration`
- `subKind: DbPolicy`
- `spec.classifierConfig`
- generic Core labels needed only by the legacy wrapper, unless deployment tooling still consumes them

Use normal Kubernetes `metadata.name` and `metadata.namespace`. Preserve Helm templates such as `{{ .Values.NAMESPACE }}` and `{{ .Values.SERVICE_NAME }}`.

## Optional converter

Use the converter when deterministic splitting and field relocation reduce repetitive work:

Resolve `<skill-directory>` to the directory containing this `SKILL.md`; do not assume the consumer repository contains a top-level `scripts/` directory.

```bash
python <skill-directory>/scripts/convert_dbaas_crs.py \
  --input deployments/dbaas-configuration.json \
  --output migrated-dbaas.yaml \
  --service-name '{{ .Values.SERVICE_NAME }}' \
  --namespace '{{ .Values.NAMESPACE }}'
```

The script reads JSON with the Python standard library. YAML input requires PyYAML. If PyYAML is unavailable, continue manually from [references/mapping.md](references/mapping.md) or use a YAML parser already provided by the environment; the converter is optional. For Helm-template YAML, the script can quote common template scalar values and comment standalone template actions. Treat all script output as a draft: resolve every warning, check resource names, and compare the result field by field with the source. Warnings about unsupported fields, dropped metadata, fallback service identity, Helm sanitization, or duplicate resources require manual review.

## Decisions to make explicitly

- Derive required `DatabaseAccessPolicy.spec.microserviceName` from the owning service only when the source context is unambiguous; otherwise ask the user.
- Move old classifier keys outside `microserviceName`, `scope`, `namespace`, `tenantId`, and `customKeys` to `spec.classifier.extraKeys`.
- Check `spec.settings` against the current CRD. Flag arrays, booleans, numbers, or objects when the schema accepts only string values; do not silently alter their meaning.
- Choose stable, DNS-compatible resource names and check for duplicate kind/name pairs across all generated files.

## Validation

1. Confirm resource counts: each declaration entry becomes one `InternalDatabase`, and each policy becomes one `DatabaseAccessPolicy`.
2. Confirm no legacy wrapper fields remain and every target-required field is present.
3. Render Helm templates before Kubernetes validation.
4. Run client-side validation, then `kubectl apply --dry-run=server` against an isolated cluster with the current CRDs.
5. Apply only to a dedicated local test cluster when requested. Verify `status.phase: Succeeded` and `Ready=True` for every generated resource.

If neither current CRD files nor a suitable cluster is available, complete the structural checks from [references/mapping.md](references/mapping.md), deliver the manifests as drafts, and state that schema and server-side validation remain pending. Do not claim that unvalidated drafts are ready to apply.

A successful reconciliation against an aggregator mock proves CRD and operator contract compatibility. It does not prove that a physical database was provisioned by a real aggregator and adapter.
