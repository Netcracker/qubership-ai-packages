# Case: the commit message for a typo fix

The input is a one-line fix of `make instal` in `README.md`. The subject is the whole message. The case is the
negative control for §3 *Сообщение коммита*, which before 1.1.0 always asked for a body after a blank line.

## Skill parts

- Text above §1 (the paragraph that hands commit slots to `change-description-authoring`)
- `SKILL.md`: §3 (Сообщение коммита), §11 (the genre item)

## Checks

1. **Subject only** (`one_line`).
2. **At most 10 words** (`at_most_10_words`).

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`.

| Run | Subject only (1) | Short (2) |
| --- | --- | --- |
| Opus r1, r2 | passes | passes (8, 7 words) |
| Sonnet r1, r2 | passes | passes (8, 6 words) |
| Opus baseline r1, r2 | fails: a body that retells the diff | fails (26, 26 words) |
| Sonnet baseline r1, r2 | passes | passes |
