A JDBC escape whose keyword was followed by a tab or a newline instead of a space was not recognized. The driver sent it to the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// returns {d\t'1999-01-09'}
```

The server then fails with `syntax error at or near "{"`. The same escape with a space works, so whether an escape was recognized depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

`SqlParseState.getMatchedPosition` skipped only the space character between the keyword and its value. It now skips any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. The backend scanner treats the same set as whitespace, and the class already defines that predicate for this purpose. A brace that does not start an escape is still left as written, whatever whitespace follows it.

`nonEscapeBraceIsUntouchedWhateverTheWhitespace` covers the behavior the change must not move. It passes both before and after the change, and it checks that `{obj\t: 1}` and a truncated `{d\t` still pass through unchanged.
