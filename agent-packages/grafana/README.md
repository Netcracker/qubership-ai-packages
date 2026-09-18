# Grafana dashboards

APM package for finding, generating, validating, and publishing Grafana dashboards across metrics, logs,
traces, and profiles.

## Skills

`dashboard-finder` searches the target Grafana, grafana.com, and this repository for a dashboard that meets
stated criteria, scores each candidate, and reports the gaps.

`dashboard-architect` builds or edits a dashboard, validates it, and publishes it to Grafana or emits it as a
grafana-operator manifest.

## Setup

Copy `.env.example` to `.env` and set `GRAFANA_URL`. Skip this if the `grafana` MCP server is configured; it
already carries the address and the credential. `.env` is gitignored.

Grafana is the only address needed. Datasource URLs and uids are read from `GET /api/datasources`, and queries
are proxied through `POST /api/ds/query`.

### Optional: the PromQL linter

`dashboard-architect` runs [grafana/dashboard-linter](https://github.com/grafana/dashboard-linter) as its
second validation stage. Without it, validation still runs but PromQL is not parsed.

`go install ...@latest` fails on this module because it carries `replace` directives. Build from a clone:

```bash
git clone --depth 1 https://github.com/grafana/dashboard-linter.git
cd dashboard-linter && go build -o "$(go env GOPATH)/bin/dashboard-linter" .
```

### Optional: VictoriaMetrics query skills

When no MCP server is configured, discovery falls back to the curl-based query skills in
[VictoriaMetrics/skills](https://github.com/VictoriaMetrics/skills), which cover metrics, logs, and traces.
Tempo and Pyroscope are not covered there and go through the Grafana datasource proxy instead.

## Validation

```bash
.apm/skills/dashboard-architect/scripts/validate.sh <dashboard.json>
```

Stage 1, `validate_dashboard.py`, needs only Python and covers every signal: grid overlap and overflow,
duplicate panel ids, references to undeclared template variables, uid limits, legacy panel types, row nesting,
and panel types the datasource cannot render.

Stage 2 is the linter, scoped to Prometheus panels. `scripts/.lint` excludes the rules that assume `job` and
`instance` scoping, which this package replaces with cluster, namespace, and pod.

## Layout

```text
agent-packages/grafana/
├── apm.yml
├── .env.example
├── prompt.md                     request phrasings used to exercise the skills
├── dashboards/                   generated output, grafana-operator format
└── .apm/
    ├── instructions/
    └── skills/
        ├── dashboard-finder/
        └── dashboard-architect/
            ├── references/       conventions, panel snippets, per-signal rules
            ├── scripts/          validator, lint config, fixtures
            └── assets/           full production dashboards, for layout reference
```
