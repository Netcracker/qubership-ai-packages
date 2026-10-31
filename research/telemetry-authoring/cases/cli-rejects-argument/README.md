# Case: a CLI rejecting its flag

The input is a Go command-line tool rejecting `--jobs` below 1 before anything connects. The fix is to pass a positive
integer, and the process exits after the message. The case is the second negative control for the subsection on what a
message on the caller's channel carries, on a CLI rather than a library and outside the JVM.

## Skill parts

- `SKILL.md`: §2 (What a message on the caller's channel carries)
- `english-developer-style`: §7 (Error and log messages)

## Checks

1. **Names the flag and the value** (`names_flag_and_value`): `--jobs` and the `%d` verb.
1. **One sentence** (`one_sentence`). No clause on what `--jobs` does, and no list of values to try or of the default.
1. **Short** (`message_at_most_15_words`).

## Results

Runs of 2026-10-31 on the skill at `9d2eab7` are under `<model>/baseline/`; the results of the skill these checks
test come with it.
