#!/usr/bin/env bash
# Run both validation stages over a dashboard JSON file.
#
# Stage 1, validate_dashboard.py, always runs and covers layout, ids, variable
# references, and panel/datasource compatibility for every signal.
#
# Stage 2, dashboard-linter, parses PromQL and is Prometheus-only. It is
# optional: a missing binary downgrades the run to a partial pass rather than
# failing it, because the structural stage still carries most of the value.
#
# Exit codes: 0 both stages clean, 1 a stage reported errors, 2 bad invocation.

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dashboard="${1:-}"

if [[ -z "$dashboard" || ! -f "$dashboard" ]]; then
    echo "usage: validate.sh <dashboard.json>" >&2
    exit 2
fi

status=0

echo "== Stage 1: structural validation"
python3 "$script_dir/validate_dashboard.py" "$dashboard" || status=1

echo
echo "== Stage 2: dashboard-linter"
if ! command -v dashboard-linter >/dev/null 2>&1; then
    cat >&2 <<'MISSING'
SKIPPED: dashboard-linter is not on PATH, so PromQL was not parsed.

Install it, then re-run. `go install ...@latest` fails because the module
carries replace directives, so build from a clone instead:

    git clone --depth 1 https://github.com/grafana/dashboard-linter.git
    cd dashboard-linter && go build -o "$(go env GOPATH)/bin/dashboard-linter" .

Stage 1 passed on its own, so this is a partial pass, not a clean one.
MISSING
else
    # --strict is required: without it the linter prints errors and still
    # exits 0, which would rubber-stamp a broken dashboard.
    # The linter reads .lint from the working directory, so run it from here.
    (cd "$script_dir" && dashboard-linter lint --strict --config .lint "$(realpath "$dashboard")") || status=1
fi

exit $status
