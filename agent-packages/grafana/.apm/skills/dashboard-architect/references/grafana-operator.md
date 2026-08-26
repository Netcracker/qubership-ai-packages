# Grafana operator output

Use this when the user wants a dashboard to ship inside a Helm chart or a Kubernetes manifest rather than
uploaded through the API.

The target is grafana-operator v4, which reads `integreatly.org/v1alpha1` `GrafanaDashboard` resources.
Confirm the operator version in the target cluster before emitting this: v5 uses the
`grafana.integreatly.org/v1beta1` API with a different spec, and the two are not interchangeable.

```yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: <name>
  labels:
    app.kubernetes.io/name: <name>
    app.kubernetes.io/component: grafana
    app.kubernetes.io/part-of: monitoring
spec:
  json: |
    <dashboard json, indented four spaces>
```

Rules:

- Validate the dashboard JSON before wrapping it. Once embedded in a YAML string the validator cannot read
  it, and the operator applies it without checking.
- Keep the JSON indented consistently under `json: |`. A single misaligned line silently truncates the block.
- A `uid` templated by Helm renders at install time, so the 40-character limit applies to the rendered value,
  not the template. `{% printf "%.40s" ... %}` is the usual way to enforce that.
- Write the file into the chart's `dashboards/` directory when the user names a repository.
