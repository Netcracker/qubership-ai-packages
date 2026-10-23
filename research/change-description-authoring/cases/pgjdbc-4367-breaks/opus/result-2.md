With generated keys requested, some multi-statement strings now return a different result shape, or fail where they used to succeed. Code that calls `getMoreResults()`, `executeUpdate()`, or passes key column names on such strings should check the lines below.

## Breaking changes

- With generated keys requested, three kinds of statement now return their keys as a result set from `getMoreResults()`, and `getUpdateCount()` is `-1` for them: an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement that follows one ending in a keyword such as `RETURNING` or `DELETE`. With 42.7.13 each of them returned an update count. Code that reads the count for such a statement now has to read the result set instead.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). With 42.7.13 it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). With 42.7.13 it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- With generated keys requested, a statement after the first that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. Before this change only the first statement of a string failed this way.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested (`RETURN_GENERATED_KEYS` or key column names), a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected the generated keys. Three defects caused this:

- The parser recognized `INSERT` only as the first statement of the string, because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- The parser took a `?` as the last character for an empty statement after the last `;`. The last statement then inherited the command type and the `RETURNING` flag of the statement before it, or got no command type after two or more statements. This affects a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the parser classified the `UPDATE` as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so the parser kept `create table begin(atomic int); insert into t(a) values(?)` as one statement, and the server rejected it.

## What

The parser now classifies each statement by its own text, so each statement gets the same `RETURNING` clause it gets when executed alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

The parser detects a `BEGIN ATOMIC` body only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, after any `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not open a body;
- with `BEGIN` and `ATOMIC` as adjacent keywords: a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: for a multi-statement string, `getGeneratedKeys()` returns no rows, both before and after this change.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Each defect has cases that fail on the parser before the fix, plus a control that passes on both versions. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 12 of the 21 strings fail on the old parser. The 6 genuine bodies pass on both. So do 3 strings that the old parser split correctly by accident, and they guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps.

Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The outcomes listed above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.

## Scope

A statement that starts with an unrecognized keyword is classified as an `INSERT` if `INSERT` appears anywhere in it. This change does not narrow that rule, because `explain insert …` and `prepare p as insert …` depend on it. The cost is the `grant insert` break listed above.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. That happens both before and after this change, and it is outside this change.
