# Dashboard conventions

Rules every generated dashboard follows. `scripts/validate.sh` enforces most of them; the rest are judgment
calls the agent applies while building.

## Template variables

Every dashboard declares these, in this order:

| Name | Type | Notes |
|---|---|---|
| `datasource` | `datasource` | Required. Set `label: "Data source"` or the linter warns. |
| `cluster` | `query` | Required. |
| `namespace` | `query` | Skip for cluster-wide dashboards. |
| `pod` | `query` | Skip for cluster-wide and namespace-wide dashboards. |
| `filter` | `adhoc` | Required. Lets the user add matchers without editing the dashboard. |

Add `container` or `endpoint` when the metrics carry those labels and the user needs to break down by them.

Ask which scope applies when the request does not make it obvious. A pod variable on a cluster-wide dashboard
forces the reader to pick a pod before seeing anything.

Rules for every variable:

- Point it at `${datasource}`. A hard-coded datasource uid breaks the dashboard on every other instance.
- Set `refresh: 2` so the variable reloads when the time range changes. `refresh: 1` reloads only on dashboard
  load, so the option list goes stale as soon as the reader pans backward.
- Set `allValue: ".*"` on query variables that offer an All option.
- Prefer `_info` metrics as the discovery source: `node_os_info`, `jvm_info`, `go_info`, `kube_pod_info`. They
  carry the label set without the churn of a counter.

```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "label": "Data source",
        "type": "datasource",
        "query": "prometheus"
      },
      {
        "name": "namespace",
        "type": "query",
        "datasource": {"type": "prometheus", "uid": "${datasource}"},
        "query": "label_values(kube_pod_info{cluster=\"$cluster\"}, namespace)",
        "refresh": 2,
        "allValue": ".*",
        "multi": false
      },
      {
        "name": "filter",
        "type": "adhoc",
        "datasource": {"type": "prometheus", "uid": "${datasource}"},
        "baseFilters": [],
        "filters": []
      }
    ]
  }
}
```

## Queries

- Reference variables in matchers: `sum(rate(http_requests_total{cluster="$cluster", namespace="$namespace"}[$__rate_interval]))`.
- Use `$__rate_interval` with `rate`, `irate`, and `increase`. A hard-coded `[5m]` breaks at wide time ranges,
  and the linter rejects it.
- Aggregate any metric ending in `_total`. Graphing a raw counter shows process uptime, not activity.
- Narrow the metric set with the `job` label during discovery. `{job="tempo"}` reveals what a service exposes.

## Panels

- Every panel gets a title, a description, and a unit. All three are blocking errors.
- Point every panel at `${datasource}`.
- Set decimals to 1, or 2 at most, unless the user asks for more precision.
- Legends show `Last *` at minimum, sorted descending, so the busiest series reads first.

## Layout

The grid is 24 columns wide. Keep `x + w <= 24` and do not overlap panels: Grafana reflows collisions silently
and the layout arrives scrambled.

Order rows by how urgently a reader needs them:

1. Critical numbers, as `stat` panels.
2. Key trends, as `timeseries`.
3. Detail, as tables, heatmaps, and per-component breakdowns.

Collapse a row when it holds heavy queries or drill-down detail. Beyond five rows, leave only the top two or
three expanded. A row that answers "is anything broken right now" stays open regardless of cost.

## Links

Link by tag rather than by uid, so a new dashboard with the same tag joins the menu automatically.

```json
{
  "links": [
    {
      "asDropdown": true,
      "tags": ["k8s"],
      "includeVars": true,
      "keepTime": true,
      "targetBlank": true,
      "type": "dashboards"
    }
  ]
}
```

Common tags: `k8s`, `java`, `go`, `cloud`, `application`.

Add drill-down links on table columns that name a resource:

| Column | Target dashboard |
|---|---|
| `node` | `Kubernetes / Node Resources` |
| `namespace` | `Kubernetes / Namespace Resources` |
| `pod` | `Kubernetes / Pod Resources` |

```text
/d/<uid>?var-datasource=$datasource&var-cluster=$cluster&var-namespace=$__cell_1
```

For container runtime metrics, link to the existing `JVM Processes` or `Go Processes` dashboard rather than
rebuilding those panels. The runtime dashboards already cover heap, GC, and thread detail.

## Dashboard metadata

- `uid`: derive from the title, lowercase, words joined by `-`. **40 characters maximum** — Grafana rejects
  anything longer on import. Abbreviate rather than truncate mid-word.
- `id`: value does not matter.
- `tags`: always include `ai-generated`. Add `unverified-queries` when any target could not be checked against
  a live datasource.
- Default time range: last 1 hour. Leave auto-refresh off.
- Leave `editable` unset or `true`.

A dashboard tagged `ai-generated` can be updated without asking. Confirm with the user before overwriting any
dashboard without that tag.

## Alerts

Never add alert rules to a dashboard. Alerting lives in its own pipeline.
