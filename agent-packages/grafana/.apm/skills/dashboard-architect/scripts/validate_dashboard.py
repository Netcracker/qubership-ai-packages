#!/usr/bin/env python3
"""Structural validation for classic-schema Grafana dashboard JSON.

Covers the failure classes a generated dashboard actually exhibits and that
`grafana/dashboard-linter` does not check: layout collisions, duplicate panel
ids, references to undeclared template variables, and panel types that the
target datasource cannot render.

Grafana accepts most of these without complaint and then silently reflows or
drops the offending panel, so the dashboard imports "successfully" and looks
wrong. Catching them before publish is the whole point of this script.

Standard library only, so it runs wherever the agent runs.

Exit codes: 0 clean or warnings only, 1 errors found, 2 the file could not be read.
"""

import argparse
import json
import re
import sys

# Grafana renders dashboards on a fixed 24-column grid.
GRID_COLUMNS = 24

# Grafana rejects a dashboard uid longer than 40 characters on import.
UID_MAX_LENGTH = 40
UID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")

# Replaced by `timeseries`, `stat`, and `table` respectively. A dashboard
# shipping these is either copied from a pre-Grafana-8 source or generated
# from a stale example.
LEGACY_PANEL_TYPES = {
    "graph": "timeseries",
    "singlestat": "stat",
    "grafana-singlestat-panel": "stat",
    "table-old": "table",
    "graph-old": "timeseries",
}

# Variables Grafana supplies itself. Matching one of these is not a missing
# declaration, so they never count as an undeclared reference.
BUILTIN_VARIABLES = {
    "__rate_interval", "__rate_interval_ms", "__interval", "__interval_ms",
    "__range", "__range_s", "__range_ms", "__from", "__to", "__timeFilter",
    "__auto", "__auto_interval", "__dashboard", "__org", "__user", "__name",
    "__series", "__field", "__value", "__data", "__cell", "__searchFilter",
    "__all", "__timezone", "timeFilter",
}

# Panel types each datasource can actually render. A `flamegraph` bound to a
# Prometheus target renders empty rather than erroring, which is why this is
# checked here.
SIGNAL_PANELS = {
    "metrics": {
        "timeseries", "stat", "gauge", "bargauge", "table", "barchart",
        "piechart", "histogram", "heatmap", "state-timeline",
        "status-history", "trend", "xychart", "canvas", "geomap",
    },
    "logs": {
        "logs", "table", "timeseries", "stat", "barchart", "piechart",
        "bargauge", "gauge", "state-timeline", "status-history", "heatmap",
    },
    "traces": {
        "traces", "table", "nodeGraph", "timeseries", "stat", "histogram",
        "heatmap",
    },
    "profiles": {"flamegraph", "table", "timeseries", "stat"},
}

# Datasource plugin id prefixes, mapped to the signal they carry.
DATASOURCE_SIGNALS = [
    ("victoriametrics-logs-datasource", "logs"),
    ("victoriametrics-traces-datasource", "traces"),
    ("victoriametrics-datasource", "metrics"),
    ("grafana-pyroscope-datasource", "profiles"),
    ("phlare", "profiles"),
    ("prometheus", "metrics"),
    ("loki", "logs"),
    ("elasticsearch", "logs"),
    ("tempo", "traces"),
    ("jaeger", "traces"),
    ("zipkin", "traces"),
]

# Rendered from static content or dashboard state, so datasource and target
# rules do not apply to them.
DATASOURCE_FREE_PANELS = {
    "row", "text", "dashlist", "news", "alertlist", "annolist", "welcome",
}

# Panels whose primary value is a number, so an unset unit shows a bare float.
UNIT_REQUIRED_PANELS = {
    "timeseries", "stat", "gauge", "bargauge", "barchart", "piechart",
    "histogram", "trend", "xychart", "heatmap",
}

# `$name`, `${name}`, `${name:csv}`, and the legacy `[[name]]` form.
VARIABLE_PATTERN = re.compile(
    r"\$(?:\{([A-Za-z0-9_]+)(?::[^}]*)?\}|([A-Za-z0-9_]+))|\[\[([A-Za-z0-9_]+)[^\]]*\]\]"
)

# `$1` in a PromQL `label_replace` is a regex capture group, not a variable.
CAPTURE_GROUP_PATTERN = re.compile(r"^[0-9]+$")

# Dashboards rendered by Helm or the Grafana operator carry template
# expressions in place of literal values, so length and charset cannot be
# checked until the chart is rendered.
TEMPLATE_EXPRESSION_PATTERN = re.compile(r"\{[{%].*?[}%]\}", re.DOTALL)

# Fields on a target that hold a query in some query language.
QUERY_FIELDS = ("expr", "query", "rawSql", "target", "labelSelector", "profileTypeId")


class Report:
    """Collects findings so a single run reports every problem, not just the first."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append((where, message))

    def warn(self, where, message):
        self.warnings.append((where, message))

    @property
    def ok(self):
        return not self.errors


def panel_label(panel):
    title = panel.get("title") or "<untitled>"
    return "panel {} \"{}\"".format(panel.get("id", "?"), title)


def iter_panels(dashboard):
    """Yield every panel, descending into the `panels` array of collapsed rows.

    A collapsed row stores its children inline rather than at the top level, so
    a walk that only reads `dashboard["panels"]` silently skips them.
    """
    for panel in dashboard.get("panels") or []:
        yield panel
        for child in panel.get("panels") or []:
            yield child


def signal_of(datasource):
    """Map a panel datasource to its signal, or None when it cannot be resolved."""
    if not isinstance(datasource, dict):
        return None
    ds_type = (datasource.get("type") or "").lower()
    for prefix, signal in DATASOURCE_SIGNALS:
        if prefix in ds_type:
            return signal
    return None


def collect_variables(dashboard):
    declared = set()
    for variable in (dashboard.get("templating") or {}).get("list") or []:
        name = variable.get("name")
        if name:
            declared.add(name)
    return declared


def referenced_variables(text):
    found = set()
    for match in VARIABLE_PATTERN.finditer(text):
        name = match.group(1) or match.group(2) or match.group(3)
        if not name or name in BUILTIN_VARIABLES:
            continue
        if CAPTURE_GROUP_PATTERN.match(name):
            continue
        found.add(name)
    return found


def check_metadata(dashboard, report):
    uid = dashboard.get("uid")
    if not uid:
        report.error("dashboard", "no uid set; Grafana assigns a random one and links break")
    elif TEMPLATE_EXPRESSION_PATTERN.search(uid):
        report.warn(
            "dashboard",
            "uid holds a template expression; verify the rendered value stays "
            "within {} characters".format(UID_MAX_LENGTH),
        )
    else:
        if len(uid) > UID_MAX_LENGTH:
            report.error(
                "dashboard",
                "uid is {} characters; Grafana rejects anything over {}".format(
                    len(uid), UID_MAX_LENGTH
                ),
            )
        if not UID_PATTERN.match(uid):
            report.error("dashboard", "uid \"{}\" contains characters outside [a-zA-Z0-9._-]".format(uid))

    if not dashboard.get("title"):
        report.error("dashboard", "no title set")

    if "schemaVersion" not in dashboard:
        report.error("dashboard", "no schemaVersion; Grafana cannot migrate the JSON on import")

    tags = dashboard.get("tags") or []
    if "ai-generated" not in tags:
        report.warn("dashboard", "missing the `ai-generated` tag that marks provenance")


def check_layout(dashboard, report):
    """Report panels that leave the grid or overlap a sibling.

    Grafana reflows overlapping panels instead of erroring, which scrambles the
    layout the dashboard was designed around.
    """
    containers = [("top level", dashboard.get("panels") or [])]
    for panel in dashboard.get("panels") or []:
        if panel.get("panels"):
            containers.append(("row \"{}\"".format(panel.get("title", "?")), panel["panels"]))

    for container, panels in containers:
        rectangles = []
        for panel in panels:
            grid = panel.get("gridPos")
            where = panel_label(panel)
            if not isinstance(grid, dict):
                report.error(where, "no gridPos")
                continue

            x, y = grid.get("x", 0), grid.get("y", 0)
            w, h = grid.get("w", 0), grid.get("h", 0)

            if x < 0 or y < 0:
                report.error(where, "negative gridPos x={} y={}".format(x, y))
            if w < 1:
                report.error(where, "gridPos w={} must be at least 1".format(w))
            if h < 1:
                report.error(where, "gridPos h={} must be at least 1".format(h))
            if x + w > GRID_COLUMNS:
                report.error(
                    where,
                    "gridPos x={} + w={} = {} exceeds the {}-column grid".format(
                        x, w, x + w, GRID_COLUMNS
                    ),
                )
            rectangles.append((x, y, w, h, where))

        for i, (ax, ay, aw, ah, a_where) in enumerate(rectangles):
            for bx, by, bw, bh, b_where in rectangles[i + 1:]:
                overlaps_x = ax < bx + bw and bx < ax + aw
                overlaps_y = ay < by + bh and by < ay + ah
                if overlaps_x and overlaps_y:
                    report.error(
                        a_where,
                        "overlaps {} at {}; Grafana will reflow both".format(b_where, container),
                    )


def check_panel_ids(dashboard, report):
    """Duplicate ids break panel links, drilldowns, and per-panel permalinks."""
    seen = {}
    for panel in iter_panels(dashboard):
        panel_id = panel.get("id")
        if panel_id is None:
            report.error(panel_label(panel), "no id")
            continue
        if panel_id in seen:
            report.error(
                panel_label(panel),
                "duplicate id {}, already used by \"{}\"".format(panel_id, seen[panel_id]),
            )
        else:
            seen[panel_id] = panel.get("title", "<untitled>")


def check_rows(dashboard, report):
    """A collapsed row must hold its children inline; an expanded one must not."""
    for panel in dashboard.get("panels") or []:
        if panel.get("type") != "row":
            continue
        where = panel_label(panel)
        collapsed = panel.get("collapsed", False)
        children = panel.get("panels") or []
        if collapsed and not children:
            report.warn(where, "collapsed row holds no panels")
        if not collapsed and children:
            report.error(
                where,
                "expanded row holds inline panels; they belong at the top level "
                "or the row must be marked collapsed",
            )
        if panel.get("gridPos", {}).get("h", 1) != 1:
            report.warn(where, "row height should be 1")


def check_variables(dashboard, report):
    declared = collect_variables(dashboard)
    for panel in iter_panels(dashboard):
        where = panel_label(panel)
        for target in panel.get("targets") or []:
            for field in QUERY_FIELDS:
                value = target.get(field)
                if not isinstance(value, str):
                    continue
                for name in referenced_variables(value):
                    if name not in declared:
                        report.error(
                            where,
                            "query references ${} but templating.list does not declare it".format(name),
                        )

    for variable in (dashboard.get("templating") or {}).get("list") or []:
        if variable.get("type") != "query":
            continue
        name = variable.get("name", "?")
        if variable.get("refresh") != 2:
            report.warn(
                "variable \"{}\"".format(name),
                "refresh is {}; use 2 so the variable reloads on time-range change".format(
                    variable.get("refresh")
                ),
            )
        query = variable.get("query")
        query_text = query if isinstance(query, str) else json.dumps(query)
        for referenced in referenced_variables(query_text):
            if referenced not in declared:
                report.error(
                    "variable \"{}\"".format(name),
                    "query references ${} which is not declared".format(referenced),
                )


def check_panels(dashboard, report):
    declared = collect_variables(dashboard)
    datasource_variable = "datasource" in declared

    for panel in iter_panels(dashboard):
        panel_type = panel.get("type")
        where = panel_label(panel)

        if panel_type in LEGACY_PANEL_TYPES:
            report.error(
                where,
                "panel type \"{}\" is removed in Grafana 11+; use \"{}\"".format(
                    panel_type, LEGACY_PANEL_TYPES[panel_type]
                ),
            )
            continue

        if panel_type in DATASOURCE_FREE_PANELS:
            continue

        if not panel.get("title"):
            report.error(where, "no title")
        if not panel.get("description"):
            report.error(where, "no description")

        targets = panel.get("targets") or []
        if not targets:
            report.error(where, "no targets; the panel renders empty")

        datasource = panel.get("datasource")
        if not isinstance(datasource, dict):
            report.error(where, "no datasource object")
        elif datasource_variable:
            uid = datasource.get("uid", "")
            if uid not in ("${datasource}", "$datasource"):
                report.error(
                    where,
                    "datasource.uid is \"{}\"; use ${{datasource}} so the variable applies".format(uid),
                )

        signal = signal_of(datasource)
        if signal and panel_type not in SIGNAL_PANELS[signal]:
            report.error(
                where,
                "panel type \"{}\" cannot render {} data from datasource type \"{}\"".format(
                    panel_type, signal, datasource.get("type")
                ),
            )

        if panel_type in UNIT_REQUIRED_PANELS:
            unit = ((panel.get("fieldConfig") or {}).get("defaults") or {}).get("unit")
            if not unit:
                report.error(where, "no unit set in fieldConfig.defaults")


def validate(dashboard):
    report = Report()
    # A dashboard exported through the Grafana API arrives wrapped.
    if "dashboard" in dashboard and isinstance(dashboard["dashboard"], dict):
        dashboard = dashboard["dashboard"]

    check_metadata(dashboard, report)
    check_layout(dashboard, report)
    check_panel_ids(dashboard, report)
    check_rows(dashboard, report)
    check_variables(dashboard, report)
    check_panels(dashboard, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dashboard", help="path to the dashboard JSON, or - for stdin")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.dashboard == "-" else open(args.dashboard, encoding="utf-8").read()
        dashboard = json.loads(raw)
    except OSError as exc:
        print("Cannot read {}: {}".format(args.dashboard, exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("Cannot parse {}: {}".format(args.dashboard, exc), file=sys.stderr)
        return 2

    report = validate(dashboard)

    if args.json:
        print(json.dumps({
            "errors": [{"where": w, "message": m} for w, m in report.errors],
            "warnings": [{"where": w, "message": m} for w, m in report.warnings],
        }, indent=2))
    else:
        for where, message in report.errors:
            print("ERROR  {}: {}".format(where, message))
        for where, message in report.warnings:
            print("WARN   {}: {}".format(where, message))
        print("\n{} error(s), {} warning(s)".format(len(report.errors), len(report.warnings)))

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
