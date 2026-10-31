# Case: an empty list the user cannot fill

The input is the empty «Упоминания» tab: entries appear only when someone else mentions the user, and the tab has no
buttons. «Создайте…» or «Добавьте…» would send the user to an action that does not exist. The case is the negative
control for §7 *Пустые состояния* («что произошло и что делать»).

## Skill parts

- Text above §1 (counts for every case)
- `SKILL.md`: §7 (Пустые состояния)
- `modules/ui-strings.md`: Пустые состояния

## Checks

1. **No action to create** (`no_create_action`).
2. **At most 20 words** (`at_most_20_words`).

## Results

Runs of 2026-10-31, graded by reading; skill tree `230514d8` for the new arm, `51b8d41` (tree `6c0cb228`) for the
baseline. Every run of both arms passes both checks and says what will appear on the tab.

A draft of 1.1.0 limited the action to a list the user can fill. Neither arm misfired here, and on that draft Sonnet
gave no action in `empty-alert-rules` in 2 runs of 2, so the draft was reverted and §7 is unchanged in 1.1.0. These
results stand for the unchanged rule.
