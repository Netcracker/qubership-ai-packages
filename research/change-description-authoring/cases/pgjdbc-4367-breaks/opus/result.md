This changes what code gets when it runs a multi-statement string with generated keys requested (`RETURN_GENERATED_KEYS` or key column names).

## Breaking changes

- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before this change, it got no `RETURNING` clause and succeeded. The same statement executed alone already failed this way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before this change, it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- Some statements now return their keys as a result set from `getMoreResults()` instead of an update count, and `getUpdateCount()` is `-1` for them. This applies to an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement that follows one ending in a keyword such as `RETURNING` or `DELETE`.
- A later statement that starts with an unrecognized keyword and contains `INSERT` now gets `RETURNING` appended and fails with a syntax error. `grant insert on t to bob` is an example. The first statement of a string already failed this way.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. As a result, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected generated keys. Three defects caused this:

- `INSERT` was recognized only in the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type at all. This affects a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so the parser kept `create table begin(atomic int); insert into t(a) values(?)` as one statement, and the server rejected it.

## What

Each statement is now classified by its own text, so it gets the same `RETURNING` clause it gets when executed alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword after any `OR REPLACE` is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.

## Scope

The parser classifies a statement that starts with an unrecognized keyword as an `INSERT` if `INSERT` appears anywhere in it. This change does not narrow that rule, because `explain insert …` and `prepare p as insert …` rely on it. That rule causes the `grant` break above.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. This happens before and after this change.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Each defect has cases that fail on the old parser, plus a control that passes on both. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The 6 real bodies pass on both, and so do 3 strings that the old parser split correctly by accident; those 3 guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps.

Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes under "Breaking changes" (except the `grant` line) and under "User-visible changes" were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.
