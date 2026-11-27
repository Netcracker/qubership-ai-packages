# Axis: vocabulary

Do the comments, the new member names, and the output text (*Output text* in `references/finding-rules.md`) use the
words of the field and of the code, rather than words the change coined? The field's words come from the well-known
standards most closely tied to what the program is for: the specification it implements, the reference of the language
or protocol it works with, the conventions of its ecosystem and of the libraries it uses. Output text also answers to
the words its typical users already know, since they read it without the code. Load the developer-style skill of the
language the text is written in (`english-developer-style` for English) and apply its rule on the field's word where it
has one (*Use the field's word* in `english-developer-style`). Use web access to read the standard where the project
implements one.

## Check

1. Find the terms. Read the added and changed comments, the names of added or renamed members, and the output text the
   change adds or rewords, in its rendered samples. List every word or phrase used as a term: a noun or verb that
   recurs, a phrase used as if the reader knew it, the words a member name is built from, and every symbol, arrow, or
   abbreviation the output text uses as notation. Name in the coverage file the rendered samples you read or rendered,
   or that the change has no output text.
2. Find the source of each. Search the standards above and the repository at the base revision. A term with a source
   in the same sense stays. A term with none is a coinage.
3. Check these shapes word by word, verbs as hard as nouns:
   - *A role word for an operation.* Where a sentence says what part something plays (where a value comes from, where it
     ends up, what decides) and the language or the standard names the operation (assignment, argument passing,
     return, a store), use the operation's word. `The column that takes the timestamp` describes a write; `the column
     the timestamp is written to` names it. That the codebase already uses the role word somewhere does not settle it:
     test the word against the operation in this sentence.
   - *A relation stated with a loose phrase.* A predicate or a sentence that states a relation the field names (an
     order, a containment, a subtyping, an implication, an equivalence) uses the field's name for it (`isSubsetOf`,
     `isSubtypeOf`, `implies`, `happensBefore`, `isEquivalentTo`), not a phrase about size or position (`fitsInside`,
     `isWithin`, `isSmallerThan`, `isUnder`). A size word is wrong for any relation where two elements can be
     incomparable (sets, types, permission sets, version constraints, events on different threads). Check member names
     here as well as prose.
   - *A phrase used as if the reader knew it.* A qualified noun or a comparison the change introduces with no definition
     (`a qualifying hop`, `the shadow route`, `on the same level as the owner`). Could a reader who knows the field and
     the codebase say which cases the phrase includes and which it excludes? If not, it is a coinage: define it at its
     first use with one concrete example, or replace it with what the code checks.
   - *A defined term in another sense.* A term the standard defines, used for a neighboring concept it defines under
     another name: the commit called by the name of the branch that points to it, the column called by the name of the
     index on it, the status code called by the name of the error class. Read each defined term in the output text
     against the standard's definition; a user who knows the standard reads the defined sense, so the text says
     something else.
   - *Notation the output invents.* A symbol, an arrow, a bracket form, or an abbreviation that none of the standard,
     the program's other output, and the tools of its kind its users already run use, such as `::` to join a file and a
     setting in a CLI message or `[!]` in a report. A user cannot look it up; write the relation it stands for in words,
     or use the notation of the standard. A code, a key, or a token that programs match, such as an error code a client
     checks, is not such notation: whether it may change is the compatibility axis's question.
   - *A metaphor* for a mechanism (`the token rides along with the request`, `the cache swallows the error`): name the
     mechanism (`is copied into the request header`, `catches and discards the exception`).
4. For each coinage, give the field's word with its source (a section of the standard, a class in the language API,
   an existing identifier), and list every place the change uses the coinage: comments, names, and output text together.

## Not a finding

A plain phrase that states the relation correctly (`walks up the superclass chain`) stays in prose, even where the
standard has a defined term for it. This exception does not cover member names: a name is what a reader searches
for, so a member name uses the standard's term. A clear metaphor the codebase already uses throughout is not this
change's to fix.

## Severity

A coinage that names a concept the standard defines, used across several comments or in a member name, is `minor`; one
class covers all its uses. In output text, a defined term in another sense or invented notation is at least `minor`,
since every user reads it, or more by *Output text* in `references/finding-rules.md`. A single loose word in one comment
is a `nit`.
