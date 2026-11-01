A JDBC escape was not recognized when its keyword was followed by a tab or a newline. It reached the server verbatim:

```java
Parser.replaceProcessing("{d\t'1999-01-09'}", true, false)
// returns {d\t'1999-01-09'}, and the server rejects it with: syntax error at or near "{"
```

`SqlParseState.getMatchedPosition` skipped only the space character after the keyword. The same escape written with a space worked. So whether the escape was recognized depended on which whitespace the caller wrote. A newline is easy to hit when the SQL is formatted across lines.

The separator can now be any character that `Parser.isSpace` accepts: space, tab, newline, carriage return, or form feed. That is the set the backend scanner treats as whitespace, and the class already defines the predicate for this purpose.

A brace that does not start an escape still passes through unchanged, whatever whitespace follows it. `nonEscapeBraceIsUntouchedWhateverTheWhitespace` covers this case and also passes without the change. It checks that `{obj\t: 1}` and a truncated `{d\t` come back as they went in.
