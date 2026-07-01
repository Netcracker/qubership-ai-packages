---
name: dbaas-declarative-transform
description: Migrate Go microservices that use Qubership DBaaS base, PostgreSQL, or MongoDB clients from runtime provisioning to deployment-time InternalDatabase and DatabaseSecretClaim resources with mounted credentials. Use when inventorying DBaaS datasource creation, generating declarative CRs, mounting DBaaS Secrets, or deciding whether service or tenant database usage can be migrated. Reject runtime-derived tenant identities and preserve every classifier key, database type, and requested role exactly.
---

# Transform DBaaS provisioning to declarative resources

Inventory every logical database identity before editing manifests. Generate one
`InternalDatabase` for each unique `(classifier, type)` and one `DatabaseSecretClaim` for each
unique `(classifier, type, requested userRole)`. Keep dynamic tenant provisioning on the existing
runtime path.

This skill covers Go services using Qubership DBaaS clients. Report non-Go client usage as outside
this skill instead of guessing its API contract.

Read [contracts.md](references/contracts.md) before generating resources. Read
[testing.md](references/testing.md) when validating generated output or running a cluster test.
Use `scripts/validate_generated.py` for deterministic inventory/resource/mount consistency checks.

## 1. Verify mounted-secret compatibility

Inspect the target service's resolved dependencies, not a sibling checkout or an assumed version.

1. Read `go.mod` and any `replace` directives.
1. Resolve the base-client source used by the build with `go list -m` or `go env GOMODCACHE`.
1. Confirm that `NewDbaaSPool` registers a provider that reads
   `/etc/secrets/dbaas-secrets`, `metadata.json`, and `connectionProperties.json` before the REST
   fallback.
1. If that provider is absent, report a required client upgrade or application integration change.
   Do not claim that manifest-only migration is possible.

Do not remove the REST fallback. Supported declarative identities should hit the mounted provider;
unsupported dynamic identities may still need runtime provisioning.

## 2. Build a datasource inventory

Search production Go files, configuration, and workload manifests. Exclude tests only after
checking that they are not the sole documentation of a wrapper's behavior.

Start with these symbols and follow aliases and wrappers to the actual database operation:

```text
NewDbaaSPool
ServiceDatabase
TenantDatabase
GetOrCreateDb
GetConnection
FindConnectionProperties
GetPgClient
GetMongoClient
BaseServiceClassifier
BaseTenantClassifier
DbParams.Classifier
BaseDbParams
```

For every call path, resolve:

- the exact database type string;
- the classifier function and every emitted key/value;
- whether each value is fixed for a deployment or derived from request/runtime context;
- `BaseDbParams.NamePrefix`, `Settings`, `PhysicalDatabaseId`, and `Role`;
- all deployment/stateful-set containers that consume the datasource;
- the source locations that prove the result.

Do not infer scope solely from `ServiceDatabase` or `TenantDatabase`. Both APIs accept an explicit
`DbParams.Classifier` that overrides their default classifier. Trace that function.

Do not default an unresolved database type to PostgreSQL. Mark the datasource `AMBIGUOUS` and stop
generation for it.

### Feasibility

Classify an identity as:

- `SUPPORTED`: every classifier value is known from source, deployment values, or environment
  configuration at deployment time;
- `NOT_SUPPORTED_DYNAMIC`: any identity value, especially `tenantId`, comes from request context,
  `tenant.Of(ctx)`, or another runtime-only source;
- `BLOCKED`: the imperative request uses a field without a confirmed declarative mapping, including
  `PhysicalDatabaseId`;
- `AMBIGUOUS`: type, classifier, role, or parameter flow cannot be proven statically.

`TenantDatabase(...)` with its default classifier is dynamic. A custom classifier supplied through
`DbParams.Classifier` may be static; judge the function, not the method name.

### Deduplicate by identity

Canonicalize classifier maps by keys and values for comparison.

- Repeated call sites with the same `(classifier, type)` share one `InternalDatabase`.
- Different types always require different `InternalDatabase` resources.
- Different classifier keys or values require different `InternalDatabase` resources.
- Different requested roles share the database but require separate claims and mounted Secrets.

Produce the inventory before making changes:

```json
{
  "datasources": [
    {
      "id": "orders-postgresql-service",
      "type": "postgresql",
      "classifier": {
        "microserviceName": "orders",
        "namespace": "orders-ns",
        "scope": "service"
      },
      "requestedRoles": [""],
      "parameters": {
        "namePrefix": "",
        "settings": {},
        "physicalDatabaseId": ""
      },
      "codeLocations": ["internal/storage/postgres.go:42"],
      "migrationFeasibility": "SUPPORTED"
    }
  ]
}
```

Report all dynamic, blocked, and ambiguous entries. Never generate placeholders that could create
the wrong database.

## 3. Map the imperative request

Preserve the runtime request exactly:

- typed classifier keys map to `spec.classifier.microserviceName`, `scope`, `namespace`, and
  `tenantId`;
- a runtime top-level extension key maps to `spec.classifier.extraKeys` so it remains top-level on
  the wire;
- a runtime nested `customKeys` object maps to `spec.classifier.customKeys`;
- `BaseDbParams.NamePrefix` maps to `InternalDatabase.spec.namePrefix`;
- database-creation `BaseDbParams.Settings` map to `InternalDatabase.spec.settings` only when every
  value is representable as a string;
- `BaseDbParams.Role` maps to `DatabaseSecretClaim.spec.userRole` exactly, including the difference
  between omitted/empty and an explicit role;
- connection-pool, migration, retry, and client options remain application configuration;
- `PhysicalDatabaseId` has no confirmed field in the current `InternalDatabase` contract: mark it
  `BLOCKED` unless the target operator/aggregator contract proves a mapping.

Mongo's default classifier adds top-level `dbClassifier: default`. Preserve it under `extraKeys`.
Apply the same rule to any custom top-level classifier extension.

## 4. Choose collision-free names

Build a stable DNS label from the full identity, not only service and scope.

1. Start with `<microservice>-<type>-<scope>`.
1. Append a static tenant ID for tenant scope.
1. Append a short meaningful discriminator for additional classifier identity fields. If no safe,
   concise discriminator exists, append the first eight lowercase hex characters of a SHA-256 hash
   of the canonical classifier JSON.
1. Normalize to lowercase DNS-1123 syntax and keep Kubernetes names at most 63 characters. Preserve
   the hash suffix when truncating.

Use these suffixes:

```text
InternalDatabase:    <identity>-db
DatabaseSecretClaim: <identity>-<role-or-default>-claim
Secret:              <identity>-<role-or-default>-credentials
Volume:              <identity>-<role-or-default>-secret
```

Check every generated resource, Secret, volume, and mount name for collisions before writing.

## 5. Generate resources

For every supported database identity, generate an `InternalDatabase`. For every requested role of
that identity, generate a claim. Use the canonical templates in
[contracts.md](references/contracts.md).

Rules:

- Set `metadata.namespace` to the workload namespace.
- Set or omit `classifier.namespace` consistently in both resources. If set, it must equal
  `metadata.namespace`.
- Copy the complete classifier and type identically into the paired claim.
- Add non-empty `app.kubernetes.io/name` to each claim; it becomes `originService`.
- Set `lazy: false` unless the existing deployment contract explicitly requires lazy provisioning.
- Omit defaulted optional fields instead of inventing values.
- Do not add `initialInstantiation` or versioning behavior unless the existing configuration
  requires it.

Prefer the consumer repository's existing Helm/declaration layout. For plain manifests, use a
coherent existing manifests directory. Do not create backup files; rely on version-control diffs.

## 6. Mount every generated Secret

Update each `Deployment` or `StatefulSet` container that consumes the corresponding role:

```yaml
volumes:
  - name: orders-postgresql-service-default-secret
    secret:
      secretName: orders-postgresql-service-default-credentials

containers:
  - name: orders
    volumeMounts:
      - name: orders-postgresql-service-default-secret
        mountPath: /etc/secrets/dbaas-secrets/orders-postgresql-service-default-credentials
        readOnly: true
```

The final path component must equal `DatabaseSecretClaim.spec.secretName`. Preserve existing Helm
expressions, volumes, mounts, init containers, and sidecars. Mount only into containers that use the
database.

## 7. Validate before completion

Perform all applicable checks from [testing.md](references/testing.md):

1. Render Helm templates before validating YAML.
1. Run `scripts/validate_generated.py --inventory <inventory.json> <rendered-or-plain-yaml>`.
1. Validate syntax and run client-side and server-side dry runs when a suitable cluster is present.
1. Compare canonical classifiers and type between each InternalDatabase and claim.
1. Verify claim role against every client request role.
1. Verify that all names are unique and DNS-compatible.
1. Verify each claim Secret has exactly one consuming volume/mount unless intentional sharing is
   documented.
1. Confirm unsupported dynamic call paths were not removed or redirected.

Do not use a one-InternalDatabase-to-one-claim count check: multiple roles legitimately create
multiple claims for one database.

## Completion report

Report:

- every discovered logical database identity and its evidence;
- supported, dynamic, blocked, and ambiguous counts;
- the deduplication decisions;
- every generated or modified file;
- validation commands and their actual results;
- dependency compatibility evidence;
- remaining runtime fallback paths and why they remain.

Call the migration complete only when generated mounted Secrets match the client lookup key:
`canonical classifier | lowercase type | trimmed requested role`.
