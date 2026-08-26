---
name: dashboard-architect
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - WebFetch
description: >-
  Build, edit, and validate Grafana dashboards over metrics, logs, traces, and profiles, then publish them to
  Grafana or emit them as grafana-operator manifests. Use when the user asks to create, change, or fix a
  dashboard, or asks to see metrics, logs, graphs, errors, or problems for a service, cluster, namespace, or
  application. Triggers on: create dashboard, build dashboard, edit dashboard, add a panel, show me metrics,
  show me errors, show me problems, visualize, SLO dashboard, RED dashboard, USE dashboard, dashboard for
  Kubernetes, dashboard as code, GrafanaDashboard manifest.
---

# Dashboard architect

Generate Grafana dashboards that import cleanly, query real metrics, and answer the question the user asked.

The output format is classic dashboard JSON. Do not emit the v2 resource model: the linter cannot parse it and
grafana-operator v4 cannot consume it.

## Pipeline

Run these in order. Do not publish before step 6 reports clean.

### 1. Scope

Establish what the dashboard must answer and how wide it reaches. Use `AskUserQuestion` when the request does
not settle these:

- Which service, cluster, namespace, or application.
- Which signals: metrics, logs, traces, profiles, or a mix.
- Scope, which decides the variable set: cluster-wide, one namespace, or one workload.

Resolve connection details once, here, first match wins:

1. The `grafana` MCP server, if configured. It carries the address and the credential.
2. `$GRAFANA_URL` and `$GRAFANA_TOKEN` from the environment.
3. `.env` in the package directory.
4. Nothing resolved: ask for the Grafana address once, and offer to persist it to `.env`.

Never ask for a VictoriaMetrics, Tempo, or Pyroscope address. `GET /api/datasources` returns the type, uid, and
url for every datasource, and `POST /api/ds/query` proxies queries to any of them. Asking separately means step
1 did not run.

Never print a token, and never write credentials anywhere but the gitignored `.env`.

### 2. Discover

**Blocking.** A dashboard built from guessed metric names is worthless, and a query that parses cleanly still
returns nothing if the name is wrong. Before writing any query, confirm the metric, field, or profile type
exists, and confirm the labels used to filter it.

Resolution order for reaching a datasource:

1. The `grafana` or VictoriaMetrics MCP server.
2. The `victoriametrics-query`, `victorialogs-query`, and `victoriatraces-query` skills, when the
   `VictoriaMetrics/skills` plugin is installed.
3. `curl` against the datasource, or through `POST /api/ds/query`. Per-signal recipes are in
   `references/signals/`.
4. Nothing reachable: build the dashboard anyway, tag it `unverified-queries`, and say so in the report.

Read `references/signals/<signal>.md` for each signal in scope. Read only those; a metrics-only dashboard has
no reason to load the traces reference.

### 3. Delegate

If the user wants to find an existing dashboard rather than build one, hand off to the `dashboard-finder`
skill and stop. When finder has already run and the user chose to extend a candidate, continue from step 4
using that dashboard as the starting point.

### 4. Design

Choose panels from the data shape, following `references/panel-selection.md`. Defaulting
everything to `timeseries` and `stat` is the most common way a dashboard ends up correct and useless.

Structure the layout by urgency: headline numbers, then trends, then detail. Apply RED to services (rate,
errors, duration) and USE to resources (utilization, saturation, errors).

Confirm each chosen panel type exists on the target instance before using it. A missing panel plugin renders
as an error box and takes its row with it.

### 5. Build

Start from `references/dashboard-skeleton.json` and add panels copied from `references/panels/`. Every
snippet already passes validation, so a panel that fails afterward was broken by an edit.

Apply `references/conventions.md` in full: variables, units, descriptions, legends, links, drill-downs, uid
rules, collapse behavior. Those rules are what the validator checks.

### 6. Validate

```bash
scripts/validate.sh <dashboard.json>
```

Stage 1 is structural and always runs. Stage 2 parses PromQL and needs `dashboard-linter` on `PATH`; a
missing binary downgrades the run to a partial pass rather than failing it.

Fix and re-run, up to three passes. Report anything still failing rather than dropping the panel or quietly
weakening the dashboard. Do not edit `scripts/.lint` to silence a finding.

### 7. Publish

Only after step 6 reports clean.

- Default: import through the `grafana` MCP server.
- The user asked for a Helm chart or a manifest: emit a `GrafanaDashboard` resource per
  `references/grafana-operator.md` instead.

A dashboard tagged `ai-generated` may be overwritten without asking. Confirm before overwriting any dashboard
without that tag.

### 8. Report

- Dashboard title and a clickable link, built from the resolved Grafana address.
- Validation result, including whether the linter ran.
- Which panel types were chosen and why, in one line each.
- Every unverified target, named, with the datasource it could not be found in.

## Editing an existing dashboard

Fetch the current JSON, apply the change, then run the full validation stage on the result. An edit that
introduces an overlapping `gridPos` or a variable reference the dashboard does not declare is the common
failure, and both are caught only by re-validating the whole dashboard rather than the edited panel.

## Alerts

Never add alert rules to a dashboard.

## Reference files

- `references/conventions.md`: always, before building.
- `references/panel-selection.md`: when choosing panel types.
- `references/panels/*.json`: when copying a panel.
- `references/signals/*.md`: one per signal in scope.
- `references/dashboard-skeleton.json`: when starting a new dashboard.
- `references/grafana-operator.md`: when the user wants a manifest.
- `assets/*.json`: when a worked example of a full production dashboard is needed.

The `assets/` dashboards are real and useful for layout and row structure, but they predate this skill's
conventions and do not pass validation. Read them for shape, not as templates.
