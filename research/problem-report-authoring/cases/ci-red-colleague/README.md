# Case: main is red, a message to the author of the commit

The input is a red `main` in the team's own repository, the failing assertion, two re-runs and a local bisect that rule
out a flake, an unchecked guess at the cause, and a blocked merge queue. The output is a Slack direct message to the
author of the commit that broke it, asking whether they fix forward or revert. It is the negative control for the goal
sentence of §3, which `references/colleague-message.md` marked as holding in every message, and for the length of the
short form: a colleague message is a few lines.

## Skill parts

- `SKILL.md`: §3 (the goal, the analysis), §6 (versions), §7 (the core), §11 (the preamble, the Goal and Colleague
  message items)
- `references/colleague-message.md`
- `english-developer-style`: runs with the case, from the working copy

## Checks

1. **The ask** (read): fix forward or revert, as a question to Dana.
2. **Identifiers** (count): `4f2a9c1`, `exportsEmptyBatch`, and the run link.
3. **Ruled out** (read): the re-runs or the local run on the parent, in a clause.
4. **The assertion verbatim** (count): `expected: <1> but was: <0>`.
5. **Short** (count): at most 100 words outside code blocks, and no code block longer than four lines.
6. **No environment** (count): no JDK, Gradle, or macOS version.
7. **No goal sentence, no template** (read): no sentence about the task the reporter could not complete, beyond the
   blocked merge queue; no headings or field labels. The guess is absent, or one clause marked as unchecked.

```bash
python3 - claude-opus-5-5/result.md <<'EOF2'
import re, sys
text = open(sys.argv[1]).read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
print('prose words (expect <= 100):', len(prose.split()))
print('longest code block lines (expect <= 4):',
      max([len(b.strip('\n').splitlines()) for b in re.findall(r'```[a-z]*\n(.*?)```', text, flags=re.S)] or [0]))
for m in ['4f2a9c1', 'exportsEmptyBatch', 'runs/88412', 'expected: <1> but was: <0>']:
    print(f'{m!r} present (expect True):', m in text)
print('environment (expect False):', bool(re.search(r'21\.0\.5|8\.10\.2|macOS', text)))
EOF2
```

## Results

Runs of 2026-10-31, graded by reading, as for [`readme-typo`](../readme-typo/README.md#results): the new arm on skill
tree `6ff543e9`, the baseline on `1daec6f3`.

| Run | Ask, identifiers, ruled out, assertion (1–4) | Short (5) | No environment (6) | No goal, no template (7) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | pass | pass (94, 94) | pass | pass |
| Sonnet r1 | pass | fail (125): the checks as a bulleted list | fail: the versions beside the local run | pass |
| Sonnet r2 | pass | pass (100) | pass | pass |
| Opus baseline r1, r2 | pass | fail (109, 122) | fail | pass; both say the trace was trimmed |
| Sonnet baseline r1, r2 | pass | fail (115, 106) | fail | pass |

No run on either tree wrote a goal sentence, so this case does not tell the narrowed goal rule from the old one. What
moved is the environment: four of four baseline runs gave the JDK, Gradle, and macOS versions of a failure CI shows too,
and one of four new runs does.
