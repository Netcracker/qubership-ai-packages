# Axis: comments

Do the doc comments and inline comments the change adds or edits say what the code does? Load the doc-comment skill of
the language (`javadoc-authoring` for Java, Kotlin, Groovy, Scala; `godoc-authoring`, `rustdoc-authoring`,
`jsdoc-authoring`, `pythondoc-authoring`). Wording, tense, sentence length, and dialect belong to the developer-style
skill of the language the comments are written in (`english-developer-style` for English); load it too.

## Check

- Every added or changed doc comment against the body of its member: each claim (a condition, a result, a `@return`, a
  `@throws`, a null case) holds for every path of the body and of the callees it relies on. A claim that holds for one
  overload but is written on another is a finding.
- Every comment left above changed code, unchanged itself: does it still hold? A comment that describes the old behavior
  is a finding.
- Comments that say different things about the same fact, in this file or in the files the change touches.
- Every added inline comment: open each member the next statement calls, and read its body and doc comment. Where the
  callee already handles the case the comment describes, the comment restates the callee's contract; ask to delete it or
  link the callee.
- An added expression a competent reader would misread or find arbitrary (a type operation, a cast, a fallback, a
  constant) with no comment: name the question the comment must answer.
- A new member with no doc comment, where the repository's rules or the doc-comment skill require one (for example, a
  rule that every non-trivial method gets a Javadoc).
- A summary defined through private neighbors ("as `foo` does, then `bar`") rather than through its result.
- Names and comments that refer by position or ordinal ("the second case", "below") rather than by content.

## Severity

A comment the code contradicts is `major` where a caller acts on it (a public contract, a `@return`, a `@throws`), and
`minor` otherwise. A missing doc comment the repository's rules require is `minor`.
