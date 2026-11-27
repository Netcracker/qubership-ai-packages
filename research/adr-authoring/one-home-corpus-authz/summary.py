"""Summarizes findings.jsonl: per-arm verdicts, shared and unique groups of confirmed findings,
and the high-severity groups with links to the lines they cover.

Usage, from the repository root:
    python3 research/adr-authoring/one-home-corpus-authz/summary.py [--high]
"""

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = 'https://github.com/Netcracker/qubership-authz-agent'


def link(row):
    """Links the first file and line range of a finding; `lines` may list more ranges after it."""
    path, start, end = re.search(r'([^/:\s]+\.md):(\d+)(?:-(\d+))?', row['lines']).groups()
    return f"{REPO}/blob/{row['commit']}/docs/decisions/{path}?plain=1#L{start}-L{end or start}"


rows = [json.loads(line) for line in open(os.path.join(HERE, 'findings.jsonl'))]
for arm in 'BV':
    mine = [r for r in rows if r['arm'] == arm]
    verdicts = collections.Counter(r['verdict'] for r in mine)
    high = sum(r['verdict'] == 'TP' and r['severity'] == 'high' for r in mine)
    print(f"{arm}: {len(mine)} findings, {dict(verdicts)}, precision {verdicts['TP'] / len(mine):.2f}, TP high {high}")
groups = collections.defaultdict(list)
for r in rows:
    if r['verdict'] == 'TP':
        groups[r['group']].append(r)
arms = collections.Counter(''.join(sorted({r['arm'] for r in g})) for g in groups.values())
print(f"TP groups: {len(groups)}; found by both {arms['BV']}, by V only {arms['V']}, by B only {arms['B']}")
if '--high' in sys.argv:
    for name, g in sorted(groups.items(), key=lambda kv: kv[1][0]['record']):
        if any(r['severity'] == 'high' for r in g):
            r = next(r for r in g if r['severity'] == 'high')
            print(f"\n{r['record']} ({name}, arms {''.join(sorted({x['arm'] for x in g}))}), owner {r['owner']}\n"
                  f"  {link(r)}\n  judge: {r['judge_reason']}")
