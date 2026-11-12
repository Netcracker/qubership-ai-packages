"""Grades the markers a script can count in the results of a russian-developer-style case.

Usage, from the repository root:
    python3 research/russian-developer-style/cases/check.py <case directory> [<result.md> ...]

Without result paths, it grades every result of the case: <model>/result*.md and <model>/baseline/*.md. It prints
one line per result and check: PASS or FAIL with the evidence it found. The verdict is the script's reading of a
marker (found, or absent), not a grade: the case README says to grade every check by reading the result.

The checks of a case are the functions registered under its directory name in CASES; each takes the text of a
result and returns (verdict, evidence).
"""

import glob
import os
import re
import sys


def body(text):
    """The result without a surrounding code fence."""
    lines = [line for line in text.strip().splitlines() if not line.startswith('```')]
    return '\n'.join(lines).strip()


def words(text):
    return len(re.findall(r'\S+', body(text)))


def result(ok, evidence):
    return ('PASS' if ok else 'FAIL', evidence)


def word_limit(limit):
    def check(text):
        n = words(text)
        return result(n <= limit, f'{n} words, limit {limit}')
    check.__name__ = f'at_most_{limit}_words'
    return check


def absent(name, pattern):
    regex = re.compile(pattern, re.I)

    def check(text):
        found = regex.findall(body(text))
        return result(not found, f'found: {found}' if found else 'none')
    check.__name__ = name
    return check


def present(name, pattern):
    regex = re.compile(pattern, re.I)

    def check(text):
        found = regex.findall(body(text))
        return result(bool(found), f'found: {found}' if found else 'none')
    check.__name__ = name
    return check


def comment_limit(limit):
    def check(text):
        comment = [line.lstrip('/ ') for line in body(text).splitlines() if line.lstrip().startswith('//')]
        n = len(re.findall(r'\S+', ' '.join(comment)))
        return result(n <= limit, f'{n} comment words, limit {limit}')
    check.__name__ = f'comment_at_most_{limit}_words'
    return check


def one_sentence(text):
    """Counts the sentences, with or without a final period.

    >>> one_sentence('Первое предложение. Второе предложение.')[0]
    'FAIL'
    >>> one_sentence('Первое предложение. Второе предложение')[0]
    'FAIL'
    >>> one_sentence('Размер выборки должен быть не меньше 0, получено {0}.')[0]
    'PASS'
    >>> one_sentence('Размер выборки должен быть не меньше 0, получено {0}')[0]
    'PASS'
    """
    sentences = [s for s in re.split(r'[.!?]+(?:\s+|$)', body(text)) if s.strip()]
    return result(len(sentences) <= 1, f'{len(sentences)} sentences')


def one_line(text):
    lines = [line for line in body(text).splitlines() if line.strip()]
    return result(len(lines) == 1, f'{len(lines)} non-empty lines')


def has_body(text):
    parts = re.split(r'\n\s*\n', body(text), maxsplit=1)
    return result(len(parts) == 2 and parts[1].strip() != '', 'body found' if len(parts) == 2 else 'subject only')


ACTION = r'\b(укажите|задайте|передайте|используйте|введите|подставьте)\b'
CREATE = r'\b(создайте|добавьте|настройте)\b'

CASES = {
    'error-negative-fetch-size': [
        absent('no_action', ACTION),
        absent('no_failed_operation', r'не удалось'),
        one_sentence,
        word_limit(12),
        present('placeholder_kept', r'\{0\}'),
    ],
    'error-config-unreadable': [
        present('names_file', r'/etc/foo/config\.yaml'),
        present('gives_action', r'FOO_CONFIG'),
    ],
    'empty-mentions': [
        absent('no_create_action', CREATE),
        word_limit(20),
    ],
    'empty-alert-rules': [
        present('gives_action', r'\bсоздайте\b'),
    ],
    'commit-typo': [
        one_line,
        word_limit(10),
    ],
    'commit-stale-token': [
        has_body,
        present('names_cause', r'стар'),
    ],
    'docstring-len': [
        comment_limit(15),
        absent('no_param_or_result_section', r'(возвращаемое значение|параметр|returns?:)'),
    ],
    'docstring-parse-port': [
        present('names_error', r'ErrPortRange'),
        present('names_range', r'65535'),
    ],
    'pr-dependency-bump': [
        word_limit(40),
        absent('no_how_to_test', r'как провер|проверка:'),
        absent('no_risks', r'\bриск'),
    ],
}


def main():
    case_dir = sys.argv[1].rstrip('/')
    checks = CASES[os.path.basename(case_dir)]
    paths = sys.argv[2:] or sorted(glob.glob(f'{case_dir}/*/result*.md') + glob.glob(f'{case_dir}/*/baseline/*.md'))
    for path in paths:
        text = open(path).read()
        for check in checks:
            verdict, evidence = check(text)
            print(f'{verdict}  {os.path.relpath(path, case_dir)}  {check.__name__}: {evidence}')


if __name__ == '__main__':
    main()
