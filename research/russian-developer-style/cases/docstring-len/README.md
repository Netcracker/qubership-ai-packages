# Case: a doc comment for `Len`

The input is `func (s *Set) Len() int`. One sentence is the whole comment. The case is the negative control for the
docstring rule, which before 1.1.0 continued «Дальше — параметры, возвращаемое значение, ошибки» with no condition.

## Skill parts

- Text above §1 (the paragraph that hands doc-comment slots to the doc-comment skill of the language)
- `SKILL.md`: §3 (Docstring), §9 (Комментарии в коде и docstrings)
- `modules/code-comments.md`: Docstring и Javadoc/KDoc/TSDoc
- `examples/before-after.md`: docstring функции

## Checks

1. **At most 15 words of comment** (`comment_at_most_15_words`).
2. **No parameter or result section** (`no_param_or_result_section`).

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`.

| Run | Short (1) | No section (2) |
| --- | --- | --- |
| Opus r1, r2 | passes (6, 6 words) | passes |
| Sonnet r1, r2 | passes (6, 6 words) | passes |
| Opus baseline r1, r2 | passes (11, 6 words) | passes |
| Sonnet baseline r1, r2 | passes (12, 11 words) | passes |

The baseline did not misfire here: three of its four runs added «Для нулевого значения — 0», which the type comment
already implies, and stayed inside the limit. The fix was made for the text (the module's own example committed the
«повтор имени без значения» antipattern), not for a measured output.
