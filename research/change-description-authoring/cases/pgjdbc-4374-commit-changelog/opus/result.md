**Commit message**

```text
fix: reject a JDBC {fn} escape that has no argument list

A JDBC function escape is written `{fn name(arguments)}`. Without the
parentheses, the driver rewrote the escape into a different statement
instead of reporting it:

    select {fn now}            ->  select ow
    select {fn now} from (t)   ->  select now} from(t)
    select {fn now             ->  select ow

The server then failed the first one with `column "ow" does not exist`.
A rewritten statement could also run by accident. For example,
`select {fn xy} from t` became `select y from t` for a table with a
column `y`.

findOpenParenthesis searched to the end of the statement rather than to
the `}` that closes the escape. When it found no `(`, escapeFunction
skipped one character and copied the rest, which dropped the `n`.

findOpenParenthesis now stops at that `}`. It skips a delimited
identifier, a line comment, and a block comment whole, because a `(` or
`}` inside one is not part of the escape. PostgreSQL accepts both
`select 1 as "we}ird"` and `select 1 as "we(ird"`. Both new errors are
PSQLException with the position, like the other malformed-escape errors
in Parser.

User-visible:
When no `(` precedes the `}` that closes the escape: PSQLException `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`, SQLState 42601.
When the SQL ends inside the escape, a quoted name, or a comment before the argument list: PSQLException `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, SQLState 42601.
`{fn "we(ird"()}` is translated, where it used to fail as an unterminated identifier.
Not changed: after the `(`, the escape is still scanned without regard to its own `}`, so `select {fn now()` becomes `select now()` with no error.
Not changed: a line comment between the name and the argument list still hides the argument list: `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`.

parseBlockComment treats `/*/` as a complete comment, so the escape in
`select 1 /*/ {fn now} */` is processed as code. That statement used to
run, because the mangled escape stayed inside what the server reads as a
comment. With this commit alone, it fails with the "has no argument
list" error. Apply PR #4363, which fixes parseBlockComment, before this
commit.
```

**`CHANGELOG.md` entry** (under `[Unreleased]` → `### Fixed`)

```markdown
* fix: a JDBC function escape with no argument list, such as `{fn now}`, is rejected with `PSQLException` and SQLState `42601` instead of being rewritten into a different statement. The error is `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`. Before this fix, `select {fn now}` was sent as `select ow` and failed with `column "ow" does not exist`. SQL that ends inside the escape, a quoted name, or a comment before the argument list now fails with `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, SQLState `42601`. Before this fix, `select {fn now` became `select ow` without an error. `{fn "we(ird"()}` no longer fails as an unterminated identifier. A statement that ran only because of the rewrite now fails, so add the parentheses. For example, `select {fn xy} from t` used to become `select y from t` for a table with a column `y` [PR #4374](https://github.com/pgjdbc/pgjdbc/pull/4374)
```
