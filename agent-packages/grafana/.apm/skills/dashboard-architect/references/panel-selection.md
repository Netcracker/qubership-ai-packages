# Panel selection

Pick the panel from the shape of the data, not from habit. Defaulting everything to `timeseries` and `stat` is
the most common way a generated dashboard ends up technically correct and useless.

## Decision table

| Data shape | Panel | Use when |
|---|---|---|
| Numeric value over time | `timeseries` | The default for any rate, gauge, or percentage tracked over a range. |
| One current number | `stat` | A headline figure. Add a sparkline for trend context. |
| Current value against a known maximum | `gauge` | Utilization where the ceiling is meaningful, such as disk or quota. |
| Same, for many series at once | `bargauge` | Per-node or per-pod utilization in a compact block. |
| Discrete state over time | `state-timeline` | Up/down, ready/not-ready, phase transitions. |
| Sparse events over time | `status-history` | Periodic checks or deploys, where gaps carry meaning. |
| Distribution across histogram buckets | `heatmap` | Latency spread over time from `_bucket` series. |
| Distribution with no time axis | `histogram` | Shape of a value across instances at one moment. |
| Categorical comparison | `barchart` | Counts by category where order matters more than trend. |
| Parts of a whole | `piechart` | Only for a handful of categories that genuinely sum to a total. |
| Instant snapshot, several columns | `table` | Per-resource detail, and the only panel that carries drill-down links. |
| Two metrics correlated | `xychart` | Scatter of one metric against another. |
| Value on a map | `geomap` | Data carrying a region, country, or coordinate label. |
| Custom layout or diagram | `canvas` | Topology and status boards where position means something. |
| Log lines | `logs` | Raw log output. Pair with a `timeseries` of the log rate above it. |
| Spans and traces | `traces` | Trace detail from Tempo, Jaeger, or VictoriaTraces. |
| Service-to-service topology | `nodeGraph` | Dependency and call graphs. |
| Profiles | `flamegraph` | CPU and memory profiles from Pyroscope. |
| Static explanation | `text` | Runbook links and dashboard notes. |
| Grouping | `row` | Section headers. Set `h: 1`. |

Panels that render dashboard state rather than query results — `dashlist`, `alertlist`, `annolist`, `news` —
are rarely worth a slot on a generated dashboard. Do not add them unless asked.

## Availability

The table covers panels built into Grafana 11, 12, and 13. Confirm anything beyond it against the target
instance rather than assuming, and check that a panel is present before using it:

```bash
curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/plugins?type=panel" | jq -r '.[] | select(.enabled) | .id'
```

The `grafana` MCP server exposes the same list. A panel absent from that output renders as "Panel plugin not
found" and takes the whole row with it.

## Snippets

`panels/` holds one minimal valid example per type. Copy the file, then change the title, description, unit,
targets, and `gridPos`. Each snippet already satisfies the validator, so a panel that fails validation after
copying was broken by an edit, not by the template.

Set the unit to match the metric. Common values: `percent` (0-100), `percentunit` (0.0-1.0), `s`, `ms`,
`bytes`, `decbytes`, `binBps`, `reqps`, `ops`, `short`, `none`.
