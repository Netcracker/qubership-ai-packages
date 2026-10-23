# Task

Write, for the change below, the commit message (the branch has one commit) and the entry for `CHANGELOG.md`, in
Markdown. The facts come from the author's pull request description, which was checked against the code and against a
running server; treat every fact in it as verified, and add none that it does not carry.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`. Its `gradle.properties` says
  `pgjdbc.version=42.7.14`; the latest release tag is `REL42.7.13`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`; the maintainers squash or rebase each pull request as they see fit.
- The history uses Conventional Commits subjects with a lowercase verb after the prefix. No issue was filed for this
  defect. The pull request is #4374.
- Files changed: `CHANGELOG.md`, `pgjdbc/src/main/java/org/postgresql/core/Parser.java` +39 -8,
  `pgjdbc/src/test/java/org/postgresql/core/ParserTest.java` +100 -0.
- `CHANGELOG.md` follows Keep a Changelog. The `[Unreleased]` section has `### Fixed`, `### Changed`, and
  `### Security` lists; two of its entries, as written:

  ```markdown
  * fix: `LargeObjectManager` operations now work inside an active XA transaction. Since 42.7.13 an XA branch keeps the caller's `autoCommit=true`, and the guard rejected large objects as if the connection were idle. It now checks the server transaction state (`getTransactionState()`) instead of `autoCommit`, so a genuine auto-commit connection with no open transaction is still refused [Issue #4309](https://github.com/pgjdbc/pgjdbc/issues/4309) [PR #4310](https://github.com/pgjdbc/pgjdbc/pull/4310)
  * fix: a protocol violation before authentication is reported as `PSQLException` with SQLState `08P01` rather than as a plain I/O error, and is no longer retried under `sslMode=allow` or `sslMode=prefer` [Issue #4015](https://github.com/pgjdbc/pgjdbc/issues/4015)
  ```

## The author's pull request description

````markdown
## Why

A JDBC function escape is written `{fn name(arguments)}`. Without the parentheses the driver rewrote the escape into a different statement instead of reporting it:

```text
select {fn now}            ->  select ow             -- server: column "ow" does not exist
select {fn now} from (t)   ->  select now} from(t)
```

`findOpenParenthesis` searched to the end of the statement rather than to the `}` that closes the escape, and when it found no `(`, `escapeFunction` skipped one character and copied the rest, which drops the `n`.

## What

`findOpenParenthesis` stops at the `}` and skips a delimited identifier, a line comment, and a block comment whole, since a `(` or `}` inside one is not part of the escape; PostgreSQL accepts both `select 1 as "we}ird"` and `select 1 as "we(ird"`. Both new errors are `PSQLException` with the position, like the other malformed-escape errors in this parser. The quoted-name skip also fixes `{fn "we(ird"()}`, which used to fail as an unterminated identifier.

## What the caller sees

- `JDBC escape function name at position {0} in SQL {1} has no argument list. Expected a name followed by parentheses, as in {fn now()}`, SQLState `42601`, when no `(` precedes the `}` that closes the escape. Such a statement used to reach the server rewritten, and could run only by accident, as when `select {fn xy} from t` became `select y from t` for a table with a column `y`.
- `Unterminated JDBC escape function call whose name starts at position {0} in SQL {1}. The SQL ends inside the escape, a quoted name, or a comment`, SQLState `42601`, when the SQL ends inside the escape, a quoted name, or a comment before the argument list. These used to be rewritten without an error: `select {fn now` became `select ow`.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

The three new parameterized tests cover an escape that is translated, one rejected for a missing argument list, and one reported as unterminated, with the `(` or `}` placed in a quoted name, a block comment, a line comment, and after the escape. Against `master`, every rejection and unterminated case fails, as do the translation cases with `(` inside a quoted name or a block comment; the other six translation cases pass there on purpose, so a scan that over-reaches fails them.

The two errors share SQLState 42601, so the tests tell them apart by message text. The test JVM runs with `user.language=TR`, so a Turkish translation of either message would break these assertions.

## Not fixed here

- A line comment between the name and the argument list still hides the argument list: `select {fn abs -- c\n (-1)}` becomes `select abs -- c(-1)`, because trimming the name drops the newline that ended the comment. This is the same on `master`.
- After the `(`, the escape is still scanned without regard to its own `}`: `select {fn now(} from t` becomes `select now(} from t)`, `select {fn now() /* } */}` becomes `select now() /*  */}`, and `select {fn now()` becomes `select now()` with no error. These are the same on `master`.
- `parseBlockComment` takes `/*/` for a complete comment, so in `select 1 /*/ {fn now} */` the escape is processed as code. On `master` the mangled escape stayed inside what the server reads as a comment and the statement ran; with this change alone it fails with the "has no argument list" error. [PR #4363](https://github.com/pgjdbc/pgjdbc/pull/4363) fixes `parseBlockComment`, and this PR should not be merged before it.


````
