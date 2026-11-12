"""Prints every comment in a case result beside the declaration it sits on.

Usage, from the repository root:
  python3 research/javadoc-authoring/cases/comments.py <result.md>...

The output is for reading, not for grading: each line is the first code line
after a comment (or before it, for a Python docstring), then the comment
squashed onto one line. A declaration with no comment does not appear.
"""
import re
import sys


def code_block(text):
    m = re.search(r"```([a-z]*)\n(.*?)\n```", text, re.S)
    return (m.group(1), m.group(2).splitlines()) if m else ('', text.splitlines())


def comments(lang, lines):
    py = lang == 'python'
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        start = i
        if s.startswith('/**') or s.startswith('/*'):
            while '*/' not in lines[i]:
                i += 1
            body = ' '.join(l.strip() for l in lines[start:i + 1])
            i += 1
        elif s.startswith('//') or (py and s.startswith('#')):
            while i < len(lines) and (lines[i].strip().startswith('//') or
                                      (py and lines[i].strip().startswith('#'))):
                i += 1
            body = ' '.join(l.strip() for l in lines[start:i])
        elif s.startswith('"""') or s.startswith("r\"\"\""):
            if s.count('"""') < 2:
                i += 1
                while '"""' not in lines[i]:
                    i += 1
            body = ' '.join(l.strip() for l in lines[start:i + 1])
            # A docstring documents the def or class above it, or the assignment above it.
            j = start - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            out.append((lines[j].strip() if j >= 0 else '?', body))
            i += 1
            continue
        else:
            # A trailing comment on a code line.
            m = re.search(r'\s(//|#)\s(.*)$' if py else r'\s(//)\s(.*)$', lines[i])
            if m:
                out.append((s[:m.start()].strip(), m.group(1) + ' ' + m.group(2)))
            i += 1
            continue
        j = i
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith('@') or
                                  lines[j].strip().startswith('#[')):
            j += 1
        out.append((lines[j].strip() if j < len(lines) else '?', re.sub(r'\s+', ' ', body)))
    return out


for path in sys.argv[1:]:
    print(f'=== {path}')
    for code, body in comments(*code_block(open(path).read())):
        print(f'  [{code[:70]}]\n      {body}')
