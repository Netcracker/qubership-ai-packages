## Why

`Parser.replaceProcessing` did not recognize a JDBC escape when a tab or a newline separated the keyword from its value. The escape reached the server verbatim, and the server rejected it:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then fails with: syntax error at or near "{"
```

The same escape written with a space worked, because `SqlParseState.getMatchedPosition` skipped only the space character. Whether the escape was recognized therefore depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across several lines.

## What

The keyword and its value may now be separated by any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. This is the set the backend scanner treats as whitespace. `Parser` already defines `isSpace` for this purpose, so the escape parser now uses the same predicate as the rest of the class.

## User-visible changes

- A `{d}`, `{ts}`, `{escape}`, or `{fn}` escape whose keyword is followed by a tab, newline, carriage return, or form feed is now translated. Before this change it was sent verbatim and failed with `syntax error at or near "{"`.
- Not changed: a brace that does not start an escape, such as `{obj\t: 1}` or a truncated `{d\t`, is still passed through unchanged, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

The new test `escapeKeywordAcceptsAnyWhitespace` runs each of the four escapes with all five whitespace characters and with a mixed run of them. Against `master` it fails at the first tab. The new test `nonEscapeBraceIsUntouchedWhateverTheWhitespace` checks that non-escape braces are still left unchanged. The existing `escapeProcessing` test still covers the forms that use a space.
