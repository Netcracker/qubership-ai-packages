# Case: a doc comment for `ParsePort`

The input is a Go function that returns a wrapped `strconv` error or `ErrPortRange`. The errors and the range are
beyond the signature, so they belong: this case is the presence check beside `docstring-len`.

## Skill parts

- Text above §1 (the paragraph that hands doc-comment slots to the doc-comment skill of the language)
- `SKILL.md`: §3 (Docstring), §9 (Комментарии в коде и docstrings)
- `modules/code-comments.md`: Docstring и Javadoc/KDoc/TSDoc
- `examples/before-after.md`: docstring функции

## Checks

1. **Names `ErrPortRange`** (`names_error`).
2. **Names the range** (`names_range`).

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`. Every run of both arms passes both
checks.
