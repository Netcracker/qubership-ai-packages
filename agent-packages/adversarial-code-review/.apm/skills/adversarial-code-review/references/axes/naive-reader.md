# Axis: naive reader

Can a reader who knows the field but has not seen this code understand the comments the change adds, and can a typical
user of the program understand the output text it alters (*Output text* in `references/finding-rules.md`)?
This axis reads the comments and the output text before the code, on purpose: once you have read the body, you no
longer notice what the text leaves out.

## Pass 1: comments and output text, before the code

Run `<skill dir>/scripts/extract-comments.py --diff-base <base> --repo <workspace>` and read its output, which lists
the doc comments the change adds or edits, each with the declaration it documents. Do not open the code yet. The script
takes the doc comments from `sb map` (ast-bro), and its docstring names the kinds it does not print, such as a module
docstring; read those from `git diff`, skipping the code lines. A file in which `sb` finds no declaration comes as its
diff, and where `sb` is not installed, the whole output is the diff, with a note on stderr that links ast-bro; read the
doc comments from it the same way, and say in your result that `sb` was missing, so the review can suggest installing
ast-bro. Where the change touches many files, start with the main source files and leave tests for last.
You may read the standard the project implements. For each comment, write down every question you could not answer
from the comment itself and the other comments listed:

- a term or phrase used as if you knew it, with no definition and no example (which cases does it include, which not?);
- a claim you cannot picture without a concrete example, or a case analysis you cannot follow;
- a missing contract: the precondition, what the member decides, when a value or a field is null or absent;
- a sentence you had to read twice, or could read two ways;
- a name, in a comment or a declaration, that you read as something else (a method that looks like a variable, a word
  that names a different concept in the language or the standard).

Where the change alters output text, read its rendered samples in this pass too (*Output text* in
`references/finding-rules.md` says where they are), as a typical user of the program: a person who knows the standards
and conventions of the field the program serves, and the tools of its kind, and has not read this implementation. A
sample in a test or a golden file is not the code that builds it; leave that code for pass 2. Where *Output text* asks
for a sample nothing renders, run the program before you open the code; where it cannot run here, render the message in
pass 2, and say in your coverage file that its questions come from a reader who has seen the code. For each sample,
write down every question that user would ask:

- a word, a symbol, or an arrangement of lines you could not say the meaning of, or could read two ways;
- a claim more certain than the program can be, such as one remedy stated as the fix where the input does not decide
  which of several is right;
- a sample that tells the user less, or less clearly, than the text it replaces.

Whether a word is the field's term is the vocabulary axis's question, and whether the text of an error says what failed
and what to do is the telemetry axis's; here, only whether the comment or the sample answers yours.

## Pass 2: the code

Open the code at the reviewed head. For each question, decide whether the comment or the sample, read again, answers
it. If not, the question stands even where the code answers it: the reader of a comment should not need the body, and
the user of the program never sees it. Use the code and its tests to write the repair concretely: the definition, the
example drawn from a test, the precondition, the resulting output text.

Keep at most the ten questions a maintainer or a user would most likely ask, most important first; drop a question the
text answers on a second read.

## Severity

A missing contract on a public or widely called member, or a claim no reader can follow without the body, is `minor`. A
missing example is `minor` where the comment states a rule with cases, and a `nit` otherwise. Output text a typical user
cannot read, or that claims more than the program can know, is `minor`, or more by *Output text* in
`references/finding-rules.md`.
