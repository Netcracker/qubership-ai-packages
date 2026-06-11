# istio-dashboard-migrate

Adapts a Grafana dashboard JSON to overlay **CPU and memory resource limits**
on its usage panels, drawing `kube_pod_container_resource_limits` as a red
reference line.

## What it does

Given a dashboard (a URL, pasted JSON, or a file under
`helm-templates/qubership-istio/dashboards`):

1. Finds the **Memory Usage** and **CPU Usage** panels by title or by the
   `container_memory_working_set_bytes` / `container_cpu_usage_seconds_total`
   expression.
2. Reuses the existing `container` label and `pod` regex to add a
   `kube_pod_container_resource_limits` target on each panel.
3. Styles each new series as a red, no-fill reference line via a
   `byFrameRefID` field override.
4. Leaves every other panel and all top-level fields (`uid`, `title`,
   `templating`, `time`, ...) untouched.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/istio-dashboard-migrate
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/istio-dashboard-migrate@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the location
your agent reads (`.claude/skills/`, `.cursor/`, ...).

## What you get

- A short instruction that fires when the agent edits a dashboard JSON under a
  `dashboards/` directory and adds resource-limit overlays. It tells the agent
  to load the `istio-dashboard-migrate` skill instead of guessing.
- The skill itself
  ([`SKILL.md`](.apm/skills/istio-dashboard-migrate/SKILL.md)) — panel
  matching, the exact target and field-override JSON to add, and a worked
  example against Grafana dashboard 7645.
