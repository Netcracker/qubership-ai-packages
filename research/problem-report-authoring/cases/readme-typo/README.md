# Case: a typo in the install command

The input is a one-word typo in a README's install command, found in a public repository that has no issue template,
no contribution guide, and no policy on reports. The report it needs is a title and two or three sentences: where the
line is, what it says, what it should say. It is the negative control for the default sections of §8 and the
checklist preamble of §11: before 1.2.0 the skill listed a version section, a reproducer, and an analysis for every
defect report with no form, so a typo got the environment of the machine that ran `pip`, a reproducer, and the
`git blame` history.

## Skill parts

- `SKILL.md`: §3 (the goal), §4 (ownership, duplicates, count), §5 (question 4, the grounding), §6 (versions, the
  source kind, the redaction sentence), §7 (the core, the reader deletion test), §8 (the sections where there is no
  form), §10 (the deliverable for `gh issue create`), §11 (the preamble and the items it answers)
- `references/worked-cases.md`: case 7
- `english-developer-style`: runs with the case, from the working copy

## Checks

1. **The core** (read): the file and section or line, `tidwatch` as written, `tidewatch` as it should be.
2. **Short** (count): at most 60 words of prose in the body, the title not counted.
3. **No sections** (count): no Markdown heading and no bold field label in the body.
4. **No environment** (count): no macOS, Python, or pip version.
5. **No search sentence** (count): the body does not list what was searched. The note may.
6. **No analysis** (read): `81ac2f7` appears in at most one clause, and nothing reads as a cause or a fix proposal past
   "it should say `pip install tidewatch`".
7. **Hand-over** (read): the note gives the `gh issue create` command with `--body-file`.

The counted checks, from this directory, with a result file as the argument:

```bash
python3 - claude-opus-5-5/result.md <<'EOF2'
import re, sys
text = open(sys.argv[1]).read()
lines = text.lstrip('\n').split('\n')
if re.fullmatch(r'(#+ |\*\*)?Title(\*\*)?:?', lines[0].strip()):
    lines = '\n'.join(lines[1:]).lstrip('\n').split('\n')
body = '\n'.join(lines[1:])
prose = re.sub(r'```.*?```', '', body, flags=re.S)
print('prose words (expect <= 60):', len(prose.split()))
print('headings or bold labels (expect False):', bool(re.search(r'^(#+ |\*\*[^*]+:?\*\*:?\s*$)', body, flags=re.M)))
print('environment (expect False):', bool(re.search(r'macOS|Python 3|pip 24', body)))
print('search sentence (expect False):', bool(re.search(r'search', body, flags=re.I)))
EOF2
```

Every result opens with its title, plain or labeled, and the snippet drops it before counting; where the first line is
only a `Title` label, the line after it is the title.

## Results

Runs of 2026-10-31 on the tree of 1.1.0, `1daec6f3` (`<model>/baseline/`), graded by reading, both models at the
default effort, each with `english-developer-style` from the working copy.

| Run | Core (1) | Short (2) | No sections (3) | No environment (4) | No search, no analysis (5, 6) | Hand-over (7) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus baseline r1, r2 | pass | fail (138, 144) | fail: Expected, Environment, Workaround, Duplicates | fail | fail: the search and `81ac2f7` | pass |
| Sonnet baseline r1, r2 | pass | fail (179, 166) | fail | fail | fail: `81ac2f7` in both, the search in r2 | pass |
