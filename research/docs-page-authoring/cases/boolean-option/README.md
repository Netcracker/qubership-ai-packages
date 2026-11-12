# Case: a boolean option with nothing past the claim

The input is a new boolean property, `disableKeepAlive`, on an options page whose boolean siblings are the header and
one line. No value is rejected, no other option reads it or is read by it, and the page carries no version markers. It
is the negative control for the option-entry table of §2: before 1.1.0 the skill asked for every slot regardless, so a
boolean got values, an interaction, and a reason to change it. The prompt states the lenient parsing on purpose, as the
detail a writer is tempted to turn into a values slot.

## Skill parts

- `SKILL.md`: §2 (An option entry), §8 (the Entry item), §9 (Worked example)
- `english-developer-style`: runs with the case, from the working copy

## Checks

1. **Header** (`header`): `disableKeepAlive`, `boolean`, default `false`, in the page's form.
2. **Claim** (`claim`): what it controls, `Connection: close` and no reuse.
3. **Short** (`short`): at most 30 words under the header.
4. **No values slot** (`no values`): nothing about how `relay.properties` parses the value; the type says it all.
5. **No scope slot** (`no scope`): the page states it once for every property.
6. **No version marker** (`no version`): no entry on the page carries one.
7. **No interaction, no reason to change it** (read): no `connectTimeout` sentence, no `Set it to true when…`. The input
   gives neither.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `edb0428b`
(`<model>/skill-tree`), the baseline on `51b8d41`.

| Run | Header, claim (1, 2) | Short (3) | No values (4) | No scope, version (5, 6) | No interaction, reason (7) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | pass | pass (21, 21 words) | pass | pass | pass |
| Sonnet r1, r2, r3, r4 | pass | fail (36, 36, 33, 34) | fail: the parsing clause in all four | pass | pass |
| Opus baseline r1, r2 | pass | fail (77, 80) | fail | pass | fail: a reason in both, r1 also `connectTimeout` |
| Sonnet baseline r1, r2 | pass | fail (87, 78) | fail | pass | fail: a reason and `connectTimeout` in both |

Opus r1 wrapped the entry in a `markdown` fence; the entry inside is graded.

The new arm dropped the reason to change it and the interaction on both models, and Opus writes the header and the
claim alone. Sonnet still adds one clause on how `relay.properties` parses a boolean, which the prompt states and the
page's boolean siblings leave out; it is the one check this case still fails. An earlier tree of 1.1.0, `cf0d5617`,
had the same Sonnet result in three runs of four.

`<model>/draft-values-parse/` holds runs of every cell made with `run-case.sh` on a wording whose values slot was also
skipped for a boolean "parsed the way the page's other options of that type are" (tree `bb26d2b7`, never committed),
moved there by hand: all four Sonnet runs kept the parsing line, and one added a reason, so the wording was dropped.
