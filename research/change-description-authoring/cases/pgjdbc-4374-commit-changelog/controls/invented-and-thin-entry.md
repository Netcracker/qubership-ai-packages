## Commit message

```text
fix: report malformed {fn} escapes instead of rewriting them

A JDBC function escape is written {fn name(arguments)}. When the
parentheses were missing, the parser rewrote the escape into a different
statement instead of reporting it. findOpenParenthesis searched to the
end of the statement rather than to the } that closes the escape. When
it found no (, escapeFunction skipped one character and copied the
rest, which dropped the first character of the name:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)
    select {fn now             ->  select ow

The server rejected the first statement with column "ow" does not exist.
Other statements ran by accident: select {fn xy} from t became
select y from t for a table with a column y.

findOpenParenthesis now stops at the } that closes the escape. It skips
each delimited identifier, line comment, and block comment as a whole,
because a ( or } inside one is not part of the escape. PostgreSQL accepts
both select 1 as "we}ird" and select 1 as "we(ird". Both new errors are
PSQLException with the position, like the parser's other errors for
malformed escapes.

This change needs the parseBlockComment fix from PR #4363 to be applied
first. Without that fix, /*/ counts as a complete comment, so the escape
in select 1 /*/ {fn now} */ is processed as code. The statement then
fails with the "has no argument list" error. Before this change it ran,
because the mangled escape stayed inside what the server reads as a
comment.

User-visible:
A statement that ran only because its escape was rewritten, such as select {fn xy} from t, now fails with the error on the next line.
`JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`, SQLState 42601, when no ( comes before the } that closes the escape.
`Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, SQLState 42601, when the SQL ends inside the escape, a quoted name, or a comment before the argument list.
{fn "we(ird"()} is translated, where it used to fail as an unterminated identifier.
Not changed: after the (, the parser still scans the escape without regard to its own }, so select {fn now(} from t becomes select now(} from t), and select {fn now() becomes select now() with no error.
Not changed: a line comment between the name and the argument list still hides the argument list, so select {fn abs -- c\n (-1)} becomes select abs -- c(-1).

Fixes #4375
```

## `CHANGELOG.md` entry (under `### Fixed`)

```markdown
* fix: a `{fn name}` escape without an argument list is reported
```
