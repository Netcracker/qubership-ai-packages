# Case: a two-paragraph feature request

The input is a small feature request: a CLI ignores `NO_COLOR`, there is a flag that turns color off, and the flag
cannot be added to invocations a third-party wrapper makes. The request it needs is the task, the observation, the
acceptance criterion, and why the flag does not serve, in two short paragraphs and a pasted output. It is the negative
control for the slots of `references/request-genre.md`, which before 1.2.0 asked every request for who else is blocked
(or "the only known case"), the non-goals, what was searched, and the alternatives.

## Skill parts

- `SKILL.md`: §3 (the opening, negative results), §4 (duplicates), §5 (questions 1, 2, 4), §7 (the core), §11 (the
  preamble and the Request item)
- `references/request-genre.md`
- `english-developer-style`: runs with the case, from the working copy

## Checks

1. **The opening** (read): the first paragraph names the task (color off in CI for every tool, or escape sequences in
   the CI log) before it names `NO_COLOR` as something quarry lacks.
2. **The acceptance criterion** (read): with `NO_COLOR` set to a non-empty value, no ANSI escape sequences in the
   output.
3. **The observation** (count): the log with `^[[` pasted.
4. **The flag, once** (read): `--color=never` works and does not serve, because of `dbt-quarry` or the number of
   invocations, stated once: beside the problem, or in one closing line, not both.
5. **Short** (count): at most 250 words of prose in the body, the title not counted.
6. **No slots that answer nobody** (count, then read): no heading or sentence for non-goals or out of scope, for who
   else is blocked or the only known case, for alternatives, or for a list of search queries. #88 appears in at most
   one sentence that says how this differs.

```bash
python3 - claude-opus-5-5/result.md <<'EOF2'
import re, sys
text = open(sys.argv[1]).read()
lines = text.lstrip('\n').split('\n')
if re.fullmatch(r'(#+ |\*\*)?Title(\*\*)?:?', lines[0].strip()):
    lines = '\n'.join(lines[1:]).lstrip('\n').split('\n')
body = '\n'.join(lines[1:])
prose = re.sub(r'```.*?```', '', body, flags=re.S)
print('prose words (expect <= 250):', len(prose.split()))
print('escape sequences pasted (expect True):', '^[[' in text)
for label, pat in [('non-goals', r'non-goal|out of scope|not ask'),
                   ('blocked', r'only (known |affected )?(case|setup|user)|who else|else is blocked|no other (party|affected)|'
                               r'(other|no) affected'),
                   ('alternatives', r'^#+ .*(alternative|why not)'), ('search list', r'searched|search(ed)? for')]:
    print(f'{label} (expect False):', bool(re.search(pat, body, flags=re.I | re.M)))
EOF2
```

## Results

Runs of 2026-10-31, graded by reading, as for [`readme-typo`](../readme-typo/README.md#results): the new arm on skill
tree `6ff543e9`, the baseline on `1daec6f3`. The baseline ran on this prompt as it stands; a first version piped the
output through `cat -v`, which made `auto` color into a pipe, and Opus spent a paragraph on the contradiction.

The word limit was 150 before the first run. A report with only the parts the checks ask for counts about 235 words,
because the quote from no-color.org alone is 40, so the limit is 250.

| Run | Opening, criterion, observation (1–3) | The flag, once (4) | Short (5) | No slots that answer nobody (6) |
| --- | --- | --- | --- | --- |
| Opus r1 | pass | fail: in the first paragraph and again after the docs | fail (307) | fail: "We know of no affected users outside our own CI" |
| Opus r2 | pass | pass | fail (286) | fail: "We are the only affected user we know of" |
| Sonnet r1 | pass | fail: again under "What we tried" | fail (349) | fail: three headings and the only-case sentence |
| Sonnet r2 | pass | fail | fail (346) | fail: a "Scope" paragraph of non-goals, and the only-case sentence |
| Opus baseline r1, r2 | pass | pass | fail (426, 447) | fail: Out of scope, Alternatives, the search queries |
| Sonnet baseline r1, r2 | pass | fail | fail (442, 392) | fail: Out of scope, Alternatives, the queries in r1 |

The new arm drops the search queries from every run, the alternatives section from every run, and the non-goals from
three of four, and cuts the prose by about a quarter. The case still fails on both models. The "only known case"
sentence is in every new run, though the slot now asks for it only where the change is costly; it comes back from the
reader table of §1, whose R2 asks who is blocked, and nothing in this change moved it. Two earlier trees of 1.2.0,
`a93b8e29` and `09cd6130`, wrote 261 to 351 words by a count that included an unlabeled title, and the sentence in two
and three runs of four.
