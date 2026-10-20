## Why

A JDBC escape whose keyword is separated from its value by a tab or a newline is not recognized. The driver passes it to the server verbatim, and the server rejects it:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skips only the plain space character. The same input with a space works, so whether the escape is recognized depends on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character that `Parser.isSpace` accepts. That method already exists for this purpose, and it accepts the set the backend scanner treats as whitespace: space, tab, newline, carriage return, and form feed.

## User-visible changes

A JDBC escape whose keyword is followed by a tab, newline, carriage return, or form feed is now translated, as it already was after a space. Previously the escape reached the server unchanged, and for `{d` the server answered `syntax error at or near "{"`.

Not changed: a brace that is not an escape, such as `{obj\t: 1}` or a truncated `{d\t`, still passes through unchanged, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` runs `{d}`, `{ts}`, `{escape}`, and `{fn}` over all five whitespace characters and a mixed run. It fails on `master` at the first tab, so it is the regression test. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` guards against matching a brace that is not an escape. The existing `escapeProcessing` test still covers the plain-space forms. The `org.postgresql.core`, `org.postgresql.test.jdbc2`, and `org.postgresql.test.jdbc3` test packages also pass.
