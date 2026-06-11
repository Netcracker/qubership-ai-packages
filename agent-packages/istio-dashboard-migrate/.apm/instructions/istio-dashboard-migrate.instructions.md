---
description: Trigger for adapting Grafana/Istio dashboard JSON to overlay CPU and memory resource limits.
applyTo: "**/dashboards/**/*.json"
---

When editing a Grafana dashboard JSON (typically under a `dashboards/`
directory, such as `helm-templates/qubership-istio/dashboards`) and adding
CPU or memory resource-limit overlays — drawing `kube_pod_container_resource_limits`
as a red reference line on a Memory Usage or CPU Usage panel — apply the
`istio-dashboard-migrate` skill.
