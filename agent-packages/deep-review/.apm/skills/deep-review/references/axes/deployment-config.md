# Axis: deployment and configuration

Finding prefix: `DEPLOY`.

How this thing is installed, configured, upgraded, and rolled back. Services and operators only.

## Configuration as a contract

- Inventory every knob: environment variables, files, flags, chart values, and anything read at runtime. For each:
  where its default lives, what unit it is in, what happens when it is absent, and what happens when it is nonsense.
- Is configuration validated at startup with a clear message, or does a bad value surface as a confusing failure an
  hour later? Fail-fast on invalid configuration is the single highest-value fix on this axis.
- Are there two sources for one setting (a flag and an environment variable, a chart value and a config map) and is
  the precedence documented and tested?
- Defaults: is the default configuration safe and useful, or does it require a profile nobody mentions? Render the
  packaging with defaults and see whether it works at all.
- Secrets: how are they delivered, are they ever logged, and what happens when one rotates while the process runs?

## Packaging

- Render every packaging artifact (Helm template, Kustomize overlay, Compose file, systemd unit) with the default
  values and with each shipped profile. A template that does not render is a finding; a template that renders into
  something that cannot start is a worse one.
- Do the profiles differ in the ways their names promise? Identical dev and prod profiles are a finding.
- Resource requests and limits against what the component actually needs at the stated scale — cross-reference
  `performance`. State the assumption behind any number you challenge.
- Probes: do liveness and readiness measure something real, and are their timings compatible with real startup?
- Permissions: does the declared access cover every call the code makes? Check the code's calls against the grants,
  not the grants against themselves. A missing grant surfaces as a runtime failure on a rare path.
- Scheduling and availability: replica count against the concurrency model, disruption budgets, spread, priority,
  termination grace period against the shutdown path.
- Does the packaging place resources consistently — one namespace convention, one naming convention, one label set?

## Lifecycle

- **Install** on a clean cluster or host, from the documented command. Does it work?
- **Upgrade** from the previously released version, with objects already present. What happens to schemas, persisted
  state, and in-flight work? Is a rolling upgrade safe with mixed versions running?
- **Rollback** to the previous version after the upgrade changed something persistent. If rollback is not possible,
  that must be documented; if it is not, that is the finding.
- **Uninstall.** What is deleted, what is left behind, and can an uninstall or a disabled feature flag cascade into
  deleting user data? This is the class of defect that ends a career — check it explicitly.
- **Coexistence** with whatever this replaces, if anything: can both run at once, and what arbitrates?

## Rules

Render and run what you can; label anything you only read as `PLAUSIBLE`. Deployment findings are cheap to claim and
expensive to be wrong about.
