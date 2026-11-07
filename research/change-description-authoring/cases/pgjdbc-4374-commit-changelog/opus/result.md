```text
fix: reject {fn name} escapes that have no argument list

A JDBC function escape is written `{fn name(arguments)}`. When the
parentheses were missing, the parser did not report the escape. It
rewrote the escape into a different statement:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)
    select {fn now             ->  select ow

The server rejects the first with `column "ow" does not exist`. Such a
statement could also run by accident: `select {fn xy} from t` became
`select y from t` for a table with a column `y`.

Parser.findOpenParenthesis searched to the end of the statement instead
of stopping at the `}` that closes the escape. When it found no `(`,
escapeFunction skipped one character and copied the rest, which dropped
the `n` of `now`.

findOpenParenthesis now stops at that `}`. It skips a delimited
identifier, a line comment, and a block comment whole, because a `(` or
`}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. Skipping the quoted
name also fixes `{fn "we(ird"()}`, which failed as an unterminated
identifier. Both new errors carry the position, like the other
malformed-escape errors in this parser.

User-visible changes.
When no `(` comes before the `}` that closes a function escape, the driver throws PSQLException with SQLState 42601: `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`
When the SQL ends inside the escape, a quoted name, or a comment before the argument list, the driver throws PSQLException with SQLState 42601: `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`
A statement that ran only because the rewrite happened to produce valid SQL, such as `select {fn xy} from t`, now fails with the first error.
`{fn "we(ird"()}` is translated instead of failing as an unterminated identifier.

Not changed.
After the `(`, the escape is still scanned without regard to its own `}`: `select {fn now(} from t` becomes `select now(} from t)`, and `select {fn now()` becomes `select now()` with no error.
A line comment between the name and the argument list still hides the argument list: `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`, because trimming the name drops the newline that ended the comment.

This change depends on the parseBlockComment fix in PR #4363, and a
backport needs that fix first. Without it, parseBlockComment takes `/*/`
for a complete comment, so the escape in `select 1 /*/ {fn now} */` is
processed as code. That statement ran before this change, because the
server read the mangled escape as part of a comment. With this change
alone, it fails with the "has no argument list" error.
```

`CHANGELOG.md`, under `[Unreleased]` → `### Fixed`:

```markdown
* fix: a JDBC function escape with no argument list, such as `{fn now}`, is now rejected and no longer rewritten into a different statement. Previously `select {fn now}` was sent as `select ow` and failed with `column "ow" does not exist`, and `select {fn xy} from t` ran as `select y from t` when the table had a column `y`. The driver now throws `PSQLException` with SQLState `42601`. When no `(` comes before the `}` that closes the escape, the message is `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. When the SQL ends inside the escape, a quoted name, or a comment, the message is `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. A `(` or `}` inside a quoted name or a comment no longer counts as part of the escape, so `{fn "we(ird"()}` is translated instead of failing as an unterminated identifier. A statement that ran only because the rewrite happened to produce valid SQL now fails [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
