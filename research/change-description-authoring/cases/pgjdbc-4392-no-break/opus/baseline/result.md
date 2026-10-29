## Why

The driver did not recognize a JDBC escape when a tab or a newline separated the keyword from its value. The escape reached the server unchanged:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}
// The server then fails with: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space works, so whether the escape was recognized depended on which whitespace character the caller wrote. SQL formatted across several lines can easily put a newline there.

## What

The separator can now be any character that `Parser.isSpace` accepts. That is the set of characters the backend scanner treats as whitespace: space, tab, newline, carriage return, and form feed. `Parser` already defines this predicate for that purpose.

A brace that does not start an escape still passes through unchanged, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

- `escapeKeywordAcceptsAnyWhitespace` tests `{d}`, `{ts}`, `{escape}`, and `{fn}` with each of the five whitespace characters and with a mixed run of them. Against `master`, it fails on the first tab.
- `nonEscapeBraceIsUntouchedWhateverTheWhitespace` checks that `{obj\t: 1}` and a truncated `{d\t` pass through unchanged.
- The existing `escapeProcessing` test still covers the forms that use a plain space.

All 8177 tests in `org.postgresql.core.*`, `org.postgresql.test.jdbc2.*`, and `org.postgresql.test.jdbc3.*` pass.
