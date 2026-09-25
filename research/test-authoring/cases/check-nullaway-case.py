"""Counts the markers of a NullAway case result that a script can count.

Usage, from the repository root:
    python3 research/test-authoring/cases/check-nullaway-case.py <case>/<model> [<diagnostic> ...]

Reads <case>/<model>/result.diff, as run-nullaway-case.sh writes it, and
prints one line per count. Each <diagnostic> is the text after
"BUG: Diagnostic contains: " that the tests have to expect somewhere. The
checks a count cannot settle are graded by reading; see the case README.
"""

import re
import sys

model_dir = sys.argv[1]
required = sys.argv[2:]
diff = open(f'{model_dir}/result.diff').read()

# One section per file; the path is taken from the "+++ b/" line.
sections = {}
for chunk in re.split(r'^diff --git ', diff, flags=re.M)[1:]:
    path = re.search(r'^\+\+\+ (?:b/(.*)|/dev/null)$', chunk, re.M)
    path = path.group(1) if path and path.group(1) else chunk.split()[0][2:]
    added = [line[1:] for line in chunk.splitlines()
             if line.startswith('+') and not line.startswith('+++')]
    sections[path] = added

production = [p for p in sections if p.startswith('nullaway/src/main/') or p == 'CHANGELOG.md']
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
print('names with "And" (read each: the outcomes of two inputs fail, the condition of one rule passes):',
      [name for name, _ in per_test if re.search(r'And[A-Z]', name)] or 'none')

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
