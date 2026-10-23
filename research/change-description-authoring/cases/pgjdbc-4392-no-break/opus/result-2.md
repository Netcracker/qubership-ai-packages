## Why

The parser did not recognize a JDBC escape when a tab or a newline separated the keyword from its value, so the escape reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then rejects it: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same escape with a space is recognized, so the result depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

## What

The separator after the keyword can now be any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, or form feed. These are the characters the backend scanner treats as whitespace. The class already defines `isSpace` for this purpose.

## User-visible changes

- `{d}`, `{ts}`, `{escape}`, and `{fn}` escapes are now translated when a tab, newline, carriage return, or form feed separates the keyword from its value.
- Not changed: a brace that does not start an escape still passes through unchanged, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

The new test `escapeKeywordAcceptsAnyWhitespace` runs `{d}`, `{ts}`, `{escape}`, and `{fn}` with each of the five whitespace characters and with a run of mixed whitespace. Against `master` it fails on the first tab. A second new test checks that `{obj\t: 1}` and a truncated `{d\t` pass through unchanged. The existing `escapeProcessing` test still covers the forms that use a plain space.
