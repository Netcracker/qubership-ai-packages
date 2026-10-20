**Commit message**

```text
fix: report malformed {fn} escapes instead of rewriting them

A JDBC function escape is written `{fn name(arguments)}`. Without the
parentheses, the driver rewrote the escape into a different statement
instead of reporting it: `select {fn now}` became `select ow`, which the
server rejects with `column "ow" does not exist`, and `select {fn xy} from t`
became `select y from t`, which runs against a table with a column `y`.

The cause is in `findOpenParenthesis`, which searched to the end of the
statement rather than to the `}` that closes the escape. When it found no
`(`, `escapeFunction` skipped one character and copied the rest, which
drops the `n`.

`findOpenParenthesis` now stops at the `}` that closes the escape. It also
skips a quoted identifier, a line comment, and a block comment whole, since a
`(` or `}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. An escape with no `(`
before its `}` is now refused, and so is an escape that the SQL ends inside
before its argument list. Both are `PSQLException`s with SQLState `42601` and
the position, like the other malformed-escape errors in this parser.

User-visible:
An escape with no argument list, such as `{fn now}`, fails in the driver with PSQLException, SQLState 42601, and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`.
An escape that the SQL ends inside before its argument list fails with PSQLException, SQLState 42601, and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`.
An escape whose quoted name contains `(`, such as `{fn "we(ird"()}`, is translated instead of failing as an unterminated identifier.

Not changed:
A line comment between the name and the argument list still hides the argument list: `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`, as before this change.
After the `(`, the escape is still scanned without regard to its own `}`: `select {fn now(} from t` becomes `select now(} from t)`, as before this change.
An escape that ends after its argument list, as in `select {fn now()`, still becomes `select now()` with no error, as before this change.
```

**CHANGELOG.md**

```markdown
* **Breaking:** fix: report malformed JDBC function escapes instead of rewriting them. An escape with no argument list, such as `{fn now}`, is now refused by the driver with SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. An escape that the SQL ends inside before its argument list now fails with SQLState `42601` and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. An escape whose quoted name contains `(`, such as `{fn "we(ird"()}`, is now translated instead of failing as an unterminated identifier. Before, `select {fn now}` became `select ow`, which the server rejected with `column "ow" does not exist`, and `select {fn now` became `select ow` with no error. [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374) A statement that ran only because the rewrite was valid SQL, such as `select {fn xy} from t` on a table with a column `y`, now fails, so add the argument list, as in `{fn now()}`.
```
