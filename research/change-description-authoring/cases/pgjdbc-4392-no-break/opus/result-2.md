## Why

A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized, and the driver sent it to the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then fails with: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the space character between the keyword and its value. The same escape written with a space is translated, so whether it worked depended on which whitespace the caller wrote, and a newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. That is the set the backend scanner treats as whitespace, and `Parser` already defines the predicate for this purpose.

## User-visible changes

- `{d}`, `{ts}`, `{escape}`, and `{fn}` escapes whose keyword is followed by a tab, newline, carriage return, or form feed are translated, as they already were with a space.
- Not changed: a brace that does not start an escape, such as `{obj\t: 1}`, and a truncated escape such as `{d\t` reach the server unchanged, whatever whitespace follows the brace.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` fails against `master` on the first tab. The tests run each of the four escapes over all five whitespace characters and a mixed run, check that the two non-escape inputs above pass through unchanged, and the existing `escapeProcessing` test still covers the space-separated forms.
