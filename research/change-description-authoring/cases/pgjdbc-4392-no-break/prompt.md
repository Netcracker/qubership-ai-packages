# Task

Write the pull request description for the change below, in Markdown, ready to paste into GitHub. The facts come from
the author's draft, which was checked against the code and against a running server; treat every fact in it as
verified, and add none that it does not carry. The draft is the author's, and you may restructure, cut, or reword it.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver.
- Target branch: `master`. Its `gradle.properties` says `pgjdbc.version=42.7.14`; the latest release tag is
  `REL42.7.14`. There is no milestone on the pull request.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template. The pull request has one commit.

## The author's draft

````markdown
## Why

A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognised, and reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space works, so the escape was recognised or not depending on which whitespace the caller happened to write — a newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character `Parser.isSpace` accepts, which is the set the backend scanner treats as whitespace: space, tab, newline, carriage return and form feed. The class already defines that predicate for exactly this purpose.

A brace that is not an escape is still left alone, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` runs each of `{d}`, `{ts}`, `{escape}` and `{fn}` over all five whitespace characters and a mixed run; it fails against `master` on the first tab. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` pins that `{obj\t: 1}` and a truncated `{d\t` still pass through unchanged, and the existing `escapeProcessing` test keeps the plain-space forms honest.

8177 tests across `org.postgresql.core.*`, `org.postgresql.test.jdbc2.*` and `org.postgresql.test.jdbc3.*` pass.

````
