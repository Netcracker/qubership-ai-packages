# Testing DBaaS declarative transformation

Use layered tests. A mounted static Secret test proves only the application-side client contract;
it does not prove that either CR is valid or that the operator creates the Secret.

## Static transformation checks

Use fixtures that cover at least:

1. a default PostgreSQL service classifier;
1. PostgreSQL and MongoDB in one service;
1. two same-type identities distinguished by classifier extensions;
1. empty and explicit requested roles for one database;
1. a static tenant classifier and a context-derived tenant classifier;
1. `NamePrefix`, string creation settings, and `PhysicalDatabaseId`;
1. direct base-client calls and DB-client wrappers;
1. Helm and plain Kubernetes workloads.

Assert semantic properties rather than byte-for-byte YAML formatting:

- inventory feasibility and evidence;
- database deduplication by classifier and type;
- claim expansion by requested role;
- exact `extraKeys`/`customKeys` placement;
- collision-free DNS names;
- classifier/type/role agreement;
- Secret-to-volume-to-mount linkage;
- dynamic and blocked identities remain unchanged.

Run the bundled validator with its pinned parser dependency:

```bash
uv run --with-requirements scripts/requirements.txt \
  scripts/validate_generated.py --inventory inventory.json <manifest-or-directory> [...]
```

Paths are relative to the deployed `dbaas-declarative-transform` skill directory. The validator
checks the inventory-to-resource cardinality, classifier/type/role identities, names, claim labels,
Secret references, and workload mounts.

## Manifest validation

Run the checks available in the target repository:

```bash
helm template <release> <chart> --namespace <namespace> > rendered.yaml
kubectl apply --dry-run=client -f <generated-path>
kubectl apply --dry-run=server -f <generated-path>
```

The server dry run is the CRD-schema check. A client dry run alone does not prove that the installed
operator accepts the CR fields.

## Mounted-client integration test

Deploy a service with a correctly formatted static Secret and a REST fallback that deliberately
fails. A successful database operation then proves that the client used the mount. This layer is
fast and useful, but it bypasses `InternalDatabase` and `DatabaseSecretClaim` reconciliation.

## CR end-to-end test

Use a disposable namespace on a cluster containing the real DBaaS operator, aggregator, and target
adapter.

1. Apply namespace binding/configuration required by the local DBaaS stack.
1. Apply `InternalDatabase` and wait for its `Ready` condition and `status.phase=Succeeded`.
1. Apply `DatabaseSecretClaim` and wait for its `Ready` condition and `status.phase=Succeeded`.
1. Verify the generated Secret contains `metadata.json` and `connectionProperties.json`.
1. Deploy the transformed workload with the generated Secret mounted.
1. Exercise connection resolution, a database ping, migrations, and one read/write operation.
1. Verify a mounted-secret hit in application logs and no runtime provisioning request for the
   tested identity in aggregator logs.
1. Exercise at least one unsupported dynamic tenant path separately and confirm it retains the
   intended runtime behavior.

Capture the exact CR status, Secret keys (never Secret values), pod status, application result, and
relevant sanitized logs as evidence.

## Cleanup safety

Use an isolated namespace and inspect the target cluster before deletion. Removing a claim removes
its managed Secret and can prevent new pods from starting. Database lifecycle after deleting an
`InternalDatabase` is operator/aggregator-version dependent; do not claim data deletion or
preservation without tracing and testing that exact stack.
