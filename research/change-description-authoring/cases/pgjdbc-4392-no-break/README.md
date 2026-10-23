# Case: pgjdbc#4392, a fix with no break aimed at a patch release

The input is the author's description of [pgjdbc/pgjdbc#4392](https://github.com/pgjdbc/pgjdbc/pull/4392): a JDBC
escape followed by a tab or a newline used to reach the server verbatim and fail, and now works. Nothing that worked
before fails or returns a different result. The target is the same `master` as in `pgjdbc-4367-breaks`, so the case is
the negative control for the rule in `SKILL.md` §2,
"A break leads the description unless the next release from the target branch is a major".

## Skill parts

- `SKILL.md`: §1, §2, §3, §4, §5, §7, §7a
- `english-developer-style`: `SKILL.md` §5

## Checks

1. **No lead.** The description opens with the problem, not with a compatibility statement.
2. **No empty section.** No `Breaking changes` heading, and no sentence saying that nothing breaks or that the change is
   compatible.
3. **Literals kept.** `{d\t'1999-01-09'}` and the server's `syntax error at or near "{"` appear as in the draft.

## Running it

As in [`pgjdbc-4367-breaks`](../pgjdbc-4367-breaks/README.md). `check.py` marks all three checks.
`controls/empty-break-section.md` is `opus/result.md` with a `Breaking changes` heading that says nothing breaks, and the
server's message retyped.

## Results

Runs of 2026-10-20 after 41fe345, on the skill whose tree id is in `<model>/skill-tree`; Haiku at effort `high`. All
four results pass all three checks: they open with the problem, carry no `Breaking changes` heading and no sentence
about compatibility, and keep both literals. Opus wrote 286 and 245 words, Haiku 279 and 272; the draft has 209. Both
baselines, run with `english-developer-style` alone, pass too: without a break, neither model adds a lead. The control
fails all three checks.
