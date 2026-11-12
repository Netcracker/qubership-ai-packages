# Case: a trivial validation error

The input is the Russian `msgstr` for `PgStatement.setFetchSize(int rows)` rejecting `rows < 0`. The fix is to pass a
non-negative value, which the message already says, and the call stops at the exception. The case is the negative
control for the error template: before 1.1.0 it asked for «Не удалось `<действие>`» + причина + что делать in every
message.

## Skill parts

- Text above §1 (the paragraph that hands the rest of a message's content to `telemetry-authoring`)
- `SKILL.md`: §3 (Сообщение об ошибке), §8 (Ошибки и логи), §11 (the genre item)
- `modules/errors-logs.md`: Шаблон ошибки, Примеры пользовательских ошибок
- `examples/before-after.md`: Ошибки и логи

## Checks

1. **No action** (`no_action`): no «Укажите», «Передайте», or another imperative that undoes the input.
2. **Not a failed operation** (`no_failed_operation`): no «Не удалось», since nothing was attempted.
3. **One sentence, at most 12 words** (`one_sentence`, `at_most_12_words`).
4. **The placeholder stays** (`placeholder_kept`).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `230514d8`, the
baseline on `51b8d41` (tree `6c0cb228`).

| Run | No action (1) | Not failed (2) | Short (3) | Placeholder (4) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes (11, 11 words) | passes |
| Sonnet r1, r2 | passes | passes | passes (10, 9 words) | passes |
| Opus baseline r1, r2 | fails: «Укажите 0 или положительное число» | passes | fails (14, 14 words) | passes |
| Sonnet baseline r1 | fails: «Передайте 0 или положительное число» | fails | fails (13 words) | passes |
| Sonnet baseline r2 | passes | passes | passes (7 words) | passes |

Every new run follows the shape of the §8 port example («должен быть не меньше 0, получено {0}»); the example is a
port, so the results do not rest on copying a fetch-size message.
