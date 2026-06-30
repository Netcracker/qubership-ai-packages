---
name: migrate-dbaas-crs
description: "Migrate legacy DBaaS declarative configuration to dbaas-operator CRDs. Use when converting legacy JSON or YAML resources found anywhere in a repository, including when the user supplies file or directory paths, from DatabaseDeclaration, DbPolicy, dbPolicy, or generic DBaaS resources with those subKind values into dbaas.netcracker.com/v1 InternalDatabase and DatabaseAccessPolicy manifests."
---

# Migrate DBaaS CRs

Convert legacy DBaaS declarations into dedicated Kubernetes resources:

- `DatabaseDeclaration` to `apiVersion: dbaas.netcracker.com/v1`, `kind: InternalDatabase`
- `DbPolicy` or `dbPolicy` to `apiVersion: dbaas.netcracker.com/v1`, `kind: DatabaseAccessPolicy`

## Inputs and scope

Accept one or more source file or directory paths from the user. Treat provided paths as the migration scope unless the
user requests broader discovery. Use files directly and search provided directories recursively by manifest content.
Verify that each path exists and report paths that contain no supported legacy resources.

If the user provides no paths, search the entire repository by content rather than assuming a directory layout. Find
JSON or YAML with `kind: DatabaseDeclaration`, `kind: DbPolicy` or `dbPolicy`, or `kind: DBaaS` plus
`subKind: DatabaseDeclaration` or `DbPolicy`. Common locations include `**/dbaas-configuration.json`, `deployments/`,
`<service-name>-deployments/`, and Helm chart `declarations/` or `templates/` directories.

## Workflow

1. Establish the migration scope from user-provided paths or content-based repository discovery.
2. Inspect the target repository's current `InternalDatabase` and `DatabaseAccessPolicy` CRD schemas.
3. Read [references/mapping.md](references/mapping.md) before editing manifests.
4. Resolve [scripts/convert_dbaas_crs.py](scripts/convert_dbaas_crs.py) relative to this `SKILL.md`.
   For bulk migration, optionally run it on a copy of the source, review every warning, and adjust the draft manually.
   Convert one or two resources directly when the script adds no value.
5. Read [references/examples.md](references/examples.md) when an exact before-and-after shape is useful.
6. Compare every generated field with the source and complete the required offline checks. Use CRD or cluster checks
   when available.

## Required output

Produce standard Kubernetes manifests. Do not retain:

- `kind: DBaaS`
- `subKind: DatabaseDeclaration`
- `subKind: DbPolicy`
- `spec.classifierConfig`
- generic Core labels needed only by the legacy wrapper, unless deployment tooling still consumes them

Use normal Kubernetes `metadata.name` and `metadata.namespace`. Preserve Helm templates such as
`{{ .Values.NAMESPACE }}` and `{{ .Values.SERVICE_NAME }}`.

## Optional converter

Use the converter when deterministic splitting and field relocation reduce repetitive work.

Resolve `<skill-directory>` to the directory containing this `SKILL.md`. Do not assume the consumer repository
contains a top-level `scripts/` directory.

```bash
python <skill-directory>/scripts/convert_dbaas_crs.py \
  --input <path-to-legacy-file> \
  --output migrated-dbaas.yaml \
  --service-name '{{ .Values.SERVICE_NAME }}' \
  --namespace '{{ .Values.NAMESPACE }}'
```

The script reads JSON with the Python standard library. YAML input requires PyYAML. If PyYAML is unavailable, continue
manually from [references/mapping.md](references/mapping.md) or use a YAML parser already provided by the environment;
the converter is optional.

For Helm-template YAML, the script can quote common template scalar values and comment standalone template actions.
Treat all script output as a draft: resolve every warning, check resource names, and compare the result field by field
with the source. Warnings about unsupported fields, dropped metadata, fallback service identity, Helm sanitization, or
duplicate resources require manual review.

## Decisions to make explicitly

- Derive required `DatabaseAccessPolicy.spec.microserviceName` from the owning service only when the source context is
  unambiguous; otherwise ask the user.
- Move old classifier keys outside `microserviceName`, `scope`, `namespace`, `tenantId`, and `customKeys` to
  `spec.classifier.extraKeys`.
- Check `spec.settings` against the current CRD. Flag arrays, booleans, numbers, or objects when the schema accepts only
  string values; do not silently alter their meaning.
- Choose stable, DNS-compatible resource names and check for duplicate kind/name pairs across all generated files.

## Validation

Always perform these offline checks; they do not require a Kubernetes cluster:

1. Confirm resource counts: each declaration entry becomes one `InternalDatabase`, and each policy becomes one
   `DatabaseAccessPolicy`.
2. Compare every migrated field with the source and resolve every converter warning.
3. Confirm no legacy wrapper or `spec.classifierConfig` fields remain.
4. Confirm every target-required field is present and check for duplicate kind/name pairs.
5. Render Helm templates before treating the manifests as deployable YAML.

When current CRD files are available, validate the rendered manifests against their OpenAPI schemas. When a suitable
isolated cluster is also available, optionally run `kubectl apply --dry-run=server`. Apply the resources only when the
user requests deployment, then verify `status.phase: Succeeded` and `Ready=True`.

Cluster access is optional and must not block the migration. If current CRD files are unavailable, deliver the
structurally checked manifests as drafts and state that schema validation remains pending. If CRD validation passes but
no cluster is available, state that server-side validation and reconciliation testing remain pending.

A successful reconciliation against an aggregator mock proves CRD and operator contract compatibility. It does not
prove that a physical database was provisioned by a real aggregator and adapter.
