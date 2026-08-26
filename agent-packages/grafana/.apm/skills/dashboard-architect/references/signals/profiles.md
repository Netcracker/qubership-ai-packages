# Signal: profiles

## Datasource

Pyroscope: plugin type `grafana-pyroscope-datasource`, queried by profile type plus a label selector.

Pyroscope has no MCP server and no VictoriaMetrics query skill. Discovery goes through the Grafana datasource
proxy. See `SKILL.md` for the resolution order.

## Target shape

```json
{
  "refId": "A",
  "queryType": "profile",
  "profileTypeId": "process_cpu:cpu:nanoseconds:cpu:nanoseconds",
  "labelSelector": "{service_name=\"$service\", namespace=\"$namespace\"}"
}
```

`queryType` selects what comes back: `profile` for a flame graph, `metrics` for a time series of the profiled
value, `both` for a panel showing each.

A `profileTypeId` has five colon-separated parts. Do not construct one by hand; read it from the backend.

## Discovery

```bash
# available profile types
curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/datasources/proxy/uid/$DS_UID/pyroscope/api/v1/ProfileTypes" | jq -r '.profileTypes[].ID'

# label names and values, for building variables
curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/datasources/proxy/uid/$DS_UID/pyroscope/api/v1/LabelNames" | jq -r '.names[]'
```

Common profile types: `process_cpu:cpu:nanoseconds:cpu:nanoseconds`,
`memory:alloc_space:bytes:space:bytes`, `memory:inuse_space:bytes:space:bytes`, `goroutines:goroutine:count:goroutine:count`.
Confirm against the instance; a language runtime only exposes the types it collects.

## Query rules

- Scope by `service_name`. A selector matching every service produces a flame graph nobody can read.
- Profiles are sampled continuously but sparsely. Keep the panel range wide enough to hold a usable sample.

## Panels

`flamegraph` for the profile itself, `timeseries` for the profiled value over time, `table` for a
top-functions list.

## Structure

A flame graph is a drill-down, not an overview. Put it on its own row, collapsed by default, below the
metrics that would prompt a reader to open it.
