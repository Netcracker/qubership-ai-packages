# Runtime and environment

## Capability model

- Capability: evidence the review needs, such as browser interaction, build, API invocation, or runtime logs.
- Implementation: a repository command, harness tool, MCP adapter, installed executable, or service that provides it.
- Runtime: an application, cluster, virtual machine, namespace, container, or remote environment.
- Owner binding: proof that the assigned root or leaf agent can invoke the selected implementation.

Derive capabilities from required coverage. A familiar tool is one possible implementation, not the requirement.

## Passive discovery

Passive discovery may inspect only:

1. repository instructions, dependencies, scripts, test configuration, and documented workflows;
2. harness and MCP tool metadata;
3. executable presence and version metadata that does not execute a review check; and
4. configured runtime, kube-context, and local cluster names without contacting workloads.

Do not run tests, builds, browsers, scanners, deployment commands, API requests, cluster resource queries, logs, or
metrics during passive discovery. Do not install or enable anything.

For every required capability, record reasonable candidate implementations in this order:

1. repository-native implementation;
2. harness-native tool or adapter;
3. implementation exposed by an approved existing runtime; and
4. another visible local implementation.

Inventory reasonable alternatives, not every program on the machine. Record whether the intended owner can invoke each
candidate. Tool absence is not capability absence; root access is not leaf access.

## Access-permission gate

After passive discovery, present candidate implementations and environments in one bounded question. Ask before
executing any candidate or contacting any environment, including local development environments and read-only access.

This first question is an access gate, not an action budget. Do not include deployment, cleanup, rollback, recovery,
Compose-stack creation, namespace creation, or cluster creation before the approved runtime inventory has completed.

For each requested permission, state:

- capability and implementation;
- exact target and access mode;
- allowed action names;
- expected local writes, service effects, and indirect work;
- approved fallback implementations;
- evidence unlocked; and
- coverage impact if denied.

Record `approved`, `denied`, or `unresolved`. Silence remains unresolved. An unresolved permission blocks execution; it
cannot be converted into a limitation merely to finish the review.

## Capability gap

When a required capability has no viable available implementation, propose an optional installation plan instead of
silently dropping the evidence or choosing a familiar product by default. Prefer a repository-declared implementation,
then an implementation documented by the active harness, and then a locally appropriate alternative.

The proposal names:

- the capability and evidence it unlocks;
- the implementation, authoritative source and version selection rule;
- the exact install or enable command and target location;
- required network access and filesystem writes;
- trust, credential, service, and other side effects;
- cleanup or uninstall actions;
- owner binding after installation; and
- the alternatives: choose another available implementation or keep the affected coverage limited.

Do not invent an installation command. Derive it from repository documentation, harness metadata, or authoritative
tool documentation. If no verified installation path is available, report that constraint and keep the permission
unresolved or the evidence unavailable as appropriate.

Installation requires explicit user approval for the exact plan. Approval to install does not authorize executing the
installed implementation as a review check or contacting a runtime. After installation, rediscover availability and
owner binding, then request execution and access permission through the normal gate.

## Approved runtime inspection

After read-only runtime access is approved, inspect existing runtimes before proposing a new namespace, release, or
environment. Record releases, namespaces, workloads, storage, routes, URLs, image identities, configuration, Helm
history, and relevant state only within the approved target and action list.

Present existing local developer releases and their alignment before proposing a new namespace, Compose project, or
cluster. Recommend the existing runtime first when it provides the best upgrade or persisted-data evidence. If a clean
runtime is preferable, state the evidence gap that it covers and the existing runtime does not.

Prove alignment with the complete `head_oid` using the strongest available evidence: build metadata, image digest,
chart or application version, container labels, rendered values, process command line, version endpoint, or deployment
timestamps. Cover every changed layer that affects the scenario:

- application artifact or image;
- effective configuration and values;
- deployment descriptor, chart, manifest, or process definition;
- schema, storage, initialization, or data migration;
- generated asset; and
- relevant external dependency version or contract.

Do not use an unaligned or unproven runtime as regression evidence.

## Runtime strategy

Select the strategy that proves the required behavior:

- Use an existing aligned runtime without mutation.
- Use an in-place update for upgrade, migration, recovery, rolling compatibility, or persisted-state evidence.
- Use a clean deployment for installability, defaults, isolation, or destructive checks.
- Use both when the diff requires both upgrade and clean-install evidence.
- Limit coverage when the user denies the required access or mutation.

Never propose a new namespace or release before discovering and presenting relevant existing local development
runtimes. Locality does not grant read-only or mutation permission.

## Action-budget gate

Before mutation, prepare one exact action budget. It names:

- environment, namespace, release, workloads, storage, and other affected resources;
- commands or action types;
- images, configuration, migrations, and generated assets to align;
- direct and indirect effects, including recovery and background jobs;
- rollback and cleanup commands or actions;
- evidence each action produces; and
- actions explicitly outside the budget.

An approval applies only to this budget. A failed check does not expand it. Return to the gate before:

- an unplanned rollback or additional upgrade;
- changing resource requests, limits, configuration, or replicas;
- deleting Helm history, Secrets, releases, namespaces, workloads, or storage;
- replacing or modifying PVCs or persistent data;
- running recovery, repair, cleanup, retention, compaction, stress, or malformed traffic; or
- using another implementation, target, or access mode.

Record every actual action, effect, failure, rollback, and cleanup in `review-state.json` immediately.

## Safe degradation

When permission is denied or an approved implementation fails, use only remaining approved evidence. Static analysis,
fixtures, rendered manifests, or existing retained logs may support limited conclusions, but never describe them as
observed runtime behavior.

Set the affected checks to `denied` or `unavailable` with impact. Do not delete their evidence slots. If a fallback is
visible but not approved, return to the access-permission gate before invoking it.
