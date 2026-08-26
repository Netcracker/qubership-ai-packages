# Signal: logs

## Datasource

- VictoriaLogs: plugin type `victoriametrics-logs-datasource`, query language LogsQL.
- Loki: plugin type `loki`, query language LogQL.

LogsQL and LogQL are different languages that look similar. Confirm which backend the datasource points at
before writing a query; a LogQL pipeline pasted into VictoriaLogs fails at query time, not at build time.

## Target shape

```json
{
  "refId": "A",
  "queryType": "instant",
  "expr": "{cluster=\"$cluster\", namespace=\"$namespace\"} error | stats by (level) count() as total"
}
```

Use `"queryType": "range"` for a rate over time and `"instant"` for a snapshot or a log list.

## Discovery

LogsQL indexes fields rather than metric names, so discovery enumerates fields and streams.

```bash
curl -s "$VM_LOGS_URL/select/logsql/field_names?start=$START" | jq -r '.values[].value'
curl -s "$VM_LOGS_URL/select/logsql/field_values?field=level&start=$START" | jq -r '.values[].value'
curl -s "$VM_LOGS_URL/select/logsql/stream_field_names?start=$START" | jq -r '.values[].value'
```

The `victorialogs-query` skill wraps these endpoints, including the auth handling.

## Query rules

- Filter by stream fields first (`{namespace="$namespace"}`), then by message content. Stream fields are
  indexed; the message body is scanned.
- Bound every query with the dashboard range. An unbounded log query scans the full retention.
- Aggregate with `| stats by (field) count()` for a chartable series; a bare filter returns log lines, which
  only the `logs` panel renders.
- Set a `limit` on any query feeding a `logs` panel.

## Panels

`logs` for raw lines. `timeseries`, `barchart`, `stat`, and `piechart` for `stats` results. `table` for
aggregated breakdowns.

## Structure

Put the log-rate `timeseries` above the `logs` panel, sharing the same filter. Rate answers "when did this
start"; the lines answer "what is it". A `logs` panel alone forces the reader to scroll to find the onset.
