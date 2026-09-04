---
name: rustdoc-authoring
description: >-
  Load before writing, editing, or reviewing a doc comment or inline comment in Rust: the comment
  on a new or changed function, type, trait, or module, a # Errors or # Panics section for behavior
  that just changed, a # Safety section on an unsafe fn, a // SAFETY: comment beside an unsafe
  block, a doc example the build compiles and runs, the comment on a test just added, a trait
  method implementation that departs from the trait's contract. Inside a coding task on a Rust
  codebase ("fix the bug", "add the method") load it as soon as the change touches a comment,
  before writing it. Also load to decide whether an item needs a comment at all, or to compare two
  versions of one. Governs what the comment says and in which order: the summary paragraph, what
  the signature already says, contract before rationale, the headings that replace tags, intra-doc
  links, examples that run as tests, when to write nothing, how far a rewrite may grow. Wording is
  english-developer-style's; load both.
---

# Authoring a Rust doc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect belong to `english-developer-style`: load it too, and defer to it on the prose. The two
compose: this skill picks the slots; that one writes the sentences.

It is the Rust sibling of `javadoc-authoring` and `godoc-authoring` and keeps their section
numbering, so a review that cites "§7b" means the same rubric in any of the three. Read this one for
Rust; do not translate either of the others in your head. The slot model transfers unchanged. Three
things do not, and they are the reason this file exists:

- **Rust's type system carries much of what a Java or Go comment has to state in prose.** `Option`
  is the nullability rule, `Result` is the error list, ownership and `&mut` are the aliasing
  contract, `Send` and `Sync` are the threading model. §4 is mostly about what is *left*.
- **A doc example compiles and runs.** The code in a doc comment is a test the build executes, so
  the strongest statement a Rust comment can make is a checked assertion rather than a claim (§6).
- **Nothing formats a doc comment for you.** Measured on rustfmt 1.8.0, stable rustfmt leaves doc
  comments byte for byte alone: it does not reflow a 180-column line, does not normalize a list
  marker, does not fix indentation. `wrap_comments` and `format_code_in_doc_comments` are
  nightly-only and off. Where `gofmt` lets a Go author write content and forget layout, you own the
  layout here. Match the wrapping width the file already uses.

Everything measured below was measured on rustc, cargo 1.92.0, clippy 0.1.92, and rustfmt 1.8.0.

## 1. The correction that matters most

"Document the why, not the what" is half wrong for a doc comment, and the wrong half does the
damage.

An inline `//` comment inside a function documents the **why**; it sits next to code the reader can
already see. A doc comment on an item documents the **contract**: what a caller may rely on, what an
implementer must guarantee, what holds before and after. That is a *what* at the level of a promise,
not a restatement of the code.

The failure mode is therefore not "explains what the code does". It is any of these:

- **Narrating the implementation.** `Iterates the entries and inserts each into the map.` The body
  already states it, and the comment becomes false on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the boilerplate every handler
  shared.` That belongs in the commit message and the pull request description. A doc comment's
  reader has to *use* or *fix* the thing, not decide whether to merge it.
- **Restating the signature.** This failure is specific to Rust and the most common. `Returns None
  when the key is absent. Takes ownership of the buffer. The error type is io::Error.` The reader
  has `Option<&V>`, `buf: Vec<u8>`, and `io::Result<_>` on the screen. A comment that spends its
  first paragraph re-typing the signature in English has spent the reader's attention on the one
  part they did not need.

**The test is the refactor, not the reader.** Rewrite the body so it behaves identically and reads
differently: a `for` loop becomes an iterator chain, a helper is inlined, a field is renamed. Every
sentence you would then have to edit was implementation, whatever it sounded like. This is the
operative rule, because it settles cases that "specification, not details" argues about forever, and
it does not soften with visibility: a private function's comment goes stale on that refactor exactly
as a `pub` one's does, and the cost of a comment that lies is the same either way.

**The caller substitutes too, and catches what the refactor cannot.** Imagine a new legitimate
caller supplying the same argument for a different reason. A sentence that then describes only the
old call path is caller context, not this item's contract. `A negative n is refused before any byte
is read` survives the substitution; `because a count taken from a length the backend declared can be
negative` does not.

Cutting is not the whole repair, because the rationale slot can be open and merely filled wrong.
Where a value came from does not explain why the item behaves as it does; a local reason, where one
exists, is a property of this item's own contract. In the example above the local reason is that
`Ok(false)` already means the requested bytes are unavailable under the normal contract, so an
invalid request is reported through `Err` and not through the same channel. Look for the local
reason before concluding that the slot was never open, then ask §2's question of it: does the rule
look arbitrary without it, or would a maintainer relax it incorrectly? A reason any reader would
have assumed fails that question and stays out, however true it is.

Provenance crosses into a callee's comment where it is that item's own contract: a protocol function
whose parameter *is* the declared length minus the header documents its own layer rather than
borrowing the one above it. **State the local rule at the lowest-level API, and the scenario at the
layer where the scenario exists.** A guard found through one concrete call path does not thereby own
that path's story.

**Sufficiency** scales with visibility: how much the comment may leave to the code beside it.

| Where | What the comment must carry |
| --- | --- |
| `pub` item reachable from outside the crate, including the methods of such a trait | Complete without the code. An implementer of your trait is a caller, so a trait's required and provided methods are public API here (§6a) |
| `pub(crate)`, `pub(super)`, private | May be elliptical and lean on the body beside it. Often there is no contract distinct from the implementation at all, and §7's "the name and types are the whole contract" usually applies |
| inline | Nothing about the contract. The reader has the code |

For an inline comment the bar is negative: **a competent reader is looking at this code and
understanding it correctly; write the comment only where they would not.** A reason that surprises,
a bound that looks arbitrary, an order that looks swappable, a branch that looks dead. Where their
expectation and the code agree, the comment is noise, and later stale noise.

A fourth failure, specific to a codebase that has been refactored, is **narrating the code's
history**. `poll now returns Pending instead of blocking, so callers no longer need their own
timeout` describes a transition between two versions, and the reader has only this one. Rewrite it
as the state that holds: what `poll` returns, and what the caller must do.

**Deleting the narration is not deleting the finding.** A comment that carries a measured number
(`a floor of 100 over top_k * 5 only moved the coupling past k = 20`, `the outline splits into 12
chunks over 473 KB`) carries a fact, and usually the fact that decided the code. Change its tense
and cut the account of how it was discovered; keep the number and what it measures. §7b step 2
counts a dropped measurement as a lost fact, not as a trim, and a tuned constant whose measurement
is gone is a constant the next reader will change back.

One exception. **The comment on a regression test may tell history, and an equivalence is not
history.** The test guards the defect, so the defect belongs in the comment: state the rule the test
asserts first, then the defect in one past-tense sentence with the error variant or the panic: `A
negative count used to be reported as available, and the caller then panicked with an index out of
bounds.` A comment that opens with the defect makes the reader reconstruct the broken version to
understand the fixed one (measured on one branch: a blind reader ranked the version that opened with
`used to` fourth of five on that ground alone). Do not narrate the old mechanism in the present
tense, and do not recast it as a chain of `would` clauses. History narration, which this section
forbids, is a sentence whose only content is that the code changed. A sentence that argues the new
behavior is safe **because it is identical to the old one** is rationale, and the old behavior is
its comparison term. Keep the comparison; it is the whole argument.

- *Keep:* `a reader that has not yet observed the store behaves exactly as every reader did before
  this flag was added: it reads from the buffer and the wrapped stream as if nothing were closed`
- *Wrong repair:* `a reader on another thread may not observe the store and may still read from
  the buffer` (the equivalence, which is the reason a `Relaxed` store is enough, is gone)

A fifth is the mirror image of the fourth: **narrating the branch that does not exist**, what the
code would do on an input it refuses, or under a rule it does not implement. History narration gives
the reader a past version of the code; this gives them a version that never existed. `If uppercase
names were allowed, the label built from this name would be rejected downstream and the deployment
would never start` describes a path no build of this code can take. No refactor can make it false
and no reader can check it, so it survives every review.

This does not ban consequences. What the code does when the contract is broken (which error variant
it returns, whether it panics, what state the value is left in) is contract, and the `# Errors` or
`# Panics` section (§6) carries it. Cut the simulation of the branch the guard prevents.

**The test: could a reader falsify the sentence by reading this repository?**

- `Returns [`Error::NotLowercase`] when the name contains an uppercase letter`: contract. It names a
  path this code has.
- `The name becomes a Kubernetes label, and a label admits no uppercase letter`: eligible. It names
  the *source* of the constraint, the shape rationale takes when it earns a slot at all. It still
  has to earn it.
- `Otherwise the deployment would be rejected and never start`: cut. Nothing here produces that, and
  the system that would is one the reader cannot see and you do not control.

**Where the reason belongs in the comment at all, name the source of the constraint rather than the
disaster it averts.** Cutting a counterfactual obliges you to put nothing in its place. §2 fills the
empty rationale slot only where the rule would otherwise look arbitrary or be easy to change
incorrectly, never merely because a source exists and is true.

A source the reader cannot infer from the code is the likeliest to earn its sentence, but
reachability is evidence, not the test. `The size must be a power of two because indexing masks with
size - 1` earns its place with the masking five lines below: the restriction looks arbitrary without
it and the next maintainer will relax it. `RFC 1234 permits three encodings` earns nothing when no
caller needs to know why this one was chosen.

Where the constraint is *enforced*, an earned sentence belongs inline beside the guard: the reader
sees the `return Err(..)` and cannot see why the value is unacceptable. Where the constraint is only
*stated*, in a doc comment, ask the question again from scratch. Completeness does not settle it: a
contract states itself completely by definition, so `the sections already say what happens` closes
nothing. The test stays the same: would the rule look arbitrary, and is it easy to change
incorrectly?

An item with more than one failure channel, an `Err` beside a sentinel `Ok(false)`, is not an
exception to that test. The `# Errors` section and the sentence on the return value state each
outcome, and a maintainer reading them is expected to keep them apart. A sentence explaining why an
invalid argument returns `Err` rather than the sentinel is the reason any reader would have assumed
(measured: a maintainer who met such a sentence in review called it common sense). Leave it out.

## 2. The four slots

A doc comment has at most four slots, in this order.

| # | Slot | Answers | Skip when |
| --- | ------ | --------- | ----------- |
| 1 | **Summary** | What is this, or when does it fire? | Never; always present |
| 2 | **Contract** | What may a caller rely on? What must an implementer guarantee? | The signature genuinely says all of it |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader do next? | The contract already implies the action |

Two rules govern the order.

**Contract before mechanism.** State the rule the reader must satisfy before the machinery that
enforces it, and before what some *other* module does. A comment that opens with a neighboring type
forces the reader to reconstruct the rule from negative examples. State it positively, in one place,
first.

**When only one slot fits, keep the contract.** Rationale is the first slot to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

**Removing a bad explanation does not create an obligation to replace it.** A rationale slot emptied
by a cut stays empty until the finished contract, read on its own, turns out to need one. Start from
the contract, not from the gap.

**Make the obligated party the subject.** Obligations come in two shapes. A *stated* obligation
carries a *must*, *has to*, *may not*, or *should*, and whoever has to comply belongs in the
subject: not the thing acted on (`Every backend message must be read through read_message_len`,
which names no one and lets `it` drift to the reader by the next clause), not the act (`relaxing a
protocol check must not be reachable`), and not an item that merely performs the act for someone
else (`mark_broken must still run` obliges `Stream`). A named item in the subject is right only
where that item is itself what must comply: `read_untracked_len must leave no envelope behind`. The
party need not be human, but it must act: a driver, a check, a reader. A mode constant or a
configured number complies with nothing.

A *census* is a rule for the next maintainer, written instead as a report on today's call sites:
`Every site that dispatches on a message type reads the tag through this function`, `CopyData is
the one such site`. It is flat indicative with no modal, so test it: **if a second such caller
appeared tomorrow, would this paragraph tell it that it is obliged?** Judge the paragraph, not the
sentence; an example may follow a law that is already correctly stated. Write the law, not the list
of today's call sites.

Watch the intransitive modal, where the party hides best: `every variant has to appear in
HARDENED`, `an unknown value must fall back to Mode::Fail`. Nothing appears or falls back on its
own; name what does it.

Out of reach of this rule: an imperative, which already addresses the party (`Call it where the
framed dialogue resumes`), including one that carries rationale (`so mirror that here`); a
constraint on a *value* (`must not exceed MAX_MESSAGE_SIZE`), which bounds a number rather than
behavior; a field comment naming who writes or reads the field, which is the membership list §4
calls for; and an inline comment whose next statement is the actor (`// The envelope must be fully
consumed` above the `end_message()` that consumes it), after checking that the next line really is
the actor and not test setup standing between the comment and the call it constrains.

Slot 4 has a Rust-specific form: the `# Examples` block. It is the Use slot written as code the
build runs, so it is the only slot that cannot silently go stale. Prefer it to a prose paragraph
describing how to call the thing (§6).

Most items need slots 1 and 2 only. An accessor needs slot 1. Do not manufacture the other slots to
fill a template; an absent slot is not a gap.

**Size the comment to the item.** A doc comment longer than the function it documents is not
automatically wrong (an invariant can be worth ten lines over a three-line method), but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two
sentences of it, and only for the part a reader would otherwise get wrong. The rest belongs in the
commit message. As a working size, a test module's comment is two to five sentences and a function
comment fits in one glance; past that you are describing the investigation, not the contract, so
keep the rule and the exception and move the rest.

A measurement does not count against that budget. `k = 20`, `473 KB`, `eight of thirty queries` are
facts under §1, and the two-sentence cap governs the prose around them: cut the account, keep the
number.

## 3. The first paragraph is the summary

Rustdoc lifts the opening of a doc comment into the item table on the parent module's page and into
the search index, where it appears with **no surrounding context**. Write it to stand alone there.

The boundary is a **blank `///` line, not a period**, and here Javadoc habits mislead. Measured on
rustc 1.92, a comment opening `/// Returns a thing, e.g. a widget. Second sentence stays on the same
line.` puts *both* sentences in the item table, and the paragraph after the blank line in neither.
So `e.g.` costs nothing here, and a second sentence you meant as detail costs the whole table row.

- **One sentence, then a blank `///` line.** If the summary takes two sentences, the first one is
  not the summary.
- **Third person, subject omitted.** `Returns the backing map.` Not `Return…`, not `This function
  returns…`. Unlike Go, the item's own name does **not** lead: rustdoc prints the name beside the
  summary already, so `parse parses the input` is a stutter.
- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it, and the summary must be readable by
  someone who never reads paragraph two. The repair is rarely to define the term earlier: the field
  almost always has a word already, and `english-developer-style` §4a gives the test for telling a
  defined term from a coinage.
- **No self-description.** Drop `Helper type that…`, `Utility for…`. Start with the verb.
- **A `const` or `static` names itself first, with its unit.** `Largest encrypted packet that this
  stream accepts, in bytes.` The reason the bound has that value is slot 3, however interesting it
  is; a comment that opens with the upstream implementation it mirrors leaves the item table saying
  nothing about the constant.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  fills the item table with a word that states nothing about what the item does. Put the qualifier
  after the summary: `Rejects a message over its limit and breaks the connection. This is the
  default.`
- **A first sentence a reader could reconstruct from the identifier carries nothing.** A test named
  `failing_output_close_still_closes_input_and_socket` does not need `Checks that a failing output
  close still closes the input and the socket.`; `cargo test` prints the name. Where the name
  states what the test establishes, the comment carries the reason, the construction the reader
  would not guess, or nothing. For a field or an accessor the same rule leads to §7: where the name
  and the types are the whole contract, write no comment.
- **A field of a `pub` struct gets the same treatment as a function.** It is a public item with a
  contract, not a label.

## 4. Genre notes

### What the signature already says

Rust encodes in types what Java and Go leave to prose. Before you write slot 2, cross off everything
the reader can see:

| The signature already says | So do not write |
| --- | --- |
| `Option<T>` | "returns `None` if absent", unless what `None` *means* here is non-obvious |
| `Result<T, E>` | "may fail"; say which `E` values arise and what a caller does about each |
| `&mut self`, `self` by value | "mutates the receiver", "consumes the value" |
| `&'a T` tied to a parameter | "the result borrows from `input`" |
| `T: Send + Sync` | "safe to share between threads" |
| `impl Iterator<Item = …>` | "returns an iterator" |

What is left is the work:

- **Panics**, with the exact condition, and whether the caller can test for it first.
- **What each error means**, beyond its type: which are the caller's fault, which are transient,
  which a retry can fix. `Result<_, io::Error>` names a type, not a taxonomy.
- **Units, ranges, encodings, time bases**: `milliseconds since the epoch`, `UTF-8 bytes`,
  `0-based`, `inclusive of both endpoints`.
- **Complexity and allocation**, where a caller would guess wrong. std documents `O(n)` for a
  reason: nothing in the signature distinguishes a lookup from a scan.
- **Laziness.** An iterator, a builder, or a future that does nothing until it is consumed or
  awaited needs one sentence saying so, because the type does not.
- **Cancellation safety** for an `async fn`: what state is lost if the future is dropped mid-poll.
  This has no encoding in the type system at all, and getting it wrong corrupts data at run time.
- **Blocking.** A synchronous call inside an async context is a defect the compiler will not catch.
- **What `Drop` does**, and whether the value must be explicitly closed, flushed, or awaited first.
- **Invariants a `pub` field must keep**, since anyone can write it.
- **Platform differences** behind a `#[cfg]`.

Name a parameter in prose, spelled exactly as in the signature, at the point where its contract
matters: `body is serialized as JSON when non-empty`. Do not walk the parameter list in order
restating types; that is the signature, transcribed. Rust has no `@param`, and it does not need one.

Every item on that list is a property of the value. Where the caller got the value is the caller's
sentence: `the caller computes this from the message header` describes one call path and ages the
day a second one appears (§1).

A function whose contract is exhausted by its name and types needs one line or nothing.

### The membership rule, not the membership list

A comment that lists the members of a set (every variant a `match` must handle, every function that
writes a field, every caller that must be updated) has transcribed a query. The list looks
authoritative, it is stale from the first refactor, and a reader who does not find their case in it
concludes the wrong thing.

State the criterion instead: *every other check rejects a value that no conforming peer can send*
beats an eight-item list of those checks, because the reader can classify a check the list has never
heard of. The criterion has to let the reader name a member: "the limits whose error message offers
this as a remedy" is true by construction and states nothing the reader could not have inferred.
Where the honest criterion is circular, the list was the answer.

Two exceptions. A set the code itself declares (an exhaustive `match` the compiler keeps honest, a
test that partitions a set of constants) fails the build when it drifts, so there the list **is**
the contract. And a list the reader needs as vocabulary (the environment variables a binary reads,
the Cargo features that change behavior) stays, because the criterion alone lets nobody write code.
What goes in that case is the rot: the version label that freezes the list, and the per-item
annotations nobody maintained.

**One question decides it: can this set gain a member without anything forcing someone to edit this
comment?** If it can, write the criterion; no build, test, or review will report the stale list. If
it cannot, because the compiler or a test fails the moment the set changes, the list is the contract
and belongs here. The question is not about size (a three-item list nobody maintains rots faster
than a twenty-item one the build keeps honest) and not about origin in a standard (standards grow:
PostgreSQL adds message types, TLS adds versions). A *closed* set is safe, and an exhaustive `match`
with no wildcard arm detects exactly that.

`#[non_exhaustive]` cuts the other way. It tells a downstream reader that the list they can see is
not the list that will exist, so a comment enumerating the variants of a `#[non_exhaustive]` enum
contradicts the attribute. State the criterion; that is the attribute's purpose.

**A trailing `...` admits that the list is incomplete, and where it belongs depends on what precedes
it.** After a
stated criterion it is fine, because the items are illustration: *every wire-compatible backend
shares it (CockroachDB, YugabyteDB, Redshift, ...)* loses nothing if the reader has never heard of
the fourth. Where the list is itself the claim, *returned by the higher layers (auth, cancel-key,
startup negotiation, ...)* reports that more members exist and gives no way to name one, so it is
neither a list nor a rule. Supply the criterion, or finish the list and accept the maintenance.

The exception is wider for a comment that ships to docs.rs (§6a), because that reader cannot open
the code to enumerate the set themselves.

### Type (struct, enum, type alias)

The type comment carries the **invariant that spans the fields and methods**. Member comments
specialize it and do not carry it; a rule stated only on a private field is a rule the type comment
is missing.

Name the collaborators the type is useless without, and the lifecycle if the value is not
free-standing. A meaningful `Default` is itself a contract worth one clause when it holds. Where the
type upholds an invariant its fields could violate (a sorted vector, a validated string, a handle
that must outlive its parent), state the invariant, because it is the reason the fields are private
and the reason the constructor exists.

Do not explain how a collaborator works internally. Link to it (§5) and let its own comment do that
job.

### Trait

A trait comment has two audiences at once, and it is the genre most often written for only one.

- **Implementers**, including implementers in crates you will never see, need the **laws**: what an
  implementation must guarantee beyond the signatures. `Ord` must be a total order consistent with
  `PartialOrd`; `Hash` must agree with `Eq`; a `Read` that returns `Ok(0)` promises end of input.
  The compiler checks none of these, so if the trait comment does not state them, nothing does.
- **Callers**, who hold only the bound `T: Trait`, need to know what that bound buys them. Anything
  a caller may rely on has to be a law, or it is not there.

A provided method's comment states what an implementation that replaces it must preserve, the Rust
equivalent of Javadoc's `@implSpec`. A required method's comment is the obligation itself.

An `unsafe trait` gets a `# Safety` section, and it points the opposite way from an `unsafe fn`
(§6): it states what an **implementer** guarantees, because the implementer writes `unsafe impl`.

### Trait method implementation

The trait's comment is one link away from yours, so your comment is read as the delta. Write the
delta and nothing else. What rustdoc puts on the implementing type's page depends on whether the
impl method has a doc comment of its own: with none, it shows the trait method's summary and a link
to the rest; with one, it shows yours and nothing of the trait's (measured on rustc 1.92.0; §6 has
the consequence).

Three cases, and the trait's contract decides which one you are in. Read it before you write.

1. **The impl obeys the trait's contract.** Write no comment. Rustdoc then shows the trait's
   documentation on the impl, and a one-line restatement of it would replace that with less.
2. **The trait's contract leaves the behavior open, and this type picks one.** State the resulting
   contract as a rule of this type, in one positive sentence: `A count of zero skips nothing and
   returns Ok(0).` The trait's freedom is not news, and a sentence spent on it is provenance (§6).
   The same holds where the impl narrows what the caller gets: `Returns an empty slice rather than
   an error.` A different result from the trait's *provided* body is this case too, not the next
   one: `Iterator::size_hint`'s provided body returns `(0, None)`, so an impl that knows its length
   writes `Returns the exact remaining length as both bounds` and does not name the provided body.
3. **The impl breaks the trait's contract.** A caller holding only `T: Trait` is about to be wrong,
   so the deviation is the reason this comment exists. Name it in the trait's own terms, with the
   condition it happens under. Check first whether the contract really forbids the behavior: a
   contract that says *may* permits it, and case 2 applies. A deviation is also a defect report, so
   raise it rather than only documenting it.

The mechanism that forced the choice is rationale and earns its slot under §2. `The cursor indexes
the buffer [`Self::buffer`] returns` explains why a seek past the end returns `Err` instead of
growing the buffer, and it stays only where a maintainer would otherwise relax the rule; a rule that
matches what the trait's provided body itself does looks arbitrary to nobody.

### Field, constant, and static

Document the unit, the range, the sentinel, and who may write it. A private `static` whose invariant
is non-obvious needs that invariant spelled out; a reader adding a write has no other source of
truth. When the type comment already states the rule, the field comment shrinks to one sentence plus
a link.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence, positively, and
before any neighboring limit comes up: `This limit bounds only what the server sends.` A comment
that leaves the scope to be inferred from a contrast (`…which governs the direction this limit does
not`) makes the reader subtract one limit from another and reconstruct the missing verb. Both halves
are facts; state them separately, this one first.

A constant whose value is a size or a duration states both forms: `1 MiB (1048576 bytes)`. Rust has
no `{@value}`: nothing in a doc comment interpolates a constant's value, so you type the digits by
hand, ungrouped, and they go stale the day someone changes the initializer. Two habits limit the
damage: put the pair on the constant itself, where the initializer is one line below and a reviewer
sees both, and link to the constant from anywhere else that needs the number rather than copying the
digits a second time. The unit has to be exact (`64000000` is `64 MB`, not `64 MiB`) or hedged in
words: `about 1 GiB (1073741823 bytes)`. The form is `english-developer-style` §5.

A run of constants with a shared rule takes one comment on the enclosing module or block and short
ones on each, not the same sentence eight times.

### `unsafe fn` and `# Safety`

An `unsafe fn` moves an obligation from the compiler to the caller, and the `# Safety` section
writes that obligation down. It is the one doc section in Rust that a program's soundness depends
on: without it the caller has no way to know what makes a call sound, and `unsafe` then marks an
obligation nobody can check.

- **Write conditions the caller can check**, in the caller's vocabulary: `ptr must be non-null,
  aligned for T, and valid for reads of len * size_of::<T>() bytes`. Not "the caller must use this
  correctly".
- **State every condition.** A `# Safety` section that lists three of four requirements is more
  dangerous than none, because it looks complete.
- **Do not explain the implementation there.** Why the function is sound given those conditions is
  rationale; the conditions themselves are the contract.

`clippy::missing_safety_doc` warns by default (verified on clippy 0.1.92) for a public `unsafe fn`
with no `# Safety` section, so this one rule has a tool behind it. Nothing checks that the section
is *correct*, or that it is complete.

### `// SAFETY:` comments

The inverse of the section above, and a genre with no equivalent in Java or Go. An `unsafe` block
consumes someone else's `# Safety` contract, and the `// SAFETY:` comment above it is the argument
that this call site satisfies it.

```rust
    // SAFETY: `idx < self.len` was checked above, and `self.ptr` is valid for
    // `self.len` initialized elements for as long as `&self` is held.
    unsafe { &*self.ptr.add(idx) }
```

It covers the callee's conditions one by one, in the caller's own terms. "This is fine because the
index is in range" is not an argument if the callee also required alignment and initialization.
`clippy::undocumented_unsafe_blocks` finds the missing ones, but it is a restriction lint and off by
default (verified), so in most crates only review asks for these.

### Inline comment

An inline comment states why this line, for a reader who can already see the line. Four failure
modes beyond narration:

- **Meta-commentary.** `…so check the length first instead` describes what the comment is doing.
  State the fact: `The header is eight bytes, so a shorter frame has no length field to read.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` mark it.
- **Counterfactual.** See §1. `if … were`, `would`, `otherwise the` mark it. Name the source of the
  constraint; do not simulate the branch the guard prevents.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is narrowed to `u32` belongs at the conversion; repeating it inside the branch that
  rejects an oversized value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`// SAFETY:` (read by `clippy::undocumented_unsafe_blocks`); `// TODO` and `// FIXME` markers;
`#[rustfmt::skip]` and `// rustfmt::skip`; `// @generated` and `// Code generated … DO NOT EDIT.`;
anything citing an issue or a URL. `#[allow]`, `#[expect]`, `#[deprecated]`, and `#[doc(hidden)]`
are attributes rather than comments: do not fold one into prose, and do not delete one because it
looks like a note.

Three Rust-specific hazards, all of them compile errors or silent behavior changes:

- **A doc comment must be followed by an item.** `///` is sugar for `#[doc = "…"]`, so a doc comment
  with nothing after it is `error: expected item after doc comment`, a hard build failure rather
  than a lint. Here Rust is kinder than Go or Java: a comment orphaned by a deleted item cannot
  survive into the repository. It also means a "comment-only" edit can fail the build, so compile
  before you claim the sweep was harmless.
- **`//!` may only appear before items.** Moving an inner doc comment below the first item in a file
  is `error[E0753]: expected outer doc comment`, plus the error above. A module comment stays at the
  top.
- **A doc comment is part of the item's attributes**, so it interacts with `#[cfg]` and
  `#[cfg_attr(docsrs, doc(cfg(…)))]`. Reordering attributes around a doc comment is safe; splitting
  a `#[doc]` group is not.

### Test module

A test is read in exactly one situation: it just went red. Write for that reader.

Rustdoc does not render `#[cfg(test)]` code at all, so no tooling reads these and the firing
condition wins over every other consideration:

```rust
    /// A header the caller set by hand survives the retry unchanged.
    #[test]
    fn retry_preserves_caller_headers() { … }
```

- **Summary = the rule the test guards**, lifted out of the body rather than invented. The rule is
  already in the assertions and nowhere else; the comment states it once, above them, so a reader
  meeting a red build does not have to reconstruct it from four `assert_eq!` calls and a fixture.
  State it positively and completely, as something you could assert. `It has to stay quiet when the
  socket did go away` leaves the reader guessing: not panic, not close twice, not log? Name the
  observable. If you cannot phrase the rule as an observation, the test probably cannot check it
  either.
- **Use = what to do about the red build.** Which set to edit, which case to add, where the failure
  message states the rest.

Deliberate duplication between the test's comment, a helper's comment, and the failure message is
correct, because each reader meets exactly one of the three. It does not extend to production code,
where the type comment and the method comment have the same reader.

**A failing test should read as a bug report, and four things write it.** Decide what each one
carries before you write the next; the reader sees them together in one report.

- **The module path** carries what every test in it shares: the unit under test and the condition
  they all sit under. `cargo test` prints it in front of the test's name, so a fact true of every
  test belongs here rather than in each of them.
- **The test's name** states what this one test establishes. `negative_count_is_refused` is a
  finding; `test_ensure_bytes` is a location that makes the reader open the file. A table-driven
  case's label is the same thing: it names the case's condition, not its ordinal. One assertion per
  test keeps the name able to do this, and keeps the report readable when several tests fail at
  once.
- **The assertion prints the values.** `assert_eq!(left, right)` prints both values as `left` and
  `right`; `assert!(left == right)` prints the expression text and neither value, and leaves a
  stack trace to reverse-engineer. `#[should_panic(expected = "…")]` names the panic message the
  same way. Choose the assertion that already prints what the reader needs, rather than describing
  it in the message (output measured on rustc 1.92.0).
- **The message adds what the other three cannot.** In a loop over cases that is which case ran, so
  `ensure_bytes(-2147483648)` is the whole message. Under a bare `assert!` it is the invariant,
  because nothing else states it, and a message on `assert!` replaces the expression text rather
  than adding to it. Where the values are arguments already, do not restate them; where the module
  or the test's name states the scenario, do not restate that either. A message read while someone
  scans a stack trace competes with the lines around it.

`panic!()` with no message shows the same defect in full: it prints `explicit panic`, which reports
that something failed and nothing else.

This does not contradict the duplication paragraph above. A name is printed in the report; a
module's comment is read only once someone opens the file. Repeating a comment in a message is the
useful duplication; repeating a name is the one that costs.

### Module and crate comment

`//!` at the top of the file, before any item. One per module; a `mod.rs` or the module's principal
file carries it.

The crate comment in `lib.rs` is the entry point and the docs.rs landing page: what the crate is
for, which types are the way in, the Cargo features and what each turns on, the minimum supported
Rust version if the crate promises one, and any rule that holds across the crate (error conventions,
panics policy, async runtime assumptions). The item list is generated; a hand-written copy is the
membership list all over again.

`#![doc = include_str!("../README.md")]` makes the README the crate documentation, which is a good
default with one hazard: **every fenced block in that README becomes a doc test**. Measured on
rustc 1.92, an untagged block containing `cargo add mycrate` fails `cargo test --doc`, and the
failure is reported against `src/lib.rs` at the line of the attribute, with no mention of the
README. Tag the README's non-Rust blocks (§6) before wiring this up.

A binary crate's module comment is user documentation: what the binary does, its flags, its
environment variables, its exit codes. There the vocabulary exception of §4 applies in full.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` are
invisible in rendered documentation, silently wrong after a reorder, and unchecked by any tool. Name
the item instead.

Rust has **intra-doc links**, which render as hyperlinks on docs.rs and in editors:

| Form | Refers to |
| --- | --- |
| `[Classifier]` | an item in scope, resolved by Rust's own name resolution |
| ``[`Vec`]`` | the same, rendered as code, and the usual form for a type |
| `[Client::send]` | an associated function, method, or field |
| `[crate::codec::Frame]` | an item by path from the crate root |
| `[std::io::Read]` | an item in another crate, imported or not |
| `[the sender](Client::send)` | the same target under different link text |
| `[struct@Frame]`, `[fn@frame]`, `[macro@frame]`, `[prim@u8]` | a name that is several things at once |

The disambiguators matter more in Rust than the table suggests: a struct and a function may share a
name in the same module, and `[frame]` then resolves to whichever the resolver reaches first.

**Unlike Go, a broken link is caught.** `rustdoc::broken_intra_doc_links` is warn-by-default
(verified on rustc 1.92): `cargo doc` reports `unresolved link to 'NoSuchItem'` and points at the
column. Two limits on that guarantee. It is a warning, so it fails nothing unless the crate denies
it or CI runs with `RUSTDOCFLAGS="-D warnings"`; and it only fires where `cargo doc` runs at all.
The unresolved link still renders as the literal text `[NoSuchItem]`, exactly as in Go, so the
reader's experience of a broken link is the same, and only your build tells you.

Two more lints worth knowing, both warn-by-default:

- **`rustdoc::invalid_html_tags`.** Rust doc comments are Markdown, so raw HTML passes through. `///
  Takes a Vec<T>` emits a literal `<T>` into the page, which the browser parses as an unknown tag
  and drops: the reader sees "Takes a Vec". Backtick every type that carries angle brackets.
- **`rustdoc::bare_urls`.** A bare URL is not auto-linked; wrap it in `<…>` or make it a Markdown
  link.

`clippy::doc_markdown` wants backticks around every identifier-shaped word, but it is a pedantic
lint and off by default (verified). Backtick identifiers anyway: it costs two characters, and the
backticks distinguish a type name from an English noun.

Repeated links go in reference definitions at the end of the comment, which keeps the prose
readable:

```rust
/// Wraps [`Frame`] for transport and passes it to [`Sink::send`].
///
/// [`Frame`]: crate::codec::Frame
/// [`Sink::send`]: futures::Sink::send
```

`rustdoc::private_intra_doc_links` warns when a public item's docs link to a private one: the link
resolves for you and points nowhere on docs.rs (§6a).

**An issue or PR number is an address, not a definition.** Name the phenomenon in the comment, then
give the number so a reader can find the history: `a length taken straight from the wire sizes the
allocation (issue #4015)`, `the desync class of bug that issue #4015 reported`. The number must not
carry the meaning: `the shape of issue #4015`, `the same format as #1231`, `the bug #4015 fixed`
count as content for someone who already knows the ticket and as nothing for everyone else. The
test: cover the number and read the sentence. If what remains states no fact, the comment has none.
A bare `see #4015` fails the same test from the other end, and a docs.rs page reaches readers with
no access to the tracker at all.

The number may open the sentence, as long as the phenomenon arrives in the same one. `The scenario
from issue #4015: a field claiming more bytes than the row envelope still holds` passes, because
covering the number leaves the failure named. The rule is about the number's role, not its position.

The same holds for a commit hash, a mailing-list thread, or a released version. It does **not** hold
for a normative source (an RFC, a protocol specification, a vendor's published documentation), which
may define a format the comment then need not restate.

**A ticket number is not a name.** `a #4015 hardening check` names nothing, and the check has a name
in the code. Use that name, and cite the number once, where the history belongs.

## 6. Sections and examples, where Javadoc has tags

Rust has no `@param`, `@return`, `@throws`, `@since`, or `@see`. §4 covers what replaces the first
two. The rest is conventional Markdown headings, written as `#` and rendered by rustdoc as
subheadings of the item:

| Heading | Carries | Lint behind it |
| --- | --- | --- |
| `# Errors` | what each error value means, and what the caller does about it | `missing_errors_doc`, pedantic, off |
| `# Panics` | the exact condition, and how the caller avoids it | `missing_panics_doc`, pedantic, off |
| `# Safety` | the caller's obligations (§4), or a trait implementer's | `missing_safety_doc`, **warn by default** |
| `# Examples` | working code the build compiles and runs | none, and it is still worth writing |

The lint names are clippy's, and the three levels were verified on clippy 0.1.92. Only `# Safety`
has a lint on by default; the other two fire under `-W clippy::pedantic`, and nothing at all asks
for an example.

std's order is `# Errors`, `# Panics`, `# Safety`, then `# Examples` last, and matching it lets a
reader who knows std skim yours. A heading with one sentence under it is fine; a heading with
nothing under it is a template being filled in.

`# Deprecated` is not one of these. Deprecation in Rust is `#[deprecated(since = "…", note = "…")]`,
an attribute rather than a section: the compiler warns at every call site and prints the `note`
there. Name the replacement in the `note`, not in a paragraph a caller has to go looking for.

**A doc comment on a trait method implementation replaces the trait's; it does not add to it.**
Rustdoc shows the trait method's documentation on the implementing type's page only where the impl
method has no doc comment of its own. Write one sentence there about a special case, and the page
now says only that (measured on rustc 1.92.0). A fact about the ordinary case that the trait
already carries is lost to this impl's reader the moment you document the special case. Either
leave the impl method undocumented and let the trait's text show, or write the complete contract of
this impl, ordinary case included, and judge it by the complete text the reader ends up with. Which
case an impl is in, and what its body may say, is §4's *Trait method implementation* genre. What
the trait permits is not a fact of this impl's contract and pays for nothing under §7a: `the trait
permits an error here, but this implementation never returns one` spends a sentence on the
provenance of a guarantee the caller already has.

Other markup: paragraphs are separated by a blank `///` line, `**bold**` and `` `code` `` work,
tables and lists work, `#` headings are demoted by rustdoc so `#` is the right level to write.

### Examples are tests, and accidental examples are too

This section has no counterpart in the sibling skills. Every fenced block in a doc comment is
compiled and run by `cargo test`. That makes an example the most durable thing in a comment, and it
turns several ordinary formatting habits into build failures.

**A fenced block with no language tag is Rust.** Measured on rustc 1.92, a block containing `cargo
build --release` fails with `expected one of '!' or '::', found 'build'`. Tag every non-Rust block:
`text`, `console`, `sh`, `toml`, `json`.

**A four-space-indented block is also an untagged code block**, because the comment is Markdown.
This is the hazard for anyone carrying the Go convention across: in a Go doc comment an indented
block is how you show a command, and in Rust it is how you get `this is not rust` handed to the
compiler. Verified: the failure is identical to the untagged-fence one. Use a tagged fence, always.

**`?` does not work in a bare example.** The block is wrapped in a `fn main()` returning `()`, so
`let n: u32 = "42".parse()?;` fails to compile. Wrap it with hidden lines:

```rust
/// ```
/// # fn main() -> Result<(), std::num::ParseIntError> {
/// let n: u32 = "42".parse()?;
/// assert_eq!(n, 42);
/// # Ok(())
/// # }
/// ```
```

**Hidden lines (a `#` and a space) are for setup the reader does not need to see**, and for nothing
else. Imports the reader must write stay visible; the `main` wrapper, an unrelated fixture, and a
`use` of a private test helper go behind `#`. A reader copies the visible lines, so hiding a line
they need turns your example into a bug report.

**Assert it rather than claim it.** `assert_eq!(buf.len(), 4)` inside the example is a claim the
build checks; the same statement in the paragraph above it is a claim that rots. Where a fact fits
in an example, put it there.

**Pick the right attribute, and never `ignore`.**

| Attribute | Compiles | Runs | Use for |
| --- | --- | --- | --- |
| *(none)* | yes | yes | the default; anything that can run offline in milliseconds |
| `no_run` | yes | no | examples that open sockets, files, or take real time |
| `should_panic` | yes | yes | demonstrating the panic `# Panics` describes |
| `compile_fail` | must fail | no | showing that the type system rejects a misuse |
| `text` | no | no | not Rust at all |

`ignore` compiles nothing and runs nothing while still looking like a checked example, so it rots
silently and the reader keeps trusting it. Use `no_run` or `text` instead; if neither fits, the
example is prose and should be written as prose.

**Two facts about which doctests actually run**, both verified and both the opposite of what people
assume:

- **A doctest on a private item does run.** `cargo test --doc` collects it and executes it. A
  private helper's example is a real test.
- **A doctest in a binary-only crate does not run at all.** In a crate with only `src/main.rs`,
  `cargo test` reports no doc-test section and a deliberately failing example passes unnoticed. If
  the crate's examples matter, the code has to live in a library target.

Each doctest compiles and links its own binary, so they are the slowest tests in the crate. That is
a second reason to write one example per concern rather than a variant per parameter: twenty
near-identical examples cost real wall-clock time on every CI run, and the reader skims them all
looking for the difference.

## 6a. When the comment ships as documentation

A doc comment on a published crate's public item is not just a comment. It is the docs.rs page, and
often a second surface: a README assembled from the crate docs, a `--help` string, a generated
client.

**The reader changes, and that is the whole section.** They are working against your API from the
outside, on a page in a browser, with no repository checked out and no `git log`. Four rules follow.

1. **Links they can follow are a strength here, unlike in Go.** Rustdoc renders an intra-doc link as
   a real hyperlink on docs.rs, so ``[`Frame`]`` costs the reader nothing and saves them a search.
   Prefer a link to a spelled-out reference. This is the opposite of the advice `godoc-authoring`
   gives, and for the opposite reason.
2. **A link this reader cannot follow has to be spelled out.** A link to a private item or a
   `#[doc(hidden)]` one resolves in your editor and points nowhere on the published page;
   `rustdoc::private_intra_doc_links` catches the first case. Name the rule instead of linking to
   the thing that states it.
3. **Say which Cargo feature an item needs.** docs.rs builds with the feature set the crate's
   metadata names, so a reader sees items their own build does not have.
   `#[cfg_attr(docsrs, doc(cfg(feature = "tls")))]` puts the badge on the page; without it the
   reader hits a missing symbol and blames the version.
4. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a
   parameter accepts, the keys a map may hold, the errors a call can produce: that list is the only
   source this reader has, so a criterion may replace it only when they can apply the criterion
   *without opening anything*. §4's own warning applies at full force: if the honest criterion is
   circular, the list was the answer, and the repair is to complete it and verify every member
   against the code in the same edit. An incomplete list shipped as documentation is worse than no
   list.

The example carries more weight on this surface than anywhere else: it is the first thing a reader
scrolls to and the thing they paste. Make it complete enough to compile in their crate (visible
imports, no hidden line they need) and keep it to the one call the item is for.

Because a published comment reaches people who cannot see a correction until the next release, the
bar rises, but it rises for **rewording**, not for **enriching**. A synonym or a smoother clause is
churn that ships. A fact the page does not carry and its reader needs is worth the release every
time, even when every sentence already there is true. "It is correct as written" settles the first
case and not the second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- an item whose name and types are the whole contract;
- a trait method implementation that adds nothing to the trait's documented contract (§4);
- a private helper whose single call site makes it obvious;
- anything the code states better, which is most narration.

Nothing forces the issue: `missing_docs` is allow-by-default (verified), so an undocumented `pub`
item builds clean. The corollary is the same as in the sibling languages, and here it has no lint
behind it: a public item with a non-obvious contract is not optional, however self-evident the name
looks to the person who just wrote it. A crate that publishes to crates.io should turn
`#![warn(missing_docs)]` on and then write comments worth the warning, not comments that restate the
name.

## 7a. Editing an existing comment

Most of the time you are rewriting a comment, not writing one. Different job, different failure
mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none takes one
away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry: a unit, a panic condition, a cancellation rule, an invariant. Name that
  fact to yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **A near-empty before-version makes the budget vacuous, not permissive.** A one-line stub, no
  comment at all, or an impl method that showed the trait's text carries no facts, so everything in
  front of you is growth and none of it has been paid. Judge it as a comment written from scratch:
  every sentence earns its slot under §2, and on a trait method implementation under §4's three
  cases. Where the branch under review wrote the paragraph an hour ago, its text carries no more
  authority than your own first draft.
- **A test is evidence, not a paying fact.** A test that pins the behavior establishes that it is
  intentional and stable enough to rely on; it does not make the behavior part of the contract,
  because a test pins implementation behavior just as readily. Name the fact a caller relies on and
  cite the test as support for it. `A test asserts it` pays for nothing on its own.
- **Decompression is paid growth.** A comment can be too dense to read while being too *short* to
  fix under the rule above, and the budget then blocks the only repair there is. Unpacking one of
  the over-compressed shapes `english-developer-style` §4 tabulates adds words and no fact, and it
  is not churn; the payment is the re-read it removes. Name the construction you unpacked instead of
  naming a fact. That skill owns which construction is which and how to unpack it; this bullet only
  states that the budget does not block it. The exemption is that narrow: it does not license
  explaining more, hedging, or a second sentence of rationale, which still need a fact.
- **Check every identifier the old comment names.** A comment written before a refactor cites types,
  fields, and functions that no longer exist. A bare name in prose compiles, renders, and lies.
  Convert what you verify into an intra-doc link, because that is the one form `cargo doc` checks
  for the next reader (§5).
- **A doc-comment edit can break the build.** Adding or editing an example changes code the test
  suite runs, and a stray indent or an untagged fence turns prose into a failing test (§6). Run
  `cargo test --doc` on any comment edit that touches a fenced or indented block. This rule has no
  counterpart in Java or Go, and it is the one most often skipped.
- **When you lift a rule into the type or trait comment, cut it from the member.** The member keeps
  the one sentence that specializes the rule, plus the link. Two full statements of the same rule
  is the most common outcome of a good structural edit and the easiest to miss, because each of the
  two reads well on its own.
- **Deleting is an edit, and every cut is reported.** A list of callers, a rejected alternative, a
  benchmark number, a reference to the change that introduced the code: cutting these is usually
  the highest-value change in the diff, even though the result looks like less work. Delete
  sentence by sentence, and report each deleted sentence with the fact it carried and where that
  fact now lives: a section, another item, the commit message, or nowhere, with the reason. A
  rationale sentence stays only where a maintainer reading the rule would ask why or would be
  tempted to relax it; the test is whether the sentence would come up as a question in code review.
  A rewrite that reads better and says less is the failure this rule exists to prevent.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule
  governs the body, not the first paragraph. A comment whose summary runs to three sentences stays
  broken until someone rewrites it, and "I had no new fact to add" is not a reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot
  be verified as comment-only, and that verification makes a large sweep safe.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

The new version will read better. It was written second, by someone who had just finished
understanding the code, and a fact that vanished leaves no trace in the text that replaced it, so
reading forward confirms that impression and finds nothing. The work therefore runs backwards: read
the **old** version carefully first, and form the verdict last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one panic condition, one error meaning, one ordering or
cancellation constraint, one lifecycle obligation, one named collaborator, one link target, one
safety requirement, or one stated default. A topic sentence is not a fact, and neither is a
restatement of the signature. What the trait permits, and what another API does, is neither: it
names nothing a caller of this item relies on, so it takes a row as provenance and pays for no
growth in step 3 (§6). Compare facts, not sentences: at sentence granularity, merging two sentences
looks like a loss and splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Four
defenses hold:

- the fact was wrong, which includes a claim the old text made and the code does not support;
- the fact moved to the type, trait, or module comment, and you can point at the sentence that now
  carries it;
- the fact moved into the code: a stricter type, a named error variant, an `assert_eq!` in the
  example that now checks what a sentence used to claim;
- the fact was rationale, the contract it explained is stated completely without it, and the
  rationale no longer earns a slot under §2.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is the sentence someone writes when they cannot find the fact and would rather not look again.

A `# Safety` requirement is the one fact class where absence has no acceptable defense short of the
first. Dropping a condition from a `# Safety` section makes every call site that relied on the
comment unsound, and the edit looks exactly like tightening the prose.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first paragraph repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification. Where the old version carried no fact (a stub, no
comment at all, an impl method that showed the trait's text), the budget measures nothing: judge
every sentence of the new version on whether it earns its slot under §2, and on a trait method
implementation under §4's three cases (§7a).

Two more exemptions, both from §7a. A stacked relative, an elliptical nominal opener, or a noun pile
unpacked into a finite clause is paid growth: the payment is the re-read it removes, and the rewrite
names the construction rather than a fact. And growth is not the only failure: a rewrite that keeps
the old version's density while changing its words has bought nothing and belongs in step 5.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the tests, or to a contract it links to. **The old comment is
provenance, not evidence.** That it made the claim shows the claim was made, not that it holds, so a
claim carried over unchanged is checked like any other. A claim that traces to none of those sources
is invented, however plausible it sounds, and plausible is the dangerous case: a wrong invariant in
a doc comment is a wrong invariant a caller will build on, and an inherited one is worse, because it
has outlived every pass that did not check it. The commit message is not a source either. It records
what someone meant to do; the comment has to describe what the code does.

**An inference from the code is not the code.** A census of call sites establishes what is true
today, not why the code is the way it is. `No caller passes a negative value` supports `nothing
inside this crate reaches the guard`, and supports nothing about who the guard is for. Design intent
traces to a comment, to a specification, or to the shape of the API itself, never to a count of
callers. This is §4's membership rule from the other end: a report on today's callers is not a
law about tomorrow's.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer
attention now and costs the next reader a `git blame` later. §7a has already settled that the old
wording stays; here you look for the places where it did not.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Four
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is
  the characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Counterfactual.** The comment describes what would happen on a path this code rules out, rather
  than what it does. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something
  else. No build step catches this, so it is the most valuable thing a comparison pass finds.

A `// SAFETY:` comment is the exception within the exception: it is an argument about the code below
it, so a change to that code invalidates the argument even when the comment still parses as true.
Re-derive it rather than re-reading it.

**7. Prove the code did not move, and prove the tests still run.**

Rust needs both halves, because a doc comment holds executable code.

For the first half, start with the check that costs one command and no dependency: read the diff
and delete every line that is a comment.

```sh
git diff <base>..HEAD -- '*.rs' | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | grep -vE '^[+-]\s*//'
```

Whatever it prints is a non-comment line the pass changed, and on a comment-only sweep it prints
nothing. Run it before you read the diff yourself: it finishes in a second, and on a sweep spanning
hundreds of lines it is the only reading that is not subject to fatigue. Its limits are the limits
of text: it cannot tell a moved line from a rewritten one, it does not see a `/* */` block, and a
re-wrapped comment counts as a change on both sides.

The precise version parses instead of matching, so re-wrapping and reordering do not affect it.
`syn` discards `//` comments outright and turns `///` and `//!` into `#[doc]` attributes, so
removing those leaves only code:

```rust
struct StripDocs;
impl syn::visit_mut::VisitMut for StripDocs {
    fn visit_attributes_mut(&mut self, attrs: &mut Vec<syn::Attribute>) {
        attrs.retain(|a| !a.path().is_ident("doc")); // /// and //! are #[doc]
    }
}
// StripDocs.visit_file_mut(&mut syn::parse_file(&src)?), then prettyplease::unparse
```

Any difference means the pass touched code, and the pass is wrong until it is explained.

For the second half, run `cargo test --doc`. Neither check above can see inside a doc example (to
`grep` it is a comment and to `syn` it is a string), so a sweep that rewrote an example is
comment-only by both proofs and can still have broken the build.

The failure this step catches is a test that stopped running, and it is quieter than a test that
fails. It is not silent: a function in a `#[cfg(test)] mod tests` that loses its `#[test]` stops
being called, and `dead_code` warns by default (verified); clippy adds `duplicated attribute` when
the lost attribute landed on a neighbor. Do not rely on that. A warning in a build that already
prints warnings is a warning nobody reads, whereas the diff check names the file and the line.
Compare the test count across the sweep as well; it costs one number.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it makes two people comparing the same pair reach
the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Lost safety condition | Restore it; no other defense applies (§7b step 2) |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and make it an intra-doc link (§5) |
| Duplicated rule | Cut the copy the type or trait comment now carries (§7a) |
| Churn | Restore the old wording |
| Density kept | Unpack the stacked relative, the elliptical opener, or the noun pile (§7a) |
| Narration | Delete the comment |
| Signature restated in prose | Delete the restatement (§4) |
| History narration | Rewrite as the state that holds now |
| Counterfactual | Cut the simulation; re-evaluate any rationale left standing under §2 |
| Unearned rationale | Cut the rationale; keep the complete contract (§2) |
| Trait provenance | Cut it; keep the resulting contract (§6) |
| Stale inline comment | Rewrite it from the code |
| Stale `// SAFETY:` argument | Re-derive it against the callee's current contract |
| Untagged or indented block | Make it a tagged fence, before the build compiles it as Rust (§6) |
| `ignore`d example | Convert to `no_run` or `text`, or delete it (§6) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the first paragraph one sentence, followed by a blank `///` line?
- Does it stand alone, with no term this comment introduces, and does it avoid repeating the item's
  own name?
- Could a reader reconstruct the first sentence from the item's name alone?
- In a regression test's comment: the rule first, the old defect in one past-tense sentence, and any
  equivalence with the old behavior kept (§1)?
- Does any sentence restate what `Option`, `Result`, `&mut`, or a trait bound already says?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Does a function that can panic have a `# Panics` section naming the condition?
- Does every `unsafe fn` have a `# Safety` section, and is every condition in it checkable by the
  caller?
- Does every `unsafe` block have a `// SAFETY:` comment that covers the callee's conditions?
- Does a trait comment state the laws an implementer must guarantee, not only what the methods do?
- On a trait method implementation: which of §4's three cases is it in, and does any sentence
  describe the trait's freedom rather than this impl's rule?
- Does a limit state what it bounds, rather than only what some neighboring limit bounds?
- Is every fenced block tagged, and is there any four-space-indented block that will be compiled as
  Rust?
- Does the example assert what the prose claims, and does it compile without a hidden line the
  reader needs?
- Any `ignore` attribute that should be `no_run` or `text`?
- Any positional reference: `below`, `above`, `the following`?
- Any bare name that should be an intra-doc link, and does `cargo doc` report no unresolved link?
- Any type with angle brackets outside backticks?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Is any rationale here commit-message material?
- Any sentence describing a previous version of the code: `now`, `no longer`, `used to`?
- Any sentence describing a code path this code does not have: what would happen if the rule were
  broken, rather than what the code does about it?
- Does every term here have a definition outside this comment, and does every name match what the
  code calls the thing (`english-developer-style` §4a)?
- For each rationale sentence: would deleting just that sentence change what a caller may rely on,
  or leave a maintainer unable to see why a constraint is there? If not, delete it.
- Would deleting the whole comment lose anything?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- If this is a rewrite: did every measured number in the old version survive it (§1)?
- If this is a rewrite touching a fenced block: did `cargo test --doc` pass?
- If this is a sweep across files: does the diff check print nothing, and does the test count match
  (§7b step 7)?
- Does every name the old comment mentioned still exist?
- Does any statement here also appear in the type, trait, or module comment?
- Any list that a criterion would replace, or that the reader's editor already answers? Can the set
  gain a member without anything forcing an edit here, and does a trailing `...` stand where no
  criterion precedes it?
- If the comment ships to docs.rs (§6a): can its reader follow every link, and is a feature gate
  named?

## 9. Worked examples

The two examples pull in opposite directions on purpose. In the first the prose shrinks, because it
was restating the signature, while the comment grows an example. In the second everything grows,
because a fact was missing. Do not read either one as the target shape.

Both are constructed rather than lifted from a real crate, and deliberately so: an example a sweeper
can recognize in the wild is an example it will paste instead of derive, and a rewrite that matches
this file word for word proves nothing about whether the rules were applied.

### A comment that re-typed the signature

**Before**: four sentences, three of which the reader can see in the declaration. The one fact the
signature does not carry, the meaning of an empty result, sits in the last clause.

```rust
/// Parses a frame from the buffer.
///
/// This method takes a shared reference to the buffer and returns an `Option`
/// containing the parsed `Frame`, or `None`. It does not modify the buffer. The
/// caller owns the returned value, and `None` is returned when the buffer holds
/// fewer bytes than a complete frame.
pub fn parse(buf: &[u8]) -> Option<Frame> { … }
```

**After**: the summary keeps its one sentence, `None` gets the only sentence it needs, and the
claim about partial input is now checked by the build rather than asserted in prose.

```rust
/// Parses one frame from the start of `buf`.
///
/// `None` means the buffer is short, not malformed: a caller reading from a stream
/// should read more bytes and try the same buffer again. A frame that is complete
/// but invalid is reported through [`Frame::validate`].
///
/// # Examples
///
/// ```
/// use mycrate::parse;
///
/// assert!(parse(&[0x01]).is_none());
/// ```
pub fn parse(buf: &[u8]) -> Option<Frame> { … }
```

Fact ledger: *returns an `Option<Frame>`*, *takes a shared reference*, *does not modify the buffer*,
*the caller owns the result*: all four absent, all four defended by step 2's third defense, since
each is in the signature. *`None` when the buffer is short*: present, and now distinguished from
the malformed case, which is the fact the old comment did not carry.

The comment as a whole is seven lines longer, and every one of those lines is the example. That
trade is the right one: the prose lost four sentences that the declaration already made, and the
growth bought the one claim in the comment that `cargo test` will keep honest. Count prose against
§7a's budget and count an example separately, or the budget will rule out the example every time.

### An `unsafe fn` whose obligations were not written down

**Before**: a summary and a reason. The reason is real and the comment is still unusable, because
nothing here tells a caller what makes a call sound.

```rust
/// Returns the element at `idx` without a bounds check.
///
/// Skipping the check matters in the decode loop, where the index is already
/// known to be in range and the branch showed up in profiles.
pub unsafe fn get_unchecked(&self, idx: usize) -> &T { … }
```

**After**: the obligations, stated as conditions the caller can check, plus the counterpart the
prose had implied and never said.

```rust
/// Returns the element at `idx` without a bounds check.
///
/// # Safety
///
/// `idx` must be less than [`Self::len`]. Calling this with any other index is
/// undefined behavior, not a panic: the read is performed regardless, and a
/// debug build will not catch it.
///
/// The returned reference borrows `self`, so no `&mut self` method may be called
/// while it is alive, including [`Self::push`], which may reallocate and leave
/// the reference dangling.
///
/// # Examples
///
/// ```
/// use mycrate::Buf;
///
/// let buf = Buf::from(vec![7u8]);
/// // SAFETY: `buf` holds one element, so index 0 is in range.
/// assert_eq!(unsafe { *buf.get_unchecked(0) }, 7);
/// ```
pub unsafe fn get_unchecked(&self, idx: usize) -> &T { … }
```

The prose grew from four lines to eleven and paid for them with three facts the original did not
carry: the bound the caller must guarantee, the consequence of breaking it (undefined behavior, and
no debug-build safety net, which a reader assumes wrongly), and the aliasing rule the returned
lifetime enforces but does not explain. The performance rationale went to the commit message under
§2: a caller who knows the rule and not the reason can still write sound code. The example's
`// SAFETY:` line serves two purposes: it is the checked demonstration of the contract, and it shows
the caller the shape of the argument they must make at their own call site.
