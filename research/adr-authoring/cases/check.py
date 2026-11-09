"""Grades the markers a script can count in the results of an adr-authoring case.

Usage, from the repository root:
    python3 research/adr-authoring/cases/check.py <case directory> [<result.md> ...]

Without result paths, it grades every result of the case: <model>/result*.md, <model>/baseline/*.md, and
controls/*.md. It prints one line per result and check: PASS or FAIL, with the evidence it found. A PASS is a marker
found, not a grade: the case README says to grade every check by reading the result.

The checks of a case are the functions registered under its directory name in CASES; each takes the text of a result
and returns (verdict, evidence).
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = ('conforms', 'violates', 'deferred', 'not touched', 'cannot tell')
FILE = re.compile(r'^#{2,4}\s*File:\s*`?([^`\n]+?)`?\s*\n+(`{3,}|~{3,})[^\n]*\n(.*?)^\2[ \t]*$', re.S | re.M)


def result(ok, evidence):
    return ('PASS' if ok else 'FAIL', evidence)


def outside_fences(text):
    """Each line of the text with a flag that says whether it sits outside every fenced block."""
    fence = None
    for line in text.split('\n'):
        m = re.match(r'^(`{3,}|~{3,})', line)
        if m and (fence is None or (m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence)
                                    and not line[len(m.group(1)):].strip())):
            yield line, False
            fence = None if fence else m.group(1)
            continue
        yield line, fence is None


def section(text, title):
    """The text under a `## <title>` heading, up to the next `## ` heading outside a fenced block."""
    out, inside = [], False
    for line, outside in outside_fences(text):
        if outside and re.match(r'^##\s', line):
            if inside:
                break
            inside = re.match(r'^##\s+' + re.escape(title) + r'\b', line) is not None
            continue
        if inside:
            out.append(line)
    return '\n'.join(out)


def verdicts(text):
    """Each rule a table row names, as `ADR-NNNN Rn`, mapped to the verdict in the cell after it."""
    out = {}
    for line in text.split('\n'):
        if not line.lstrip().startswith('|'):
            continue
        cells = [c.strip().strip('*`').strip() for c in line.strip().strip('|').split('|')]
        for i, cell in enumerate(cells[:-1]):
            m = re.search(r'ADR-(\d{4})\s+(R\d+)', cell)
            if m:
                verdict = cells[i + 1].lower().strip('*` ')
                key = f'ADR-{m.group(1)} {m.group(2)}'
                out.setdefault(key, next((v for v in VERDICTS if verdict.startswith(v)), verdict))
                break
    return out


def verdict_is(title, rule, expected):
    def check(text):
        body = section(text, title) if title else text
        got = verdicts(body).get(rule)
        return result(got == expected, f'{rule} in "{title or "the result"}": {got}')
    check.__name__ = f'{(title or "change").lower().replace(" ", "_")}_{rule.split()[1].lower()}_{expected.replace(" ", "_")}'
    return check


def verdict_not_in(title, rule, forbidden):
    def check(text):
        body = section(text, title) if title else text
        got = verdicts(body).get(rule)
        return result(got not in forbidden, f'{rule} in "{title or "the result"}": {got}')
    check.__name__ = f'{(title or "change").lower().replace(" ", "_")}_{rule.split()[1].lower()}_not_{"_or_".join(f.replace(" ", "_") for f in forbidden)}'
    return check


def deferral_named(title, marker):
    def check(text):
        body = section(text, title)
        found = re.search(marker, body)
        return result(found is not None, found.group(0) if found else f'no deferral named in "{title}"')
    check.__name__ = f'{title.lower().replace(" ", "_")}_names_the_deferral'
    return check


def files(text):
    return [(m.group(1).strip(), m.group(3)) for m in FILE.finditer(text)]


def message(text):
    m = re.search(r'^#{2,4}\s*Message to the user[^\n]*\n(.*?)(?=^##\s|^#{2,4}\s*File:|\Z)', text, re.S | re.M)
    return m.group(1) if m else ''


NEGATION = re.compile(r"\b(?:no|not|never|nothing)\b|n.t\b", re.I)


def affirmed(pattern, text):
    """The first sentence of the text that matches the pattern and carries no negation."""
    for sentence in re.split(r'(?<=[.!?])\s+|\n', text):
        if re.search(pattern, sentence, re.I) and not NEGATION.search(sentence):
            return sentence
    return None


def records(fs, number=None):
    """The record files among the files: docs/adr or docs/decisions, a numbered name, not the README."""
    pat = r'docs/(?:adr|decisions)/(\d{4})-[^/]*\.md$'
    return [(p, c) for p, c in fs if re.search(pat, p) and (number is None or re.search(pat, p).group(1) == number)]


def heading_block(content, name):
    m = re.search(r'^#{2,4}\s*' + re.escape(name) + r'\s*\n(.*?)(?=^#{1,4}\s|\Z)', content, re.S | re.M)
    return m.group(1) if m else ''


# writer-vague-notes

COUNT = r'(?:\d+|one|two|three|four|five|six)'
NUMBERED_RETRIES = re.compile(r'\b' + COUNT + r'\s+(?:(?:more|further|additional|extra)\s+)?(?:retr\w*|attempts?|tries|times)\b'
                              r'|\b(?:retr\w*|attempts?)\s+(?:(?:up to|at most)\s+)?' + COUNT
                              + r'\b(?!\s*(?:seconds?|s|ms)\b)', re.I)


def vague_record(text):
    recs = records(files(text))
    return recs[0][1] if recs else ''


def record_0001(text):
    recs = records(files(text), '0001')
    return result(bool(recs), recs[0][0] if recs else f'record files: {[p for p, _ in records(files(text))]}')


def guide_added(text):
    found = [p for p, _ in files(text) if re.search(r'docs/(?:adr|decisions)/README\.md$', p)]
    return result(bool(found), found[0] if found else 'no README.md beside the records')


def retry_placeholder(text):
    rec = vague_record(text)
    rules = heading_block(rec, 'Rules') or rec
    lines = [ln for ln in rules.split('\n') if re.search(r'retr', ln, re.I)]
    holder = [ln for ln in lines if re.search(r'<[^>\n]+>', ln)]
    invented = next((m for ln in lines for m in [NUMBERED_RETRIES.search(re.sub(r'`?<[^>\n]*>`?', '', ln))] if m),
                    None)
    ok = bool(holder) and invented is None
    return result(ok, (f'invented count: {invented.group(0)}' if invented else
                       (holder[0].strip()[:110] if holder else 'no placeholder on a retry line')))


def retry_open_point(text):
    block = heading_block(vague_record(text), 'Open points')
    found = re.search(r'[^\n]*retr[^\n]*', block, re.I)
    return result(found is not None, found.group(0).strip()[:110] if found else 'no open point asks for the retries')


def timeout_kept(text):
    rec = vague_record(text)
    kept = re.search(r'\b5\s*(?:seconds|s)\b|\b5000\s*ms\b', rec)
    holder = re.search(r'<[^>\n]*time[^>\n]*>', rec, re.I)
    return result(kept is not None and holder is None,
                  'timeout placeholder: ' + holder.group(0) if holder else (kept.group(0) if kept else 'no 5 seconds'))


def owner_not_invented(text):
    block = heading_block(vague_record(text), 'Owner')
    handle = re.search(r'@[\w-]+', block)
    holder = re.search(r'<[^>\n]+>|\bTBD\b|not (?:yet )?(?:assigned|settled|decided)', block, re.I)
    asked = re.search(r'owner', message(text), re.I)
    ok = handle is None and holder is not None and asked is not None
    return result(ok, f'owner: {block.strip()[:60]!r}' + ('' if asked else '; the message does not ask for an owner'))


def user_told_guide(text):
    found = re.search(r'README|reading guide', message(text))
    return result(found is not None, found.group(0) if found else 'the message does not mention the guide')


def status_proposed(text):
    block = heading_block(vague_record(text), 'Status')
    return result('Proposed' in block, block.strip()[:40] or 'no Status section')


# writer-accepted-record

def original_0007():
    prompt = open(os.path.join(HERE, 'writer-accepted-record', 'prompt.md'), encoding='utf-8').read()
    return re.search(r'^````markdown\n(.*?)^````', prompt, re.S | re.M).group(1)


def norm(text):
    return '\n'.join(line.rstrip() for line in text.strip().split('\n'))


def new_record_0008(text):
    recs = records(files(section(text, 'Request 1')), '0008')
    ok = bool(recs) and 'TOKEN_ALG_NONE' in recs[0][1] and 'ADR-0007' in recs[0][1]
    return result(ok, recs[0][0] if recs else 'no record 0008 in Request 1')


def accepted_untouched(text):
    recs = records(files(section(text, 'Request 1')), '0007')
    if not recs:
        return result(True, 'ADR-0007 not given in Request 1')
    same = norm(recs[0][1]) == norm(original_0007())
    return result(same, 'ADR-0007 unchanged' if same else 'ADR-0007 edited in Request 1')


def user_told_unchanged(text):
    if accepted_untouched(text)[0] == 'FAIL':
        return result(False, 'ADR-0007 edited in Request 1')
    found = re.search(r'[^.\n]*(?:stays|unchanged|untouched|as it is|not (?:edit|change|modif)|n.t (?:edit|change)|is final|'
                      r'cannot be edited)[^.\n]*', message(section(text, 'Request 1')), re.I)
    return result(found is not None, found.group(0).strip()[:110] if found else 'no word that ADR-0007 stays as it is')


def only_link_fixed(text):
    recs = records(files(section(text, 'Request 2')), '0007')
    if not recs:
        return result(False, 'no ADR-0007 in Request 2')
    expected = norm(original_0007().replace('(0006-key-sources.md)', '(0006-trusted-key-sources.md)'))
    got = norm(recs[0][1])
    if got == expected:
        return result(True, 'only the link changed')
    diff = [b for a, b in zip(expected.split('\n'), got.split('\n')) if a != b]
    return result(False, f'other lines changed: {diff[:1] or "length differs"}')


def no_new_record_r2(text):
    others = [p for p, _ in records(files(section(text, 'Request 2'))) if not re.search(r'/0007-', p)]
    return result(not others, 'no new record' if not others else f'new records: {others}')


# writer-two-decisions

SPLIT = re.compile(r'[^.\n]*(?:(?:separate|own|second|another|two)\s+(?:records?|ADRs?)|second one)[^.\n]*'
                   r'|[^.\n]*\bsplit\b[^.\n]*', re.I)


def r1_at_most_one_record(text):
    recs = records(files(section(text, 'Request 1')))
    return result(len(recs) <= 1, f'{len(recs)} record file(s): {[p for p, _ in recs]}')


def r1_split_proposed(text):
    found = affirmed(SPLIT.pattern, message(section(text, 'Request 1')))
    return result(found is not None, found.strip()[:110] if found else 'no split proposed')


def r2_one_record(text):
    recs = records(files(section(text, 'Request 2')))
    return result(len(recs) == 1, f'{len(recs)} record file(s): {[p for p, _ in recs]}')


def r2_no_split(text):
    found = re.search(r'[^.\n]*(?:propose|suggest|recommend|should|could|want)[^.\n]{0,80}(?:separate|own|second|'
                      r'another)\s+(?:record|ADR)[^.\n]*|[^.\n]*\bsplit (?:it|this|them|the)\b[^.\n]*',
                      message(section(text, 'Request 2')), re.I)
    return result(found is None, f'split proposed: {found.group(0).strip()[:110]}' if found else 'no split proposed')


def no_guide_written(text):
    found = [p for p, _ in files(text) if re.search(r'README\.md$', p)]
    return result(not found, f'guide written: {found}' if found else 'no guide written')


CASES = {
    'checker-partial-delivery': [verdict_is('Change A', 'ADR-0007 R5', 'violates'),
                                 verdict_is('Change B', 'ADR-0007 R5', 'conforms'),
                                 deferral_named('Change B', r'[^\n]*(?:#12|[Dd]efer)[^\n]*'),
                                 verdict_not_in('Change A', 'ADR-0007 R4', ('violates', 'cannot tell', 'conforms')),
                                 verdict_not_in('Change B', 'ADR-0007 R4', ('violates', 'cannot tell', 'conforms'))],
    'checker-open-point': [verdict_is('Change A', 'ADR-0007 R4', 'violates'),
                           verdict_is('Change B', 'ADR-0007 R4', 'cannot tell'),
                           verdict_not_in('Change A', 'ADR-0007 R5', ('violates', 'cannot tell', 'conforms')),
                           verdict_not_in('Change B', 'ADR-0007 R5', ('violates', 'cannot tell', 'conforms'))],
    'checker-proposed-replacement': [verdict_is('Change', 'ADR-0010 R7', 'violates'),
                                     verdict_is('Change', 'ADR-0010 R9', 'deferred'),
                                     verdict_not_in(None, 'ADR-0020 R3', VERDICTS)],
    'writer-vague-notes': [record_0001, guide_added, retry_placeholder, retry_open_point, timeout_kept,
                           owner_not_invented, user_told_guide, status_proposed],
    'writer-accepted-record': [new_record_0008, accepted_untouched, user_told_unchanged, only_link_fixed,
                               no_new_record_r2, no_guide_written],
    'writer-two-decisions': [r1_at_most_one_record, r1_split_proposed, r2_one_record, r2_no_split, no_guide_written],
}


def main():
    case_dir = sys.argv[1].rstrip('/')
    name = os.path.basename(case_dir)
    if name not in CASES:
        sys.exit(f'no checks registered for {name}')
    paths = sys.argv[2:] or sorted(glob.glob(f'{case_dir}/*/result*.md') + glob.glob(f'{case_dir}/*/baseline/*.md')
                                   + glob.glob(f'{case_dir}/controls/*.md'))
    for path in paths:
        text = open(path, encoding='utf-8').read()
        print(os.path.relpath(path, case_dir))
        for check in CASES[name]:
            verdict, evidence = check(text)
            print(f'  {verdict:4} {check.__name__}: {evidence}')


if __name__ == '__main__':
    main()
