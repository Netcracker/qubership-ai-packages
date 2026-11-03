# Case: the commit message for a non-obvious fix

The input is a retry loop that reused a stale token after a 401, with the symptom users saw and the new test. A body
that says why belongs here: this case is the presence check beside `commit-typo`, so that deleting the body rule did not
drop the body where the reader needs it.

## Skill parts

- Text above §1 (the paragraph that hands commit slots to `change-description-authoring`)
- `SKILL.md`: §3 (Сообщение коммита), §11 (the genre item)

## Checks

1. **Has a body** (`has_body`).
2. **The body names the cause** (`names_cause`): the request was retried with the old token.

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`.

| Run | Body (1) | Cause (2) |
| --- | --- | --- |
| Opus r1, r2 | passes | passes |
| Sonnet r1, r2 | passes | passes |
| Opus baseline r1, r2 | passes | passes |
| Sonnet baseline r1, r2 | passes | passes |
