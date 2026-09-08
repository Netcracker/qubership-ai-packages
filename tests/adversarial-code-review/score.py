import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
expected_path = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'expected.json'
expected = json.loads(expected_path.read_text())
runs = json.loads(Path(sys.argv[1]).read_text())
failed = False
for name, rows in runs.items():
    actual = {row['id']: row for row in rows}
    if len(actual) != len(rows) or set(actual) != set(expected):
        raise ValueError(f'{name}: missing, duplicate, or unexpected case IDs')
    failures = []
    for case, rule in expected.items():
        row = actual[case]
        valid = True
        for key, value in rule.items():
            observed = row.get('action' if key == 'actions' else key)
            valid = valid and (
                value is None or (observed in value if isinstance(value, list) else observed == value)
            )
        if 'reply' in rule:
            valid = valid and isinstance(row.get('reply'), bool)
        if not valid:
            failures.append(case)
    print(f'{name}: {len(expected) - len(failures)}/{len(expected)}')
    if failures:
        print('  Failed: ' + ', '.join(failures))
        failed = True
sys.exit(1 if failed else 0)
