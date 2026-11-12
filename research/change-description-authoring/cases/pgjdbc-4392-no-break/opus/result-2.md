A JDBC escape was not recognized when a tab or a newline separated its keyword from its value. The escape was sent to the server unchanged:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// -> {d\t'1999-01-09'}      the server then rejects it: syntax error at or near "{"
```

The same input with a space is translated. Whether the escape worked therefore depended on which whitespace the caller wrote, and SQL formatted across lines easily puts a newline there. `SqlParseState.getMatchedPosition` skipped only the space character.

The separator after the keyword can now be any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, or form feed. The backend scanner treats the same set as whitespace, and `Parser` already defines the predicate for this purpose. A brace that is not an escape still passes through unchanged, such as `{obj\t: 1}` or a truncated `{d\t`. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` covers that case.
