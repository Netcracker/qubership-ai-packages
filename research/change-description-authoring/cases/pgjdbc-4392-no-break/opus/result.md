## Why

A JDBC escape whose keyword was separated from its value by a tab or a newline was not recognized, and the driver sent it to the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// returns {d\t'1999-01-09'}; the server rejects it with: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` accepted only the space character after the keyword. The same escape written with a space works, so whether it was recognized depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

## What

The separator is now any character `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed, which is the set the backend scanner treats as whitespace. `Parser` already defines that predicate for this purpose.

## User-visible changes

- `{d}`, `{ts}`, `{escape}`, and `{fn}` escapes whose keyword is followed by a tab, newline, carriage return, or form feed are translated the same way as with a space.
- Not changed: a brace that does not open an escape, such as `{obj\t: 1}` or a truncated `{d\t`, is passed through unchanged, whatever whitespace follows it.

## How to verify

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

The new `escapeKeywordAcceptsAnyWhitespace` fails against `master` on the first tab. The new tests run each escape keyword over all five whitespace characters and a mixed run, and check that a non-escape brace is left untouched; the existing `escapeProcessing` test still covers the plain-space forms.
