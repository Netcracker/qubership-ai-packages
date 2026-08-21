---
name: dashboard-finder
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - WebFetch
description: >-
  Find an existing Grafana dashboard that meets stated criteria, score how well each candidate fits, and
  report the gaps. Use when the user asks whether a dashboard already exists, asks to find or reuse one
  instead of building it, or asks what dashboards cover a service. Triggers on: find a dashboard, is there a
  dashboard, existing dashboard, do we already have, reuse a dashboard, search grafana.com, community
  dashboard, which dashboard shows.
---

# Dashboard finder

Find dashboards that already answer the user's question, score them against the stated criteria, and report
what each one misses.

Hand off to `dashboard-architect` when the user decides to build or extend instead.

## Pipeline

### 1. Establish criteria

Extract from the request, asking only when a scoring input is genuinely missing:

- Signal and backend: metrics, logs, traces, profiles.
- Subject: the service, workload, or component.
- Required views: rate, errors, latency, saturation, state, cost.
- Scope: cluster-wide, one namespace, one workload.

### 2. Search, cheapest source first

```bash
# 1. already installed on the target instance
curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/search?type=dash-db&query=$TERM" | jq -r '.[] | "\(.uid)\t\(.title)"'

# 2. the community library
curl -s "https://grafana.com/api/dashboards?search=$TERM&orderBy=downloads&direction=desc&pageSize=20" \
  | jq -r '.items[] | "\(.id)\t\(.name)\t\(.downloads)"'

# 3. previously generated, in this repository
```

The `grafana` MCP server covers the first source. Search source 3 with `Glob` over `dashboards/`.

Search the subject, not the phrasing. A request about "our Java service memory" finds dashboards under `jvm`,
`java`, and `micrometer`, none of which contain the user's service name.

### 3. Score each candidate

| Criterion | Weight | Check |
|---|---|---|
| Datasource type | hard gate | The dashboard's datasource type matches the signal. A miss disqualifies. |
| Metrics present | 0.4 | Fraction of the dashboard's metric names that exist in the user's datasource. |
| Scope variables | 0.2 | Carries the cluster, namespace, or pod variables the request needs. |
| View coverage | 0.2 | Covers the required views from step 1. |
| Freshness | 0.1 | `schemaVersion` 39 or newer, and no `graph`, `singlestat`, or `table-old` panels. |
| Version fit | 0.1 | Panel types used are available on the target Grafana. |

The metrics check carries the most weight because it is the one that decides whether the dashboard works.
A community dashboard can read perfectly and reference an exporter the user does not run. Extract the metric
names from the candidate's targets, then confirm them against the live datasource using the same discovery
chain `dashboard-architect` uses. Skipping this step turns the score into decoration.

Freshness and version fit come from reading the candidate JSON directly, which also catches dashboards that
would import broken.

### 4. Report and ask

Present at most two candidates. For each: title, score, a clickable link or the grafana.com id, what it
covers, and what it misses by name.

Then ask what to do, with `AskUserQuestion`:

- Import as-is.
- Import and hand off to `dashboard-architect` to fill the gaps.
- Discard and build a new dashboard.

Ask even when a candidate scores well. A user who asked for a dashboard to be built should not silently
receive somebody else's instead. When nothing clears the datasource gate, say so plainly and offer to build.

### 5. Import

Only when the user chose to import. Community dashboards need work before they are usable:

- Rewrite hard-coded datasource uids to `${datasource}`, and add the `datasource` variable if it is missing.
- Check the `uid` against the 40-character limit.
- Run `../dashboard-architect/scripts/validate.sh` on the result. A downloaded dashboard is no more trusted
  than a generated one.
- Tag it `ai-generated` only if it was modified. An unmodified import keeps its original provenance.
