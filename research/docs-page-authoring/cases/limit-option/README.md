# Case: a size limit that owes every slot

The input is a new size property, `maxHeaderSize`, with a built-in default of 64 KiB, a literal error when a response
passes it, an existing mode (`strictParsing=false`) that turns the built-in limit off, and a stated reason to raise it.
Scope is the same for every property on the page, and the page carries no version markers. The case checks that the
skip conditions 1.1.0 gave the option-entry slots do not drop a slot that has content.

## Skill parts

- `SKILL.md`: §2 (An option entry), §6 (quoting an error), §8 (the Entry item), §9 (Worked example)
- `english-developer-style`: runs with the case, from the working copy

## Checks

1. **Header** (`header`): `maxHeaderSize`, a size type, default unset, and what unset means.
2. **Built-in limit as a value** (`built-in limit`, `no constant`): 64 KiB or 65536 bytes, not `DEFAULT_MAX_HEADER_SIZE`.
3. **Values** (`binary suffix`): the suffix forms, and that they are binary.
4. **At the limit** (`literal error`): the message as the code emits it, the limit shown as a placeholder (§6), and that
   the connection closes.
5. **Interaction** (`interaction`): a set value applies whatever `strictParsing` says; `strictParsing=false` turns off
   the built-in limit only.
6. **When to change it** (`when to change`): large cookies or tokens.
7. **No version marker, no scope sentence** (`no version`, read): the page carries neither per entry.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `edb0428b`
(`<model>/skill-tree`), the baseline on `51b8d41`.

| Run | Header, limit (1, 2) | Values (3) | At the limit (4) | Interaction (5) | When to change (6) | No version, scope (7) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | pass | pass | r1 passes; r2 partial: fills in `65536` for the limit | pass | pass | pass |
| Sonnet r1, r2 | pass | pass | pass | pass | pass | pass |
| Opus baseline r1, r2 | pass | pass | pass | pass | pass | pass |
| Sonnet baseline r1, r2 | pass | pass | pass | pass | pass | r2 fails: a scope sentence and `Since TBD` |

No new run dropped a slot. Opus r1 wrapped the entry in a `markdown` fence. Filling in the default where the error
has a placeholder is §6's rule, which 1.1.0 left alone; on the earlier tree `cf0d5617` both Opus runs did it. Two runs
per arm cannot tell whether the rate moved. `<model>/draft-values-parse/` holds runs on a dropped wording (see the
boolean case); none of them dropped a slot either.
