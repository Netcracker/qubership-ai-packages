**Commit message**

```text
fix: reject a JDBC function escape that has no argument list

A JDBC function escape is written `{fn name(arguments)}`. Without the
parentheses, the parser rewrote the escape into a different statement
instead of reporting it:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)

The server then failed with `column "ow" does not exist`. A statement
could also run by accident: `select {fn xy} from t` became
`select y from t` for a table with a column `y`. SQL that ended inside
the escape was rewritten the same way, so `select {fn now` became
`select ow`.

`findOpenParenthesis` searched to the end of the statement rather than
to the `}` that closes the escape. When it found no `(`, `escapeFunction`
skipped one character and copied the rest, which dropped the `n`.

`findOpenParenthesis` now stops at the `}`. It skips a delimited
identifier, a line comment, and a block comment whole, because a `(` or
`}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. Both new errors are
`PSQLException` with the position, like the other malformed-escape
errors in this parser.

User-visible:
When no `(` precedes the `}` that closes the escape: `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`, SQLState 42601.
When the SQL ends inside the escape, a quoted name, or a comment before the argument list: `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, SQLState 42601.
`{fn "we(ird"()}` is translated; it used to fail as an unterminated identifier.
Not changed: a line comment between the name and the argument list still hides the argument list, so `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`.
Not changed: after the `(`, the escape is still scanned without regard to its own `}`, so `select {fn now(} from t` becomes `select now(} from t)` and `select {fn now()` becomes `select now()` with no error.

This change needs the `parseBlockComment` fix from PR #4363 first.
Without it, `/*/` counts as a complete comment, so the escape in
`select 1 /*/ {fn now} */` is processed as code. That statement used to
run, and it would fail with the "has no argument list" error.
```

**`CHANGELOG.md` entry, under `### Fixed`**

```markdown
* fix: a JDBC function escape without an argument list, such as `{fn now}`, is now reported as `PSQLException` with SQLState `42601` instead of being rewritten into a different statement. Previously `select {fn now}` reached the server as `select ow` and failed with `column "ow" does not exist`, and `select {fn now` was rewritten the same way. The new messages are `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}` and `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. A `(` or `}` inside a quoted name or a comment no longer ends the function name, so `{fn "we(ird"()}` now works. Some statements used to run only because of the rewrite, such as `select {fn xy} from t` running as `select y from t`, and these now fail [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
