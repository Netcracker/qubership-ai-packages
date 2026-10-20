## Why

A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized, and it reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}, and the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space works, so whether the escape was recognized depended on the whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. That is the set the backend scanner treats as whitespace, and `Parser.isSpace` already defines it.

## User-visible changes

- A JDBC escape keyword followed by a tab, newline, carriage return, or form feed is now recognized, as it already is with a space. The statement is no longer passed to the server verbatim.
- Not changed: a brace that does not start an escape is still left alone, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` runs each of `{d}`, `{ts}`, `{escape}`, and `{fn}` over all five whitespace characters and a mixed run. It fails against `master` on the first tab. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` pins that `{obj\t: 1}` and a truncated `{d\t` still pass through unchanged. The existing `escapeProcessing` test still covers the plain-space forms. The `org.postgresql.core.*`, `org.postgresql.test.jdbc2.*`, and `org.postgresql.test.jdbc3.*` packages also pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
