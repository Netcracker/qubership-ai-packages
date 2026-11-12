# Case: review pgjdbc/pgjdbc#4307 at 88ea54fa, a hand-written SQL scanner that regresses three kinds of query

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#4307][pr] at `88ea54fa`, one commit on
top of `3a699d57`. The gold answer comes from the maintainer's inline comments on that commit: five comments, and the
author replied in the thread or changed the code near each of them. The review was written in 2026, and reviews from
2025 on may have been written with an agent's help.

The change replaces the `StringTokenizer` in `PgResultSet.parseQuery()`, which took the token after the first `FROM` as
the table of an updatable `ResultSet`, with a character scanner, `findTableName`, that tracks parenthesis depth and
skips literals, quoted identifiers, dollar-quoted strings, and comments. The scanner is a second copy of a lexer the
driver already has in `org.postgresql.core.Parser`, and each place where the copy differs from `Parser` makes a query
that the old tokenizer handled no longer updatable: a backslash escape in a literal, a named dollar-quote tag, and a
query wrapped in parentheses.

The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/4307

## What it exercises

- Area *Correctness and data integrity*: boundary and invalid inputs of a lexer, traced character by character against
  inputs the old code accepted.
- Area *Structural defects*, the bullet on reusing the canonical helper instead of adding a near-duplicate: the scanner
  duplicates `Parser.parseSingleQuotes`, `parseDollarQuotes`, `parseLineComment`, and `parseBlockComment`.
- Area *Verification and documentation*: the new tests cover the cases the author thought of, not the lexical cases the
  scanner handles.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial. One finding that names several of the
defects in checks 1-3, each with its cause, passes each of those checks.

1. **Backslash escapes end the literal early.** Pass: a finding that `skipQuoted` (`PgResultSet.java` line 2155) treats
   only a doubled quote as an escape, so an `E'...'` string with `\'` inside, or any literal with `\'` under
   `standard_conforming_strings = off`, ends early; a `(` after it raises the depth and the real closing quote opens a
   literal that runs past the outer `FROM`, so a query such as `select id, name, E'\'(' as x from updateable` is no
   longer updatable. Partial: the report says the scanner duplicates `Parser` and should reuse
   `Parser.parseSingleQuotes` without naming escape strings. Fail: neither.
   `grep -niE "skipQuoted|backslash|E'|standard_conforming|parseSingleQuotes|escape" result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4307#discussion_r4346052153))
2. **A named dollar-quote tag is never recognized.** Pass: a finding that `isIdentifierPart` (line 2249) accepts `$`, so
   the loop at line 2192 in `dollarQuoteTagEnd` consumes the `$` that closes the tag and the method returns -1 for every
   named tag such as `$tag$`; the string is then scanned as plain text and a parenthesis inside it is counted. Partial:
   the report says dollar quoting is handled differently from `Parser.parseDollarQuotes` without naming the tag defect.
   Fail: neither.
   `grep -niE 'dollar|\$tag|dollarQuoteTagEnd|isIdentifierPart|isDollarQuoteContChar' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4307#discussion_r4346052173))
3. **A parenthesized query loses its table.** Pass: a finding that `findTableName` counts depth from the start of the
   string and accepts `FROM` only at `depth == 0` (line 2098), so a query wrapped in parentheses, such as
   `(select id, name from updateable where id = 1)`, resolves no table and is no longer updatable, where the old
   tokenizer found it. Partial: the report questions the depth-zero rule without naming a query it breaks. Fail:
   neither.
   `grep -niE 'parenthes|wrapped|depth|\(select' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4307#discussion_r4346052177))
4. **The tests miss the cases the scanner handles.** Pass: a finding that the new tests in `UpdateableResultTest.java`
   (lines 152-231) cover only a scalar subquery, a `(` in a string literal, a function call, and a quoted identifier,
   and do not exercise at least two of: comments containing `(`, dollar-quoted strings, escape strings, a parenthesized
   query, a `FROM` inside a function call such as `extract(year from now())` or `substring(name from 1 for 2)`, or a
   comment between `FROM` and the table name. Partial: the report names only one such case, or only says the three
   parenthesis tests repeat one body and should be a parameterized test. Fail: neither.
   `grep -niE 'UpdateableResultTest|ParameterizedTest|extract|substring|comment|test' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4307#discussion_r4346052185))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, boundary and invalid
  inputs
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Structural defects*, reuse of the canonical helper
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that cover behavior
  and regression paths

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `3a699d57d957ca0c2b86e619d001a8763a130027` (the parent of the pull request's commit), and `88ea54facd0e7e800ce9761eb5767f4963349d54` (the commit the review was written on). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-4307-updatable-table-scanner <model> <label> <rev>
```
