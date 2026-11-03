An escape whose keyword is separated from its value by a tab or a newline is not recognized, so it reaches the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the space character, so whether an escape was recognized depended on which whitespace the caller wrote. A newline is easy to hit when SQL is formatted across lines.

The separator is now any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. That is the set the backend scanner treats as whitespace, and the class already defines the predicate, so the change reuses it instead of adding a second list. Each of these separators now gives the same result as a space. A brace that is not an escape is still left alone, whatever whitespace follows it.

`nonEscapeBraceIsUntouchedWhateverTheWhitespace` passes without this change. It pins that `{obj\t: 1}` and a truncated `{d\t` still pass through unchanged, which is the side this change must not move.
