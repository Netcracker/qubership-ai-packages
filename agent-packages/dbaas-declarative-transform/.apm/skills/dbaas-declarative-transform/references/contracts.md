# DBaaS declarative and mounted-secret contracts

Use this reference when generating or reviewing `InternalDatabase`, `DatabaseSecretClaim`, and
workload mounts.

## Identity model

The database identity is the complete classifier plus database type. The mounted-secret client key
adds the requested role:

```text
database identity = canonical(classifier) | lowercase(type)
mounted lookup    = canonical(classifier) | lowercase(type) | trim(requested role)
```

Classifier equality includes extension keys and their JSON values. Key order does not matter; a
missing key, extra key, different value, or nested-vs-top-level placement does matter.

The operator defaults an omitted classifier namespace from `metadata.namespace` before calling the
aggregator and writing Secret metadata. The running client normally enriches an omitted namespace
from `microservice.namespace`. Both sides must resolve to the same value.

## Classifier mapping

Use typed fields for the standard identity:

```yaml
classifier:
  microserviceName: orders
  namespace: orders-ns
  scope: service
```

Add `tenantId` only when it is part of a deployment-known tenant identity.

Preserve a runtime top-level extension with `extraKeys`:

```yaml
classifier:
  microserviceName: catalog
  namespace: catalog-ns
  scope: service
  extraKeys:
    dbClassifier: default
```

The operator flattens `extraKeys`, producing runtime wire identity
`{"dbClassifier":"default", ...}`. Do not put a top-level runtime key under `customKeys`; that
would instead produce `{"customKeys":{"dbClassifier":"default"}, ...}` and identify a different
database.

Use `customKeys` only when the runtime classifier itself contains a nested `customKeys` object.
Never repeat reserved keys (`microserviceName`, `scope`, `namespace`, `tenantId`, `customKeys`) in
`extraKeys`.

## InternalDatabase template

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: orders-postgresql-service-db
  namespace: orders-ns
spec:
  classifier:
    microserviceName: orders
    namespace: orders-ns
    scope: service
  type: postgresql
  lazy: false
```

Optional mappings supported by the current CR contract are:

- `BaseDbParams.NamePrefix` to `spec.namePrefix`;
- string-valued database creation settings to `spec.settings`;
- explicitly configured versioning and initial-instantiation behavior to their corresponding
  structures.

Do not copy client connection-pool, migration, retry, or datasource settings into `spec.settings`.
Do not silently drop `PhysicalDatabaseId`; block that identity until a target-contract mapping is
confirmed.

## DatabaseSecretClaim template

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: DatabaseSecretClaim
metadata:
  name: orders-postgresql-service-default-claim
  namespace: orders-ns
  labels:
    app.kubernetes.io/name: orders
spec:
  classifier:
    microserviceName: orders
    namespace: orders-ns
    scope: service
  type: postgresql
  userRole: ""
  secretName: orders-postgresql-service-default-credentials
```

The label is mandatory in the current operator controller and is sent as `originService` in the
aggregator get-by-classifier request.

Set `userRole` to the exact role passed by the client. Empty and explicit `admin` are different
mounted lookup keys even if the aggregator eventually resolves both to administrator credentials.
Create separate claims and mounts when one database is requested with multiple roles.

## Generated Secret contract

The operator creates an opaque Secret with two data keys:

```text
metadata.json
connectionProperties.json
```

`metadata.json` carries the canonical classifier, type, requested `userRole`, and descriptive
database fields. `connectionProperties.json` carries the adapter response. Mount the Secret as a
directory at:

```text
/etc/secrets/dbaas-secrets/<DatabaseSecretClaim.spec.secretName>
```

The base client scans immediate subdirectories of `/etc/secrets/dbaas-secrets`. It does not infer a
classifier from the directory name.

## Runtime behavior

In a compatible base client, `NewDbaaSPool` includes the mounted-secret provider in its logical DB
provider chain. `GetOrCreateDb` and `GetConnection` first try providers and call the DBaaS REST API
only after every provider misses.

Therefore, prove all three points before claiming a successful migration:

1. the resolved client contains and registers the provider;
1. the mounted Secret metadata produces exactly the requested lookup key;
1. logs or an isolated fallback endpoint prove that the successful request did not reach REST.
