## Breaking changes

When generated keys are requested (`RETURN_GENERATED_KEYS` or key column names), each statement in a multi-statement string now gets the same `RETURNING` clause it gets when executed alone. Code that relied on the old classification sees these changes. In each case, the old behavior is what this branch was checked against with the 42.7.13 driver.

- **Breaks:** With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). Before, that statement got no `RETURNING` clause and succeeded. The same statement executed alone already fails this way. Request only key columns that the statement's table has.
- **Breaks:** `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). Before, it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- **Breaks:** Three kinds of statement now return their keys as a result set from `getMoreResults()` instead of an update count, and `getUpdateCount()` is `-1` for them:
  - an `INSERT` that is not the first statement;
  - a last statement that ends in `?`;
  - a statement after one that ends in a keyword such as `RETURNING` or `DELETE`.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without its `RETURNING` clause, so it returned an update count where the caller expected keys. Three defects caused this:

- `INSERT` was recognized only as the first statement of the string. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more earlier statements, it got no command type at all. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement, and the server rejected it.

## What

Each statement is now classified by its own text. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, past `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).
- Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, before and after this change.

## Scope

In a statement that starts with an unrecognized keyword, an `INSERT` anywhere in the statement makes the parser classify it as an `INSERT`. With generated keys requested, `grant insert on t to bob` therefore gets `RETURNING` appended and fails with a syntax error. This already happened to the first statement of a string. Now that `INSERT` is recognized in every statement, it also happens to later ones. This change does not narrow which `INSERT` counts, because `explain insert …` and `prepare p as insert …` depend on the same rule.

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. This happens before and after this change.

## How to verify

Some test cases pass on the old parser too, and they are controls. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, the 6 genuine bodies pass on both parsers. So do 3 strings that the old parser split correctly by accident, and they guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps.

Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The caller-visible outcomes above were checked against PostgreSQL 17, once with the 42.7.13 driver and once with this branch.
