# Documentation conventions

The target page's own format always wins. Read the page, and its neighbors when you create a new one, then match their
heading case, heading levels, table columns, link style, note style, and table-of-contents markup. The formats below
are defaults for a page that has no format to copy yet, and for a repository with no existing page of that kind.

Page paths in this reference are roles from `SKILL.md` step 1, such as "the `parameters` page". Resolve each one
through the documentation map.

## Contents

- [General rules](#general-rules)
- [Table of contents](#table-of-contents)
- [Parameter tables](#parameter-tables)
- [Feature page](#feature-page)
- [Monitoring page](#monitoring-page)
- [Troubleshooting entry](#troubleshooting-entry)
- [Links and images](#links-and-images)

## General rules

- One H1 per page, as its title. Sections are `##` and deeper.
- Standard Markdown; HTML only where a table needs it.
- Fenced code blocks carry a language tag: `yaml`, `bash`, `shell`, or `text`.
- Parameter names in prose are in backticks: `global.tls.enabled`.
- Wrap and break lines the way the page already does. If the repository pins a markdownlint line length, stay
  within it.
- No trailing whitespace, and one newline at the end of the file.

## Table of contents

When the page has a table of contents, add an entry for every section you add, in the page's existing markup. Many
pages wrap it in `<!-- TOC -->` markers:

```markdown
<!-- TOC -->
- [Section one](#section-one)
  - [Subsection A](#subsection-a)
- [Section two](#section-two)
<!-- TOC -->
```

Anchors are the heading in lowercase, with spaces replaced by hyphens and punctuation removed.

## Parameter tables

Keep the columns of the table you are adding to. When you start a new table and the repository has none to copy, use
these five columns:

```markdown
| Parameter | Type | Mandatory | Default value | Description |
| --------- | ---- | --------- | ------------- | ----------- |
| componentName.param1 | string | no | default | Specifies ... |
```

- **Parameter**: the full dot-notation path, such as `kafka.resources.limits.cpu`.
- **Type**: `string`, `bool`, `int`, `[]string`, `json`, `yaml`, or a link to a Kubernetes type, such as
  `[Kubernetes SecurityContext](https://pkg.go.dev/k8s.io/api/core/v1#SecurityContext)`.
- **Mandatory**: `yes` or `no`.
- **Default value**: the default from `values.yaml`, or `n/a`.
- **Description**: starts with a verb: "Specifies ...", "Indicates whether ...", "Defines ...".

Parameters are usually grouped by component, one heading and one table per component. Read the page's headings to find
the component's section and append the row to its table. When a component has no section yet, add one in the order and
naming style the page already uses.

## Feature page

Create the page in the `features` location with a file name in the style of its neighbors. When there is no neighbor
to copy, start from this outline and drop the sections the feature does not need; a simple feature can have only an
overview and its configuration:

````markdown
# Feature name

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Limitations](#limitations)

## Overview

What the feature does and when to use it. Link the `architecture` or `installation` page where it helps.

## Prerequisites

What must be in place before the feature is turned on.

## Configuration

How to turn the feature on, with a snippet taken from `values.yaml`:

```yaml
featureName:
  enabled: true
```

| Parameter | Type | Mandatory | Default value | Description |
| --------- | ---- | --------- | ------------- | ----------- |
| featureName.enabled | bool | no | false | Indicates whether the feature is enabled. |

## Usage

How to use the feature once it is on.

## Limitations

Known limitations and incompatibilities.
````

Link the new page from the `parameters` page when it has parameters, from the `architecture` page when it adds a
component, and from the pages of features it interacts with.

## Monitoring page

When there is no monitoring page to copy, use this outline:

```markdown
# Monitoring topic

## Overview

What is monitored.

## Configuration

How to turn on the metrics, dashboards, or alerts.

## Dashboards

### Panel group name

- `metric_name`: what the metric shows.

## Alerts

| Alert name | Severity | Description |
| ---------- | -------- | ----------- |
| AlertName | critical | What the alert means and what to check first. |
```

List metrics as bullets with the metric name in backticks. Add a screenshot only when you have the image; otherwise
describe the panel in text and mention the missing screenshot in the plan.

## Troubleshooting entry

When the `troubleshooting` page has no entry to copy, use one section per issue:

```markdown
## Issue title

### Description

What happens and when.

### Alerts

Which alerts fire.

### Stack trace

Typical log output.

### How to solve

Numbered resolution steps.

### Recommendations

How to prevent the issue from recurring.
```

## Links and images

Use the link style the page already uses: relative to the page (`../installation.md#parameters`) or relative to the
repository root (`/docs/installation.md#parameters`). Root-relative links resolve on GitHub and GitLab but not in every
static-site generator, so do not introduce them on a page that uses relative links.

Store a new image in the `images` location, named like the images beside it, and reference it in the same link style:

```markdown
![Dashboard overview](images/dashboard-overview.png)
```

External links use the full URL with descriptive link text:

```markdown
[Kubernetes documentation](https://kubernetes.io/docs/)
```
