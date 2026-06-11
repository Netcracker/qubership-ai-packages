---
name: istio-dashboard-migrate
description: >
  Adapts Grafana dashboard JSON to add CPU and memory resource limit overlays to
  resource usage panels. Use this skill whenever the user wants to add resource
  limits (CPU limits, memory limits) to a Grafana dashboard, adapt a Grafana
  dashboard JSON with kube_pod_container_resource_limits metrics, or modify an
  Istio/Kubernetes Grafana dashboard to show limit lines. Also triggers for any
  request to "add limits to dashboard", "show resource limits in Grafana",
  "overlay limits on CPU/memory panels", or when a user provides a Grafana
  dashboard JSON and asks to add resource limit visibility.
---

# Istio Dashboard Migrate — Grafana Limit Overlays

Adds CPU and memory resource limit overlays to Grafana dashboard panels, using
`kube_pod_container_resource_limits` metrics as a red reference line.

## What This Skill Does

Given a Grafana dashboard JSON (either a URL or pasted JSON), produce an adapted
version where the resource usage panels include limit overlays:

1. **Memory Usage panel** — adds a `kube_pod_container_resource_limits` target
   for `resource="memory"`, styled as a red line with no fill
2. **CPU Usage panel** — adds a `kube_pod_container_resource_limits` target for
   `resource="cpu"`, styled as a red line with no fill

## Step-by-Step Process

### 1. Obtain the Source Dashboard

- If the user provides a URL, fetch it via `web_fetch`
- If the user pastes JSON directly, use that
- If the user uploads a file, read it from `helm-templates/qubership-istio/dashboards`

### 2. Parse and Identify Panels

Find panels by `"title"` (case-insensitive) or by inspecting `targets[].expr`:

| Panel | Title match | Expr match |
|---|---|---|
| Memory | `"Memory Usage"` | `container_memory_working_set_bytes` |
| CPU | `"CPU Usage"` | `container_cpu_usage_seconds_total` |

From the existing targets, extract:
- `container` label value (e.g. `"discovery"`)
- `pod` regex pattern (e.g. `"istiod-.*"`)

Use those same values in the limit queries.

### 3. Apply Memory Limit Overlay

Add to `targets[]` of the memory panel (use next unused letter for refId):

```json
{
  "datasource": { "type": "prometheus", "uid": "$datasource" },
  "alias": "limit",
  "expr": "kube_pod_container_resource_limits{container=\"<CONTAINER>\",pod=~\"<POD_PATTERN>\",resource=\"memory\"}",
  "legendFormat": "Memory Limit ({{pod}})",
  "refId": "F"
}
```

Add to `fieldConfig.overrides[]`:

```json
{
  "matcher": { "id": "byFrameRefID", "options": "F" },
  "properties": [
    { "id": "custom.lineWidth", "value": 2 },
    { "id": "custom.fillOpacity", "value": 0 },
    { "id": "color", "value": { "fixedColor": "red", "mode": "fixed" } }
  ]
}
```

### 4. Apply CPU Limit Overlay

Add to `targets[]` of the CPU panel (use refId `"B"`, or next unused letter):

```json
{
  "datasource": { "type": "prometheus", "uid": "$datasource" },
  "alias": "limit",
  "expr": "kube_pod_container_resource_limits{container=\"<CONTAINER>\",pod=~\"<POD_PATTERN>\",resource=\"cpu\"}",
  "legendFormat": "CPU Limit ({{pod}})",
  "refId": "B"
}
```

Add to `fieldConfig.overrides[]`:

```json
{
  "matcher": { "id": "byFrameRefID", "options": "B" },
  "properties": [
    { "id": "custom.lineWidth", "value": 2 },
    { "id": "custom.fillOpacity", "value": 0 },
    { "id": "color", "value": { "fixedColor": "red", "mode": "fixed" } }
  ]
}
```

### 5. Preserve Everything Else

Do NOT modify any other panels, or top-level fields: `uid`, `title`,
`schemaVersion`, `templating`, `time`, `refresh`, `__inputs`, `__requires`.

### 6. Output

Construct the full adapted JSON in memory (no scripts), write it to
the same files using `create_file`, and call `present_files`.

## Common Patterns

| Dashboard | Container | Pod Pattern |
|---|---|---|
| Istio Control Plane (istiod) | `discovery` | `istiod-.*` |
| Generic k8s app | app name | `<app>-.*` |

## Example: Istio Dashboard 7645

Source: `https://grafana.com/api/dashboards/7645/revisions/300/download`

Changes:
- Memory panel (id 4): added memory limit target (refId `F`) + red-line override
- CPU panel (id 6): added CPU limit target (refId `B`) + red-line override
