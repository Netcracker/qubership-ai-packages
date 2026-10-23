**Commit message**

```text
fix: reject malformed JDBC function escapes instead of rewriting them

Previously, a JDBC function escape without an argument list, such as {fn now},
was rewritten into a different statement instead of being reported.
findOpenParenthesis searched to the end of the statement rather than to
the } that closes the escape. When it found no (, escapeFunction skipped
one character and copied the rest, which dropped the n.

select {fn now} reached the server as select ow, and the server failed with
column "ow" does not exist. An escape that the SQL ends inside, such as
select {fn now, was rewritten the same way with no error.

findOpenParenthesis now stops at the } that closes the escape. It skips a
delimited identifier, a line comment, and a block comment whole, because a
( or } inside one is not part of the escape. PostgreSQL accepts both
select 1 as "we}ird" and select 1 as "we(ird". An escape with no ( before
its closing } is reported, and so is one whose SQL ends before its argument
list. Both errors are PSQLException with the position, like the other
malformed-escape errors in this parser.

User-visible:
An escape with no ( before its closing } is now rejected instead of being rewritten. select {fn xy} from t used to run as select y from t, which only worked for a table with a column y. It now fails with PSQLException, SQLState 42601, and the message "JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}". Add the parentheses, as in {fn xy()}.
An escape whose SQL ends inside it, a quoted name, or a comment before its argument list is now rejected instead of being rewritten without an error. select {fn now used to become select ow. It now fails with PSQLException, SQLState 42601, and the message "Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment".
A ( or } inside a quoted name, a line comment, or a block comment is no longer taken as part of the escape: {fn "we(ird"()} is translated, where it used to fail as an unterminated identifier.

Not changed:
A line comment between the name and the argument list still hides the argument list: select {fn abs -- c, then a line break and (-1)}, still becomes select abs -- c(-1).
Text after the ( is still scanned without regard to the escape's own }: select {fn now(} from t still becomes select now(} from t), select {fn now() /* } */} becomes select now() /*  */}, and select {fn now() still becomes select now() with no error.
```

**CHANGELOG.md**

```markdown
* **Breaking:** fix: a JDBC function escape with no `(` before its closing `}`, such as `{fn xy}`, is now rejected instead of being rewritten into another statement. `select {fn xy} from t` used to run as `select y from t`, which only worked for a table with a column `y`. Add the parentheses, as in `{fn xy()}`. The error is SQLState `42601` with the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. An escape whose SQL ends inside it, a quoted name, or a comment before its argument list is also rejected with SQLState `42601`, with the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`. It used to be rewritten without an error, as `select {fn now` became `select ow`. A `(` or `}` inside a quoted name or a comment is no longer taken as part of the escape, so `{fn "we(ird"()}` is translated instead of failing as an unterminated identifier. [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
