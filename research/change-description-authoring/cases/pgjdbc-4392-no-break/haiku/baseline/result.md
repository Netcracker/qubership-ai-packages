## Why

A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized, so it reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}
// The server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space is recognized, so whether the escape is recognized depends on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character that `Parser.isSpace` accepts. That is the set the backend scanner treats as whitespace: space, tab, newline, carriage return, and form feed.

A brace that does not start an escape is still left alone.

## How to verify

Run the parser tests:

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` runs the `d`, `ts`, `escape`, and `fn` escapes with each of the five whitespace characters, and with a mixed run of them. It fails against `master` on the first tab.

`nonEscapeBraceIsUntouchedWhateverTheWhitespace` pins that `{obj\t: 1}` and a truncated `{d\t` pass through unchanged. The existing `escapeProcessing` test still covers the plain-space forms.

8177 tests across `org.postgresql.core.*`, `org.postgresql.test.jdbc2.*`, and `org.postgresql.test.jdbc3.*` pass.
