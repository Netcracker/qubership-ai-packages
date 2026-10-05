#!/usr/bin/env sh
# Runs the frictionless spec modules that encode the behavior of the case's
# change, and any other spec module that differs from the case's base, in the
# checkout given as the argument, and prints how many tests ran and which
# failed. Makes a Python 3.11 environment with uv in .python/case, a directory
# the repository's .gitignore already ignores, on the first run.
set -eu
repo=${1:?usage: build.sh <frictionless checkout>}
case_dir=$(cd "$(dirname "$0")" && pwd)
base=$(cat "$case_dir/base")

py=$repo/.python/case/bin/python
if [ ! -x "$py" ]; then
  uv venv -q --python 3.11 "$repo/.python/case"
  uv pip install -q --python "$py" -e "${repo}[sql]" pytest pytest-lazy-fixtures pytest-mock \
    pytest-vcr requests-mock pytest-dotenv pytest-timeout
fi

# The modules whose expectations the change moves, and every spec module the
# session added or changed.
modules=$( {
  printf '%s\n' frictionless/resource/__spec__/test_validate_schema.py \
    frictionless/package/__spec__/test_validate.py \
    frictionless/table/__spec__/test_header.py \
    frictionless/analyzer/__spec__/test_resource.py
  git -C "$repo" diff --name-only "$base" -- 'frictionless/*/__spec__/*.py'
  git -C "$repo" ls-files --others --exclude-standard -- 'frictionless/*/__spec__/*.py'
} | grep '/test_[^/]*\.py$' | sort -u)

report=$(mktemp)
log=$(mktemp)
status=0
# $modules is split on purpose: one path each.
# shellcheck disable=SC2086
(cd "$repo" && "$py" -m pytest -q -p no:cacheprovider --junitxml="$report" $modules > "$log" 2>&1) || status=$?

python3 - "$report" "$log" "$status" <<'PY'
import os, sys
import xml.etree.ElementTree as ET
report, log, status = sys.argv[1], sys.argv[2], int(sys.argv[3])
ran, failed = 0, []
if os.path.getsize(report):
    for tc in ET.parse(report).getroot().iter('testcase'):
        if tc.find('skipped') is not None:
            continue
        ran += 1
        if tc.find('failure') is not None or tc.find('error') is not None:
            failed.append(f"{tc.get('classname').rsplit('.', 1)[-1]}.{tc.get('name')}")
if ran == 0:
    tail = open(log).read().splitlines()[-10:]
    print(f'no test ran, and pytest exited with {status}' + ''.join(f'\n  {l}' for l in tail))
elif status != 0 and not failed:
    print(f'{ran} tests ran and none failed, but pytest exited with {status}; see {log}')
else:
    print(f'{ran} tests ran, {len(failed)} failed' + ''.join(f'\n  {t}' for t in failed))
PY
[ "$status" -eq 0 ]
