# Documentation Conventions Reference

This reference describes the format conventions, templates, and style rules used in project documentation. Read this before creating or updating any doc file.

## Table of Contents

- [General style rules](#general-style-rules)
- [Table of Contents in documents](#table-of-contents-in-documents)
- [Parameter tables](#parameter-tables)
- [Feature documentation template](#feature-documentation-template)
- [Monitoring documentation template](#monitoring-documentation-template)
- [Troubleshooting documentation template](#troubleshooting-documentation-template)
- [Cross-references and links](#cross-references-and-links)
- [Image references](#image-references)
- [installation.md structure](#installationmd-structure)
- [architecture.md structure](#architecturemd-structure)

---

## General Style Rules

1. Use Title Case for all headings.
2. Use standard Markdown. No HTML unless required for complex tables.
3. Start each document with a Table of Contents as a bulleted list of anchor links (see below).
4. Use `#` for top-level headings, `##` for sections, `###` for subsections.
5. Use fenced code blocks with language tags: ` ```yaml `, ` ```bash `, ` ```shell `.
6. Notes use bold prefix: `**Note**: Your note text here.` or `**Note!** Your note text here.`
7. Parameter names in prose use backtick formatting: `global.tls.enabled`.
8. Keep line lengths reasonable — no hard wrap, but break at logical points.
9. Do not add trailing whitespace or extra blank lines at end of file.

## Table of Contents in Documents

Docs use an HTML comment-wrapped ToC block:

```markdown
<!-- TOC -->

- [Section One](#section-one)
  - [Subsection A](#subsection-a)
  - [Subsection B](#subsection-b)
- [Section Two](#section-two)

<!-- TOC -->
```

When adding new sections, add corresponding ToC entries. Anchors are lowercase, spaces replaced with hyphens, special characters removed.

## Parameter Tables

Parameter tables use standard markdown table syntax. Every table has exactly these five columns:

```markdown
| Parameter | Type | Mandatory | Default value | Description |
| --------- | ---- | --------- | ------------- | ----------- |
```

### Column Specifications

- **Parameter**: Full dot-notation path (e.g., `global.tls.enabled`, `kafka.resources.limits.cpu`)
- **Type**: One of `string`, `bool`, `int`, `json`, `yaml`, `[]string`, or a Kubernetes type link like `[Kubernetes Sec Context](https://pkg.go.dev/k8s.io/api/core/v1#SecurityContext)`
- **Mandatory**: `yes` or `no`
- **Default value**: The actual default, or `n/a` if none
- **Description**: Starts with a verb — "Specifies ...", "Indicates whether ...", "Defines ..."

### Section Organization

Parameters in `installation.md` are grouped under `##` headings by component. Each component section has a single table:

```markdown
## ComponentName

| Parameter            | Type   | Mandatory | Default value | Description   |
| -------------------- | ------ | --------- | ------------- | ------------- |
| componentName.param1 | string | no        | default       | Specifies ... |
```

### Chart Structure in installation.md

`installation.md` contains **one unified parameter reference** for all Helm charts in the project. Parameters are grouped by component under `##` headings.

**Before adding parameters, read `installation.md`'s Table of Contents** to discover the actual component sections for this project. Do not assume section names — they vary between projects.

Common section types (names differ per project):

- Cloud / global integration parameters
- Operator deployment parameters
- Primary data service parameters
- Monitoring / metrics exporter parameters
- UI component parameters
- Replication / data movement parameters
- Backup and restore parameters
- Integration test parameters
- CRD init / bootstrap job parameters

When adding parameters, find the correct component section and append rows to the existing table. If a genuinely new component needs its own section, create a `##` heading in logical order matching the naming style already used in the file.

## Feature Documentation Template

Feature docs live in `docs/public/`. Use a kebab-case filename matching the feature name.

### Minimal Template

```markdown
# Feature Name

<!-- TOC -->

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
  - [Installation Parameters Description](#installation-parameters-description)
- [Usage](#usage)
- [Limitations](#limitations)

<!-- TOC -->

# Overview

Brief description of what the feature does and why it's useful.

# Prerequisites

What must be in place before using this feature.

# Configuration

How to enable and configure the feature. Include relevant `values.yaml` snippets:

` ``yaml
featureName:
  enabled: true
  param1: value1 ` ``

## Installation Parameters Description

| Parameter           | Type | Mandatory | Default value | Description                              |
| ------------------- | ---- | --------- | ------------- | ---------------------------------------- |
| featureName.enabled | bool | no        | false         | Indicates whether to enable the feature. |

# Usage

Practical usage instructions and examples.

# Limitations

Known limitations, caveats, or incompatibilities.
```

### Conventions Observed in Existing Feature Docs

- The overview section references the architecture or installation docs where appropriate
- Configuration examples use real YAML from `values.yaml`
- Cross-references to related features or troubleshooting use repo-root-relative links
- Most feature docs include a ToC at the top if they have more than two sections
- Simple features can be very brief — just Overview and Configuration

## Monitoring Documentation Template

Monitoring docs live in `docs/public/monitoring.md` (primary) and component-specific sections within it. Standalone monitoring docs for components (e.g., `docs/public/alerts.md`) follow this structure:

```markdown
# Monitoring Topic

## Overview

Brief description of what is monitored.

## Configuration

How to enable the metrics, dashboards, or alerts.

## Dashboards

Description of dashboard panels.

### Panel Section Name

![Panel Screenshot](/docs/public/images/panel-name.png)

- `metric_name` - Description of what this metric shows.

## Alerts

| Alert name | Severity | Description            |
| ---------- | -------- | ---------------------- |
| AlertName  | critical | What this alert means. |
```

### Conventions

- Metrics are listed as bullet points with backtick-formatted metric names
- Screenshots are stored in `docs/public/images/`
- If screenshots aren't available for new metrics, note them with a TODO or describe in text

## Troubleshooting Documentation Template

Troubleshooting docs in `docs/public/troubleshooting.md` follow this per-issue structure:

```markdown
## Issue Title

### Description

What the issue is and when it occurs.

### Alerts

Which Prometheus alerts fire for this issue.

### Stack Trace

Typical log output or stack trace associated with this issue.

### How to Solve

Step-by-step resolution instructions.

### Recommendations

How to prevent recurrence or tune for resilience.
```

Scenario-specific troubleshooting lives in `docs/public/scenarios/`.

## Cross-References and Links

Use repo-root-relative paths for internal links:

```markdown
[Feature Name](/docs/public/feature-name.md)
[Installation Guide](/docs/public/installation.md)
[Backup Daemon](/docs/public/backup-daemon.md#configuration)
```

For external links, use full URLs:

```markdown
[Apache Kafka](https://kafka.apache.org/)
[Kubernetes Documentation](https://kubernetes.io/docs/concepts/...)
```

When adding a new feature doc, ensure it's referenced from:

1. `installation.md` — in the prerequisites or parameters section if it has configurable params
2. `architecture.md` — if it adds a new component or deployment variant
3. Related feature docs — if it interacts with other features

## Image References

Images are stored in `docs/public/images/` with subdirectories by topic:

```
docs/public/images/
├── kafka-monitoring_*.png    # Kafka monitoring dashboard screenshots
├── kafka-topics_*.png        # Kafka topics dashboard screenshots
├── kmm-monitoring_*.jpg      # Mirror Maker monitoring screenshots
└── ...
```

Reference format:

```markdown
![Alt Text](/docs/public/images/image-name.png)
```

## installation.md Structure

**Always read the actual file's ToC first.** The exact section names, component headings, and ordering vary by project.

Typical top-level structure (names will differ):

1. **ToC** — `<!-- TOC -->` wrapped bullet list of anchor links
2. Introductory / general information section
3. **Prerequisites** — CRDs, permissions, pre-deployment resources, storage, cloud prerequisites
4. Best practices and sizing recommendations
5. **Parameters** — one unified section; one `##` heading per component
6. **Installation** — step-by-step instructions with examples
7. **Upgrade** — upgrade procedures and migration steps
8. **Rollback**
9. Additional features / advanced configuration
10. Frequently asked questions

When adding new parameters, find the appropriate component section (use `docs/README.md` to map file patterns to section names) and append rows to the existing table. If a genuinely new component needs its own section, create a `##` heading in logical order matching the naming style already in the file.

## architecture.md Structure

**Always read the actual file's ToC first.** Component names vary by project.

Typical structure (names will differ):

1. **ToC** — `<!-- TOC -->` wrapped bullet list
2. **Overview** — description of the service and platform value
3. **Delivery and Features** — bullet list of capabilities with cross-references to feature docs
4. **Components** — one `##` section per major component
5. **Supported Deployment Schemes** — HA, Non-HA, DR, managed cloud integrations

When adding a new component, add a `##` section under the Components heading and add it to the Delivery and Features bullet list. Cross-reference the feature doc if one exists.
