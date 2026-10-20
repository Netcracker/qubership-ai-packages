A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized, and it reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space works, so whether the escape was recognized depended on the whitespace the caller happened to write. A newline is easy to hit when the SQL is formatted across lines.

The separator is now any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. That is the set the backend scanner treats as whitespace, and `Parser` already defines the predicate for this purpose.

User-visible:
A JDBC escape whose keyword is separated from its value by a tab, newline, carriage return, or form feed is now recognized, as it already is after a space. Previously the escape reached the server unchanged, and the server answered `syntax error at or near "{"`.

Not changed:
A `{` that does not start an escape, such as `{obj\t: 1}` or a truncated `{d\t`, still passes through unchanged, whatever whitespace follows it.

Run the parser tests:

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

Two new tests. `escapeKeywordAcceptsAnyWhitespace` runs `{d}`, `{ts}`, `{escape}`, and `{fn}` over all five whitespace characters and a mixed run; it fails against `master` on the first tab. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` pins the brace case that is not an escape. The existing `escapeProcessing` test still covers the plain-space forms.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
