# Case: an empty list the user can fill

The input is the empty «Правила оповещений» page: no rule means no alerts, and the page has a «Создать правило»
button. Here the empty state owes the action. The case is the presence check beside `empty-mentions`.

## Skill parts

- Text above §1 (counts for every case)
- `SKILL.md`: §7 (Пустые состояния)
- `modules/ui-strings.md`: Пустые состояния

## Checks

1. **Gives the action** (`gives_action`): «Создайте…».

## Results

Runs of 2026-10-31, graded by reading; trees as in `empty-mentions`.

| Run | Action (1) |
| --- | --- |
| Opus r1, r2 | passes |
| Sonnet r1 | passes |
| Sonnet r2 | fails: «Пока вы не создадите хотя бы одно, оповещения не отправляются» explains, does not ask |
| Opus baseline r1, r2 | passes |
| Sonnet baseline r1 | fails: describes what a rule is |
| Sonnet baseline r2 | passes |

The draft of 1.1.0 that limited the action to a list the user can fill failed this check in both Sonnet runs (tree
`999f2485`, not committed). Sonnet misses the action in one run of two with the unchanged rule as well; that is a
watch item, not a change of this release.
