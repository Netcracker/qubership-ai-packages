"""Grades the markers a script can count in the results of an english-developer-style case.

Usage, from the repository root:
    python3 research/english-developer-style/cases/check.py <case directory> [<result.md> ...]

Without result paths, it grades every result of the case: <model>/result*.md and <model>/baseline/*.md. It prints
one line per result and check: PASS, FAIL, or READ, with the evidence it found. A PASS is a marker found, not a
grade: the case README says to grade every check by reading the result. READ marks a check the script leaves to the
reader.

The checks of a case are the functions registered under its directory name in CASES; each takes the text of a
result and returns (verdict, evidence).
"""

import glob
import os
import re
import sys

HEADING = re.compile(r'^#{1,6} (.*)$', re.M)
QUOTE = re.compile(r'^> ?(.*)$', re.M)


def words(text):
    return len(re.findall(r'\S+', text))


def result(ok, evidence):
    return ('PASS' if ok else 'FAIL', evidence)


def word_limit(limit):
    def check(text):
        n = words(text)
        return result(n <= limit, f'{n} words, limit {limit}')
    check.__name__ = f'at_most_{limit}_words'
    return check


def no_heading(text):
    found = HEADING.findall(text)
    return result(not found, f'headings: {found}')


def no_quote(text):
    found = QUOTE.findall(text)
    return result(not found, f'quoted lines: {found}')


def names_commit(text):
    return result('3f9c2ab' in text, 'names 3f9c2ab' if '3f9c2ab' in text else 'no 3f9c2ab')


REVIEW = ('Thanks, a few things. The test duplicates what `StatementTest.testSetFetchSize` already checks, so I would '
          'rather extend that one than add a new class. Throwing here could break applications that call '
          '`setFetchSize(-1)` to mean "fetch everything", which the old code silently allowed. And should '
          '`PgPreparedStatement` get the same check, or does it inherit it?')
POINTS = ('The test duplicates', 'Throwing here could break', 'And should `PgPreparedStatement`')


def heading_per_point(text):
    found = HEADING.findall(text)
    return result(len(found) == len(POINTS), f'headings: {found}')


def each_point_quoted_in_order(text):
    """Every point opens with a quote of the reviewer's sentence, in the reviewer's order."""
    positions = []
    for start in POINTS:
        m = re.search(r'^> ?' + re.escape(start), text, re.M)
        positions.append(m.start() if m else -1)
    ok = -1 not in positions and positions == sorted(positions)
    return result(ok, f'quote positions: {positions}')


def quotes_verbatim(text):
    """Every quoted line is a substring of the review comment, so nothing was paraphrased."""
    bad = [q for q in QUOTE.findall(text) if q.strip() and q.strip() not in REVIEW]
    return result(not bad, f'not in the comment: {bad}' if bad else 'every quoted line is in the comment')


def no_count_of_points(text):
    m = re.search(r'\b(two|three|four|both|all three) (points|questions|things|concerns|comments)\b', text, re.I)
    return result(not m, f'count: {m.group(0)!r}' if m else 'no count of the points')


def concedes_before_dispute(text):
    return ('READ', 'does the setFetchSize(-1) section say first that the old code allowed it?')


def asks_test_decision(text):
    return ('READ', 'does the test section ask whether to add the negative case to StatementTest too?')


def one_sentence(text):
    body = text.strip().strip('`')
    n = len(re.findall(r'[.!?](\s|$)', body))
    return result(n <= 1, f'{n} sentence ends in {body!r}')


def placeholder_kept(text):
    return result('{0' in text, 'has {0}' if '{0' in text else 'no {0} placeholder')


def no_apostrophe(text):
    """A single quote in a MessageFormat pattern turns the placeholders after it into literals."""
    body = text.strip().strip('`')
    return result("'" not in body, 'apostrophe found' if "'" in body else 'no apostrophe')


def names_file_and_reason(text):
    ok = '/etc/foo.yaml' in text and re.search(r'permission denied', text, re.I)
    return result(bool(ok), 'path and reason named' if ok else 'path or reason missing')


def gives_action(text):
    m = re.search(r'FOO_CONFIG|group\W{0,2}foo|foo\W{0,2}group', text)
    return result(bool(m), f'action marker {m.group(0)!r}' if m else 'no FOO_CONFIG and no group foo')


def no_consequence(text):
    """Execution stops at this message, so it carries no consequence."""
    m = re.search(r'\bexit|no default|will not start|cannot continue|stopp', text, re.I)
    return result(not m, f'consequence: {m.group(0)!r}' if m else 'no consequence clause')


CASES = {
    'review-nit-fixed': [word_limit(15), no_heading, no_quote, names_commit],
    'review-three-points': [heading_per_point, each_point_quoted_in_order, quotes_verbatim, no_count_of_points,
                            concedes_before_dispute, asks_test_decision, word_limit(400)],
    'error-negative-fetch-size': [one_sentence, word_limit(12), placeholder_kept, no_apostrophe],
    'error-config-unreadable': [names_file_and_reason, gives_action, no_consequence, word_limit(40)],
}


def main():
    case_dir = sys.argv[1].rstrip('/')
    checks = CASES[os.path.basename(case_dir)]
    paths = sys.argv[2:] or sorted(glob.glob(f'{case_dir}/*/result*.md') +
                                   glob.glob(f'{case_dir}/*/baseline/result*.md'))
    for path in paths:
        text = open(path).read()
        for check in checks:
            verdict, evidence = check(text)
            print(f'{verdict:4} {os.path.relpath(path, case_dir)} {check.__name__}: {evidence}')


if __name__ == '__main__':
    main()
