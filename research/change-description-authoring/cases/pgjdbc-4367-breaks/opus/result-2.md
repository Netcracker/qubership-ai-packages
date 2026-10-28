With generated keys requested (`RETURN_GENERATED_KEYS` or key column names), statements after a `;` in a multi-statement string now get a `RETURNING` clause in more cases. Code that relied on those statements running without one breaks as follows.

## Breaking changes

- With key column names, a statement after a `;` whose table lacks one of those columns now fails with `column "id" does not exist` (SQLState `42703`). With 42.7.13 it got no `RETURNING` and succeeded. The same statement executed alone already fails this way.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, now fails with `A result was returned when none was expected.` (SQLState `0100E`). With 42.7.13 it returned the update count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- With generated keys requested, some statements now return their keys from `getMoreResults()` as a result set where 42.7.13 returned an update count, and `getUpdateCount()` is `-1` for them. This applies to an `INSERT` that is not the first statement, to a last statement that ends in `?`, and to a statement that follows one ending in a keyword such as `RETURNING` or `DELETE`.
- With generated keys requested, a later statement that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. It used to run because `INSERT` was not recognized after the first statement. The first statement of a string already failed this way.

## Why

`Parser.parseJdbcSql` classified a statement differently depending on what came before it in the string. With generated keys requested, a statement after a `;` could be sent without the `RETURNING` clause it gets when executed alone. It then returned an update count where the caller expected the generated keys. Three defects caused this:

- The parser recognized `INSERT` only as the first statement of the string, because the check was inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- The parser read a `?` as the last character as an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements it got no command type at all. A common string has this shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags of the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was also too loose: any two consecutive keywords after any `CREATE` opened a body. `BEGIN` and `ATOMIC` are ordinary identifiers, so `create table begin(atomic int); insert into t(a) values(?)` was kept as one statement, and the server rejected it.

## What

The parser now classifies each statement by its own text, so each statement gets the `RETURNING` clause it gets when executed alone. Batch-rewrite eligibility is unchanged: only the first statement can be rewritten.

The parser still treats a statement as an `INSERT` when it starts with an unrecognized keyword and contains `INSERT` anywhere. This change does not narrow that rule, because `explain insert …` and `prepare p as insert …` depend on it. The `grant` break above follows from it.

A `BEGIN ATOMIC` body is now detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword after `OR REPLACE` is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not count;
- when `BEGIN` and `ATOMIC` are adjacent keywords; a comment may stand between them, but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

## User-visible changes

- `create table begin(atomic int); insert into t(a) values(?)` no longer fails with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Not changed: `getGeneratedKeys()` returns no rows for a multi-statement string, both before and after this change.

## Scope

With `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error. This happens both before and after this change, and the change does not address it.

## How to verify

In `ParserTest`, each defect also has a control case that passes on both the old and the new parser. In `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`, 9 of the 21 strings pass on the old parser. Six are real bodies. The other three are strings that the old parser split correctly by accident, and they guard the new checks. `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible` pins the batch-rewrite rule that this change keeps, and it passes on both.

Every SQL string in the tests runs on PostgreSQL 17, except the two whose test names say "invalid SQL". The caller-visible outcomes above were checked against PostgreSQL 17 with the 42.7.13 driver and with this branch.
