**Breaking changes.**
These breaks affect code that requests generated keys (`RETURN_GENERATED_KEYS` or key column names) for a string of several statements. The statements after the first now get the `RETURNING` clause they get when executed alone. Before this change, the driver sent them without it (checked with 42.7.13).

- With generated keys requested, three kinds of statement now return their keys as a result set from `getMoreResults()` instead of an update count: an `INSERT` that is not the first statement, a last statement that ends in `?`, and a statement after one that ends in a keyword such as `RETURNING` or `DELETE`. `getUpdateCount()` is `-1` for these statements.
- `executeUpdate()` on a statement prepared with generated keys, such as `set search_path to public; insert into t(a) values(?)`, fails with `A result was returned when none was expected.` (SQLState `0100E`). Before this change it returned the count of the first statement and no keys. A string whose last statement is an `UPDATE` or `DELETE` that does not end in `?` already failed this way.
- With key column names, a statement after a `;` fails with `column "id" does not exist` (SQLState `42703`) if its table lacks one of those columns. Before this change it got no `RETURNING` and succeeded. Executed alone, such a statement already fails the same way.
- A statement after a `;` that starts with an unrecognized keyword and contains `INSERT`, such as `grant insert on t to bob`, now gets `RETURNING` appended and fails with a syntax error. The first statement of a string already failed this way.

`Parser.parseJdbcSql` classified a statement by what came before it in the string. As a result, a statement after a `;` could lose the `RETURNING` clause it gets when executed alone. There were three causes:

- `INSERT` was recognized only in the first statement because the check sat inside the branch that decides batch-rewrite eligibility. `UPDATE` and `DELETE` had no such limit.
- A `?` as the last character was taken for an empty statement after the last `;`. The last statement then took the command type and `RETURNING` flag of the statement before it. After two or more statements, it got no command type at all. This hits a common shape: `update t set a=1; update t set a=?`.
- The `;` branch reset the statement flags before it examined the keyword in front of the `;`, so that keyword set the flags on the next statement. In `select; update t set a=1`, the `UPDATE` was classified as a `SELECT`.

`BEGIN ATOMIC` detection was too loose. Any `CREATE` followed by the keywords `BEGIN` and `ATOMIC` opened a body, but `BEGIN` and `ATOMIC` are ordinary identifiers. So `create table begin(atomic int); insert into t(a) values(?)` stayed one statement and failed with `cannot insert multiple commands into a prepared statement` (SQLState `42601`).

Each statement is now classified by its own text. A `BEGIN ATOMIC` body is detected only where PostgreSQL allows one:

- in a `CREATE` whose object keyword, after an optional `OR REPLACE`, is `FUNCTION` or `PROCEDURE`, so a column or alias named `function` elsewhere does not open a body;
- with `BEGIN` and `ATOMIC` as adjacent keywords, where a comment may stand between them but a comma, a parenthesis, a quoted identifier, or a literal may not;
- outside parentheses, so `return (select begin atomic from t)` is not a body.

**Not changed.**
- Only the first statement of a string can be batch-rewritten.
- `getGeneratedKeys()` returns no rows for a multi-statement string.

**Scope.** This change does not narrow which `INSERT` counts. A statement that starts with an unrecognized keyword and contains `INSERT` anywhere is classified as an `INSERT`, and `explain insert …` and `prepare p as insert …` rely on that rule. A separate problem is also out of scope: with `preferQueryMode=simple` or `extendedForPrepared`, a multi-statement `Statement` executed with generated keys loses its `;` and fails with a syntax error, before and after this change.

Some tests pass on the old parser and protect behavior that must not change: `onlyTheFirstInsertOfTheStringIsBatchRewriteCompatible`, and 9 of the 21 strings in `aSemicolonEndsAStatementUnlessInsideABeginAtomicBody`. Those 9 are the 6 genuine bodies and 3 strings the old parser split correctly by accident, which test the new checks. Every SQL string in the tests runs on PostgreSQL 17, except the two named "invalid SQL". The breaking changes and the `BEGIN ATOMIC` failure above were checked on PostgreSQL 17 with the 42.7.13 driver and with this branch.
