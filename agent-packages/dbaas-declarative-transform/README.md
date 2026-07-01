# DBaaS declarative transform

Migrate Go services using Qubership DBaaS clients from runtime database provisioning to
`InternalDatabase` and `DatabaseSecretClaim` resources with mounted credentials.

The skill inventories complete classifier identities, database types, creation parameters, and
requested roles before generating resources. It supports deployment-known service and tenant
identities and leaves request-context-derived tenant identities on the runtime path.

Invoke the `dbaas-declarative-transform` skill from a service repository. Review the inventory and
generated diff before applying it to a cluster.
