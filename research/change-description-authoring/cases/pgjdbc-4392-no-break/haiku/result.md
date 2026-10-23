A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized, so it reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the plain space character. The same input with a space works, so whether the escape was recognized depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

The separator is now any character that `Parser.isSpace` accepts: space, tab, newline, carriage return and form feed. That is the set the backend scanner treats as whitespace, and the class already defines the predicate for this purpose. A brace that does not start an escape is left alone, whatever whitespace follows it.

User-visible: An escape whose keyword is separated from its value by a tab, carriage return, form feed or newline is processed as an escape, the same as with a space. Before this change, the driver sent it verbatim and the server rejected it with `syntax error at or near "{"`.

Not changed: A `{` that does not start a known escape is passed through unchanged, whatever whitespace follows it, so `{obj\t: 1}` and a truncated `{d\t` stay as written.

To verify, run:

```bash
./gradlew --quiet :postgresql:test --tests 'org.postgresql.core.ParserTest'
```

`escapeKeywordAcceptsAnyWhitespace` runs the `d`, `ts`, `escape` and `fn` keywords with each of the five whitespace characters and with a run that mixes them. It fails on `master` at the first tab. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` guards the non-escape case, and the existing `escapeProcessing` test still covers the plain-space forms. The broader `org.postgresql.core.*`, `org.postgresql.test.jdbc2.*` and `org.postgresql.test.jdbc3.*` suites also pass.
