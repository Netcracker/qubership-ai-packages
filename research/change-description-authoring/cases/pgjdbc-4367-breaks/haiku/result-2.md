## Breaking changes

Code that sends several statements in one string, with generated keys requested, gets a different result or an error for a statement after the first `;`.

- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before this change it got no `RETURNING` clause and succeeded. A statement that runs alone already fails the same way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before this change it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- An `INSERT` that is not the first statement, a last statement ending in `?`, or a statement after one that ends in a keyword such as `RETURNING` or `DELETE` now returns its keys as a result set from `getMoreResults()`, where it returned an update count. `getUpdateCount()` is `-1` for it.
- A statement after a `;` that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. Before this change that statement was sent without `RETURNING`.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on the text before it in the same string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when it runs alone. The caller then got an update count where it expected the generated keys. Three defects lead there:

- `INSERT` was recognized only as the first statement of the string. The check sat inside the branch that decides batch-rewrite eligibility, while `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or, after two or more statements, no command type. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before the keyword in front of the `;` was examined, so that keyword set them on the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was loose as well. Any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept in one statement, and the server rejected it.

## What

Each statement is now classified by its own text, so it gets the `RETURNING` clause it gets when it runs alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere is ignored;
- with `BEGIN` and `ATOMIC` as adjacent keywords; a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.

## Verification

Each defect has cases that fail on the parser before the fix, and a control that passes on both.

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

A passing run means the cases above pass on this branch.

`aSemicolonEndsAStatementUnlessInsideABeginAtomicBody` has 21 strings, and 12 of them fail on the old parser. The 6 genuine bodies pass, and so do 3 strings the old parser split correctly by accident, which guard the new checks.

`onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps.

Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The caller-visible outcomes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

## Scope

This change does not narrow which `INSERT` counts, because `explain insert …` and `prepare p as insert …` rely on the same rule.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change. This change leaves that alone.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
