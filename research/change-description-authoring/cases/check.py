"""Grades the markers a script can count in the results of a change-description-authoring case.

Usage, from the repository root:
    python3 research/change-description-authoring/cases/check.py <case directory> [<result.md> ...]

Without result paths, it grades every result of the case: <model>/result*.md, <model>/baseline/*.md, and
controls/*.md. It prints one line per result and check: PASS, FAIL, or READ, with the evidence it found. READ marks
a check the script cannot settle; the case README states the question a reader answers. A PASS is a marker found,
not a grade: the README says to grade every check by reading the result.

The checks of a case are the functions registered under its directory name in CASES; each takes the text of a
result and returns (verdict, evidence).
"""

import glob
import os
import re
import sys

FENCE = re.compile(r'^(`{3,}|~{3,})([^\n`]*)\n(.*?)^\1[ \t]*$', re.S | re.M)
SUBJECT = re.compile(r'^[a-z]+(\([^)]*\))?!?: \S')
HEADING = re.compile(r'^#{1,6} ', re.M)
LEAD_IN = re.compile(r'\*\*(Scope|Breaking changes|User-visible changes|Not changed)[.:]?\*\*')
CHECKBOX = re.compile(r'^\s*(?:[*-]|\d+\.)\s*\[[ xX]\]', re.M)
MERGE_BASE = 'f171cd8af6fc5f341c765309af0c1ab0db6fbfb7'
HEAD_4424 = 'e6bf0181251063d4cb2fc8324e28fc4f6cde1313'


def fences(text):
    """Returns (info string, body) for every fenced block, outermost first."""
    return [(m.group(2).strip(), m.group(3)) for m in FENCE.finditer(text)]


def prose(text):
    """The text with fenced blocks removed."""
    return FENCE.sub('', text)


def words(text):
    return len(re.findall(r"[A-Za-z0-9`'][^\s]*", text))


def commits(text):
    """The commit messages: plain fenced blocks shaped as a subject, a blank line, and a body."""
    out = []
    for info, body in fences(text):
        first = body.lstrip('\n').split('\n', 1)[0]
        # A one-line block under a title heading is the title, not a commit.
        lines = body.strip('\n').split('\n')
        shaped = SUBJECT.match(first) or (len(first) <= 72 and len(lines) > 1 and not lines[1].strip())
        if info in ('', 'text', 'txt', 'git', 'gitcommit') and shaped and len(lines) >= 3:
            out.append(body.strip('\n'))
    return out


def commit_body(message):
    return message.split('\n', 1)[1] if '\n' in message else ''


def section(text, pattern):
    """The text from the first heading or bold label matching pattern to the next heading of the same or higher level."""
    lines = text.split('\n')
    start = None
    level = 7
    fence = None
    for i, line in enumerate(lines):
        f = re.match(r'^(`{3,}|~{3,})', line)
        if f and (fence is None or f.group(1).startswith(fence)):
            fence = None if fence else f.group(1)
            continue
        if fence:
            continue
        m = re.match(r'^(#{1,6}) (.*)$', line) or re.match(r'^()\*\*(.*?)\*\*\s*$', line)
        if start is None:
            if m and re.search(pattern, m.group(2), re.I):
                start, level = i + 1, len(m.group(1)) or 7
        elif m and (len(m.group(1)) or 7) <= level:
            return '\n'.join(lines[start:i])
    return '\n'.join(lines[start:]) if start is not None else None


def description(text):
    """The pull request description: the largest markdown fence under a description heading, else that section."""
    sec = section(text, r'description')
    if sec is None:
        return text
    blocks = [b for info, b in fences(sec) if info in ('markdown', 'md', '')]
    blocks = [b for b in blocks if not SUBJECT.match(b.lstrip('\n').split('\n', 1)[0])]
    return max(blocks, key=len) if blocks else sec


def title(text):
    sec = section(text, r'title')
    if sec is None:
        m = re.search(r'^.*\btitle\b.*$', text, re.I | re.M)
        if not m:
            return None
        sec = text[m.end():]
        inline = re.sub(r'^.*\btitle\b\W*', '', m.group(0), flags=re.I).strip().strip('`*').strip()
        if inline:
            return inline
    blocks = fences(sec)
    if blocks and sec.lstrip().startswith(('```', '~~~')):
        return blocks[0][1].strip().split('\n')[0]
    for line in sec.split('\n'):
        line = line.strip().strip('`').strip()
        if line:
            return line
    return None


def result(ok, evidence):
    return ('PASS' if ok else 'FAIL', evidence)


# Checks shared by the pgjdbc-4466 variants.

def outcome_blocks(text):
    """The text under each User-visible marker or Breaking heading, up to the next marker or heading."""
    return [m.group(0) for m in re.finditer(
        r'(User-visible|Breaking)[^\n]*\n.*?(?=\n\s*((\*\*)?Not changed|#{1,6} |\*\*[A-Z]|```)|\Z)', text, re.S)]


def outcome_lines_unwrapped(text):
    """Each outcome under a lead-in or label is one line: no indented continuation, and no line after one that ends mid-sentence."""
    wrapped = []
    for m in re.finditer(r'^(?:(?:\*\*)?(?:User-visible changes|Not changed|Breaking changes)\.(?:\*\*)?|(?:User-visible|Not changed):)(.*)\n((?:[^\n]*\S[^\n]*\n?)*)',
                         text, re.M):
        lines = ([m.group(1).strip()] if m.group(1).strip() else []) + m.group(2).rstrip('\n').split('\n')
        lines = [l for l in lines if l.strip() and not l.startswith('```')]
        for prev, line in zip(lines, lines[1:]):
            if line[0].isspace() or line[0].islower() or not re.search(r'[.:;!?)`"\']\*{0,2}$', prev.rstrip()):
                wrapped.append(line.strip()[:40])
    return result(not wrapped, f'wrapped outcome lines: {wrapped}' if wrapped else 'one line per outcome')


def user_visible_without_invented_code(text):
    blocks = outcome_blocks(text)
    if not re.search(r'User-visible', text):
        return result(False, 'no User-visible marker or heading')
    found = [b for b in blocks if re.search(r'PostgreSQL JDBC Driver[ `]+(X\.Y\.Z|42\.7|<|followed|suffixed|and the|plus|with)', b)
             or re.search(r'driver version|version of the driver', b)]
    if not found:
        return result(False, 'no outcome line names the new default')
    invented = [m for b in found for m in
                re.findall(r'SQLState|\b[0-9][0-9A-Z]{4}\b|\w+Exception|HTTP \d{3}|exit code', b)]
    return result(not invented, f'metadata on the line: {invented}' if invented else 'value and condition, no code')


def every_commit_full_with_issue(text):
    msgs = commits(text)
    if not msgs:
        return result(False, 'no commit message found')
    bad = [m.split('\n', 1)[0] for m in msgs if '#2404' not in m or words(commit_body(m)) < 30]
    return result(not bad, f'short or without #2404: {bad}' if bad else f'{len(msgs)} commit(s), each full with #2404')


def first_commit_full_with_issue(text):
    msgs = commits(text)
    if not msgs:
        return result(False, 'no commit message found')
    m = msgs[0]
    ok = '#2404' in m and 'pg_stat_activity' in m and words(commit_body(m)) >= 30
    return result(ok, f'first commit: {m.split(chr(10), 1)[0]!r}, {words(commit_body(m))} body words, '
                      f'#2404 {"in" if "#2404" in m else "missing"}, pg_stat_activity '
                      f'{"in" if "pg_stat_activity" in m else "missing"}')


def fixups_folded(text):
    subjects = [m.split('\n', 1)[0] for m in commits(text)]
    left = [s for s in subjects if re.match(r'(add tests|apply suggestion)', s, re.I)]
    return result(subjects and not left, f'subjects: {subjects}')


def title_is_subject(text):
    t = title(text)
    ok = bool(t) and re.match(r'^[a-z]+(\([^)]*\))?!?: [a-z]', t) and not t.endswith('.')
    return result(bool(ok), f'title: {t!r}')


def template_headings_kept(text):
    d = description(text)
    ok = any(h in d for h in ('All Submissions', 'New Feature Submissions', 'Changes to Existing Features'))
    return result(ok, 'template headings in the description' if ok else 'template headings missing')


def description_as_commit_body(text):
    d = description(text)
    heads = HEADING.findall(d)
    boxes = CHECKBOX.findall(d)
    urls = re.findall(r'https://github\.com/pgjdbc/pgjdbc/(?:blob|tree)/\S+', d)
    ok = not heads and not boxes and not urls
    return result(ok, f'{len(heads)} heading(s), {len(boxes)} checkbox(es), {len(urls)} URL(s) to the repository code')


def verification_one_line(text):
    d = description(text)
    found = [x for x in sentences(d) if re.search(r'\btests?\b|Test\b|server', x)]
    return ('READ', f'{len(found)} sentence(s) on the tests: {[x[:80] for x in found]}')


def detection_commands(text):
    cmd = '\n'.join(b for info, b in fences(text) if 'git log' in b)
    if not cmd:
        return result(False, 'no git log command')
    lines = [line for line in cmd.split('\n') if 'git log' in line or line.startswith('target=')]
    typed = [line for line in lines if re.search(r"\bmaster\b|'origin/|upstream/master", line)]
    ok = re.search(r'^remote=upstream\b', cmd, re.M) and '"$target" --' in cmd and not typed
    return result(bool(ok), f'remote=upstream {"set" if "remote=upstream" in cmd else "missing"}, '
                            f'"$target" -- {"used" if chr(34) + "$target" + chr(34) + " --" in cmd else "missing"}, '
                            f'branch typed: {typed}')


# pgjdbc-4424-docs-only

def no_test_verification_named(text):
    ok = 'git grep' in text and 'build.gradle.kts' in text
    return result(ok, f'git grep {"named" if "git grep" in text else "missing"}, '
                      f'build.gradle.kts {"named" if "build.gradle.kts" in text else "missing"}')


def no_headings(text):
    heads = HEADING.findall(description(text))
    return result(not heads, f'{len(heads)} heading(s)')


def no_plain_outcome_labels(text):
    """A description that becomes a commit body marks its outcomes with the lead-ins, not the plain labels."""
    found = re.findall(r'^(?:User-visible|Not changed):', description(text), re.M)
    return result(not found, f'plain labels: {found}' if found else 'no plain outcome labels')


def no_lead_in_labels(text):
    found = [m.group(0) for m in LEAD_IN.finditer(description(text))]
    return result(not found, f'lead-ins: {found}' if found else 'no lead-ins')


def no_outcome_lead_ins_in_description(text):
    """A description that is never a commit body carries its outcomes in prose, not under the body's lead-ins."""
    found = re.findall(r'\*\*(?:User-visible changes|Not changed)[.:]?\*\*', description(text))
    return result(not found, f'outcome lead-ins: {found}' if found else 'no outcome lead-ins')


def section_heading_text(text):
    ok = 'Extending the test suite with new tests' in text
    return result(ok, 'heading text cited' if ok else 'section cited without its heading text')


def changed_files_link_at_head(text):
    """Links into a file the change edits point at the head commit, except to a section only the merge base has."""
    urls = re.findall(r'https://github\.com/pgjdbc/pgjdbc/blob/([^/\s)]+)/(TESTING\.md|\.github/pull_request_template\.md)'
                      r'(#[\w-]*)?', text)
    if not any(p == 'TESTING.md' for _, p, _ in urls):
        return result(False, 'no link to the rendered TESTING.md section')
    removed = {'#new-feature-submissions'}
    wrong = [f'{p}{a}@{sha[:10]}' for sha, p, a in urls
             if sha != (MERGE_BASE if a in removed else HEAD_4424)]
    return result(not wrong, f'links at the wrong commit: {wrong}' if wrong else f'{len(urls)} link(s), each at the right commit')


def unchanged_code_link_at_merge_base(text):
    urls = re.findall(r'https://github\.com/pgjdbc/pgjdbc/blob/([^/\s)]+)/pgjdbc/build\.gradle\.kts(#L\d+(?:-L\d+)?)?', text)
    if not urls:
        return result(False, 'no link to pgjdbc/build.gradle.kts')
    wrong = [f'{sha[:10]}{anchor}' for sha, anchor in urls if sha != MERGE_BASE or not anchor]
    return result(not wrong, f'wrong commit or no line range: {wrong}' if wrong else 'at the merge base, with lines')


# pgjdbc-4370-verbose

def prose_under(limit):
    def check(text):
        n = words(prose(text))
        return result(n <= limit, f'{n} prose words')
    check.__name__ = f'prose_at_most_{limit}_words'
    return check


def facts_kept_4370(text):
    markers = ['SocketTimeoutException', '#4358', '#4359', '75 ms', '149 ms', 'EOFException']
    missing = [m for m in markers if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'all kept')


def scope_lead_in_4370(text):
    """The overlap with #4359 sits in a Scope slot that opens with the lead-in, not under a heading."""
    paras = [x.strip() for x in re.split(r'\n\s*\n', prose(description(text))) if x.strip()]
    # The Scope paragraph and the list that follows it, up to the next paragraph of prose.
    blocks = []
    extending = False
    for x in paras:
        m = LEAD_IN.match(x)
        if m and m.group(1) == 'Scope':
            blocks.append(x)
            extending = True
        elif extending and re.match(r'[*-] |\d+\. ', x):
            blocks[-1] += '\n\n' + x
        else:
            extending = False
    ok = [x for x in blocks if '#4359' in x]
    heads = HEADING.findall(description(text))
    return result(bool(ok) and not heads, f'{len(ok)} Scope paragraph(s) naming #4359, {len(heads)} heading(s)')


def scope_lead_in_under_template(text):
    """The template has no Scope heading, so the Scope slot opens with the lead-in under one of its headings."""
    d = description(text)
    paras = [x.strip() for x in re.split(r'\n\s*\n', prose(d)) if x.strip()]
    ok = [x for x in paras if (m := LEAD_IN.match(x)) and m.group(1) == 'Scope']
    added = re.findall(r'^#{1,6} .*\bScope\b.*$', d, re.M | re.I)
    return result(bool(ok) and not added, f'{len(ok)} Scope lead-in(s), Scope heading(s): {added}')


def break_lead_in_before_headings(text):
    """The break opens the description with its lead-in, ahead of the template's first heading, under no heading."""
    d = description(text)
    first = [x for x in re.split(r'\n\s*\n', prose(d).strip()) if x.strip()][:1]
    ok = bool(first) and (m := LEAD_IN.match(first[0])) is not None and m.group(1) == 'Breaking changes'
    added = re.findall(r'^#{1,6} .*\bbreak.*$', d, re.M | re.I)
    return result(ok and not added, f'opens with the lead-in: {ok}, break heading(s): {added}')


def new_test_not_marked(text):
    """The diff shows which test is new; the description does not say it."""
    found = re.search(r'`?\w+Test`?\s*\(new\)|\bnew (test|test class)\b[^.\n]{0,60}\w+Test'
                      r'|\w+Test`?[^.\n]{0,40}\bis new\b|\b(\d+|one|two|three|four|five) new tests?\b'
                      r'|^\s*\**New tests?:', text, re.I | re.M)
    return result(not found, f'marked new: {found.group(0)!r}' if found else 'no test is marked new')


def coverage_lost_named(text):
    ok = re.search(r'skipDoesNotFallBackToReadingByteByByte|no test (now )?(limits|bounds|checks|counts)', text)
    return ('READ', f'marker found: {ok.group(0)!r}' if ok else 'no marker: read for a sentence on the coverage lost')


def no_construction_in_verification(text):
    sec = section(text, r'verif|test')
    if sec is None:
        m = re.search(r'^.*SkipTest.*$', prose(text), re.M)
        sec = prose(text)[m.start():] if m else ''
    found = [m for m in ['Long.MIN_VALUE', 'Long.MAX_VALUE', '8192', 'one byte short', '-1, -2'] if m in sec]
    return result(not found, f'construction in the verification slot: {found}' if found else 'none found')


def no_test_command(text):
    """CI runs the tests; the description carries no command that runs them."""
    found = re.search(r'gradlew[^\n]*(\btest\b|--tests)|\bmvn\b[^\n]*\btest\b', text)
    return result(not found, f'test command: {found.group(0)[:100]!r}' if found else 'no test command')


def no_test_narration(text):
    """No sentence says a test fails without the change, counts passing tests, or narrates a revert."""
    pat = (r'fails? (against|on) `?master|fails? on the base|fail(s|ed)? without (the|this) (change|fix)|'
           r'\brevert(s|ing|ed)?\b[^.]{0,80}\bfail|with the production change reverted|before the fix[^.]{0,40}\bfail|'
           r'\b\d+ tests\b(?![^.]*without)[^.]{0,80}\bpass|against (the old|master)\b[^.]{0,80}\bfail|'
           r'\b\w+ of (the|its) \w+ cases\b[^.]{0,40}\bfail')
    found = [x for x in sentences(text) if re.search(pat, x, re.I)]
    return result(not found, f'narrated: {found[0][:160]!r}' if found else 'no test narration')


def no_tool_footer(text):
    found = re.search(r'Generated with', text)
    return result(not found, 'tool footer present' if found else 'no tool footer')


# Checks of the authz-agent cases: rule trailers where the records number their rules, and none where they do not.

RULE_LINE = re.compile(r'^[ \t>*-]*(?:\*\*)?(Implements|Defers)(?:\*\*)?:[ \t]*(.*)$', re.M)
PLACEHOLDER = re.compile(r'\[(?:PR )?#N+\]|#N{2,}|\bTBD\b|\bto the wiring change\b', re.I)
NO_ISSUE = re.compile(r'no\s+(?:open\s+)?(?:issue|pull\s+request)|not?\s+(?:yet\s+)?(?:have|has)\s+an\s+issue'
                      r'|without\s+an\s+issue|has\s+no\s+(?:issue|pull\s+request|number)', re.I)
IMPLEMENTS_208 = {('0091', '23'), ('0091', '37'), ('0091', '38'), ('0091', '39')}
WAITING_208 = {('0092', '2'), ('0095', '2'), ('0095', '16')}
IMPLEMENTS_159 = ({('0091', r) for r in ('6', '8', '10')}
                  | {('0094', r) for r in ('4', '5', '6', '7', '8', '10', '11', '12', '13', '16', '17', '18', '22', '24',
                                           '25', '27', '29')})
DEFERS_159 = {('0094', '20'): '175', ('0092', '7'): '203'}
WAITING_159 = {('0094', '1')}


def rule_line(text, key):
    """Every line of the text under this key, joined, so that a second line of the same key is graded too."""
    found = [m.group(2) for m in RULE_LINE.finditer(text) if m.group(1) == key]
    return '; '.join(found) if found else None


def rule_pairs(line):
    """The (record, rule) pairs a text names: `ADR-0095 R2, R16` gives two pairs of ADR-0095."""
    pairs, record = set(), None
    for adr, rule in re.findall(r'ADR-(\d{4})|\bR(\d+)\b', line):
        if adr:
            record = adr
        elif record:
            pairs.add((record, rule))
    return pairs


def deferrals(line):
    """Each (record, rule) pair of a Defers line, mapped to the number its segment defers it to, or None."""
    out = {}
    for segment in line.split(';'):
        target = re.search(r'\bto\s+#(\d+)\b', segment)
        for pair in rule_pairs(segment):
            out[pair] = target.group(1) if target else None
    return out


def end_trailers(text):
    """The last paragraph of a text outside fenced blocks, where every line of it is a `Key: value` trailer."""
    last = prose(text).rstrip().split('\n\n')[-1]
    lines = [ln for ln in last.split('\n') if ln.strip()]
    return last if lines and all(re.match(r'^[A-Za-z-]+: \S', ln) for ln in lines) else ''


def trailers_ok(block, implements, defers):
    """Whether a trailer block names exactly these implemented rules and these deferrals, and nothing invented."""
    imp, dfr = rule_line(block, 'Implements'), rule_line(block, 'Defers')
    if imp is None or rule_pairs(imp) != implements:
        return False
    if not defers:
        return dfr is None
    return dfr is not None and deferrals(dfr) == defers and not PLACEHOLDER.search(dfr)


def description_trailers(implements, defers):
    def check(text):
        block = end_trailers(description(text))
        if not block:
            return result(False, 'the description does not end with a trailer paragraph')
        return result(trailers_ok(block, implements, defers), block.replace('\n', ' | ')[:150])
    check.__name__ = 'description_ends_with_rule_trailers'
    return check


def commit_trailers(implements, defers):
    def check(text):
        msgs = commits(text)
        if not msgs:
            return result(False, 'no commit message')
        block = end_trailers(msgs[-1])
        return result(bool(block) and trailers_ok(block, implements, defers), block.replace('\n', ' | ')[:150])
    check.__name__ = 'commit_ends_with_rule_trailers'
    return check


def waiting_rules_named(waiting):
    def check(text):
        body = prose(description(text))
        block = end_trailers(description(text))
        if block:
            body = body[:body.rfind(block.split('\n')[0])]
        named = waiting <= rule_pairs(body)
        marker = NO_ISSUE.search(body)
        ok = named and marker is not None
        return result(ok, (marker.group(0) if marker else 'no word that the change has no issue')
                      + ('' if named else f'; rules not named: {sorted(waiting - rule_pairs(body))}'))
    check.__name__ = 'waiting_rules_named_in_prose'
    return check


def no_placeholder(text):
    found = PLACEHOLDER.search(text)
    if found:
        return result(False, f'placeholder: {found.group(0)}')
    for m in RULE_LINE.finditer(text):
        if m.group(1) == 'Defers':
            for segment in m.group(2).split(';'):
                if rule_pairs(segment) and not re.search(r'\bto\s+#\d+\b', segment):
                    return result(False, f'Defers target that is not a number: {segment.strip()[:80]}')
    return result(True, 'no placeholder')


def scope_lead_in_before_trailers(text):
    d = prose(description(text))
    lead = re.search(r'\*\*Scope[.:]?\*\*', d)
    block = end_trailers(description(text))
    ok = lead is not None and bool(block) and lead.start() < d.rfind(block.split('\n')[0])
    return result(ok, '**Scope.** ahead of the trailers' if ok else 'no **Scope.** lead-in ahead of the trailers')


def no_rule_lines(text):
    found = [m.group(0).strip() for m in RULE_LINE.finditer(text)]
    return result(not found, f'rule lines: {found}' if found else 'no rule lines')


def no_rule_numbers(text):
    found = sorted(set(re.findall(r'\bR\d+\b', text)))
    return result(not found, f'rule numbers: {found}' if found else 'no rule numbers')


def links_at_merge_base(text):
    urls = re.findall(r'https://github\.com/pgjdbc/pgjdbc/blob/([^/\s)]+)/', text)
    wrong = [u[:12] for u in urls if u != MERGE_BASE]
    return result(not wrong, f'{len(urls)} link(s), not at the merge base: {wrong}')


# pgjdbc-4412-comment-only

def no_old_comment_quoted_4412(text):
    """The comments and messages the diff removes are shown by the diff and are not quoted again."""
    old = ['autoCommit is false on a connection returned by getConnection',
           '2nd phase commit must be issued using an idle connection',
           'should have restored connection autocommit mode']
    found = [m for m in old if m.lower() in text.lower()]
    return result(not found, f'quoted: {found}' if found else 'no removed wording quoted')


def contradictions_kept_4412(text):
    """The two comments that contradicted the code keep the code side, which the comment hunk does not show."""
    missing = [m for m in ['pg_has_role', '64000'] if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'both kept')


def renames_named_4412(text):
    missing = [m for m in ['onePhaseBranch_leavesAutoCommitUnchanged', 'endThenJoinBranch_leavesAutoCommitUnchanged']
               if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'both new names')


def runtime_noop_checked_4412(text):
    return ('READ', 'read: is "nothing changes at run time" stated once, with how it was checked (comments stripped)?')


# pgjdbc-4367-breaks and pgjdbc-4392-no-break

def break_lines_lead_4367(text):
    first = [x for x in re.split(r'\n\s*\n', prose(text).strip()) if x.strip()][:3]
    ok = (re.search(r'\bbreak', first[0], re.I) if first else False) or any(
        re.search(r'\*\*Breaks?:?\*\*|^#{1,6} .*[Bb]reak', p, re.M) for p in first)
    return result(ok, 'break lines among the first three blocks' if ok else f'opens with {first[0][:100]!r}')


def break_label_4367(text):
    """The case has no template, so the description opens with the break lead-in, under no heading."""
    d = description(text)
    first = [x for x in re.split(r'\n\s*\n', prose(d).strip()) if x.strip()][:1]
    ok = bool(first) and (m := LEAD_IN.match(first[0])) is not None and m.group(1) == 'Breaking changes'
    heads = HEADING.findall(d)
    return result(ok and not heads, f'opens with the lead-in: {ok}, {len(heads)} heading(s)')


def literals_kept_4367(text):
    markers = ['42703', '0100E', 'A result was returned when none was expected.', '42601',
               'cannot insert multiple commands into a prepared statement']
    missing = [m for m in markers if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'all kept')


def stated_once_4367(text):
    return ('READ', 'read: is any break line repeated in the Why slot or a later outcome list?')


def no_lead_4392(text):
    first = [x for x in re.split(r'\n\s*\n', prose(text).strip()) if x.strip()][0]
    bad = re.search(r'break|compatib', first, re.I)
    return result(not bad, f'opens with {first[:100]!r}')


def no_empty_section_4392(text):
    found = re.findall(r'^#{1,6} .*[Bb]reak.*$|\*\*Breaking changes[.:]?\*\*|nothing breaks|no breaking|backward[s-]? compatible|fully compatible|is compatible',
                       text, re.M | re.I)
    return result(not found, f'found: {found}' if found else 'no empty section')


def literals_kept_4392(text):
    markers = ["{d\\t'1999-01-09'}", 'syntax error at or near "{"']
    missing = [m for m in markers if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'both kept')


# pgjdbc-4374-commit-changelog

def outcome_lines_4374(text):
    msgs = commits(text)
    body = commit_body(msgs[0]) if msgs else ''
    m = re.search(r'^(?:User-visible:|(?:\*\*)?User-visible changes\.(?:\*\*)?$).*?(?=\n\s*\n(?!\S*\s*(?:"|`|When|Unterminated|JDBC))|\Z)', body, re.S | re.M)
    if not m:
        return result(False, 'no User-visible paragraph in the commit body')
    lines = [line for line in m.group(0).split('\n') if line.strip()]
    texts = ['has no argument list', 'Unterminated JDBC escape function call']
    bad = [t for t in texts if not any(t in line and '42601' in line for line in lines)]
    return result(not bad, f'without the text and 42601 on one line: {bad}' if bad else 'both texts with 42601')


def nothing_invented_4374(text):
    numbers = set(re.findall(r'#(\d{3,5})\b', text)) - {'4374', '4363'}
    codes = set(re.findall(r'SQLState `?([0-9A-Z]{5})', text)) - {'42601'}
    return result(not numbers and not codes, f'other numbers: {sorted(numbers)}, other SQLStates: {sorted(codes)}')


def changelog_entry_4374(text):
    entries = [line for line in text.split('\n') if re.match(r'\s*[*-] (\*\*Breaking:\*\* )?fix', line)]
    if not entries:
        return result(False, 'no changelog bullet starting with fix')
    e = entries[-1]
    checks = {
        'reference': '[PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)' in e,
        'symptom literal': bool(re.search(r'select ow|column "ow" does not exist|\{fn now\}', e)),
        'new error': 'has no argument list' in e or '42601' in e,
    }
    return result(all(checks.values()), str(checks))


# pgjdbc-4423-no-outcome

def no_outcome_slot(text):
    found = re.findall(r'User-visible|Not changed|Breaking', text)
    return result(not found, f'found: {found}' if found else 'no outcome slot')


def no_changelog_entry(text):
    entries = [line for line in text.split('\n') if re.match(r'\s*[*-] (test|fix|feat|chore|build)(\(\w+\))?:', line)]
    stated = re.search(r'no (changelog|CHANGELOG)|does not need (a|an) (changelog|entry)|needs no (changelog|entry)'
                       r'|\bNONE\b|no entry', text, re.I)
    ok = not entries and stated
    return result(bool(ok), f'entries: {entries[:1]}, absence stated: {bool(stated)}')


# jdk-33173-audit

def sentences(text):
    return re.split(r'(?<=[.!?])\s+', re.sub(r'\s+', ' ', prose(text)))


def finder_not_named(text):
    """The slot ends at the condition; what found the defect is the route, not the result."""
    found = [x for x in sentences(text)
             if re.search(r'\baudit(?! log)|\bfound (it|this|the defect)|turned (it|this) up|\bspotted\b|\bCodex\b'
                          r'|static analysis', x, re.I)]
    return result(not found, f'finder named: {found[0][:120]!r}' if found else 'what found the defect is not named')


def no_absence_claim(text):
    pat = (r"(has not|hasn't|have not|haven't|never|not) (yet )?(been )?(observed|seen|reported|hit|reproduced)"
           r"|no (failure|crash|report|symptom)s? (has|have|was|were) (been )?(observed|seen|reported)"
           r"|nobody (has )?(reported|seen|observed)|no known (failure|crash|report)")
    found = [x for x in sentences(text) if re.search(pat, x, re.I)]
    return result(not found, f'absence stated: {found[0][:160]!r}' if found else 'no claim about failures seen or not seen')


def no_predicted_symptom(text):
    found = [x for x in sentences(text)
             if re.search(r'is_same_object|IsSameObject|\bJNI\b', x)
             and re.search(r'NullPointerException|InternalError|null `?UNSAFE|crash|would (fail|throw)|could (fail|throw)', x)]
    return ('READ', f'candidate: {found[0][:200]!r}' if found else 'no candidate sentence')


def no_hunk_translation(text):
    """A sentence that says the per-site initializations are removed reads the removal hunks aloud."""
    found = [x for x in sentences(text)
             if re.search(r'initiali[sz](e|es|ed|ation|ations)\b', x)
             and re.search(r'\b(are|is|were) (now )?(\w+ and )?(removed|dropped|deleted|gone)\b|\b(drops?|removes?|deletes?)\b', x)]
    return result(not found, f'hunk read aloud: {found[0][:200]!r}' if found else 'no removal hunk read aloud')


def alternative_by_mechanism(text):
    found = [x for x in sentences(text)
             if re.search(r'value\.bsm\.debug|initPhase1|system propert', x, re.I)
             and re.search(r'smaller|rather than|instead of (adding|patching)|one (more )?call|did not take|rejected', x, re.I)]
    return ('READ', f'candidate obstacle the change removes: {found[0][:200]!r}' if found else 'no candidate sentence')


def answered_question_not_open(text):
    found = [x for x in sentences(text) if 'VERBOSE' in x and ('?' in x or re.search(r'open question|undecided|left open', x, re.I))]
    return result(not found, f'kept open: {found[0][:160]!r}' if found else 'not presented as open')


def property_named(text):
    return result('value.bsm.debug' in text, 'value.bsm.debug named' if 'value.bsm.debug' in text else 'the removed property is not named')


# calcite-5330-open-question

def break_leads_5330(text):
    """The break (a key reporting NONE validated before and now fails) opens the description, ahead of the problem.

    The break may open with its lead-in ahead of every template heading. A run of an earlier skill put the template's
    Jira Link section first, and the break lines after one short paragraph that says which code breaks, or under a
    heading of their own."""
    t = prose(text)
    opening = [x for x in re.split(r'\n\s*\n', t.strip()) if x.strip()][:1]
    if (opening and (m := LEAD_IN.match(opening[0])) and m.group(1) == 'Breaking changes'
            and re.search(r'NONE|reject|fail', opening[0])):
        return result(True, f'opens with the lead-in: {opening[0][:120]!r}')
    heads = [h for h in re.findall(r'^#{1,6} (.*)$', t, re.M) if h.strip() != 'Jira Link']
    if heads and re.search(r'break', heads[0], re.I):
        return result(True, f'first heading after the Jira link: {heads[0]!r}')
    t = t.split('## Changes Proposed', 1)[-1]
    blocks = [x.strip() for x in re.split(r'\n\s*\n', t) if x.strip()]
    first = blocks[0] if blocks else ''
    if re.search(r'\bbreak', first, re.I) and re.search(r'NONE|reject|fail', first):
        return result(True, f'first paragraph: {first[:120]!r}')
    if first.startswith('#') and re.search(r'break', first.split('\n')[0], re.I):
        return result(True, f'opens with {first.splitlines()[0]!r}')
    if len(blocks) > 1 and words(first) <= 60 and re.match(r'#{1,6} .*break', blocks[1], re.I):
        return result(True, f'a short paragraph, then {blocks[1].splitlines()[0]!r}')
    return result(False, f'first paragraph: {first[:120]!r}')


def maintainer_question_kept(text):
    found = [x for x in sentences(text)
             if ('?' in x and re.search(r'NONE|permissive|#5331|VECTOR|reject|close', x))
             or re.search(r'\b(decide|decision|choose)\b', x, re.I)]
    return result(bool(found), f'question: {found[0][:200]!r}' if found else 'no question or decision asked of the maintainer')


def compatibility_not_settled(text):
    found = re.findall(r'not a breaking change|no breaking change|backward[s-]? compatible|fully compatible|does not break', text, re.I)
    return result(not found, f'settled: {found}' if found else 'compatibility left to the maintainer')


def answered_question_not_reopened(text):
    """A question on whether types are comparable at run time; the maintainer's "should a type" question is check 2's."""
    found = [x for x in sentences(text) if '?' in x and re.search(r'comparable at run ?time|all types', x, re.I)
             and not re.search(r'\bshould (?:a|such a) type\b', x, re.I)]
    return result(not found, f'reopened: {found[0][:160]!r}' if found else 'not asked again')


def calcite_template_kept(text):
    ok = '## Jira Link' in text and '## Changes Proposed' in text
    return result(ok, 'both template headings' if ok else 'a template heading is missing')


# pgjdbc-4501-manual-check

def manual_check_literal_4501(text):
    missing = [m for m in ['25433->5433', '25434->5434', 'PG_REPLICA_TWO_PUBLISH_PORT=25434'] if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'the command and its output kept as literals')


def no_route_4501(text):
    found = re.search(r'nothing else (in the repository )?uses|no longer carries', text, re.I)
    return result(not found, f'route left: {found.group(0)!r}' if found else 'no search result or bookkeeping')


# pgjdbc-4388-contract-fix

def snippet_shown_4388(text):
    ok = any('never reached' in b or '// throws' in b for _, b in fences(text))
    return result(ok, 'the old lines are shown' if ok else 'no snippet of the old close()')


def no_route_4388(text):
    found = re.search(r'adversarial|Codex|found by|review(ed)? by|findings', text, re.I)
    return result(not found, f'route left: {found.group(0)!r}' if found else 'what found the defect is not named')


def no_break_lead_4388(text):
    """A second close() that throws broke Closeable; fixing it is a fix, not a break that leads."""
    first = [x for x in re.split(r'\n\s*\n', text.strip()) if x.strip()][:1]
    found = re.search(r'\bBreaking\b|^#{1,6} .*\bbreak', first[0], re.I | re.M) if first else None
    return result(not found, f'opens with {first[0][:80]!r}' if found else 'no break lead')


def passes_without_named_4388(text):
    ok = 'closeReportsAFailedRelease' in text
    return ('READ', 'named: read that it is the test that passes without the change' if ok
            else 'not named: read for a sentence on the test that passes without the change')


# pgjdbc-4420-test-sites

def site_mapping_kept_4420(text):
    """The tests guard several sites, and the diff does not pair them; the pairing is the content."""
    names = ['addBatch', 'QueryWithReturningColumnsKey', 'BaseQueryKey', 'executeCachedSql', 'CachedQueryCreateAction']
    paired = sorted({m for line in re.split(r'\n|(?<=[.;])\s', prose(text)) for m in names
                     if m in line and re.search(r'\btests?\b|\bcases?\b|"off"|"on"|default|(?-i:[a-z]\w*Test\b)|`\w+\(?\)?`\s*\|\s*$',
                                               line.replace(m, ''), re.I)})
    return result(len(paired) >= 3, f'sites paired with a test: {paired}')


def removed_tests_named_4420(text):
    missing = [m for m in ['testBatchEscapeProcessing', 'escapeProcessing'] if m not in text]
    return result(not missing, f'missing: {missing}' if missing else 'the removed tests are named')


def no_route_4420(text):
    found = re.search(r'\bmutants?\b|\bmutation\b|(?<![A-Za-z])I (checked|applied|broke)\b|\bbroke (one|each)\b', text,
                      re.I)
    return result(not found, f'route left: {found.group(0)!r}' if found else 'no mutation narration')


CASES = {
    'pgjdbc-4367-breaks': [break_lines_lead_4367, break_label_4367, stated_once_4367, literals_kept_4367,
                           no_outcome_lead_ins_in_description],
    'pgjdbc-4392-no-break': [no_lead_4392, no_empty_section_4392, literals_kept_4392,
                             no_outcome_lead_ins_in_description],
    'pgjdbc-4466-squash-default': [user_visible_without_invented_code, first_commit_full_with_issue,
                                   title_is_subject, template_headings_kept, scope_lead_in_under_template,
                                   break_lead_in_before_headings, outcome_lines_unwrapped,
                                   no_outcome_lead_ins_in_description],
    'pgjdbc-4466-squash-title-description': [user_visible_without_invented_code, title_is_subject,
                                             description_as_commit_body, verification_one_line,
                                             no_plain_outcome_labels, break_lead_in_before_headings,
                                             outcome_lines_unwrapped],
    'pgjdbc-4466-squash-or-rebase': [user_visible_without_invented_code, every_commit_full_with_issue,
                                     fixups_folded, title_is_subject, template_headings_kept,
                                     scope_lead_in_under_template, break_lead_in_before_headings,
                                     outcome_lines_unwrapped, no_outcome_lead_ins_in_description],
    'pgjdbc-4466-merge-commit-title-description': [user_visible_without_invented_code, every_commit_full_with_issue,
                                                   fixups_folded, title_is_subject, description_as_commit_body,
                                                   verification_one_line, no_plain_outcome_labels,
                                                   break_lead_in_before_headings, outcome_lines_unwrapped],
    'pgjdbc-4466-detection-failed': [detection_commands, user_visible_without_invented_code,
                                     every_commit_full_with_issue, description_as_commit_body, verification_one_line,
                                     no_plain_outcome_labels, break_lead_in_before_headings, outcome_lines_unwrapped],
    'pgjdbc-4424-docs-only': [no_test_verification_named, no_headings, no_lead_in_labels, section_heading_text,
                              changed_files_link_at_head, unchanged_code_link_at_merge_base],
    'pgjdbc-4370-verbose': [prose_under(500), facts_kept_4370, new_test_not_marked, coverage_lost_named,
                            no_construction_in_verification, links_at_merge_base, no_test_command,
                            no_test_narration, scope_lead_in_4370],
    'pgjdbc-4374-commit-changelog': [outcome_lines_4374, nothing_invented_4374, changelog_entry_4374],
    'pgjdbc-4423-no-outcome': [no_outcome_slot, no_changelog_entry],
    'calcite-5330-open-question': [break_leads_5330, maintainer_question_kept, compatibility_not_settled,
                                   answered_question_not_reopened, calcite_template_kept,
                                   scope_lead_in_under_template, break_lead_in_before_headings,
                                   no_outcome_lead_ins_in_description],
    'jdk-33173-audit': [finder_not_named, no_absence_claim, no_predicted_symptom, no_hunk_translation,
                        alternative_by_mechanism, answered_question_not_open, property_named],
    'pgjdbc-4501-manual-check': [manual_check_literal_4501, no_route_4501, no_tool_footer, prose_under(110)],
    'pgjdbc-4388-contract-fix': [snippet_shown_4388, no_route_4388, no_break_lead_4388, no_test_command,
                                 no_test_narration, passes_without_named_4388, prose_under(220), no_tool_footer],
    'pgjdbc-4420-test-sites': [site_mapping_kept_4420, removed_tests_named_4420, no_route_4420, no_test_command,
                               prose_under(330), no_tool_footer],
    'authz-agent-208-rule-lines': [description_trailers(IMPLEMENTS_208, {}), waiting_rules_named(WAITING_208),
                                   no_placeholder, scope_lead_in_before_trailers, no_headings,
                                   commit_trailers(IMPLEMENTS_208, {})],
    'authz-agent-159-defers-targets': [description_trailers(IMPLEMENTS_159, DEFERS_159), waiting_rules_named(WAITING_159),
                                       no_placeholder, scope_lead_in_before_trailers, no_headings,
                                       commit_trailers(IMPLEMENTS_159, DEFERS_159)],
    'authz-agent-208-prose-records': [no_rule_lines, no_rule_numbers, no_headings],
    'pgjdbc-4412-comment-only': [no_old_comment_quoted_4412, contradictions_kept_4412, renames_named_4412,
                                 runtime_noop_checked_4412, prose_under(150)],
}


def unwrap(text):
    """A result written as one markdown fence is graded as the text inside it."""
    blocks = [b for info, b in fences(text) if info in ('markdown', 'md')]
    if len(blocks) == 1 and len(blocks[0]) > 0.8 * len(text):
        return blocks[0]
    return text


def main():
    case_dir = sys.argv[1].rstrip('/')
    name = os.path.basename(case_dir)
    if name not in CASES:
        sys.exit(f'no checks registered for {name}')
    paths = sys.argv[2:] or sorted(glob.glob(f'{case_dir}/*/result*.md') + glob.glob(f'{case_dir}/*/baseline/*.md')
                                   + glob.glob(f'{case_dir}/controls/*.md'))
    for path in paths:
        text = unwrap(open(path).read())
        print(os.path.relpath(path, case_dir))
        for check in CASES[name]:
            verdict, evidence = check(text)
            print(f'  {verdict:4} {check.__name__}: {evidence}')


if __name__ == '__main__':
    main()
