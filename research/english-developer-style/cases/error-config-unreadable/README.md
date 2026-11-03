# Case: a configuration file the user cannot read

The input is a command-line tool that cannot open `/etc/foo.yaml` (`EACCES`) and exits. The fix is not to undo
anything the message names: the user joins the file's group or points `FOO_CONFIG` at another file. The case is the
presence check beside `error-negative-fetch-size`: the 2.2.0 rule that keeps an action out of a trivial validation
must keep it in here.

## Skill parts

- `SKILL.md`: §7 (Error and log messages)

## Checks

1. **Names the file and the reason** (`names_file_and_reason`).
2. **Gives an action** (`gives_action`): the group `foo`, or `FOO_CONFIG`.
3. **No consequence** (`no_consequence`). The tool exits; "foo has no default configuration, so it exits" is a
   consequence of a message after which nothing runs.
4. **Length** (`at_most_40_words`).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `0f6d7512`
(`<model>/skill-tree`), the baseline on `9d2eab7`. The baseline skill's error example was
`Set FOO_CONFIG to a readable path`, so the baseline runs had this case's action in front of them.

| Run | File and reason (1) | Action (2) | No consequence (3) | Words (4) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | 31, 31 |
| Sonnet r1, r2 | passes | passes | passes | 24, 25 |
| Opus baseline r1, r2 | passes | passes | passes | 27, 27 |
| Sonnet baseline r1, r2 | passes | passes | fails: "no default configuration" | 29, 27 |

A first draft of the 2.2.0 rule said to add an action "only where" the fix is not undoing the input; one of two Sonnet
runs then dropped the action. The rule as committed states both sides and shows an action in the rule.
