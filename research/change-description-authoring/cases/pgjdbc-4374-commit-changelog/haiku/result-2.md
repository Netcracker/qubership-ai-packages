**Commit message**

```text
fix: report malformed JDBC function escapes instead of rewriting them

A JDBC function escape is written {fn name(arguments)}. Without the
argument list, the driver rewrote the escape into a different
statement, and the server ran that statement instead:

    select {fn now}        ->  select ow
    select {fn xy} from t  ->  select y from t

The first fails on the server with `column "ow" does not exist`. The
second runs and selects column y instead of calling the function, if
the table has a column y. An unterminated escape was rewritten the
same way: `select {fn now` became `select ow` with no error.

`findOpenParenthesis` searched to the end of the statement instead of
stopping at the `}` that closes the escape, so a `(` after the escape
was taken as its argument list. It now stops at that `}`, and it skips
a quoted identifier, a line comment, or a block comment whole, since a
`(` or `}` inside one is not part of the escape. PostgreSQL accepts
both `select 1 as "we}ird"` and `select 1 as "we(ird"`. An escape with
no argument list, or one the SQL ends inside before its argument list,
is now reported as a PSQLException with the position, like the other
malformed-escape errors in this parser.

User-visible:
An escape with no argument list, such as `select {fn now}`, fails with SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`.
An escape the SQL ends inside before its argument list, such as `select {fn now`, fails with SQLState `42601` and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`.
An escape whose quoted name contains `(` or `}`, such as `{fn "we(ird"()}`, is translated, where it used to fail as an unterminated identifier.

Not changed:
A line comment between the function name and its argument list still hides the argument list: `select {fn abs -- c`, a newline, and `(-1)}` become `select abs -- c(-1)`.
Text after the `(` is still scanned without regard to the escape's own `}`: `select {fn now(} from t` becomes `select now(} from t)`, and `select {fn now()` becomes `select now()` with no error.
```

**CHANGELOG.md**

```markdown
* **Breaking:** fix: a JDBC function escape with no argument list, such as `select {fn now}`, or one the SQL ends inside before its argument list, such as `select {fn now`, now fails with SQLState `42601` instead of being rewritten and sent to the server. The messages are `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}` and `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. An escape whose quoted name contains `(` or `}`, such as `{fn "we(ird"()}`, is now translated, where it used to fail as an unterminated identifier. [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374) Add the parentheses to each function escape that lacks them.
```
