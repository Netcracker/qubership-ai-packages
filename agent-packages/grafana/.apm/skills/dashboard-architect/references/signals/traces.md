# Signal: traces

## Datasource

| Backend | Plugin type | Query language |
|---|---|---|
| Tempo | `tempo` | TraceQL |
| Jaeger | `jaeger` | Jaeger search parameters |
| VictoriaTraces | `victoriametrics-traces-datasource` | Jaeger-compatible search |

## Target shape

Tempo, TraceQL search:

```json
{
  "refId": "A",
  "queryType": "traceql",
  "query": "{resource.service.name=\"$service\"} | duration > 100ms"
}
```

Tempo also serves a service graph through `"queryType": "serviceMap"`, which feeds a `nodeGraph` panel.

Jaeger and VictoriaTraces take structured search fields rather than a query string:

```json
{
  "refId": "A",
  "queryType": "search",
  "service": "$service",
  "operation": "$operation",
  "limit": 20
}
```

## Discovery

```bash
curl -s "$VM_TRACES_URL/api/services" | jq -r '.data[]'
curl -s "$VM_TRACES_URL/api/services/$SERVICE/operations" | jq -r '.data[]'
```

`$VM_TRACES_URL` already includes the `/select/jaeger` prefix. The `victoriatraces-query` skill covers these,
and works against a real Jaeger too, since the API is the same.

## Query rules

- Populate the `service` variable from the live service list, never from a guess.
- Filter by duration or status on any trace-search panel. An unfiltered search returns the newest traces,
  which are rarely the interesting ones.
- Tempo attribute names are prefixed by scope: `resource.service.name`, `span.http.status_code`.

## Panels

`traces` for the span waterfall, `nodeGraph` for the service graph, `table` for a searchable trace list.

## Structure

Traces answer "why is this request slow", not "how many are slow". Pair a trace panel with the RED metrics
for the same service, and link from the latency panel into the trace search so the reader arrives with the
time range already narrowed.
