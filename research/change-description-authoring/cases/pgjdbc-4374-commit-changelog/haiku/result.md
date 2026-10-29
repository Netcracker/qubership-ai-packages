### Commit message

```text
fix: reject malformed JDBC function escapes instead of rewriting them

A JDBC function escape is written {fn name(arguments)}. Without the
argument list, the driver rewrote the escape into a different statement
instead of reporting it. findOpenParenthesis searched to the end of the
statement rather than to the } that closes the escape, and when it found
no ( , escapeFunction skipped one character of the name and copied the
rest.

select {fn now} became select ow, which the server rejects with column
"ow" does not exist. select {fn xy} from t became select y from t, which
ran against a table with a column y. select {fn now became select ow
with no error.

findOpenParenthesis now stops at the } that closes the escape. It skips a
quoted identifier, a line comment, or a block comment whole, because a (
or } inside one of them is not part of the escape. PostgreSQL accepts
both select 1 as "we}ird" and select 1 as "we(ird".

User-visible:
An escape with no ( before the } that closes it throws PSQLException with SQLState 42601 and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. Write the argument list, as in {fn now()}, in any statement that relied on the old rewrite.
An escape that the SQL ends inside, a quoted name, or a comment before its argument list throws PSQLException with SQLState 42601 and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. Close the escape in any statement that relied on the old rewrite.
A quoted function name that contains ( , such as {fn "we(ird"()}, is translated. It used to fail as an unterminated identifier.

Not changed:
A line comment between the function name and the argument list still hides the argument list: select {fn abs -- c\n (-1)} becomes select abs -- c(-1), where \n is a newline.
After the ( , the escape is still scanned without regard to its own } : select {fn now(} from t becomes select now(} from t), select {fn now() /* } */} becomes select now() /*  */}, and select {fn now() becomes select now() with no error.
```

### CHANGELOG.md

```markdown
* **Breaking:** fix: a JDBC function escape with no argument list, such as `{fn now}`, is rejected with `PSQLException` instead of being rewritten into another statement. Before, `select {fn now}` was sent to the server as `select ow`, and `select {fn xy} from t` as `select y from t`, which ran against a table with a column `y`. The error has SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. An escape that the SQL ends inside, such as `select {fn now`, is also rejected with SQLState `42601` and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. Write the argument list, as in `{fn now()}`, and close every escape in any statement that relied on the rewrite. A `(` or `}` inside a quoted name or a comment is no longer read as part of the escape, so `{fn "we(ird"()}` is now translated. [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
