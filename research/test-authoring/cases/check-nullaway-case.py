"""Counts the markers of a NullAway case result that a script can count.

Usage, from the repository root:
    python3 research/test-authoring/cases/check-nullaway-case.py <case>/<model> [<diagnostic> ...]

Reads <case>/<model>/changed-files.txt and the changed files beside it, as
run-nullaway-case.sh writes them, compares each file other than production
code with its version at the case's base commit, fetched from
raw.githubusercontent.com, and prints one line per count. Each <diagnostic>
is the text after "BUG: Diagnostic contains: " that the tests have to expect
somewhere. The checks a count cannot settle are graded by reading; see the
case README.
"""

import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

model_dir = sys.argv[1].rstrip('/')
required = sys.argv[2:]
base = open(os.path.join(os.path.dirname(model_dir), 'base')).read().strip()


def at_base(path):
    url = f'https://raw.githubusercontent.com/uber/NullAway/{base}/{path}'
    try:
        return urllib.request.urlopen(url).read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ''
        raise


# The added lines of each changed file: production against the commit the
# session started from, which leaves them empty when nothing changed; every
# other file against the base.
sections = {}
production = []
for line in open(f'{model_dir}/changed-files.txt').read().splitlines():
    kind, status, path = line.split(maxsplit=2)
    if kind == 'production':
        production.append(path)
        continue
    new = os.devnull if status == 'D' else os.path.join(model_dir, os.path.basename(path))
    with tempfile.NamedTemporaryFile('w', suffix='.java') as old:
        old.write('' if status == 'A' else at_base(path))
        old.flush()
        # git's own diff, so that the lines count as added exactly as git shows them.
        diff = subprocess.run(['git', 'diff', '--no-index', '-U0', old.name, new],
                              capture_output=True, text=True).stdout
    sections[path] = [d[1:] for d in diff.splitlines() if d.startswith('+') and not d.startswith('+++')]

tests = {p: a for p, a in sections.items() if '/src/test/' in p}
other = [p for p in sections if p not in production and p not in tests]
print('production files changed (expect none):', production or 'none')
print('files changed outside the tests (read each):', other or 'none')

code = '\n'.join(line for added in tests.values() for line in added)
methods = re.split(r'^\s*@Test\b', code, flags=re.M)[1:]
marker = 'BUG: Diagnostic contains:'
per_test = []
for body in methods:
    name = re.search(r'void\s+(\w+)\s*\(', body)
    per_test.append((name.group(1) if name else '?', body.count(marker)))

print('tests added:', len(per_test))
print('tests with no marker:', sum(1 for _, n in per_test if n == 0))
print('most markers in one test (expect 1):', max((n for _, n in per_test), default=0))
for name, n in per_test:
    flag = '  <- two cases that expect a report' if n > 1 else ''
    print(f'  {n} {name}{flag}')
print('names with "And" or "But" (read each: the outcomes of two inputs fail, the condition of one rule passes):',
      [name for name, _ in per_test if re.search(r'(And|But)[A-Z]', name)] or 'none')

for diagnostic in required:
    print(f'expects {diagnostic!r} (expect True):', f'{marker} {diagnostic}' in code)

# A helper that assembles a source from pieces of syntax: formatting or
# concatenation around the text of a source, or a new helper method that
# returns one.
assembled = [line.strip() for line in code.splitlines()
             if re.search(r'\.formatted\(|String\.format\(|"""\s*\+|\+\s*"""|"\s*\+\s*\w', line)]
print('lines that assemble a source (expect none):', assembled or 'none')
helpers = re.findall(r'^\s*(?:private|static|public)[^=;(]*\s(\w+)\s*\([^)]*String[^)]*\)\s*\{', code, re.M)
print('new helpers that take a String (read each):', helpers or 'none')
