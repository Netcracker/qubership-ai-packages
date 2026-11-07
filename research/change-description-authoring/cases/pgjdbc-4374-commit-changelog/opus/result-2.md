```text
fix: reject a {fn name} escape without an argument list

A JDBC function escape is written {fn name(arguments)}. Without the
parentheses, the parser did not report an error. It rewrote the escape
into a different statement:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)

The server then failed with `column "ow" does not exist`, or the
statement ran by accident: `select {fn xy} from t` became
`select y from t` for a table with a column `y`. SQL that ended inside
the escape was rewritten the same way with no error, so `select {fn now`
became `select ow`.

findOpenParenthesis searched to the end of the statement, not to the `}`
that closes the escape. When it found no `(`, escapeFunction skipped one
character and copied the rest, which dropped the `n`.

findOpenParenthesis now stops at the `}`. It skips a delimited
identifier, a line comment, and a block comment whole, because a `(` or
`}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. Both new errors are
PSQLException with the position, like the parser's other errors for a
malformed escape.

This change depends on the parseBlockComment fix in #4363.
parseBlockComment takes `/*/` for a complete comment, so in
`select 1 /*/ {fn now} */` the escape is processed as code. Before this
change, the mangled escape stayed inside what the server reads as a
comment, and the statement ran. With this change alone, the statement
fails with the "has no argument list" error.

User-visible changes.
A {fn name} escape with no `(` before the `}` that closes it throws PSQLException with SQLState 42601: `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`
SQL that ends inside the escape, a quoted name, or a comment before the argument list throws PSQLException with SQLState 42601: `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`
`{fn "we(ird"()}` is translated, where it used to fail as an unterminated identifier.

Not changed.
After the `(`, the escape is still scanned without regard to its own `}`: `select {fn now()` becomes `select now()` with no error, `select {fn now(} from t` becomes `select now(} from t)`, and `select {fn now() /* } */}` becomes `select now() /*  */}`.
A line comment between the name and the argument list still hides the argument list: `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`, because trimming the name drops the newline that ended the comment.
```

```markdown
* fix: a JDBC function escape without an argument list, such as `{fn now}`, now throws `PSQLException` with SQLState `42601` and the message `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. Before, the driver rewrote it into another statement: `select {fn now}` became `select ow`, and the server reported `column "ow" does not exist`. SQL that ends inside the escape, a quoted name, or a comment before the argument list, such as `select {fn now`, now throws `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment` with the same SQLState. Before, it was rewritten with no error. `{fn "we(ird"()}` is now translated, where it used to fail as an unterminated identifier. A statement that ran only because of the rewrite now fails: `select {fn xy} from t` used to become `select y from t` on a table with a column `y`. Add the parentheses, as in `{fn xy()}` [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
