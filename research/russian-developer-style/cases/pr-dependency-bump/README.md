# Case: the description of a dependency bump

The input is a pull request that bumps `testify` in `go.mod` and nothing else. The case is the negative control for §3
*Описание PR* and its module copy, which before 1.1.0 asked for «Зачем, что сделано, как проверить, какие риски» and
three blocks under headings in every description.

## Skill parts

- Text above §1 (the paragraph that hands description slots to `change-description-authoring`)
- `SKILL.md`: §3 (Описание PR), §11 (the genre item)
- `modules/code-comments.md`: Описание PR
- `examples/before-after.md`: размытое описание PR

## Checks

1. **At most 40 words** (`at_most_40_words`).
2. **No «Как проверить»** (`no_how_to_test`).
3. **No risks paragraph** (`no_risks`).

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`.

| Run | Short (1) | No how-to-test (2) | No risks (3) |
| --- | --- | --- | --- |
| Opus r1, r2 | passes (33, 37 words) | passes | passes |
| Sonnet r1, r2 | passes (37, 34 words) | passes | passes |
| Opus baseline r1 | passes (40 words) | fails | passes |
| Opus baseline r2 | fails (57 words) | fails | fails: «Риски минимальные» |
| Sonnet baseline r1, r2 | fails (57, 55 words) | fails | fails: «Риск небольшой», «Рисков нет» |

The new runs open with three different verb forms: «Обновил… не трогал» (Opus r1), «Плановое обновление» (Opus r2),
«Обновляет» (Sonnet r1), «Обновляем» (Sonnet r2). No rule of the skill governs this, and the case does not check it.
