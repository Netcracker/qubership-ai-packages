# Deployment and configuration

## Deployment behavior

Use the repository's normal rendering or installation path with representative default, development, and production
values. Verify startup, health and readiness, configured external entry points, routes or ingress, TLS, secret
references, probes, resource requests and limits, and startup ordering. Inspect the rendered result rather than relying
only on source templates.

Check generated assets, initialization and migration jobs, hooks, and configuration generation for deterministic
output, correct ordering, restart safety, and actionable failures. Confirm that documentation and examples use valid
keys, types, defaults, and precedence. Treat credentials and generated secrets as sensitive evidence.

When compatibility applies, render or validate old deployment values against the changed descriptors. Identify removed
or renamed values, changed defaults, newly required inputs, and behavior that differs between upgrade and clean install.

## Multi-layer alignment

Deployed behavior is aligned only when every changed layer that affects the scenario matches the target:

- application artifact or image;
- effective configuration and values;
- deployment descriptor, chart, manifest, or process definition;
- schema, storage, or initialization migration;
- generated asset consumed at build, install, or runtime; and
- external dependency version or contract relevant to the changed behavior.

Record proof for each applicable layer. A matching application revision does not compensate for stale configuration,
descriptors, migrations, generated assets, or external contracts. Mark affected checks partial when any required layer
cannot be proven aligned.

Use equivalent local, container, virtual-machine, or orchestrated deployment evidence. Helm, Docker, and Kubernetes are
implementations only when the repository or selected environment uses them; they are not universal requirements.
