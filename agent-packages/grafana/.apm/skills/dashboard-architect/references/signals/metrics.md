# Signal: metrics

## Datasource

- Prometheus: plugin type `prometheus`, query language PromQL.
- VictoriaMetrics through the Prometheus API: plugin type `prometheus`, query language PromQL.
- VictoriaMetrics through its native plugin: plugin type `victoriametrics-metrics-datasource`, query
  language MetricsQL.

Read the real type from `GET /api/datasources` rather than assuming. The native VictoriaMetrics plugin has
shipped under more than one id, and `dashboard-linter` only parses targets whose datasource type is
`prometheus`.

## Target shape

```json
{
  "refId": "A",
  "expr": "sum(rate(http_requests_total{cluster=\"$cluster\"}[$__rate_interval])) by (service)",
  "legendFormat": "{{service}}",
  "instant": false
}
```

Set `"format": "table", "instant": true` for `table`, `barchart`, `xychart`, `geomap`, and `trend`.

## Discovery

Confirm the metric exists, then confirm its labels, before writing a query.

```bash
# metric names exposed by one service
curl -s "$VM_METRICS_URL/api/v1/label/__name__/values?match[]=\{job=\"$JOB\"\}" | jq -r '.data[]'

# labels on a metric, then values for one label
curl -s "$VM_METRICS_URL/api/v1/labels?match[]=$METRIC" | jq -r '.data[]'
curl -s "$VM_METRICS_URL/api/v1/label/namespace/values?match[]=$METRIC" | jq -r '.data[]'
```

Prefer the `victoriametrics-query` skill or an MCP server when either is available. See `SKILL.md` for the
full resolution order.

## Query rules

- Aggregate every counter. A metric ending in `_total` graphed raw shows accumulation since process start.
- Use `$__rate_interval` for `rate`, `irate`, and `increase`.
- Compute quantiles with `histogram_quantile` over `sum by (le, ...) (rate(..._bucket[...]))`. Summing
  pre-computed quantiles across instances is arithmetically wrong.
- Reach for `topk` on per-pod breakdowns. A namespace with 300 pods renders an unreadable legend.

## Panels

`timeseries`, `stat`, `gauge`, `bargauge`, `table`, `barchart`, `piechart`, `histogram`, `heatmap`,
`state-timeline`, `status-history`, `trend`, `xychart`, `canvas`, `geomap`.

## Structure

Apply RED to services: rate, errors, duration. Apply USE to resources: utilization, saturation, errors.
