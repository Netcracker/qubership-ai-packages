# Change analysis guide

Map each changed file to the documentation roles it affects. The roles are defined in step 1 of `SKILL.md`, and the
documentation map built there tells you which page plays each role in this repository. This guide never names a page
path; when it says "the `parameters` page", use the page the map assigns to `parameters`.

## Contents

- [Classify changed files](#classify-changed-files)
- [Extract the details each role needs](#extract-the-details-each-role-needs)
- [Decide which pages to touch](#decide-which-pages-to-touch)
- [Examples](#examples)

## Classify changed files

Classify by path and content. Look up the exact chart directories, API packages, and service directories in the
repository itself (`git ls-files`, `ls`); the patterns below are shapes, not paths.

| Changed file | Category | Primary role | Secondary roles |
| --- | --- | --- | --- |
| `values.yaml` of any Helm chart | Helm parameters | `parameters` | `features` page of that feature |
| Helm template (`templates/*.yaml`, `templates/*.tpl`) | New parameter or changed behavior | `parameters` | `features`, `architecture` |
| Operator API types (`*_types.go`) or generated CRD YAML | CRD fields | `parameters` | `architecture`, `features` |
| Controller or reconciler code | Feature or behavior change | `features` | `parameters`, `troubleshooting` |
| Builders of Kubernetes objects (Deployments, Services, RBAC) | Deployment shape | `architecture` | `installation`, `security` |
| Dashboards, Prometheus or Telegraf configuration | Monitoring | `monitoring` | `parameters` |
| Alert rules | Alerts | `alerts` | `troubleshooting` |
| Container image sources (`Dockerfile`, `docker-*/`) | Component or version change | `architecture` | `installation` |
| Bootstrap or CRD init jobs | Prerequisites | `installation` | `troubleshooting` |
| TLS, authentication, or RBAC code and templates | Security | `security` | `parameters` |
| CI configuration, `Makefile`, contributor scripts | Developer workflow | `developer` | |
| Documentation pages | Consistency | The page itself | `index` |

A directory that matches no row: read its `README` or nearest `values.yaml` to learn what it does, then classify it by
purpose. A change that matches no row at all needs no documentation; say so, as `SKILL.md` step 3 requires.

## Extract the details each role needs

### Parameters

For each added key, record:

- the full dot-notation path, such as `backupDaemon.s3.enabled`;
- the type (`string`, `bool`, `int`, `[]string`, `json`, `yaml`, or a Kubernetes type);
- whether it is mandatory;
- the default from `values.yaml`, or `n/a`;
- what it configures, from the templates that read it and the comments beside it.

For a changed default, record the old and new value. For a removed or renamed key, remove or rename its row, search
every documentation page for the old name, and fix each reference. When a whole feature goes away, add a deprecation
note to its page or remove the page and the links to it. Do not leave a stale row behind.

### Features

A feature is new when the diff adds a controller, a CRD field that turns on new behavior, a new Deployment or Service,
or a new `*.enabled` or `*.install` flag. Record its purpose, prerequisites, parameters, how the user turns it on, and
its limitations.

### Monitoring and alerts

Record new or changed dashboard panels, exporter queries, Telegraf inputs and outputs, and alert rules with their
severity.

### Architecture

Record new images or services, new CRDs, new ports or calls between components, and new deployment modes.

## Decide which pages to touch

- New parameter: add a row to the `parameters` page, in the section for its component.
- Removed or renamed parameter: update the row, fix references on every page, and deprecate the feature page if the
  feature is going away.
- New feature: create a page in the `features` location, link it from the `parameters` page if it has parameters, and
  add it to the `architecture` page if it adds a component.
- Changed feature: update its `features` page, and the `parameters` and `troubleshooting` pages if parameters or
  failure modes changed.
- Changed monitoring or alerts: update the `monitoring` or `alerts` page.
- Changed components or interactions: update the `architecture` page.
- Changed install or upgrade steps: update the `installation` page.
- Changed failure modes or recovery: update the `troubleshooting` page.
- Changed TLS, authentication, or RBAC: update the `security` page.
- Changed contributor workflow: update the `developer` page.
- A page created, renamed, moved, or deleted: update the `index` page if the repository has one.

When the role a change needs maps to nothing, follow `SKILL.md` step 1: propose a page and confirm it before you create
it.

## Examples

### New key in `values.yaml`

The diff adds `backupDaemon.s3.aliases` to a chart's `values.yaml`. Open the `parameters` page, find the section for the
backup daemon, and add a row in the table's existing column order:

```markdown
| backupDaemon.s3.aliases | yaml | no | n/a | Specifies S3 bucket aliases the backup daemon uses for backup and restore. |
```

### New feature

The diff adds a template `encrypted-access.yaml`, an `encryptedAccess:` section in `values.yaml`, and a reconciler
`encrypted_access_reconciler.go`. Plan, and confirm with the user:

1. A new page in the `features` location, named like its neighbors (for example `encrypted-access.md`).
1. Parameter rows for `encryptedAccess.*` on the `parameters` page.
1. A line in the feature list of the `architecture` page.
1. A link from the `security` page, because the feature concerns TLS.

### Changed dashboard

The diff adds panels to a Grafana dashboard ConfigMap. Describe the new panels in the matching dashboard section of the
`monitoring` page. If the page shows screenshots and you cannot produce one, say so in the plan instead of linking an
image that does not exist.

### New alert rule

The diff adds a Prometheus alert. Add a row with the alert name, severity, and meaning to the `alerts` page, and link
the matching `troubleshooting` entry if one exists.
