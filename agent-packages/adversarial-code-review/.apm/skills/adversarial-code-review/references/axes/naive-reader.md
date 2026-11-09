# Axis: naive reader

Can a reader who knows the field but has not seen this code understand the comments the change adds? This axis reads the
comments before the code, on purpose: once you have read the body, you no longer notice what the comment leaves out.

## Pass 1: comments only

Run `<skill dir>/scripts/extract-comments.py <workspace> <base>` and read its output, which lists every comment block
the change adds or edits, each with the declaration it documents. Do not open the code yet. Where the change has doc
comments in a syntax the script does not extract (its docstring names the ones it does), read those from `git diff`,
skipping the code lines. Where the change touches many files, start with the main source files and leave tests for last.
You may read the specification the project implements. For each comment, write down every question you could not answer
from the comment itself and the other comments listed:

- a term or phrase used as if you knew it, with no definition and no example (which cases does it include, which not?);
- a claim you cannot picture without a concrete example, or a case analysis you cannot follow;
- a missing contract: the precondition, what the member decides, when a value or a field is null or absent;
- a sentence you had to read twice, or could read two ways;
- a name, in a comment or a declaration, that you read as something else (a method that looks like a variable, a word
  that names a different concept in the language or the specification).

Whether a word is the field's term is the vocabulary axis's question; here, only whether the comment answers yours.

## Pass 2: the code

Open the code at the reviewed head. For each question, decide whether the comment, read again, answers it. If not, the
question stands even where the code answers it: the reader of a comment should not need the body. Use the code and its
tests to write the repair concretely: the definition, the example drawn from a test, the precondition.

Keep at most the ten questions a maintainer would most likely ask, most important first; drop a question the comment
answers on a second read.

## Severity

A missing contract on a public or widely called member, or a claim no reader can follow without the body, is `minor`. A
missing example is `minor` where the comment states a rule with cases, and a `nit` otherwise.
