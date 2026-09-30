# Change Analysis Guide

This reference describes how to systematically analyze staged git changes and map them to documentation updates.

## Table of Contents

- [Step 1: Gather the diff](#step-1-gather-the-diff)
- [Step 2: Classify changed files](#step-2-classify-changed-files)
- [Step 3: Extract documentation-relevant details](#step-3-extract-documentation-relevant-details)
- [Step 4: Map to doc files](#step-4-map-to-doc-files)
- [File pattern to documentation mapping](#file-pattern-to-documentation-mapping)
- [Examples](#examples)

---

## Step 1: Gather the Diff

First, determine the current branch:

```bash
git rev-parse --abbrev-ref HEAD
```

**If on a non-`main` branch**, gather two scopes and union them:

```bash
# Branch scope — all changes since this branch diverged from main
git diff main...HEAD

# Staged scope — changes staged for the current commit
git diff --cached
```

Use the union of both scopes for classification. This ensures the skill catches undocumented changes made earlier in the branch, not just the current staged diff.

**If on `main`**, only analyze the staged scope:

```bash
git diff --cached
```

Also check for new untracked files that may be staged:

```bash
git status --short
```

## Step 2: Classify Changed Files

Group each changed file into categories based on its path using the generic rules below. For exact chart directories, API paths, and service names, inspect the filesystem directly (run `ls` on relevant directories and use `find`). For the exact doc files and component section names to use, read the ToC of `installation.md` and consult the [File pattern to documentation mapping](#file-pattern-to-documentation-mapping) table in this file.

Generic category rules:

- **Helm values files** (`values.yaml` under any chart directory) → Helm parameters category
- **Helm templates** (`templates/*.yaml` under any chart directory) → may introduce new params or change behavior
- **CRD type definitions** (`*_types.go` under any API directory) → CRD types category; new fields = new params, removed fields = stale rows
- **Controller logic** (`controllers/**/*.go`) → may introduce features or change behavior
- **Kubernetes object builders** (provider/builder code in controllers) → may affect architecture or install docs
- **Monitoring config** (Telegraf, Grafana, Prometheus files in any monitoring directory) → monitoring category
- **Service directories** (backup, exporter, replication, UI, etc.) → classify by purpose using the project's `docs/README.md` mapping
- **Container image directories** (`docker-*/`) → may affect architecture or installation
- **Bootstrap/init jobs** → update installation prerequisites
- **Integration test suites** → may affect installation parameters section
- **Documentation files** (`docs/**`) → review for consistency with code changes

**How to handle unknown service directories**: if a directory doesn't match any of the above categories, read its `README` or nearest `values.yaml` to determine what it does, then classify it using the mapping table below.

**If no changed files match any category**, tell the user explicitly: "I analyzed the diff — no documentation changes are required." Do not silently finish.

## Step 3: Extract Documentation-Relevant Details

For each category of changes, extract specific details:

### Helm Parameter Changes

Look for:

- New keys added to `values.yaml`
- Changed default values
- Removed or renamed parameters

For **removed or renamed parameters**:

- Remove the corresponding row(s) from the parameter table in `installation.md`
- If the removal affects a whole feature section, add a deprecation notice or remove the section
- Check for cross-references to the removed parameter in other docs and clean them up
- Do not leave stale rows — incorrect documentation is worse than no documentation

For each **new parameter**, determine:

- Full dot-notation path (e.g., `backupDaemon.s3.enabled`)
- Type (string, bool, int, []string, json, yaml)
- Whether it's mandatory
- Default value
- What it configures (read surrounding code/comments)

### Feature Changes

Look for:

- New controller files or significant new logic in existing controllers
- New CRD spec fields (in `*_types.go` or generated CRD YAML in `operator/charts/helm/*/crds/`)
- New services or Deployments added to Helm templates
- New feature flags (new `*.enabled` or `*.install` parameters)

For each new feature, determine:

- Feature name and purpose
- Prerequisites (new CRDs, permissions, external dependencies)
- Configuration parameters
- How users interact with it
- Limitations or caveats

### Metrics / Monitoring Changes

Look for:

- New or modified Grafana dashboard ConfigMaps in any monitoring chart directory (see `docs/README.md` for the exact path)
- Changed Telegraf input/output config
- New Prometheus alert rules
- New or changed exporter queries

### Architecture Changes

Look for:

- New Docker images or services (new `docker-*` dirs or Dockerfiles)
- New CRDs (new files under `operator/api/`)
- Changed component interactions (new API calls, new ports, new dependencies)
- New deployment modes (new values sections, new Helm templates)

## Step 4: Map to Doc Files

Based on classification, determine exactly which doc files to touch:

### Decision Tree

- Is there a new Helm parameter?
  - YES → Update `installation.md` parameter table in the correct component section
- Is a Helm parameter removed or renamed?
  - YES → Remove or update the row in `installation.md`; clean up cross-references; add deprecation notice if the whole feature is going away
- Is there a new feature?
  - YES → Create `docs/public/<feature-name>.md`
  - Add cross-reference in `installation.md` prerequisites or parameters
  - Add to `architecture.md` feature list if it's a major component
- Is an existing feature changed?
  - YES → Update the existing `docs/public/<feature>.md`
  - Update `installation.md` if parameters changed
  - Update `troubleshooting.md` if failure modes changed
- Are metrics, dashboards, or alerts changed?
  - YES → Update `docs/public/monitoring.md` or `docs/public/alerts.md`
- Is the architecture affected?
  - YES → Update `docs/public/architecture.md`
- Are install or upgrade steps affected?
  - YES → Update relevant sections in `docs/public/installation.md`
- Are troubleshooting procedures affected?
  - YES → Update `docs/public/troubleshooting.md` or `docs/public/scenarios/`
- Is security affected (TLS, auth, RBAC)?
  - YES → Update `docs/public/security.md` or `docs/public/security/<topic>.md`
- Are internal developer workflows affected?
  - YES → Update `docs/internal/developing.md` or `docs/internal/operator-guide.md`
- None of the above?
  - → Tell the user: "I analyzed the diff — no documentation changes are required."

## File Pattern to Documentation Mapping

Quick reference for common change type → doc mappings. File path patterns are intentionally generic globs — inspect the filesystem directly for the exact chart directories, API paths, and service dirs in this project. Check the ToC of `installation.md` for the exact component section names to use.

| Changed file type                            | Primary doc to update                          | Secondary docs                                 |
| -------------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| Any `*/charts/helm/*/values.yaml`            | `installation.md` (matching component section) | Feature doc if feature-specific                |
| Any `*/api/**/*_types.go`                    | `installation.md`                              | `architecture.md`, feature docs                |
| Controller for a backup/restore service      | Feature doc for that service                   | `installation.md` (backup section)             |
| Controller for monitoring/metrics            | `monitoring.md`                                | `installation.md` (monitoring section)         |
| Controller for replication/mirroring         | Replication feature doc                        | `installation.md` (replication section)        |
| Controller for a UI component                | `architecture.md`                              | `installation.md` (UI section)                 |
| Controller for auto-rebalancing/self-healing | Rebalancing feature doc                        | `installation.md` (rebalancing section)        |
| Monitoring config directory changes          | `monitoring.md` or `alerts.md`                 |                                                |
| Exporter service directory changes           | `monitoring.md` (exporter section)             | `installation.md` (exporter section)           |
| `docker-*/` image changes                    | `architecture.md`                              | `installation.md` if version or config changes |
| CRD init / bootstrap job changes             | `installation.md` (Prerequisites section)      | `troubleshooting.md`                           |

## Examples

### Example 1: New parameter Added to values.yaml

Diff shows `backupDaemon.s3.aliases` added to a chart's `values.yaml`.

Action:

1. Open `docs/public/installation.md`
2. Find the backup daemon component section under `# Parameters` (the exact heading depends on this project — read the ToC)
3. Add a row to the parameter table:

```markdown
| backupDaemon.s3.aliases | yaml | no | n/a | Specifies S3 bucket aliases for the backup daemon to use during backup/restore operations. |
```

### Example 2: New Feature — Encrypted External Access

Diff shows new Helm template `encrypted-access.yaml`, new values section `encryptedAccess:`, and new controller file `encrypted_access_reconciler.go`.

Actions:

1. Create `docs/public/encrypted-access.md` using the feature template
2. Add parameter rows in `installation.md` under a new `## Encrypted Access` section (or append to the primary service section if minimal)
3. Add a bullet point to the feature list in `architecture.md`
4. Cross-reference from `security.md` since it relates to TLS/encryption

### Example 3: Changed Grafana Dashboard ConfigMap

Diff shows new panels added to a Grafana dashboard ConfigMap inside a monitoring chart directory.

Actions:

1. Open `docs/public/monitoring.md`
2. Add descriptions for the new panels in the appropriate dashboard section
3. Note that screenshots may need updating (add a TODO comment in the doc)

### Example 4: New Alert Rule Added

Diff shows a new Prometheus alert in the monitoring chart.

Actions:

1. Open `docs/public/alerts.md`
2. Add a row to the alerts table with the alert name, severity, and description
3. If the alert relates to an existing troubleshooting scenario, cross-reference it from `troubleshooting.md`

### Example 5: New Engine Mode or Major Migration Path

Diff shows changes to a controller implementing a new operational mode (e.g., a migration from one storage/consensus backend to another).

Actions:

1. Update or create a feature doc in `docs/public/` describing the migration
2. Update `installation.md` if mode-specific parameters changed
3. Update `architecture.md` if the deployment scheme description changes
