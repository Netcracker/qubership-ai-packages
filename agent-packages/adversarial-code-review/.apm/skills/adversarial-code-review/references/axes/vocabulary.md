# Axis: vocabulary

Do the comments and the new member names use the words of the field (the specification the project implements, the
language, the libraries it uses) and of the code, rather than words the change coined? Load `english-developer-style`
and apply its section *Use the field's word*. Use web access to read the specification where the project implements one.

## Check

1. Find the terms. Read the added and changed comments and the names of added or renamed members. List every word or
   phrase used as a term: a noun or verb that recurs, a phrase used as if the reader knew it, the words a member name is
   built from.
2. Find the source of each. Search the specification, the language reference, and the repository at the base revision. A
   term with a source in the same sense stays. A term with none is a coinage.
3. Check these shapes word by word, verbs as hard as nouns:
   - *A role word for an operation.* Where a sentence says what part something plays (where a value comes from, where it
     ends up, what decides) and the language or the specification names the operation (assignment, argument passing,
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
   - *A metaphor* for a mechanism (`the token rides along with the request`, `the cache swallows the error`): name the
     mechanism (`is copied into the request header`, `catches and discards the exception`).
4. For each coinage, give the field's word with its source (a section of the specification, a class in the language API,
   an existing identifier), and list every place the change uses the coinage, comments and names together.

## Not a finding

A plain phrase that states the relation correctly (`walks up the superclass chain`) stays in prose, even where the
specification has a defined term for it. This exception does not cover member names: a name is what a reader searches
for, so a member name uses the specification's term. A clear metaphor the codebase already uses throughout is not this
change's to fix.

## Severity

A coinage that names a concept the specification defines, used across several comments or in a member name, is `minor`;
one class covers all its uses. A single loose word in one comment is a `nit`.
