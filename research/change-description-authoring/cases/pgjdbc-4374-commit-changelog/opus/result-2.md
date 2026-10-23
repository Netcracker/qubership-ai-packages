```text
fix: report a JDBC {fn} escape without parentheses instead of rewriting it

Previously, a JDBC function escape with no argument list, such as
`{fn now}`, was rewritten into a different statement instead of being
reported:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)

The first one failed on the server with `column "ow" does not exist`.
A statement could also run by accident: `select {fn xy} from t` became
`select y from t` for a table with a column `y`. SQL that ended inside
the escape was rewritten without an error too, so `select {fn now`
became `select ow`.

findOpenParenthesis searched for the `(` up to the end of the statement
instead of up to the `}` that closes the escape. When it found no `(`,
escapeFunction skipped one character and copied the rest, which dropped
the first letter of the name.

findOpenParenthesis now stops at the closing `}`. It skips a delimited
identifier, a line comment, and a block comment as a whole, because a
`(` or `}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. Skipping the quoted
name also fixes `{fn "we(ird"()}`, which used to fail as an unterminated
identifier. Both new errors are PSQLException with the position, like
the other malformed-escape errors in Parser.

User-visible:
A statement that ran only because the rewrite produced valid SQL, such as `select {fn xy} from t`, now fails with the "has no argument list" error below.
When no `(` comes before the `}` that closes the escape: PSQLException, SQLState 42601, `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`
When the SQL ends inside the escape, a quoted name, or a comment before the argument list: PSQLException, SQLState 42601, `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`
`{fn "we(ird"()}` is translated instead of failing as an unterminated identifier.
Not changed: after the `(`, the escape is still scanned without regard to its own `}`, so `select {fn now()` still becomes `select now()` with no error, and `select {fn now(} from t` becomes `select now(} from t)`.
Not changed: a line comment between the name and the argument list still hides the argument list, so `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`.

Merge this after #4363. parseBlockComment takes `/*/` for a complete
comment, so `select 1 /*/ {fn now} */` has its escape processed as code.
Before this change, the mangled escape stayed inside what the server
reads as a comment, and the statement ran. With this change but without
#4363, the statement fails with the "has no argument list" error.
```

```markdown
* **Breaking:** fix: a JDBC function escape with no argument list, such as `{fn now}`, is now reported as `PSQLException` with SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. Previously the driver rewrote it into a different statement: `select {fn now}` reached the server as `select ow` and failed with `column "ow" does not exist`. SQL that ends inside the escape, a quoted name, or a comment before the argument list, such as `select {fn now`, now fails with `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, also SQLState `42601`. A `(` or `}` inside a quoted name or a comment no longer counts as part of the escape, so `{fn "we(ird"()}` is translated instead of failing as an unterminated identifier [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374). Some statements used to run only because the rewrite happened to produce valid SQL, as when `select {fn xy} from t` became `select y from t` for a table with a column `y`. Those statements now fail: add the parentheses to the escape.
```
