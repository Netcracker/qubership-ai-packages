"""Counts the markers a script can find in the results of a docs-page-authoring case.

Usage, from the repository root:
    python3 research/docs-page-authoring/cases/check.py <case directory>

It prints one line per result and check: PASS or FAIL, with the evidence it found. A PASS is a marker found, not a
grade: grade every check by reading the result against its question in the case README.
"""

import glob
import os
import re
import sys


def body(text):
    lines = [l for l in text.strip().splitlines() if l.strip() and not l.startswith('```')]
    return lines[0], lines[1:]


def words(lines):
    return sum(len(l.split()) for l in lines)


def has(pattern, flags=re.I):
    def check(text):
        m = re.search(pattern, text, flags)
        return m is not None, m.group(0) if m else 'none'
    return check


def lacks(pattern, flags=re.I):
    def check(text):
        m = re.search(pattern, text, flags)
        return m is None, m.group(0) if m else 'none'
    return check


def header(name, type_):
    def check(text):
        first, _ = body(text)
        return f'`{name}`' in first and type_ in first, first
    return check


def body_words(limit):
    def check(text):
        _, rest = body(text)
        n = words(rest)
        return n <= limit, f'{n} words under the header, {len(rest)} lines'
    return check


CASES = {
    'boolean-option': [
        ('header', header('disableKeepAlive', 'boolean')),
        ('claim', has(r'Connection: close')),
        ('short', body_words(30)),
        ('no values', lacks(r'case-insensitive|any other (value|string)|parses? as|reads as|typo')),
        ('no scope', lacks(r'RelayClient\.create|every request the client')),
        ('no version', lacks(r'\bSince\b')),
    ],
    'limit-option': [
        ('header', header('maxHeaderSize', 'size')),
        ('built-in limit', has(r'64 ?KiB|65536')),
        ('no constant', lacks(r'DEFAULT_MAX_HEADER_SIZE', 0)),
        ('binary suffix', has(r'binary|1024')),
        ('literal error', has(r'response headers exceed maxHeaderSize of')),
        ('interaction', has(r'strictParsing')),
        ('when to change', has(r'cookie|token')),
        ('no version', lacks(r'\bSince\b')),
    ],
}


def main():
    case_dir = sys.argv[1].rstrip('/')
    checks = CASES[os.path.basename(case_dir)]
    for path in sorted(glob.glob(f'{case_dir}/*/result*.md') + glob.glob(f'{case_dir}/*/baseline/result*.md')):
        text = open(path).read()
        for name, check in checks:
            ok, evidence = check(text)
            print(f"{'PASS' if ok else 'FAIL'}  {os.path.relpath(path, case_dir)}  {name}: {evidence}")


main()
