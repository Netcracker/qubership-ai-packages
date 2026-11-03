A JDBC escape whose keyword is separated from its value by a tab or a newline is not recognized, so it reaches the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then answers: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skips only the plain space character between the keyword and its value, so the same input with a space works. Whether the escape is recognized depends on which whitespace the caller wrote, and a newline is easy to hit when the SQL is formatted across lines.

The separator is now any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, and form feed. That is the set the backend scanner treats as whitespace, and the class already defines the predicate for this purpose.

User-visible: An escape whose keyword is followed by a tab, carriage return, newline, or form feed is now processed the same as with a space.

Not changed: A brace that does not start an escape, such as `{obj\t: 1}`, is still passed through unchanged, whatever whitespace follows it.

`nonEscapeBraceIsUntouchedWhateverTheWhitespace` passes without the change too; it pins the non-escape side, which the change must not move.
