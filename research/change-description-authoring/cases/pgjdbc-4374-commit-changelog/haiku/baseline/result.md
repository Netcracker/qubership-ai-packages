## Commit message

```text
fix: report malformed JDBC function escapes instead of rewriting them

A JDBC function escape has the form {fn name(arguments)}. Without the
parentheses, the driver rewrote the escape into a different statement
instead of reporting it:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)

findOpenParenthesis searched to the end of the statement rather than
to the } that closes the escape. When it found no `(`, escapeFunction
skipped one character and copied the rest, which dropped the n.

findOpenParenthesis now stops at the } that closes the escape. It
skips a delimited identifier, a line comment, and a block comment
whole, because a `(` or `}` inside one of them is not part of the
escape. PostgreSQL accepts both `select 1 as "we}ird"` and
`select 1 as "we(ird"`.

An escape with no `(` before its closing `}` now fails with a
PSQLException that has the position and SQLState 42601, as the other
malformed-escape errors in this parser do. The same applies when the
SQL ends inside the escape, a quoted name, or a comment before the
argument list. Those statements used to be rewritten without an error,
so `select {fn now` became `select ow`.

The quoted-name skip also fixes `{fn "we(ird"()}`, which used to fail
as an unterminated identifier.

Three parameterized tests in ParserTest cover a translated escape, an
escape rejected for a missing argument list, and one reported as
unterminated. The `(` or `}` sits in a quoted name, a block comment, a
line comment, or after the escape. The two errors share SQLState 42601,
so the tests tell them apart by message text. The test JVM runs with
user.language=TR, so a Turkish translation of either message would
break these assertions.

parseBlockComment accepts `/*/` as a complete comment, so in
`select 1 /*/ {fn now} */` the escape is processed as code and fails
with the missing argument list error. On master that statement ran,
because the mangled escape stayed inside what the server reads as a
comment. PR #4363 fixes parseBlockComment and should be merged first.
```

## CHANGELOG.md

```markdown
* fix: a JDBC function escape with no argument list, such as `{fn now}`, is now rejected instead of being rewritten into a different statement. It fails with SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. An escape that the SQL ends inside, including inside a quoted name or a comment before its argument list, fails with SQLState `42601` and the message `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, instead of being rewritten. A `(` or `}` inside a quoted name or comment is now skipped, so `{fn "we(ird"()}` is translated instead of failing as an unterminated identifier. [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
