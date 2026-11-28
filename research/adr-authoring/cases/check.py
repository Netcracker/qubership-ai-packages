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


def would_violate(rule):
    def check(text):
        found = re.search(r'[^\n]*would violate[^\n]*' + re.escape(rule) + r'[^\n]*|[^\n]*' + re.escape(rule)
                          + r'[^\n]*would violate[^\n]*', text, re.I)
        return result(found is not None, found.group(0).strip()[:110] if found else f'no "would violate {rule}" line')
    check.__name__ = f'would_violate_{rule.split()[0].lower().replace("-", "")}_{rule.split()[1].lower()}'
    return check


def no_trailer_error(rule):
    def check(text):
        """The rule on a line that names a trailer error, or in the list items under a "Trailer errors:" label."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if not re.search(r'trailer errors?', line, re.I):
                continue
            if re.search(r'trailer errors?\W*(?:none|no\b|nothing)|\b(?:no|none|not)\b[^\n]*trailer error', line, re.I):
                continue
            items = [line]
            if re.search(r'trailer errors?\W*:?\W*$', line, re.I):
                for nxt in lines[i + 1:]:
                    if not nxt.strip() and items[1:]:
                        break
                    if nxt.strip() and not re.match(r'\s*(?:[-*]|\d+\.)\s', nxt):
                        break
                    items.append(nxt)
            if any(rule in item for item in items):
                return result(False, f'listed as an error: {" ".join(" ".join(items).split())[:100]}')
        return result(True, 'not an error')
    check.__name__ = f'no_trailer_error_{rule.split()[0].lower().replace("-", "")}_{rule.split()[1].lower()}'
    return check


def old_violation_named(title, marker):
    def check(text):
        body = section(text, title)
        rows = '\n'.join(ln for ln in body.split('\n') if not ln.lstrip().startswith('|'))
        found = re.search(r'[^\n]*(?:' + marker + r')[^\n]*', rows)
        return result(found is not None, found.group(0).strip()[:110] if found else f'no word of the older violation in "{title}"')
    check.__name__ = f'{title.lower().replace(" ", "_")}_names_the_older_violation'
    return check


def no_advisory_for(rule):
    def check(text):
        found = re.search(r'[^\n]*would violate[^\n]*' + re.escape(rule) + r'[^\n]*', text, re.I)
        return result(found is None, f'advisory for a binding rule: {found.group(0).strip()[:100]}' if found else 'no advisory line')
    check.__name__ = f'no_advisory_{rule.split()[0].lower().replace("-", "")}_{rule.split()[1].lower()}'
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


def section_span(content, name):
    """The offsets of the section headed `name`, its heading line included, up to the next heading of the same or a
    higher level, or None. A heading inside a fenced block neither starts nor ends the section."""
    start = level = None
    pos = 0
    for line, outside in outside_fences(content):
        if outside and level is None:
            m = re.match(r'^(#{1,6})\s*' + re.escape(name) + r'\s*$', line)
            if m:
                start, level = pos, len(m.group(1))
        elif outside:
            m = re.match(r'^(#{1,6})\s', line)
            if m and len(m.group(1)) <= level:
                return start, pos
        pos += len(line) + 1
    return (start, len(content)) if level is not None else None


def section_block(content, name):
    """The section headed `name`, as `section_span` finds it, or '' where the content has no such heading."""
    span = section_span(content, name)
    return content[span[0]:span[1]] if span else ''


def without_section(content, name):
    """The content with the section headed `name` taken out."""
    span = section_span(content, name)
    return content[:span[0]] + content[span[1]:] if span else content


BLOCK_START = re.compile(r'^\s{0,3}#{1,6}\s|^\s*[-*+]\s|^\s*\|')
ORDERED_START = re.compile(r'^(\s*)(\d+)[.)]\s')


def blocks(text):
    """The Markdown blocks of the text, each with its lines joined: a paragraph, a heading, a list item, a table row,
    or a line of a fenced block.

    A line that starts with a number and a period continues the open block unless the number is 1, which CommonMark
    lets interrupt a paragraph, or the open block began with such a marker at the same indentation, as the next item
    of an ordered list. Other indentation rules of CommonMark are not modeled.
    """
    out, lines = [], []
    for line, outside in outside_fences(text):
        ordered = ORDERED_START.match(line)
        first = ORDERED_START.match(lines[0]) if lines else None
        item = ordered and (int(ordered.group(2)) == 1 or (first and first.group(1) == ordered.group(1)))
        if lines and (not outside or not line.strip() or BLOCK_START.match(line) or item):
            out.append(' '.join(' '.join(lines).split()))
            lines = []
        if not outside:
            out += [' '.join(line.split())] if line.strip() else []
        elif line.strip():
            lines.append(line)
            if re.match(r'^\s{0,3}#{1,6}\s', line):
                out.append(' '.join(line.split()))
                lines = []
    if lines:
        out.append(' '.join(' '.join(lines).split()))
    return out


def sentences(text, ends='.;'):
    """The sentences of the text, split after a character of `ends` inside each Markdown block, so that no sentence
    runs from one block into the next."""
    return [s for b in blocks(text) for s in re.split(r'(?<=[' + re.escape(ends) + r'])\s+', b) if s]


def excerpt(text, start, end, width=100):
    """The text from `start` to `end` whole, in a window of about `width` characters, or the match alone where it is
    longer, with whitespace collapsed and "..." where the window cuts the text."""
    span = max(width, end - start)
    a = max(0, min(start - (span - (end - start)) // 2, len(text) - span))
    b = max(end, min(len(text), a + span))
    return ('...' if a else '') + ' '.join(text[a:b].split()) + ('...' if b < len(text) else '')


# writer-vague-notes

RULE_LINE = re.compile(r'^\s*[-*]\s*\*\*R(\d+)\*\*\s*\(([^)]*)\)\.?\s*(.*(?:\n(?![ \t]*(?:[-*]|\d+\.)\s)[ \t]+\S.*)*)', re.M)

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


def guide_not_added(text):
    found = [p for p, _ in files(text) if re.search(r'(?:^|/)(?:README|AGENTS)\.md$', p)]
    return result(not found, f'written before the user agreed: {found}' if found else 'no guide and no AGENTS.md change')


def retry_placeholder(text):
    rec = vague_record(text)
    lines = [' '.join(body.split()) for _, _, body in RULE_LINE.findall(rec) if re.search(r'retr', body, re.I)]
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


def guide_asked(text):
    """A question in the message that offers the guide and names the trailers it commits the team to."""
    sentences = re.split(r'(?<=[.!?])\s+|\n(?=\S)', message(text))
    for i, sentence in enumerate(sentences):
        window = ' '.join(sentences[max(0, i - 1):i + 3])
        if '?' in sentence and re.search(r'README|guide', window) and re.search(r'trailer|Implements|Defers', window):
            return result(True, ' '.join(sentence.split())[:110])
    return result(False, 'no question that offers the guide near a mention of the trailers')


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


# writer-structural

def request_file(text, request, pattern):
    found = [(p, c) for p, c in files(section(text, request)) if re.search(pattern, p)]
    return found[0] if found else (None, '')


def record_of(text, request, number):
    recs = records(files(section(text, request)), number)
    return recs[0][1] if recs else ''


def r1_record_0012(text):
    recs = records(files(section(text, 'Request 1')), '0012')
    return result(bool(recs), recs[0][0] if recs else 'no record 0012 in Request 1')


def r1_metadata_from_repository(text):
    rec = record_of(text, 'Request 1', '0012')
    found = re.search(r'^####\s+Owner\b', rec, re.M)
    other = re.search(r'^#{2,3}\s+Owner\b', rec, re.M)
    return result(found is not None, '#### Owner' if found else (f'{other.group(0)!r}' if other else 'no Owner heading'))


def r1_rules_from_template(text):
    rec = record_of(text, 'Request 1', '0012')
    found = re.search(r'^#{2,4}\s+Rules\b', rec, re.M) and RULE_LINE.search(rec)
    return result(bool(found), 'a Rules heading and numbered rules' if found else 'no Rules heading or no numbered rule')


def r1_structural_tag(text):
    """Each rule about the HTTP imports carries a tag that the written guide maps to internal/token/."""
    rec = record_of(text, 'Request 1', '0012')
    _, guide = request_file(text, 'Request 1', r'docs/adr/README\.md$')
    rules = [(n, re.findall(r'`([^`]+)`', tag) or [tag.strip()], body) for n, tag, body in RULE_LINE.findall(rec)
             if re.search(r'internal/http|net/http|HTTP (?:package|import)', body)]
    if not rules:
        return result(False, 'no rule about importing internal/http or net/http')
    for n, tags, _ in rules:
        mapped = [tg for tg in tags if re.search(r'[^\n]*' + re.escape(tg) + r'[^\n]*internal/token', guide)]
        if not mapped:
            return result(False, f'R{n} tagged {tags}, which the guide does not map to internal/token/')
    return result(True, '; '.join(f'R{n} ({", ".join(tags)})' for n, tags, _ in rules))


def r1_confirmation_names_check(text):
    block = heading_block(record_of(text, 'Request 1', '0012'), 'Confirmation')
    return result('token-no-http' in block, 'token-no-http' if 'token-no-http' in block else 'no Confirmation naming token-no-http')


def r1_guide_added(text):
    path, guide = request_file(text, 'Request 1', r'docs/adr/README\.md$')
    ok = path is not None and 'internal/token' in guide and re.search(r'`docs/(?:adr/)?`[^\n]*(?:no layer|none|outside)|'
                                                                      r'(?:no layer|outside)[^\n]*`docs/(?:adr/)?`', guide, re.I)
    return result(bool(ok), path if ok else ('no docs/adr/README.md' if path is None
                                             else 'the guide maps no internal/token/ or lists no docs/adr/ outside'))


def r1_agents_paragraph(text):
    path, agents = request_file(text, 'Request 1', r'(?:^|/)AGENTS\.md$')
    ok = (path is not None and 'docs/adr/README.md' in agents and re.search(r'Implements|trailer', agents)
          and 'go test ./...' in agents and 'internal/token' not in agents)
    return result(bool(ok), path if ok else ('no AGENTS.md change' if path is None
                                             else 'AGENTS.md does not name the guide and the trailers, copies the map, '
                                                  'or lost a line'))


def r2_guide_untouched(text):
    found = [p for p, _ in files(section(text, 'Request 2')) if re.search(r'(?:^|/)(?:README|AGENTS)\.md$', p)]
    return result(not found, f'rewritten in Request 2: {found}' if found else 'guide and AGENTS.md left alone')


def r2_citation_without_condition(text):
    """A sentence of record 0013, outside a link, that says what ADR-0012 requires of the HTTP packages.

    Finding one fails. The subject is the one `r1_structural_tag` reads: `internal/http`, `net/http`, or an HTTP
    package or import. The marker pairs it with any word of prohibition in the sentence, so a sentence that says
    something else about an HTTP package fails as well: a FAIL is a possible copy, graded by reading.
    """
    rec = re.sub(r'\[[^\]]*\]\([^)]*\)', '', record_of(text, 'Request 2', '0013'))
    for sentence in sentences(rec, '.;:'):
        subject = re.search(r'internal/http|net/http|HTTP (?:package|import)', sentence)
        condition = subject and re.search(
            r"\b(?:out of|free of|cannot|can't|can not|must not|may not|not import|never import|forbid\w*"
            r"|bars?|no token package)\b", sentence, re.I)
        if condition:
            return result(False, 'possible copy of the condition of ADR-0012, grade by reading: ' + excerpt(
                sentence, min(subject.start(), condition.start()), max(subject.end(), condition.end())))
    return result(True, 'no condition of ADR-0012 copied')


SUBJECT_BEFORE = re.compile(r'(?<![\w`])(?!(?:the|a|an|this|that|its|their)\b)[\w`/.-]+\s+'
                            r'(?:rule|restriction|requirement|invariant|check|ban|limit)s?'
                            r'(?:\s+(?:of|in)\s+|\s*\(|,\s*)$', re.I)


def r2_citation_names_subject(text):
    """A citation of a rule of ADR-0012 in record 0013 with no subject right before it. Finding one fails.

    The marker reads a noun phrase right before the number: a noun such as rule, restriction, or check with another
    word before it that is not an article or a pronoun, and after it "of", "in", an opening parenthesis, or a comma, as
    in "the import rule of ADR-0012 R1" or "the import rule (ADR-0012 R1)". A subject written after the number passes
    only by reading, so a FAIL is a possible citation without a subject. A link counts by its text, and a record that
    cites no rule of ADR-0012 passes.
    """
    rec = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', record_of(text, 'Request 2', '0013'))
    cited = False
    for sentence in sentences(rec, '.;:'):
        for m in re.finditer(r'ADR-0012 R\d+', sentence):
            cited = True
            if not SUBJECT_BEFORE.search(sentence[:m.start()]):
                return result(False, 'possible citation without its subject, grade by reading: '
                              + excerpt(sentence, m.start(), m.end()))
    return result(True, 'each citation of ADR-0012 names its subject' if cited else 'no rule of ADR-0012 cited')


def r2_behavior_rule(text):
    rec = record_of(text, 'Request 2', '0013')
    found = next((body for _, _, body in RULE_LINE.findall(rec) if '401' in body and 'TOKEN_ALG_NONE' in body), None)
    return result(found is not None, found[:110] if found else 'no rule with HTTP 401 and TOKEN_ALG_NONE in record 0013')


def r2_no_confirmation_entry(text):
    block = heading_block(record_of(text, 'Request 2', '0013'), 'Confirmation')
    entry = re.search(r'^\s*[-*]\s*\*\*R\d+[^\n]*', block, re.M)
    return result(entry is None, f'entry for a check that does not exist: {entry.group(0).strip()[:100]}' if entry
                  else 'no Confirmation entry')


# writer-defect-and-guarantee

def rule_lines(record):
    return [' '.join(body.split()) for _, _, body in RULE_LINE.findall(record)]


def no_rule_on(pattern, what):
    def check(text):
        found = next((ln for ln in rule_lines(record_of(text, 'Request 1', '0007')) if re.search(pattern, ln, re.I)),
                     None)
        return result(found is None, f'rule on {what}: {found[:100]}' if found else f'no rule on {what}')
    check.__name__ = f'r1_no_rule_on_{what.replace(" ", "_")}'
    return check


def r1_bug_proposed(text):
    msg = message(section(text, 'Request 1'))
    ok = re.search(r'\bissue\b', msg, re.I) and re.search(r'\bbug\b', msg, re.I) and re.search(r'entrypoint', msg, re.I)
    found = re.search(r'[^\n]*\bbug\b[^\n]*', msg, re.I)
    return result(bool(ok), found.group(0).strip()[:110] if ok else 'no Bug issue for the entrypoint in the message')


def r1_volumes_with_the_fix(text):
    """A chart volume named in Request 1's message after its first mention of a bug, where the proposed issue starts."""
    msg = message(section(text, 'Request 1'))
    bug = re.search(r'\bbug\b', msg, re.I)
    found = bug and re.search(r'[^\n]*(?:emptyDir|/etc/ssl/certs|ca-certificates)[^\n]*', msg[bug.start():])
    return result(bool(found), found.group(0).strip()[:110] if found else
                  ('no chart volume after the bug' if bug else 'no bug in the message'))


FIX_WORD = r'(?:\bbug\b|\bfix\w*|restor\w*|\buntil\b|\btracked\b|\bremov\w*|\bdrop\w*|\bswitch\w*)'
FIX_SUBJECT = r'(?:entrypoint|Dockerfile|\bCMD\b)'


def r1_record_names_no_fix(text):
    """A line of Request 1's record that names the entrypoint, `CMD`, or the Dockerfile with a bug, its fix, or its tracking."""
    rec = record_of(text, 'Request 1', '0007')
    found = re.search(rf'[^\n]*{FIX_SUBJECT}[^\n]*{FIX_WORD}[^\n]*|[^\n]*{FIX_WORD}[^\n]*{FIX_SUBJECT}[^\n]*', rec, re.I)
    return result(found is None, f'the record names the fix: {found.group(0).strip()[:100]}' if found
                  else 'the record names no issue and no fix')


def r1_no_entrypoint_choice(text):
    block = heading_block(record_of(text, 'Request 1', '0007'), 'Open points')
    point = re.search(r'[^\n]*entrypoint[^\n]*', block, re.I)
    if point:
        return result(False, f'open point: {point.group(0).strip()[:100]}')
    for sentence in re.split(r'(?<=[.!?])\s+|\n', message(section(text, 'Request 1'))):
        if ('?' in sentence and re.search(r'entrypoint', sentence, re.I) and re.search(r'\bor\b', sentence)
                and re.search(r'binary|\bCMD\b|\bkeep', sentence, re.I)):
            return result(False, f'question: {sentence.strip()[:100]}')
    return result(True, 'no open point and no question that offers the entrypoint as a choice')


def r1_guarantee_as_fact(text):
    rec = record_of(text, 'Request 1', '0007')
    if '/tmp/cert' not in rec:
        return result(True, 'the record does not name /tmp/cert')
    context = heading_block(rec, 'Context')
    found = re.search(r'[^\n]*/tmp/cert[^\n]*', context)
    ok = found is not None and re.search(r'base image|platform-base|README|contract', context, re.I)
    return result(bool(ok), found.group(0).strip()[:110] if ok else 'Context names no /tmp/cert with its source')


def rule_with(request, *markers):
    def check(text):
        found = next((ln for ln in rule_lines(record_of(text, request, '0007')) if all(m in ln for m in markers)), None)
        return result(found is not None, found[:110] if found else f'no rule with {" and ".join(markers)}')
    check.__name__ = f'{request.lower().replace("request ", "r")}_rule_{markers[-1].lower().replace(" ", "_")}'
    return check


def no_defect(request):
    """A sentence of the request's message that names a bug or calls something a defect, other than to deny one."""
    def check(text):
        for sentence in re.split(r'(?<=[.!?])\s+|\n', message(section(text, request))):
            if (re.search(r'\bbug\b|\b(?:is|as) a defect\b', sentence, re.I)
                    and not re.search(r'\b(?:no|not (?:treated )?(?:as )?a|neither a)\s+(?:bug|defect)', sentence, re.I)):
                return result(False, f'defect named: {sentence.strip()[:100]}')
        return result(True, 'no bug and no defect named')
    check.__name__ = f'{request.lower().replace("request ", "r")}_no_defect'
    return check


# writer-one-home

def record_0007_in(request):
    def check(text):
        recs = records(files(section(text, request)), '0007')
        return result(bool(recs), recs[0][0] if recs else f'no record 0007 in {request}')
    check.__name__ = f'{request.lower().replace("request ", "r")}_record_0007'
    return check


def service_account_rule(text):
    """The first rule of Request 1's record that makes a service account token an M2M token, or None."""
    return next((ln for ln in rule_lines(record_of(text, 'Request 1', '0007'))
                 if re.search(r'service account', ln, re.I) and 'M2M' in ln
                 and not re.search(r'\bnot (?:an )?M2M', ln)),
                None)


def r1_service_account_m2m(text):
    """A rule of Request 1's record that makes a service account token an M2M token. Finding one passes."""
    found = service_account_rule(text)
    return result(found is not None,
                  found[:110] if found else 'no rule that makes a service account token an M2M token')


def r1_service_account_rule_alone(text):
    """The service account rule of Request 1's record, read for a citation of ADR-0004. Finding one fails."""
    found = service_account_rule(text)
    if found is None:
        return result(False, 'no rule that makes a service account token an M2M token')
    at = found.find('ADR-0004')
    return result(at < 0, 'the rule cites ADR-0004: ' + excerpt(found, at, at + len('ADR-0004')) if at >= 0
                  else 'the rule cites no rule of ADR-0004')


def r2_no_401_copied(text):
    """A sentence of Request 2's record, outside its rules, that gives ADR-0003 R4 or ADR-0004 R3 their HTTP 401.

    Finding one fails. The Rules section is dropped whole, its topic headings included.
    """
    for sentence in sentences(without_section(record_of(text, 'Request 2', '0007'), 'Rules')):
        cited, status = re.search(r'ADR-0003 R4|ADR-0004 R3', sentence), re.search(r'\b401\b', sentence)
        if cited and status:
            return result(False, 'possible copy of the 401 of a cited rule, grade by reading: ' + excerpt(
                sentence, min(cited.start(), status.start()), max(cited.end(), status.end())))
    return result(True, 'no 401 of a cited rule outside the rules')


def cited_records_linked(text):
    """A record that a record 0007 cites but does not link under **Related ADRs**. Finding one fails."""
    missing = []
    for request in ('Request 1', 'Request 2'):
        rec = record_of(text, request, '0007')
        linked = {n for label, _ in re.findall(r'\[([^\]]*)\]\(([^)]*)\)', section_block(rec, 'Related ADRs'))
                  for n in re.findall(r'ADR-(\d{4})', label)}
        cited = set(re.findall(r'ADR-(\d{4})', without_section(rec, 'Related ADRs'))) - {'0007'}
        missing += [f'{request}: ADR-{n} not linked' for n in sorted(cited - linked)]
    return result(not missing, ', '.join(missing) if missing else 'Related ADRs links every cited record')


def not_copied(request, pattern, what):
    """A line of the request's record that copies what a rule of another record decides. Finding one fails."""
    def check(text):
        for line in record_of(text, request, '0007').split('\n'):
            found = re.search(pattern, line, re.I)
            if found:
                return result(False, f'possible copy of the {what}, grade by reading: '
                              + excerpt(line, found.start(), found.end()))
        return result(True, f'no {what} in the record')
    check.__name__ = f'{request.lower().replace("request ", "r")}_no_{what.replace(" ", "_")}'
    return check


def r1_one_tenant_rule(text):
    """The rules of Request 1's record that limit a token that is not M2M to its tenant; one is expected."""
    found = []
    for ln in rule_lines(record_of(text, 'Request 1', '0007')):
        not_m2m, tenant = re.search(r'\bnot (?:an )?M2M', ln), re.search(r'tenant', ln, re.I)
        if not_m2m and tenant:
            found.append(excerpt(ln, min(not_m2m.start(), tenant.start()), max(not_m2m.end(), tenant.end()), 60))
    return result(len(found) == 1, f'{len(found)} rules' + ''.join(f' | {ln}' for ln in found))


def r1_no_legacy_rule(text):
    for ln in rule_lines(record_of(text, 'Request 1', '0007')):
        found = re.search(r'TOKEN_ISSUER_UNKNOWN|\blegacy\b', ln)
        if found:
            return result(False, 'rule on the mode legacy: ' + excerpt(ln, found.start(), found.end()))
    return result(True, 'no rule on the mode legacy')


def r1_other_records_untouched(text):
    others = [p for p, _ in records(files(section(text, 'Request 1'))) if not re.search(r'/0007-', p)]
    return result(not others, f'other records written: {others}' if others else 'only record 0007 written')


EXCEPTION = re.compile(r'\b(?:except\w*|other than|instead of|rather than|unless|apart from|but not'
                       r'|does not (?:cover|apply))\b', re.I)


def r2_exception_kept(text):
    """A rule of Request 2's record that gives HTTP 401 and excepts `TOKEN_KEYS_UNAVAILABLE`. Finding one passes.

    The exception may cite ADR-0005 R2 for the response or name the code alone: the record that holds the response
    states it either way. The marker reads HTTP 401 and the code in one rule, and not whether or which way the rule
    excepts the code: the evidence names the first such rule that also holds a word that excepts, with the word, or the
    first such rule and "no word that excepts", for the reader to grade.
    """
    found = [(n, ' '.join(body.split())) for n, _, body in RULE_LINE.findall(record_of(text, 'Request 2', '0007'))]
    found = [(n, body, EXCEPTION.search(body)) for n, body in found
             if 'TOKEN_KEYS_UNAVAILABLE' in body and re.search(r'\b401\b', body)]
    if not found:
        return result(False, 'no rule with HTTP 401 and TOKEN_KEYS_UNAVAILABLE')
    n, _, word = next((f for f in found if f[2]), found[0])
    return result(True, f'R{n} has HTTP 401, TOKEN_KEYS_UNAVAILABLE, and ' + (f'"{word.group(0)}"' if word else
                  'no word that excepts') + '; grade by reading whether and which way it excepts')


GITLAB_ROUTES = {'-', 'badges', 'blame', 'blob', 'builds', 'commits', 'create', 'create_dir', 'edit', 'files',
                 'find_file', 'new', 'preview', 'raw', 'refs', 'tree', 'update', 'wikis'}


def link_repository(destination):
    """The repository that a link destination leads to, as a lowercased path, or None where the marker cannot tell.

    On github.com it is the first two segments of the path. On gitlab.com the marker takes the leading segment to name
    a group or a user, and the repository runs up to the next segment that GitLab reserves as a one-segment route for
    projects and subgroups, such as `-`, `blob`, or `tree`, or to the end of the path. Any other host, GitHub Pages
    included, names no repository the marker reads. The angle brackets around a destination and a title after it are
    dropped first.
    """
    url = re.match(r'\s*<?([^\s<>]*)', destination).group(1)
    m = re.match(r'https?://(?:www\.)?(github|gitlab)\.com/([^#?]+)', url, re.I)
    if not m:
        return None
    segments = [seg for seg in m.group(2).split('/') if seg]
    if m.group(1).lower() == 'github':
        segments = segments[:2]
    else:
        segments = segments[:next((i for i, seg in enumerate(segments) if i > 0 and seg in GITLAB_ROUTES),
                                  len(segments))]
    return '/'.join(segments).removesuffix('.git').lower() or None


def foreign_record_form(text):
    """A mention of ADR-0012 in a record 0007 that does not carry `example/platform`. Finding one fails.

    A mention in the link of a line under **Related ADRs** passes when the link's URL leads to the repository
    example/platform, or names no repository and the link's label names `example/platform`, as `link_repository`
    reads the URL. Any other mention, a link in the text included, needs `example/platform` right before it.
    """
    cited = False
    for request in ('Request 1', 'Request 2'):
        rec = record_of(text, request, '0007')
        span = section_span(rec, 'Related ADRs')
        links = [(span[0] + lk.start(), span[0] + lk.end(), lk)
                 for lk in re.finditer(r'\[([^\]]*)\]\(([^)]*)\)', rec[span[0]:span[1]])] if span else []
        for m in re.finditer(r'ADR-0012', rec):
            cited = True
            link = next((lk for a, b, lk in links if a <= m.start() < b), None)
            if link is not None:
                repo, shown = link_repository(link.group(2)), ' '.join(link.group(0).split())
                if repo is not None and repo != 'example/platform':
                    return result(False, f'{request}: link to {repo}, not example/platform: {shown}')
                if repo is None and 'example/platform' not in link.group(1):
                    return result(False, f'{request}: link whose URL names no repository that the marker reads and '
                                         f'whose text does not name example/platform: {shown}')
            elif not re.search(r'example/platform\W{0,3}$', rec[max(0, m.start() - 20):m.start()]):
                return result(False, f'{request}: expected "example/platform ADR-0012", the repository before the '
                                     f'number, in: ' + excerpt(rec, m.start(), m.end(), 80))
    return result(True, 'every ADR-0012 carries example/platform' if cited else 'ADR-0012 not cited')


def no_see_also(text):
    """A citation in a record 0007, outside **Related ADRs**, that `see`, `see also`, `cf.`, or `compare` introduces.

    Finding one fails. Such a citation points at a rule and gives no reason the reader needs; a citation that points
    in other words passes the marker and is graded by reading. A link counts by its text.
    """
    for request in ('Request 1', 'Request 2'):
        rec = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', without_section(record_of(text, request, '0007'), 'Related ADRs'))
        for block in blocks(rec):
            m = re.search(r'\b(?:see(?:\s+also)?|cf\.|compare)\s+(?:[^.;]{0,60}?\s)?(?:\S+/\S+\s+)?ADR-\d{4}(?: R\d+)?',
                          block, re.I)
            if m:
                return result(False, f'{request}: possible citation that only points, grade by reading: '
                              + excerpt(block, m.start(), m.end()))
    return result(True, 'no citation introduced by see, see also, cf., or compare')


# coder-trailers

def fenced_after(text, heading):
    m = re.search(r'^#{2,4}\s*' + re.escape(heading) + r'[^\n]*\n+(`{3,}|~{3,})[^\n]*\n(.*?)^\1[ \t]*$', text,
                  re.S | re.M)
    return m.group(2) if m else ''


def trailers(body):
    blocks = [b for b in re.split(r'\n\s*\n', body.strip()) if b.strip()]
    if not blocks:
        return []
    lines = blocks[-1].split('\n')
    return lines if all(re.match(r'^[A-Za-z][\w-]*:\s', ln) for ln in lines) else []


def defers_r5(change, part):
    def check(text):
        body = fenced_after(section(text, change), part)
        tr = trailers(body)
        defers = next((ln for ln in tr if ln.startswith('Defers:')), None)
        claims = next((ln for ln in tr if ln.startswith('Implements:') and 'ADR-0007 R5' in ln), None)
        ok = defers is not None and re.search(r'ADR-0007 R5 to #12\b', defers) and claims is None
        return result(bool(ok), ' | '.join(tr) if tr else f'no trailer paragraph in the {part.lower()}')
    check.__name__ = f'{change.lower().replace(" ", "_")}_{part.lower().replace(" ", "_")}_defers_r5'
    return check


def no_rule_trailers(change):
    def check(text):
        body = section(text, change)
        found = [ln for part in ('Commit message', 'Pull request description')
                 for ln in fenced_after(body, part).split('\n') if re.match(r'^(?:Implements|Defers):', ln)]
        return result(not found, f'rule trailers: {found}' if found else 'no rule trailers')
    check.__name__ = f'{change.lower().replace(" ", "_")}_no_rule_trailers'
    return check


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
                                     verdict_not_in(None, 'ADR-0020 R3', VERDICTS),
                                     would_violate('ADR-0020 R3'),
                                     no_trailer_error('ADR-0020 R3')],
    'checker-structural': [verdict_is('Change A', 'ADR-0012 R1', 'violates'),
                           verdict_not_in('Change A', 'ADR-0012 R2', ('violates', 'cannot tell', 'conforms')),
                           verdict_not_in('Change B', 'ADR-0012 R1', ('violates', 'cannot tell', 'conforms')),
                           verdict_not_in('Change B', 'ADR-0012 R2', ('violates', 'cannot tell', 'conforms')),
                           verdict_is('Change C', 'ADR-0012 R1', 'violates'),
                           verdict_not_in('Change C', 'ADR-0012 R2', ('violates', 'cannot tell', 'conforms')),
                           old_violation_named('Change C', r'internal/http/auth|session\.go')],
    'checker-proposed-binding': [verdict_is('Change A', 'ADR-0007 R5', 'violates'),
                                 verdict_is('Change B', 'ADR-0007 R5', 'conforms'),
                                 deferral_named('Change B', r'[^\n]*(?:#12|[Dd]efer)[^\n]*'),
                                 verdict_not_in('Change A', 'ADR-0007 R4', ('violates', 'cannot tell', 'conforms')),
                                 verdict_not_in('Change B', 'ADR-0007 R4', ('violates', 'cannot tell', 'conforms')),
                                 no_advisory_for('ADR-0007 R5')],
    'writer-vague-notes': [record_0001, guide_not_added, retry_placeholder, retry_open_point, timeout_kept,
                           owner_not_invented, guide_asked, status_proposed],
    'writer-structural': [r1_record_0012, r1_metadata_from_repository, r1_rules_from_template, r1_structural_tag,
                          r1_confirmation_names_check, r1_guide_added, r1_agents_paragraph, r2_behavior_rule,
                          r2_no_confirmation_entry, r2_guide_untouched, r2_citation_without_condition,
                          r2_citation_names_subject],
    'coder-trailers': [defers_r5('Change 1', 'Commit message'), defers_r5('Change 1', 'Pull request description'),
                       no_rule_trailers('Change 2')],
    'writer-accepted-record': [new_record_0008, accepted_untouched, user_told_unchanged, only_link_fixed,
                               no_new_record_r2, no_guide_written],
    'writer-two-decisions': [r1_at_most_one_record, r1_split_proposed, r2_one_record, r2_no_split, no_guide_written],
    'writer-defect-and-guarantee': [record_0007_in('Request 1'), no_rule_on(r'entrypoint|\bCMD\b', 'the entrypoint'),
                                    no_rule_on(r'/tmp/cert|private CA|CA certificate|trust store', 'the certificates'),
                                    no_rule_on(r'emptyDir|/etc/ssl/certs|ca-certificates', 'the chart volumes'),
                                    r1_bug_proposed, r1_volumes_with_the_fix, r1_no_entrypoint_choice,
                                    r1_guarantee_as_fact, r1_record_names_no_fix,
                                    rule_with('Request 2', '401', 'TOKEN_ALG_NONE'),
                                    rule_with('Request 2', '401', 'TOKEN_ALG_SYMMETRIC'), no_defect('Request 2'),
                                    rule_with('Request 3', 'TLS', '1.2'), no_defect('Request 3'), no_guide_written],
    'writer-one-home': [record_0007_in('Request 1'), r1_service_account_m2m, r1_service_account_rule_alone,
                        not_copied('Request 1', r'system:serviceaccount', 'sub prefix'),
                        not_copied('Request 1', r'topology', 'namespace list'),
                        not_copied('Request 1', r'providers file|(?:no|without a) provider', 'provider rule'),
                        r1_one_tenant_rule,
                        r1_no_legacy_rule, r1_other_records_untouched, record_0007_in('Request 2'),
                        rule_with('Request 2', '401'), r2_exception_kept,
                        not_copied('Request 2', r'\b503\b|Retry-After', '503 response'), r2_no_401_copied,
                        cited_records_linked, no_guide_written, foreign_record_form,
                        not_copied('Request 1', r'\bnetcracker\b', 'audience'), no_see_also],
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
