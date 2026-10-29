A JDBC escape whose keyword is separated from its value by a tab or a newline was not recognized. The driver sent it to the server verbatim, and the server rejected it with `syntax error at or near "{"`:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// returns {d\t'1999-01-09'} unchanged
```

`SqlParseState.getMatchedPosition` skipped only the space character, so the same escape written with a space worked. A newline is easy to hit when the SQL is formatted across several lines.

The separator can now be any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. The backend scanner treats the same set as whitespace. `{d}`, `{ts}`, `{escape}`, and `{fn}` are now recognized with any of these characters, or a mix of them, after the keyword. A brace that does not start an escape, such as `{obj\t: 1}` or a truncated `{d\t`, still passes through unchanged. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` covers these cases, and it passes without the change as well.
