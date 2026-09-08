---
name: jsdoc-authoring
description: >-
  Load before writing, editing, or reviewing a doc comment or inline comment in JavaScript or TypeScript: a TSDoc block
  on an exported declaration, a @param type in a checked .js file, the it string of a test just added, a regression test
  that names the old defect, a method that overrides a base class or implements an interface member, an inline note
  beside a new check, a @ts-expect-error or eslint-disable-next-line comment, a comment that ships in a .d.ts. Inside a
  coding task on a JavaScript or TypeScript codebase ("fix the bug", "add the hook") load it as soon as the change
  touches a comment, before writing it. Also load to decide whether a declaration needs a comment at all, or to compare
  two versions of one. Governs what the comment says and in which order: the summary section, contract before rationale,
  a type in a tag, tags and links, when to write nothing, how far a rewrite may grow. Wording is
  english-developer-style's; load both.
---

# Authoring a JSDoc or TSDoc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and dialect belong to
`english-developer-style`: load it too, and defer to it on the prose. The two compose: this skill picks the slots; that
one writes the sentences.

It covers both languages, because they share one comment syntax, one tag vocabulary, one Markdown body, and one language
service behind the editor hover where most readers meet the comment. TSDoc is the standardized subset that API Extractor
and TypeDoc read; JSDoc is the older, looser superset. Where a rule differs between the two dialects, this file says so.
One rule differs between a `.ts` file and a checked `.js` file, and it inverts: that is §3a, the most important section
here for an agent that writes both.

Conventions carried in from another language's doc comments go wrong in three places, so do not translate them in your
head: the summary ends at the first block tag rather than at the first period (§3), Markdown is the markup (§5), and a
tag that states a type is either redundant or the code itself, depending on the file it sits in (§3a, §6).

**The formatter does not own the layout.** Measured on Prettier 3.9.6, a doc comment is re-indented to a single leading
`*` column and otherwise left alone: prose is not reflowed, inner runs of spaces are not collapsed, and a line past
`--print-width` is not wrapped. Every line break inside a doc comment is your decision, and it survives every format
run, including the stale ones.

## 1. The correction that matters most

"Document the why, not the what" is half wrong for a doc comment, and the wrong half does the damage.

An inline `//` comment documents the **why**; it sits next to code the reader can already see. A doc comment documents
the **contract**: what a caller may rely on, what an implementer must guarantee, what holds before and after. That is a
*what* at the level of a promise, not a restatement of the code.

The failure mode is therefore not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Maps over the entries and pushes each into the result array.` The body already
  states it, and the comment becomes false on the next refactor.
- **Justifying the code's existence.** `This hook was extracted because three components repeated the same effect.`
  That belongs in the commit message and the pull request description. A doc comment's reader has to *use* or *fix* the
  thing, not decide whether to merge it.

**The test is the refactor, not the reader.** Rewrite the body so it behaves identically and reads differently: a `for`
loop becomes a `reduce`, a helper is inlined, a field is renamed. Every sentence you would then have to edit was
implementation, whatever it sounded like. This is the operative rule, because it settles cases that "specification, not
details" argues about forever, and it does not soften with visibility: a non-exported function's comment goes stale on
that refactor exactly as an exported one's does, and the cost of a comment that lies is the same either way.

**The caller substitutes too, and catches what the refactor cannot.** Imagine a new legitimate caller supplying the same
argument for a different reason. A sentence that then describes only the old call path is caller context, not this
function's contract. `A negative count throws a RangeError before any byte is read` survives the substitution; `because
a length parsed from the Content-Length header can be negative` does not.

Cutting is not the whole repair, because the rationale slot can be open and merely filled wrong. Where a value came from
does not explain why the function behaves as it does; a local reason, where one exists, is a property of this function's
own contract. Look for the local reason before concluding that the slot was never open, then ask §2's question of it:
does the rule look arbitrary without it, or would a maintainer relax it incorrectly? A reason any reader would have
assumed fails that question and stays out, however true it is.

Provenance crosses into a callee's comment where it is that function's own contract: a frame parser whose parameter *is*
the declared payload length minus the header documents its own layer rather than borrowing the one above it. **State the
local rule at the lowest-level API, and the scenario at the layer where the scenario exists.** A guard found through one
concrete call path does not thereby own that path's story.

**Sufficiency** scales with visibility: how much the comment may leave to the code beside it.

| Where | What the comment must carry |
| --- | --- |
| exported, `public`, `protected` | Complete without the code. A subclasser is a caller, so `protected` is public API here (§6a) |
| non-exported, `private`, `#private` | May be elliptical and lean on the body beside it. Often there is no contract distinct from the implementation at all, and §7's "the name and types are the whole contract" usually applies |
| inline | Nothing about the contract. The reader has the code |

For an inline comment the bar is negative: **a competent reader is looking at this code and understanding it correctly;
write the comment only where they would not.** A reason that surprises, a bound that looks arbitrary, an order that
looks swappable, a branch that looks dead. Where their expectation and the code agree, the comment is noise, and later
stale noise.

A third failure, specific to a codebase that has been refactored, is **narrating the code's history**. `This now returns
a Promise, so callers no longer get the value synchronously` describes a transition between two versions, and the reader
has only this one. Rewrite it as the state that holds: what the function returns, and when the value is available.

One exception. **The comment on a regression test may tell history, and an equivalence is not history.** The defect is
what the test guards, so it belongs in the comment: state the rule the test asserts first, then the defect in one
past-tense sentence with the error class or its `code`: `An empty header value used to be reported as absent, and the
caller then failed with a TypeError.` A comment that opens with the defect makes the reader reconstruct the broken
version to understand the fixed one (measured on one branch: a blind reader ranked the version that opened with `used
to` fourth of five on that ground alone). Do not narrate the old mechanism in the present tense, and do not recast it as
a chain of `would` clauses. History narration, which this section forbids, is a sentence whose only content is that the
code changed. A sentence that argues the new behavior is safe **because it is identical to the old one** is rationale,
and the old behavior is its comparison term. Keep the comparison; it is the whole argument.

- *Keep:* `a caller that passes no signal behaves exactly as every caller did before the option was added: the request
  runs to completion or to the timeout`
- *Wrong repair:* `a caller that passes no signal is unaffected by abort handling` (the equivalence, which is the reason
  the new option is compatible, is gone)

A fourth is the mirror image of the third: **narrating the branch that does not exist**, what the code would do on an
input it refuses, or under a rule it does not implement. History narration gives the reader a past version of the code;
this gives them a version that never existed. `If a colon were allowed through, the header line would be split
downstream and the proxy would reject the whole request` describes a path no build of this code can take. No refactor
can make it false and no reader can check it, so it survives every review.

This does not ban consequences. What the code does when the contract is broken (which error, which return value, what
state the object is left in) is contract, and the `@throws` line (§6) carries it. Cut the simulation of the branch the
guard prevents.

**The test: could a reader falsify the sentence by reading this repository?**

- `Throws a TypeError when the name contains a colon`: contract. It names a path this code has.
- `The name becomes an HTTP field name, and the field-name grammar admits no colon`: eligible. It names the *source* of
  the constraint, the shape rationale takes when it earns a slot at all. It still has to earn it.
- `Otherwise the request would be split and the proxy would reject it`: cut. Nothing here produces that, and the system
  that would is one the reader cannot see and you do not control.

**Where the reason belongs in the comment at all, name the source of the constraint rather than the disaster it
averts.** Cutting a counterfactual obliges you to put nothing in its place. §2 fills the empty rationale slot only where
the rule would otherwise look arbitrary or be easy to change incorrectly, never merely because a source exists and is
true.

A source the reader cannot infer from the code is the likeliest to earn its sentence, but reachability is evidence, not
the test. `The size must be a power of two because indexing masks with size - 1` earns its place with the masking five
lines below: the restriction looks arbitrary without it and the next maintainer will relax it. `RFC 1234 permits three
encodings` earns nothing when no caller needs to know why this one was chosen.

Where the constraint is *enforced*, an earned sentence belongs inline beside the guard: the reader sees the `throw` and
cannot see why the value is unacceptable. Where the constraint is only *stated*, in a doc comment, ask the question
again from scratch. Completeness does not settle it: a contract states itself completely by definition, so `the tags
already say what happens` closes nothing. The test stays the same: would the rule look arbitrary, and is it easy to
change incorrectly?

A function with more than one failure channel, a throw beside an `undefined` return, is not an exception to that test.
The tags state each outcome, and a maintainer reading them is expected to keep them apart. A sentence explaining why an
invalid argument throws rather than returning `undefined` is the reason any reader would have assumed (measured: a
maintainer who met such a sentence in review called it common sense). Leave it out.

## 2. The four slots

A doc comment has at most four slots, in this order.

| # | Slot | Answers | Skip when |
| --- | ------ | --------- | ----------- |
| 1 | **Summary** | What is this, or when does it fire? | Never; always present |
| 2 | **Contract** | What may a caller rely on? What must an implementer guarantee? | The signature genuinely says all of it |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader do next? | The contract already implies the action |

Two rules govern the order.

**Contract before mechanism.** State the rule the reader must satisfy before the machinery that enforces it, and before
what some *other* module does. A comment that opens with a neighboring class forces the reader to reconstruct the rule
from negative examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first slot to cut, not the last. A reader who knows the
rule and not the reason can still write correct code; the reverse is false.

**Removing a bad explanation does not create an obligation to replace it.** A rationale slot emptied by a cut stays
empty until the finished contract, read on its own, turns out to need one. Start from the contract, not from the gap.

**Make the obligated party the subject.** Obligations come in two shapes. A *stated* obligation carries a *must*, *has
to*, *may not*, or *should*, and whoever has to comply belongs in the subject: not the thing acted on (`The listener
must be removed on unmount`, which names no one and lets `it` drift to the reader by the next clause), not the act
(`awaiting the stream must not be reachable after close`), and not a member that merely performs the act for someone
else (`dispose must still run` obliges the caller). A named member in the subject is right only where that member is
itself what must comply: `dispose must be safe to call twice`. The party need not be human, but it must act: the caller,
the router, a subclass. A union member or a configured limit complies with nothing.

A *census* is a rule for the next maintainer, written instead as a report on today's call sites: `Called by the router
before every handler`, `createClient is the only caller`. It is flat indicative with no modal, so test it: **if a second
such caller appeared tomorrow, would this paragraph tell it that it is obliged?** Judge the paragraph, not the sentence;
an example may follow a law that is already correctly stated. Write the law, not the roll call.

Watch the intransitive modal, where the party hides best: `every code has to appear in ERROR_CODES`, `an unknown value
must fall back to "fail"`. Nothing appears or falls back on its own; name what does it.

Out of reach of this rule: an imperative, which already addresses the party (`Call this before the first render`),
including one that carries rationale (`so mirror the DOM behavior here`); a constraint on a *value* (`must be ≤
Number.MAX_SAFE_INTEGER`), which bounds a number rather than behavior; a comment naming who writes or reads a property,
which is the membership rule §4 calls for; and an inline comment whose next statement is the actor (`// Queue must be
flushed` above the `flush()` that flushes it), after checking that the next line really is the actor and not test setup
standing between the comment and the call it constrains.

Most declarations need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots to fill a template;
an absent slot is not a gap.

**Size the comment to the declaration.** A doc comment longer than the function it documents is not automatically wrong
(an invariant can be worth ten lines over a one-line accessor), but it is a signal to re-read. When you check, the
surplus is almost always rationale: keep at most two sentences of it, and only for the part a reader would otherwise get
wrong. The rest belongs in the commit message. As a working size, the comment at the top of a test file is two to five
sentences and a function comment fits in one hover; past that you are describing the investigation, not the contract, so
keep the rule and the exception and move the rest.

## 3. The first sentence, and where the summary ends

Write the first sentence in the third person with the subject omitted: `Returns the backing map.` Not `Return…`, not
`This function returns…`, and not `parseHeaders returns…`. The name is already on the line below and in every listing
that renders the comment.

**The summary is a section, not a sentence.** Everything before the first block tag is the summary, and `@remarks` is
the tag that ends it deliberately. Tooling that builds an index of many API items shows the summary and nothing else, so
the boundary you care about is the first block tag, not the first period. Two consequences follow, and a habit formed on
another language's first-sentence rule predicts the opposite of both:

- `e.g.` and `i.e.` do **not** truncate anything. Leave them alone.
- A four-paragraph comment with no block tag is a four-paragraph summary, and every index page in the generated docs
  carries all four. Keep the summary to one sentence and push the rest behind `@remarks`.

JSDoc's vocabulary spells the same idea the other way around: the whole prose block is the description, and `@summary`
is the tag that marks the short line an index should show. Use whichever one the repository already uses (§6), but do
not leave four paragraphs unmarked in either.

The rest of the summary rule:

- **No term this comment invents.** `Guards the inventory of backend messages` fails, because "inventory" means nothing
  until paragraph two defines it, and the summary must be readable by someone who never reads paragraph two. The repair
  is rarely to define the term earlier: the field almost always has a word already, and `english-developer-style` §4a
  gives the test for telling a defined term from a coinage.
- **No self-description.** Drop `This class is responsible for…`, `Helper that…`, `Utility for…`. Start with the verb.
- **One sentence.** If it takes two, the first one is not the summary.
- **A property or constant names its unit, not its type.** `Largest payload this stream accepts, in bytes.` The type is
  already in the signature; the unit never is. The reason the bound has that value is slot 3, however interesting it is;
  a comment that opens with the upstream implementation it mirrors leaves the index saying nothing about the constant.
- **A qualifier is not a summary.** `Internal.`, `Deprecated.`, `Default.` as the opening sentence fills every index
  page with a word that states nothing about what the declaration does. Put the qualifier after the summary (`Rejects a
  message over its limit and closes the connection. This is the default.`) or in the tag that exists for it
  (`@internal`, `@deprecated`, `@defaultValue`).
- **A first sentence a reader could reconstruct from the identifier carries nothing.** A test whose string reads
  `it('closes the input and the socket when the output close fails')` does not need a doc comment saying `Checks that a
  failing output close still closes the input and the socket.`; the report prints the string. Where the string states
  what the test establishes, the comment carries the reason, the construction the reader would not guess, or nothing.
  For a property or a getter the same rule leads to §7: where the name and the types are the whole contract, write no
  comment.

## 3a. The rule that inverts: a type in a tag

This is the one place where the same comment is correct in one file and wrong in the next, and the file extension
decides, not taste.

**In TypeScript, a type in a tag is noise.** `@param {string} name` and `@returns {number}` restate the signature the
reader is already looking at, and nothing checks them. Measured on TypeScript 5.9.3 and 7.0.2: a `.ts` file whose
`@param` names a parameter that does not exist compiles clean, and so does an invented `@nosuchtag`. Write
`@param name - what the caller must pass that the type does not say`, and let the type be the type.

**In JavaScript with `checkJs` (or a `// @ts-check` pragma), a type in a tag is code.** The same compiler reads
`@param {string}`, `@returns`, `@type`, and `@typedef` as the file's type annotations. Measured on the same two
compilers, in a `.js` file: `len(42)` against `@param {string} name` is `error TS2345`, and a `@param` whose name no
longer matches the parameter is `error TS8024`.

Three things follow, and they are the reason this section is not a footnote:

1. **Editing a type tag in a checked `.js` file is a code change.** "Comments only" does not cover it, a comment sweep
   does not include it, and §7b's proof does not see it (step 7).
2. **The tag that is noise in `.ts` is the contract in `.js`.** Deleting `@param {string}` from a checked `.js` file
   deletes a type. Before carrying a TypeScript habit into a `.js` file, check whether the project checks it: `checkJs`
   in `tsconfig.json`, or `// @ts-check` at the top of the file.
3. **In `.ts`, an identifier in a tag rots in silence.** Nothing tells you. §7a's instruction to grep every name the old
   comment mentions applies at full force there, and only in `.js` does a compiler do part of it for you.

## 4. Genre notes

### Class, interface, and type alias

The type's comment carries the **invariant that spans the members**. Member comments specialize it and do not carry it;
a rule stated only on a private field is a rule the type's comment is missing.

Name the collaborators the type is useless without, the concurrency or reentrancy model if there is one, and the
lifecycle if instances are not free-standing: which factory constructs it, whether `new` is allowed, whether it must be
disposed, and what using it after disposal does. Do not explain how a collaborator works internally; link to it and let
its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set (every event a component emits, every function that writes a field, every
caller that must be updated) has transcribed a query. The list is stale from the first refactor, and a reader who does
not find their case in it concludes the wrong thing.

State the criterion instead: *every other status rejects a request no conforming server can answer* beats an eight-item
list of those statuses, because the reader can classify a status the list has never heard of. The criterion has to let
the reader name a member: "the options whose error message offers this as a remedy" is true by construction and states
nothing the reader could not have inferred. Where the honest criterion is circular, the list was the answer.

Two exceptions. A set the code itself declares (a union type, a `const` object the code derives a type from, a `switch`
whose exhaustiveness the compiler checks) fails the build when it drifts, so there the list **is** the contract, and
duplicating it in prose is the defect. And a list the reader needs as vocabulary (the keys an options object accepts,
the values an environment variable takes) stays, because the criterion alone lets nobody write code. What goes in that
case is the rot: the version label that freezes the list, and the per-item annotations nobody maintained.

**One question decides it: can this set gain a member without anything forcing someone to edit this comment?** If it
can, write the criterion; no build, test, or review will report the stale list. If it cannot, because the compiler or a
test fails the moment the set changes, the list is the contract and belongs here. The question is not about size (a
three-item list nobody maintains rots faster than a twenty-item one the build keeps honest) and not about origin in a
standard (standards grow: HTTP adds status codes, TLS adds versions). A *closed* set is safe, and the compiler
confirms it only where something makes the `switch` over the union exhaustive: a `default` branch that assigns the
value to `never`, an explicit return type on the function, or `noImplicitReturns`. A `switch` with none of these is a
list nothing checks.

**A trailing `...` admits that the list is incomplete, and where it belongs depends on what precedes it.** After a
stated criterion it is fine, because the items are illustration: *every runtime that implements the Fetch standard
shares it (Node, Deno, Bun, ...)* loses nothing if the reader has never heard of the third. Where the list is itself the
claim, *rejected by the higher layers (auth, session refresh, route guards, ...)* reports that more members exist and
gives no way to name one, so it is neither a list nor a rule. Supply the criterion, or finish the list and accept the
maintenance.

### Function and method

Slot 2 carries the work, and the types answer much of it on their own, so the bar for a sentence is high. State these,
and only where the signature does not already:

- whether a returned array, object, or `Map` is a live view or a copy, and whether the caller may mutate it;
- whether an argument is retained after the call, and whether the callee mutates it;
- what `undefined` means where the type allows it, and how it differs from an absent property;
- whether the function throws synchronously or returns a rejected promise, and which errors a caller is expected to
  match, by `instanceof`, by a `code` property, or through `error.cause`;
- whether a callback runs synchronously or on a later tick, and how many times;
- whether the method may be detached from its receiver and passed as a callback, or needs its `this`;
- what an `AbortSignal` does: whether abort rejects, resolves, or only stops future work;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- idempotence and ordering guarantees, and whether a returned iterable may be consumed more than once;
- side effects the name does not advertise, including I/O, storage, and module-level state.

Every item on that list is a property of the value. Where the caller got the value is the caller's sentence: `the
caller reads this from the Content-Length header` describes one call path and ages the day a second one appears (§1).

A function whose contract is exhausted by its name and types needs one line or nothing.

**Overloads document themselves separately.** In TypeScript each overload signature carries its own doc comment, and
the implementation signature's comment is not shown to callers, so a contract written only above the implementation
reaches nobody. In JavaScript the same shape is `@overload` blocks.

### Override and interface implementation

The reader has the inherited comment, or part of it. Measured on TypeScript 5.9.3, the language service takes the
summary and the tag block from the base method or the interface member independently, each only where the override's
own is empty. In the hover, an override with no doc comment shows the base's summary and tags; an override whose comment
is prose with no block tag shows that prose followed by the base's tags; an override with a `@param` or `@remarks` of
its own shows the base's summary followed by its own tags alone, and the base's `@remarks`, `@param`, and `@returns` are
gone. Your comment is read as the delta, and the hover assembles that delta by section. Write the delta, and check what
the reader is left holding.

Three cases, and the inherited contract decides which one you are in. Read it before you write.

1. **The override obeys the inherited contract.** Write no comment; the hover shows the inherited one whole. A bare
   `{@inheritDoc}` is not the same thing: TSDoc defines the tag and a generator that processes it copies the inherited
   text into the page, but the language service does not expand it and shows the tag text itself as the summary
   (measured on 5.9.3). Where a lint rule demands a comment on every method, report the rule rather than filling it.
2. **The inherited contract leaves the behavior open, and this class picks one.** State the resulting contract as a rule
   of this class, in one positive sentence: `A count of zero or less skips nothing and returns 0.` The inherited freedom
   is not news, and a sentence spent on it is provenance (§6). The same holds where the override narrows what the caller
   gets: `Returns an empty array rather than undefined.` A different result from the base class's *own implementation*
   is this case too, not the next one: where the base `supportsSeek()` returns `false` and its contract says *where
   supported*, an override returning `true` writes `Returns true; seek and rewind are supported` and does not name the
   base class.
3. **The override breaks the inherited contract.** A caller holding a base-class or interface reference is about to be
   wrong, so the deviation is the reason this comment exists. Name it in the base's own terms, with the condition it
   happens under. Check first whether the contract really forbids the behavior: a contract that says *may* permits it,
   and case 2 applies. A deviation is also a defect report, so raise it rather than only documenting it.

The mechanism that forced the choice is rationale and earns its slot under §2. `The read position indexes the buffer
{@link BufferedReader.buffer} returns` explains why a negative count cannot be honored, and it stays only where a
maintainer would otherwise relax the rule; a rule that matches what the base class itself does looks arbitrary to
nobody.

### Property, field, and constant

Document the unit, the range, the sentinel, and who may write it. A module-level constant whose membership rule is
non-obvious needs that rule spelled out; a reader adding an entry has no other source of truth. When the type's comment
already states the rule, the property comment shrinks to one sentence plus a link.

State a default with `@defaultValue` (`@default` in JSDoc) rather than in prose, so the tooling can render it in the
same table as the type.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence, positively, and before any neighboring
limit comes up: `This limit bounds only what the server sends.` A comment that leaves the scope to be inferred from a
contrast (`…which governs the direction this limit does not`) makes the reader subtract one limit from another and
reconstruct the missing verb. Both halves are facts; state them separately, this one first.

A constant whose value is a size or a duration states both forms. TSDoc has no tag that inlines a constant's value, so
the digits are typed by hand: `1 MiB (1048576 bytes)`. Both the digits and the unit can then go stale, so the pair
belongs in the comment on the constant itself, where the initializer is on the next line, and not in a caller's comment.
The unit has to be exact (`64000000` is `64 MB`, not `64 MiB`) or hedged in words: `about 1 GiB (1073741823 bytes)`.
The form is `english-developer-style` §5.

### Inline comment

An inline comment states why this line, for a reader who can already see the line. Four failure modes beyond narration:

- **Meta-commentary.** `…so check the flag here instead` describes what the comment is doing. State the fact: `The flag
  is only settled after hydration.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` mark it.
- **Counterfactual.** See §1. `if … were`, `would`, `otherwise the` mark it. Name the source of the constraint; do not
  simulate the branch the guard prevents.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason a value is coerced
  with `Number()` belongs at the coercion; repeating it inside the branch that rejects `NaN` splits one thought across
  two places.

### Comments a tool reads, not a human

Leave these alone; rewording, reflowing, or moving them changes behavior or destroys a record:

`// @ts-check`, `// @ts-nocheck`, `// @ts-ignore`, `// @ts-expect-error`; `/* eslint-disable */`,
`// eslint-disable-next-line <rule>`, `// biome-ignore lint/<rule>: <reason>`; `// prettier-ignore`;
`/* istanbul ignore next */`, `/* v8 ignore next */`; `/*#__PURE__*/`; `/* webpackChunkName: "…" */` and
`/* @vite-ignore */`; `/// <reference types="…" />`; `/** @jsx … */` and `/** @jsxImportSource … */`;
`//# sourceMappingURL=`; `/** @type {…} */` on a config export; `// Code generated … DO NOT EDIT.`; `TODO` and `FIXME`
markers; anything citing an issue or a URL.

Four placement hazards when you restructure code around them:

- **A directive applies to the next line, so reflowing retargets it.** Splitting a call across lines moves the reported
  position; inserting anything between the directive and its statement orphans it. `// @ts-expect-error` at least fails
  loudly when it stops covering an error; measured, that is `error TS2578: Unused '@ts-expect-error' directive`.
  `// @ts-ignore` never reports anything, and an unused `// eslint-disable-next-line` is caught only where
  `linterOptions.reportUnusedDisableDirectives` is left on.
- **`/*#__PURE__*/` annotates the call expression, not the statement.** It has to sit immediately before the call.
  Moving it to its own line above the statement is the natural thing to do while tidying, and it silently drops the
  tree-shaking hint that kept the call out of the bundle.
- **A `/** @type {…} */` cast belongs to the parenthesized expression that follows it.** Detach it and it becomes an
  ordinary doc comment on the statement; in a checked file, the cast is gone and the types change (§3a).
- **A blank line does not detach a doc comment.** Measured on TypeScript 5.9.3 and 7.0.2, declaration emit kept a doc
  comment that was separated from its declaration by a blank line. Do not "repair" such a gap on the theory that it is
  broken, and do not introduce one either: every human who opens the file reads it as detached.

### Test file

A test file is read in exactly one situation: it just went red. Write for that reader.

- **Summary = the rule the test guards**, stated positively and completely, as something you could assert. `It has to
  stay quiet when the socket did go away` leaves the reader guessing: not throw, not retry, not log? Name the
  observable. If you cannot phrase the rule as an observation, the test probably cannot check it either.
- **Use = what to do about the red build.** Which fixture to edit, which case to add, where the failure message states
  the rest.
- **The `describe` and `it` strings are the comment.** The reader sees them in the failure output before any file is
  opened, so they name the condition rather than the subject: `it('rejects with AbortError when the signal fires
  mid-flight')` beats `it('handles abort')`, and both beat `it('works')`. A doc comment above a test that repeats its
  `it` string has said everything twice and nothing once. Where the string states what the test establishes, the
  comment, if there is one, carries the reason or the construction (§3).

Deliberate duplication between a test's comment, a helper's comment, and the failure message is correct, because each
reader meets exactly one of the three. It does not extend to production code, where the type's comment and the member's
comment have the same reader.

**A failing test should read as a bug report, and four things write it.** Decide what each one carries before you write
the next; the reader sees them together in one report.

- **The `describe` string** carries what every test in the block shares: the unit under test and the condition they all
  sit under. A fact true of every test belongs here rather than in each `it`.
- **The `it` string** states what this one test establishes. `it('refuses a negative count')` is a finding;
  `it('ensureBytes')` is a location that makes the reader open the file. One assertion per test keeps the string able
  to do this, and keeps the report readable when several tests fail at once.
- **The assertion prints the values.** `assert.strictEqual(actual, expected)` and `expect(actual).toBe(expected)`
  print both values and an inline diff between them in the runner's output. `assert.ok(actual === expected)` prints the
  source expression (`The expression evaluated to a falsy value: assert.ok(actual === expected)`) and
  `expect(actual === expected).toBe(true)` prints `false`; neither prints the operand values, so the reader is left with
  a stack trace to reverse-engineer. `assert.throws(fn, RangeError)` and `expect(fn).toThrow(RangeError)` print the
  expected error class the same way. Choose the assertion that already prints what the reader needs, rather than
  describing it in a message.
- **The message adds what the other three cannot.** In a parameterized test (`it.each`, `test.each`) that is which case
  ran, so the `%s` or `$name` placeholder in the `it` string is the whole message. Under a bare `assert.ok` it is the
  invariant, because nothing else states it. Where the values are arguments already, do not restate them; where the
  `describe` or `it` string states the scenario, do not restate that either. A message read while someone scans a stack
  trace competes with the lines around it.

`assert.fail()` with no message is that defect at its limit: it reports that something is wrong and nothing else.

This does not contradict the duplication paragraph above. A string is printed in the report; a comment at the top of the
file is read only once someone opens it. Repeating a comment in a message is the useful duplication; repeating a string
is the one that costs.

### Module documentation

One comment per entry point, at the top of the file, tagged `@packageDocumentation` for TSDoc or `@module` for JSDoc.
Without the tag it is read as documentation for whatever declaration happens to follow it.

It is the entry point: what the module is for, which exports are the way in, which are internal, and any rule that holds
across the module (naming, error conventions, what must be disposed). The export list is generated; a hand-written copy
is the membership list all over again.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following options` are invisible in a rendered page
and in an editor hover, silently wrong after a reorder, and unchecked by most toolchains. Name the target instead.

| Form | Refers to |
| --- | --- |
| `` `identifier` `` | code the reader will not navigate to: a literal, a CLI flag, a JSON key |
| `{@link Thing}` | a declaration the reader may want to follow |
| `{@link Thing.member}` | a member of a declaration |
| `{@link Thing.member \| custom text}` | the same, with the sentence's own wording (TSDoc spelling) |
| `{@link https://example.com \| the spec}` | an external page |

Markdown is the markup: backticks for inline code, a blank `*` line for a paragraph break, a fenced block for a sample.
There is no `{@code}` and no `<p>`, and writing either one ships the tag itself to the reader. JSDoc's older link
spellings (`{@link Thing|text}` with no spaces, and `{@link Thing text}`) still parse in many tools; follow the file you
are in rather than converting a codebase mid-edit.

**Know what checks your links, because it is not the compiler.** Measured on TypeScript 5.9.3 and 7.0.2,
`{@link NoSuchThing}` compiles clean and emits nothing. What does check:

- **TypeDoc** warns through `validation.invalidLink`, which is on by default, and fails the build only under
  `treatValidationWarningsAsErrors`.
- **API Extractor** reports `ae-unresolved-link` for a declaration reference it cannot resolve.
- **Your editor** resolves the link in the hover, where most readers meet it, and a broken one shows as literal text
  there.

None of these runs unless your build runs it. Find out which of the three your project has before you treat a green
build as proof, and prefer a `{@link}` to a bare backticked name either way, because a reference something *can* check
beats one nothing can.

**An issue or PR number is an address, not a definition.** Name the phenomenon in the comment, then give the number so a
reader can find the history: `a length read from the frame header sizes the allocation (issue #4015)`. The number must
not carry the meaning: `the shape of issue #4015`, `the same format as #1231`, `the bug #4015 fixed` count as content
for someone who already knows the ticket and as nothing for everyone else. The test: cover the number and read the
sentence. If what remains states no fact, the comment has none. A bare `see #4015` fails the same test from the other
end, and a TypeDoc page reaches readers with no access to the tracker at all.

The number may open the sentence, as long as the phenomenon arrives in the same one. `The scenario from issue #4015: a
frame claiming more bytes than the message still holds` passes, because covering the number leaves the failure named.
The rule is about the number's role, not its position.

The same holds for a commit hash, a mailing-list thread, or a released version. It does **not** hold for a normative
source (an RFC, a protocol specification, a vendor's published documentation), which may define a format the comment
then need not restate.

**A ticket number is not a name.** `a #4015 hardening check` names nothing, and the check has a name in the code. Use
that name, and cite the number once, where the history belongs.

## 6. Tags

**Pick one vocabulary per repository and stay in it.** TSDoc is the small standardized set that API Extractor and
TypeDoc agree on, and `eslint-plugin-tsdoc` enforces its syntax. JSDoc is the larger, looser one that
`eslint-plugin-jsdoc` checks. They overlap but disagree on spellings (`@returns` versus `@return`, `@defaultValue`
versus `@default`, `@typeParam` versus `@template`), and a file that mixes them renders wrong somewhere.

- **A tag earns its line by adding what the signature lacks.** `@param value - The value` is noise in any language and
  worse here, because the type sits three characters away in the same hover. A lint rule that demands a tag per
  parameter produces that noise at scale; report that rather than filling it in.
- **`@param name - description`.** The hyphen is TSDoc's separator between the name and the prose, and the generators
  expect it.
- **`@returns` when the summary does not already say it.** `Returns the backing map.` followed by `@returns the backing
  map` is one sentence billed twice.
- **`@throws`** is not in TSDoc's standard set but is widely rendered; use it to say what a caller matches on, not
  merely that something can fail. In an async function, say whether the failure arrives as a rejection.
- **`@remarks`** ends the summary section (§3). Everything the index page should not carry goes after it.
- **`@example`** earns its place on published API and almost nowhere else. It is a fenced code block, and it goes stale
  like any other code that nothing compiles.
- **`@deprecated`** must name the replacement. Editors strike through every call site, so it is one of the few tags a
  machine acts on.
- **`@typeParam T - …`** (`@template` in JSDoc) when a type parameter has a constraint the reader must satisfy that the
  `extends` clause does not express.
- **`{@inheritDoc}`** is the tag for an override that adds nothing, where the repository's generator processes it. Which
  case an override is in, and what its body may say, is §4's *Override* genre. What the base permits is not a fact of
  this declaration's contract and pays for nothing under §7a: `the interface permits undefined, but this implementation
  never returns it` spends a sentence on the provenance of a guarantee the caller already has.
- **A tag block you write on an override replaces the inherited one; it does not add to it.** Measured on TypeScript
  5.9.3, the hover takes the tags from the base only where the override has no block tag of its own, so moving one
  special case into `@returns` drops everything the inherited `@returns`, `@param`, and `@remarks` said about the
  ordinary case, and the reader ends up with a shorter contract than they had. Keep the specialization in the prose,
  with no block tag, and the inherited tags survive untouched; or write the complete tag block on purpose. Judge it by
  the complete hover the reader ends up with, not by the sentence you moved.
- **Release tags** (`@public`, `@beta`, `@alpha`, `@internal`) are build inputs, not notes (§6a).
- Tag order: summary, `@remarks`, `@typeParam`, `@param`, `@returns`, `@throws`, `@example`, `@defaultValue`, `@see`,
  `@deprecated`, release tag last.

Two syntax hazards that have nothing to do with content:

- **A line that starts with `@` is read as a block tag.** A scoped package name or an email address at the start of a
  line becomes a bogus tag and swallows the paragraph under it. Wrap it in backticks, or move it off the line start.
- **`*/` ends the comment, wherever it appears.** A glob, a regular expression, or a code sample containing `*/`
  terminates the doc comment early and turns the rest of it into a syntax error, or worse, into code.

## 6a. When the comment ships as documentation

A doc comment on an exported declaration reaches people through the `.d.ts` that ships in the package: declaration emit
copies it verbatim (measured on TypeScript 5.9.3 and 7.0.2), and for most consumers that hover **is** the documentation,
whether or not you also publish a site. The same text may reach a second surface: a TypeDoc page, an API Extractor
report, an OpenAPI or JSON Schema `description` a generator lifts out of it, a `--help` string.

**The reader changes, and that is the whole section.** They work against your API from the outside: they cannot open
the code, cannot resolve a link to something you did not export, and have no `git log`. Three rules follow.

1. **Know which surface the comment lands on, because the markup differs.** In an editor hover and on a TypeDoc page,
   Markdown renders and `{@link}` is a hyperlink. In a `description` a generator lifts into YAML or JSON, backticks,
   pipes, and `{@link}` all arrive as literal text. Write plain sentences for the second case, and check what your
   generator does before assuming the first.
2. **A reference the reader cannot follow has to be spelled out.** A `{@link}` to a declaration the package does not
   export resolves in your editor and points nowhere for them; API Extractor names the related defect
   `ae-forgotten-export` when such a type leaks into the public signature. Name the rule instead of linking to the thing
   that states it.
3. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values an option accepts, the
   keys a result object may hold: that list is the only source this reader has, so a criterion may replace it only when
   the reader can apply the criterion *without opening anything*. §4's own warning applies at full force: if the honest
   criterion is circular, the list was the answer, and the repair is to complete it and verify every member against the
   code in the same edit. An incomplete list shipped as documentation is worse than no list.

Then the mechanics, where the two dialects part company.

**A release tag is a build switch.** Measured on TypeScript 5.9.3 and 7.0.2, `--stripInternal` removes an `@internal`
declaration from the emitted `.d.ts` entirely: not its comment, the whole declaration. API Extractor keys its trimmed
rollups and its checked-in `.api.md` report off the same tags. Adding or removing one is an API change that happens to
be spelled as a comment edit, and it belongs in its own commit with the regenerated output.

**Prose is cheaper than a release tag, but not free.** An `.api.md` report is designed to diff only on contractual
change, so rewording a summary does not touch it. A committed OpenAPI spec or JSON Schema generated from the same
comments does diff on every word. Where the generated output is committed, regenerate and commit it, or the drift check
fails.

Because some edits cost that diff, the bar rises, but it rises for **rewording**, not for **enriching**. A synonym or a
smoother clause is churn that ships. A fact the description does not carry and its reader needs is worth the diff every
time, even when every sentence already there is true. "It is correct as written" settles the first case and not the
second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one by going stale. Skip
it for:

- a declaration whose name and types are the whole contract, which in TypeScript is more declarations than in a language
  with weaker types, because the reader sees the types in the same hover;
- an override or implementation that adds nothing to the documented contract;
- a component prop whose name and type say it;
- a non-exported helper whose single call site makes it obvious;
- anything the code states better, which is most narration.

The corollary: an exported declaration with a non-obvious contract is not optional, however self-evident the name looks
to the person who just wrote it.

A rule that demands a doc comment on everything (`jsdoc/require-jsdoc`, or TypeDoc's `validation.notDocumented` pointed
at every reflection) manufactures exactly the comments this section exists to prevent. Scope it to the public API or
turn it off; do not satisfy it.

## 7a. Editing an existing comment

Most of the time you are rewriting a comment, not writing one. Different job, different failure mode: a rewrite drifts
longer, because every restructuring pass adds a sentence and none takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the old comment did not
  carry: a unit, a side effect, a mutation rule, an invariant. Name that fact to yourself; if you cannot, you are
  re-phrasing, and the old wording stays.
- **A near-empty before-version makes the budget vacuous, not permissive.** `{@inheritDoc}`, a one-line stub, or no
  comment at all carries no facts, so everything in front of you is growth and none of it has been paid. Judge it as a
  comment written from scratch: every sentence earns its slot under §2, and on an override under §4's three cases. Where
  the branch under review wrote the paragraph an hour ago, its text carries no more authority than your own first draft.
- **A test is evidence, not a paying fact.** A test that pins the behavior establishes that it is intentional and stable
  enough to rely on; it does not make the behavior part of the contract, because a test pins implementation behavior
  just as readily. Name the fact a caller relies on and cite the test as support for it. `A test asserts it` pays for
  nothing on its own.
- **Decompression is paid growth.** A comment can be too dense to read while being too *short* to fix under the rule
  above, and the budget then blocks the only repair there is. Unpacking one of the over-compressed shapes
  `english-developer-style` §4 tabulates adds words and no fact, and it is not churn; the payment is the re-read it
  removes. Name the construction you unpacked instead of naming a fact. That skill owns which construction is which and
  how to unpack it; this bullet only states that the budget does not block it. The exemption is that narrow: it does not
  license explaining more, hedging, or a second sentence of rationale, which still need a fact.
- **Check every identifier the old comment names.** A comment written before a refactor cites options, constants, and
  methods that no longer exist. In a `.ts` file nothing tells you: a stale name in prose, in backticks, or in a
  `{@link}` compiles and renders (§3a, §5). Grep each one, and convert what you verify into a `{@link}`, so the next
  reader at least gets a link that visibly fails.
- **When you lift a rule into the type's comment, cut it from the member.** The member keeps the one sentence that
  specializes the rule, plus the link. Two full statements of the same rule is the most common outcome of a good
  structural edit and the easiest to miss, because each of the two reads well on its own.
- **Deleting is an edit, and every cut is reported.** A list of callers, a rejected alternative, a benchmark number, a
  reference to the pull request that introduced the code: cutting these is usually the highest-value change in the diff,
  even though the result looks like less work. Delete sentence by sentence, and report each deleted sentence with the
  fact it carried and where that fact now lives: a tag, another declaration, the commit message, or nowhere, with the
  reason. A rationale sentence stays only where a maintainer reading the rule would ask why or would be tempted to relax
  it; the test is whether the sentence would come up as a question in code review. A rewrite that reads better and says
  less is the failure this rule exists to prevent.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule governs the body, not the
  first sentence. A four-paragraph summary with no `@remarks`, or one that opens `This function is a wrapper around X`,
  stays broken until someone rewrites it, and "I had no new fact to add" is not a reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot be verified as
  comment-only, and that verification makes a large sweep safe. In a checked `.js` file, editing a type tag is moving
  code (§3a).

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions and have to
establish what actually changed: reviewing someone else's edit, checking your own before you commit it, or judging a
machine-generated one.

The new version will read better. It was written second, by someone who had just finished understanding the code, and a
fact that vanished leaves no trace in the text that replaced it, so reading forward confirms that impression and finds
nothing. The work therefore runs backwards: read the **old** version carefully first, and form the verdict last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one mutation or ownership rule, one side effect, one ordering or timing constraint, one
lifecycle obligation, one named collaborator, one link target, or one stated default. A topic sentence is not a fact,
and neither is a restatement of the signature. What the base class or interface permits, and what another API does, is
neither: it names nothing a caller of this declaration relies on, so it takes a row as provenance and pays for no growth
in step 3 (§6). Compare facts, not sentences: at sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Four defenses hold:

- the fact was wrong, which includes a claim the old text made and the code does not support;
- the fact moved to the type's comment or the module comment, and you can point at the sentence that now carries it;
- the fact moved into a tag where §6 places it, or into the signature itself: a narrowed type, a renamed parameter, a
  default the declaration now states;
- the fact was rationale, the contract it explained is stated completely without it, and the rationale no longer earns a
  slot under §2.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of those is the sentence
someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you name the fact. A
first sentence repaired under §3 pays for itself and is exempt. Restructuring at equal length is free and needs no
justification. Where the old version carried no fact (`{@inheritDoc}`, a stub, no comment at all), the budget measures
nothing: judge every sentence of the new version on whether it earns its slot under §2, and on an override under §4's
three cases (§7a).

Two more exemptions, both from §7a. A stacked relative, an elliptical nominal opener, or a noun pile unpacked into a
finite clause is paid growth: the payment is the re-read it removes, and the rewrite names the construction rather than
a fact. And growth is not the only failure: a rewrite that keeps the old version's density while changing its words has
bought nothing and belongs in step 5.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the tests, or to a contract it links to. **The old comment is provenance, not
evidence.** That it made the claim shows the claim was made, not that it holds, so a claim carried over unchanged is
checked like any other. A claim that traces to none of those sources is invented, however plausible it sounds, and
plausible is the dangerous case: a wrong invariant in a doc comment is a wrong invariant a caller will build on, and an
inherited one is worse, because it has outlived every pass that did not check it. The commit message is not a source
either. It records what someone meant to do; the comment has to describe what the code does.

**An inference from the code is not the code.** A census of call sites establishes what is true today, not why the code
is the way it is. `No caller passes a negative value` supports `nothing inside this package reaches the guard`, and
supports nothing about who the guard is for. Design intent traces to a comment, to a specification, or to the shape of
the API itself, never to a count of callers. This is §4's membership rule from the other end: a roll call of today's
callers is not a law about tomorrow's.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer attention now and costs the
next reader a `git blame` later. §7a has already settled that the old wording stays; here you look for the places where
it did not. Where the comment feeds a committed generated file (§6a), the churn arrives with that file's diff attached.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Four failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is the characteristic
  failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Counterfactual.** The comment describes what would happen on a path this code rules out, rather than what it does.
  §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else. No build step
  catches this, so it is the most valuable thing a comparison pass finds.

A comment something other than a human reads is out of scope for all of these; see §4 for the list and for what moving
one breaks.

**7. Prove the code did not move, and in `.js` prove the types did not either.**

A sweep that edits comments across many files is reviewable only if the claim "comments only" is mechanical rather than
asserted. Parse each file before and after and re-print it without comments:

```javascript
const ts = require("typescript");
const src = require("node:fs").readFileSync(path, "utf8");
const sf = ts.createSourceFile(path, src, ts.ScriptTarget.Latest, false);
// identical output before and after means no executable code moved
process.stdout.write(ts.createPrinter({ removeComments: true }).printFile(sf));
```

Any difference means the pass touched code, and the pass is wrong until it is explained.

**This proof is complete for `.ts` and incomplete for checked `.js`.** The printer discards exactly what §3a says is
code there: run it over a `.js` file and `@param {string}` and `/** @type {…} */` vanish, so a sweep that changed both
would still print identically. The second leg is a diagnostic comparison: `tsc --noEmit` before and after must report
the same set. Without it, the strip-and-compare result is evidence about the wrong file type.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it makes two people comparing the same pair reach the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and make it a `{@link}` (§5) |
| Duplicated rule | Cut the copy the type's comment now carries (§7a) |
| Churn | Restore the old wording |
| Density kept | Unpack the stacked relative, the elliptical opener, or the noun pile (§7a) |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Counterfactual | Cut the simulation; re-evaluate any rationale left standing under §2 |
| Unearned rationale | Cut the rationale; keep the complete contract (§2) |
| Base-class provenance | Cut it; keep the resulting contract (§6) |
| Stale inline comment | Rewrite it from the code |
| Summary with no `@remarks` boundary | Cut it to one sentence and move the rest (§3) |
| Retargeted directive | Put it back adjacent to the line it suppresses (§4) |
| Type tag changed in a checked `.js` file | Treat it as a code change and review it as one (§3a) |
| Release tag added or removed | Regenerate the shipped output and split the commit (§6a) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the first sentence third person with the subject omitted, standing alone, with no term this comment introduces?
- Does the summary end where you meant it to, or does a missing `@remarks` push four paragraphs onto every index page?
- Could a reader reconstruct the first sentence from the declaration's name or the test's `it` string alone?
- In a regression test's comment: the rule first, the old defect in one past-tense sentence, and any equivalence with
  the old behavior kept (§1)?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test from the comment
  alone?
- Is any rationale here commit-message material?
- Any sentence describing a previous version of the code: `now`, `no longer`, `used to`?
- Any sentence describing a code path this code does not have: what would happen if the rule were broken, rather than
  what the code does about it?
- Does the comment explain another module's internals instead of linking to it?
- Any positional reference: `below`, `above`, `the following`, `the other way`?
- Does a limit state what it bounds, rather than only what some neighboring limit bounds?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Any backticked name that should be a `{@link}`, and does anything in this build check the links?
- Does every tag add something the signature does not, and in a `.ts` file, does any tag carry a type that the signature
  already states?
- If this is a `.js` file: is `checkJs` or `// @ts-check` on, and did this edit change a type (§3a)?
- On an override or an interface implementation: which of §4's three cases is it in, does any sentence describe the
  base's freedom rather than this method's rule, and does a tag of your own hide the inherited tags the caller still
  needs (§6)?
- Does every term here have a definition outside this comment, and does every name match what the code calls the thing
  (`english-developer-style` §4a)?
- For each rationale sentence: would deleting just that sentence change what a caller may rely on, or leave a maintainer
  unable to see why a constraint is there? If not, delete it.
- Would deleting the whole comment lose anything?
- Is every `@ts-expect-error`, `eslint-disable-next-line`, `/*#__PURE__*/`, and `@type` cast still worded and placed
  exactly as it was?
- If the comment ships as documentation (§6a): can its reader follow every reference without opening the code, and did
  you regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the type's comment or on a `@param` line?
- Any list that a criterion would replace, or that the reader's editor already answers? Can the set gain a member
  without anything forcing an edit here, and does a trailing `...` stand where no criterion precedes it?
- Does every name the old comment mentioned still exist?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the facts were already there. The
second grows, because they were missing. Do not read either one as the target shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a sweeper can recognize in
the wild is an example it will paste instead of derive, and a rewrite that matches this file word for word proves
nothing about whether the rules were applied.

### A TypeScript method, where the tags restated the types

**Before**: four tags, no contract. Every one of them is readable off the signature, and the one thing a caller can get
wrong is not stated anywhere.

```typescript
/**
 * Gets the headers.
 *
 * @param name - The name.
 * @returns {string[]} The values.
 */
getAll(name: string): string[] {
  return this.#store.get(name.toLowerCase()) ?? [];
}
```

**After**: the summary carries what the tags were spending four lines on, and the body carries the two facts the
signature cannot: the case rule and the ownership of the returned array.

```typescript
/**
 * Returns every value recorded for a header, in the order it was added.
 *
 * @remarks
 * Header names are matched case-insensitively. The array is a live view of the store: mutate it
 * and the recorded header changes with it. Copy it before handing it to a caller you do not
 * control. An unknown name yields an empty array rather than `undefined`.
 */
getAll(name: string): string[] { … }
```

What changed, slot by slot: the summary stopped restating the method name and gained the ordering guarantee (§3);
`@param` and `@returns` went, because a type is not a fact in TypeScript (§3a, §6); the `{string[]}` in `@returns` went
with them; and slot 2 appeared, carrying case-insensitivity, aliasing, and the empty-versus-`undefined` rule (§4). Two
lines longer, and every added line names a fact the reader would otherwise discover by breaking something.

### A checked JavaScript function, where the failure contract was missing

The file below is `.js` under `checkJs`, so its type tags are the signature (§3a). Watch them come through the rewrite
untouched: they are code, and this is a comment edit.

**Before**: narrates the implementation, and leaves out everything a caller has to handle.

```javascript
/**
 * Sends the request. Loops over the attempts, waiting a bit longer each time,
 * and returns the response when one of them works.
 *
 * @param {string} url
 * @param {{ attempts?: number, signal?: AbortSignal }} [options]
 * @returns {Promise<Response>}
 */
export async function fetchWithRetry(url, { attempts = 3, signal } = {}) { … }
```

**After**: states what the caller may rely on, what reaches them on failure, and what abort does.

```javascript
/**
 * Sends a GET request, retrying a failed attempt with exponential backoff.
 *
 * Only a network failure and a 5xx response are retried; a 4xx comes back as-is on the first
 * attempt, because a retry sends the same request and gets the same status. Every failure
 * arrives as a rejection, never as an error the caller can catch synchronously: after the last
 * attempt the promise rejects with the final error, and `error.cause` holds the one before it.
 * Aborting `signal` rejects with an `AbortError` without waiting out the pending backoff.
 *
 * @param {string} url - an absolute URL; a relative one rejects
 * @param {{ attempts?: number, signal?: AbortSignal }} [options] - `attempts` counts total tries,
 *   not retries, so `1` disables the backoff entirely
 * @returns {Promise<Response>} - the first response that was not retried, 4xx included
 */
export async function fetchWithRetry(url, { attempts = 3, signal } = {}) { … }
```

The rewrite grew by six lines and paid for them with four facts the original did not carry: which responses are retried
and why, that failures arrive as rejections with a `cause` chain, what abort does to a pending backoff, and that
`attempts` counts tries rather than retries, the off-by-one a reader gets wrong because the name reads either way.
`Loops over the attempts` went, because the body already said it (§1).

The three tag lines are the ones to check twice in review. Their prose grew, which is an ordinary comment edit; their
braces did not change, and that keeps the diff safe to read as one. Had a `{number}` become a `{number | string}` in the
same pass, that would be a signature change wearing a comment's clothes, and §7b's strip-and-compare proof would not
have caught it.
