## Commit message

```text
fix: reject a JDBC function escape that has no argument list

A JDBC function escape is written `{fn name(arguments)}`. Without the
parentheses, the parser rewrote the escape into a different statement
instead of reporting an error:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)

findOpenParenthesis searched to the end of the statement rather than to
the `}` that closes the escape. When it found no `(`, escapeFunction
skipped one character and copied the rest, which dropped the `n`. Such a
statement reached the server rewritten and could run by accident:
`select {fn xy} from t` became `select y from t` for a table with a
column `y`.

findOpenParenthesis now stops at the `}` that closes the escape. It skips
a delimited identifier, a line comment, and a block comment whole,
because a `(` or `}` inside one is not part of the escape. The parser
reports two new errors. Both are PSQLException with SQLState 42601 and
the position of the name, like the other malformed-escape errors in the
parser:

- "JDBC escape function name at position {0} in SQL {1} has no argument
  list" when no `(` precedes the `}` that closes the escape.
- "Unterminated JDBC escape function call whose name starts at position
  {0} in SQL {1}" when the SQL ends inside the escape, a quoted name, or
  a comment before the argument list. `select {fn now` used to become
  `select ow` with no error.

Skipping the quoted name also fixes `{fn "we(ird"()}`, which used to fail
as an unterminated identifier.

parseBlockComment takes `/*/` for a complete comment, so in
`select 1 /*/ {fn now} */` the parser processes the escape as code.
Before this change, the mangled escape stayed inside what the server
reads as a comment, and the statement ran. With this change alone, it
fails with the "has no argument list" error. PR #4363 fixes
parseBlockComment.

These cases behave as they did before this change:

- A line comment between the name and the argument list hides the
  argument list: `select {fn abs -- c\n (-1)}` becomes
  `select abs -- c(-1)`, because trimming the name drops the newline
  that ended the comment.
- After the `(`, the parser scans the escape without regard to its own
  `}`: `select {fn now(} from t` becomes `select now(} from t)`, and
  `select {fn now()` becomes `select now()` with no error.
```

## `CHANGELOG.md` entry (under `[Unreleased]`, `### Fixed`)

```markdown
* fix: a JDBC function escape without an argument list, such as `select {fn now}`, is rejected with `PSQLException` and SQLState `42601` instead of being rewritten into a different statement. The driver used to send it to the server as `select ow`, and a statement such as `select {fn xy} from t` ran as `select y from t` when the table had a column `y`. The error text starts with `JDBC escape function name at position`, and ends with `has no argument list` after the position and SQL. When the SQL ends inside the escape, a quoted name, or a comment before the argument list, the error starts with `Unterminated JDBC escape function call`. A `(` or `}` inside a quoted name or a comment no longer counts as part of the escape, so `{fn "we(ird"()}` is translated instead of failing as an unterminated identifier [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
