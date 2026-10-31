"""Grades the markers a script can count in the results of a telemetry-authoring case.

Usage, from the repository root:
    python3 research/telemetry-authoring/cases/check.py <case directory> [<result.md> ...]

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


def words(text):
    return len(re.findall(r'\S+', text))


def message(text):
    """The message itself: the result without a code fence, Java concatenation, or a tool prefix."""
    text = re.sub(r'^```\w*$', '', text, flags=re.M)
    return ' '.join(re.findall(r'"((?:[^"\\]|\\.)*)"', text)) or text.strip()


def result(ok, evidence):
    return ('PASS' if ok else 'FAIL', evidence)


def message_at_most(limit):
    def check(text):
        n = words(message(text))
        return result(n <= limit, f'{n} words in the message, limit {limit}')
    check.__name__ = f'message_at_most_{limit}_words'
    return check


def at_most(limit):
    def check(text):
        n = words(text)
        return result(n <= limit, f'{n} words, limit {limit}')
    check.__name__ = f'at_most_{limit}_words'
    return check


def one_sentence(text):
    found = re.findall(r'[.;!?](?=\s+\S)', message(text))
    return result(not found, f'{len(found) + 1} sentences')


def contains(name, *needles):
    def check(text):
        missing = [n for n in needles if n not in text]
        return result(not missing, f'missing {missing}' if missing else f'has {list(needles)}')
    check.__name__ = name
    return check


def lacks(name, pattern):
    def check(text):
        found = re.findall(pattern, text, re.I)
        return result(not found, f'found {found[:3]}' if found else 'absent')
    check.__name__ = name
    return check


def read(name):
    def check(text):
        return ('READ', 'grade by reading')
    check.__name__ = name
    return check


def no_apostrophe(text):
    return result("'" not in message(text), 'apostrophe' if "'" in message(text) else 'none')


CASES = {
    'error-negative-timeout': [
        contains('names_parameter_and_value', 'connectTimeout', 'millis'),
        one_sentence,
        message_at_most(15),
    ],
    'cli-rejects-argument': [
        contains('names_flag_and_value', '--jobs', '%d'),
        one_sentence,
        message_at_most(15),
    ],
    'limit-max-result-buffer': [
        contains('placeholders_kept', '{0', '{1'),
        no_apostrophe,
        lacks('why_the_limit', r'^(?!.*memory)'),
        contains('names_the_property', 'maxResultBuffer'),
        read('value_form'),
        lacks('alternative_to_raising', r'^(?!.*(fetch ?size|fewer rows))'),
        read('connection_closed'),
        read('no_wrong_advice'),
        read('length'),
    ],
    'build-check-release-jars': [
        read('why_the_check'),
        contains('names_the_module', 'org.example:foo'),
        contains('diagnose_command_filled_in', '--dependency org.example:foo'),
        contains('limit_with_its_file', 'total-size-limit', 'expected_release_artifacts.txt'),
        contains('accept_command', ':src:dist:verifyReleaseDependencies -PupdateExpectedJars'),
        read('not_intended_path'),
        read('what_to_report'),
        read('nothing_invented'),
    ],
    'review-retry-loop': [
        read('log_and_throw_named'),
        read('per_attempt_warn_named'),
        lacks('no_stack_line_proposal', r'AGENTS\.md'),
        lacks('no_per_item_none', r'(?m)^\s*[-|].{0,20}\b(none|nothing to report)\b'),
        read('no_new_instrument'),
        read('no_rows_for_a_private_constant'),
        at_most(500),
    ],
}


def main():
    case = os.path.normpath(sys.argv[1])
    checks = CASES[os.path.basename(case)]
    paths = sys.argv[2:] or sorted(glob.glob(f'{case}/*/result*.md') + glob.glob(f'{case}/*/baseline/*.md'))
    for path in paths:
        text = open(path).read()
        for check in checks:
            verdict, evidence = check(text)
            print(f'{os.path.relpath(path, case)}\t{check.__name__}\t{verdict}\t{evidence}')


if __name__ == '__main__':
    main()
