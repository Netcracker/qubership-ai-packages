## Why

With generated keys requested (`RETURN_GENERATED_KEYS` or key column names), a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone, so it returned an update count where the caller expected the generated keys. `Parser.parseJdbcSql` classified each statement by what came before it in the string, through three defects:

- `INSERT` was recognized only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it, or no command type after two or more statements. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1` the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was loose as well: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement, and the server rejected it.

## What

Each statement is classified by its own text, so it gets the `RETURNING` clause it gets alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them and a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- **Breaks:** with key column names, a statement after a `;` whose table lacks one of those columns fails with `column "id" does not exist` (SQLState `42703`). With the 42.7.13 driver it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- **Breaks:** `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, fails with `A result was returned when none was expected.` (SQLState `0100E`). With the 42.7.13 driver it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- With generated keys requested, an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement after one that ends in a keyword such as `RETURNING` or `DELETE` return their keys as a result set from `getMoreResults()` instead of an update count, and `getUpdateCount()` is `-1` for them.
- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Each defect has cases that fail on the old parser and a control that passes on both. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The 6 genuine bodies pass on both, and so do 3 strings the old parser split correctly by accident, which guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule this change keeps. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The user-visible changes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

## Scope

A statement that starts with an unrecognized keyword and contains `INSERT` anywhere is classified as an `INSERT`. With generated keys requested, `grant insert on t to bob` therefore gets `RETURNING` appended and fails with a syntax error. That already happened for the first statement of a string, and recognizing `INSERT` in every statement extends it to the later ones. This change does not narrow which `INSERT` counts, because `explain insert …` and `prepare p as insert …` rely on the same rule.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change.
