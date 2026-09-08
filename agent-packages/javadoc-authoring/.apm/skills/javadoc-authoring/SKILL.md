---
name: javadoc-authoring
description: >-
  Load before writing, editing, or reviewing a doc comment or inline comment in Java, Kotlin,
  Groovy, or Scala: a Javadoc for a new or changed method or class, a @throws or @param for
  behavior that just changed, the comment on a test just added, a regression test that names the
  old defect, an override that departs from the inherited contract, an inline note beside a new
  check. Inside a coding task on a JVM codebase ("fix the bug", "add the method") load it as soon
  as the change touches a comment, before writing it. Also load to decide whether a member needs a
  comment at all, or to compare two versions of one. Governs what the comment says and in which
  order: the summary fragment, contract before rationale, tags and links, when to write nothing,
  how far a rewrite may grow. Wording is english-developer-style's; load both.
---

# Authoring a Javadoc comment

This skill governs **what a doc comment says and in what order**. Wording, tone, sentence length,
and dialect belong to `english-developer-style`: load it too, and defer to it on the prose. The two
compose: this skill picks the slots; that one writes the sentences.

Everything below is written for Javadoc and holds for the JVM's other doc-comment dialects, which
share its tag vocabulary and its summary-table rendering. KDoc differs in one place worth knowing
before you reach §5: it links with `[Foo]` and `[Foo.bar]` rather than `{@link}`, and it has no
`{@code}`; backticks do that job.

Do not carry these rules into a language outside that family. Python's own PEP 257 prescribes the
imperative `Return that` where this file prescribes `Returns that` (§3), and which mood wins there
is a project decision rather than a given. Rust, TypeScript, and JavaScript each have reference and
tag machinery that §5 and §6 do not describe, and Rust's doc comments compile and run as tests.
Those languages need their own rules, not a translation of these.

## 1. The correction that matters most

"Document the why, not the what" is half wrong for a doc comment, and the wrong half does the
damage.

An inline `//` comment documents the **why**; it sits next to code the reader can already see. A doc
comment documents the **contract**: what a caller may rely on, what an implementer must guarantee,
what holds before and after. That is a *what* at the level of a promise, not a restatement of the
code.

The failure mode is therefore not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Loops over the entries and adds each to the map.` The body
  already states it, and the comment becomes false on the next refactor.
- **Justifying the code's existence.** `This class was added because the old approach did not
  scale.` That belongs in the commit message and the PR description. A doc comment's reader has to
  *use* or *fix* the thing, not decide whether to merge it.

**The test is the refactor, not the reader.** Rewrite the body so it behaves identically and reads
differently: a loop becomes a stream, a helper is inlined, a field is renamed. Every sentence you
would then have to edit was implementation, whatever it sounded like. This is the operative rule,
because it settles cases that "specification, not details" argues about forever, and it does not
soften with visibility: a private method's comment goes stale on that refactor exactly as a public
one's does, and the cost of a comment that lies is the same either way.

**The caller substitutes too, and catches what the refactor cannot.** Imagine a new legitimate
caller supplying the same argument for a different reason. A sentence that then describes only the
old call path is caller context, not this member's contract. `A negative n is refused before any
byte is read` survives the substitution; `because a count taken from a length the backend declared
can be negative` does not.

Cutting is not the whole repair, because the rationale slot can be open and merely filled wrong.
Where a value came from does not explain why the member behaves as it does; a local reason, where
one exists, is a property of this member's own contract. Look for the local reason before concluding
that the slot was never open, then ask §2's question of it: does the rule look arbitrary without it,
or would a maintainer relax it incorrectly? A reason any reader would have assumed fails that
question and stays out, however true it is.

Provenance crosses into a callee's comment where it is that member's own contract: a protocol method
whose parameter *is* the declared length minus the header documents its own layer rather than
borrowing the one above it. **State the local rule at the lowest-level API, and the scenario at the
layer where the scenario exists.** A guard found through one concrete call path does not thereby own
that path's story.

**Sufficiency** scales with visibility: how much the comment may leave to the code beside it.

| Where | What the comment must carry |
| --- | --- |
| `public`, `protected` | Complete without the code. A subclasser is a caller, so `protected` is public API here (§6a) |
| package-private, `private` | May be elliptical and lean on the body beside it. Often there is no contract distinct from the implementation at all, and §7's "the name and types are the whole contract" usually applies |
| inline | Nothing about the contract. The reader has the code |

For an inline comment the bar is negative: **a competent reader is looking at this code and
understanding it correctly; write the comment only where they would not.** A reason that surprises,
a bound that looks arbitrary, an order that looks swappable, a branch that looks dead. Where their
expectation and the code agree, the comment is noise, and later stale noise.

A third failure, specific to a codebase that has been refactored, is **narrating the code's
history**. `The pool now hands back a wrapper, so unwrap() no longer returns the physical
connection` describes a transition between two versions, and the reader has only this one. Rewrite
it as the state that holds: what `unwrap()` returns, and why.

One exception. **The comment on a regression test may tell history, and an equivalence is not history.**
The defect is what the test guards, so it belongs in the comment: state the rule the test asserts
first, then the defect in one past-tense sentence with the exception class: `A negative count used to
be reported as available, and the caller then failed with StringIndexOutOfBoundsException.` A comment
that opens with the defect makes the reader reconstruct the broken version to understand the fixed
one (measured on one branch: a blind reader ranked the version that opened with `used to` fourth of
five on that ground alone). Do not narrate the old mechanism in the present tense, and do not recast
it as a chain of `would` clauses. History narration, which this section forbids, is a sentence whose
only content is that the code changed. A sentence that argues the new behavior is safe **because it
is identical to the old one** is rationale, and the old behavior is its comparison term. Keep the
comparison; it is the whole argument.

- *Keep:* `a reader that has not yet observed the write behaves exactly as every reader did before this
  field was added: it reads from the buffer and the wrapped stream as if nothing were closed`
- *Wrong repair:* `a reader on another thread may not observe the write and may still read from the
  buffer` (the equivalence, which is the reason the non-volatile field is safe, is gone)

A fourth is the third one turned sideways: **narrating the branch that does not exist**, what the
code would do on an input it refuses, or under a rule it does not implement. History narration gives
the reader a past version of the code; this gives them a version that never existed. `If uppercase
names were allowed, the label built from this name would be rejected downstream and the deployment
would never start` describes a path no build of this code can take. No refactor can make it false
and no reader can check it, so it survives every review.

This does not ban consequences. What the code does when the contract is broken (which exception,
which return value, what state the object is left in) is contract, and the `@throws` line (§6)
carries it. Cut the simulation of the branch the guard prevents.

**The test: could a reader falsify the sentence by reading this repository?**

- `Throws IllegalArgumentException when the name contains an uppercase letter`: contract. It names a
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
sees the `throw` and cannot see why the value is unacceptable. Where the constraint is only
*stated*, in a doc comment, ask the question again from scratch. Completeness does not settle it: a
contract states itself completely by definition, so `the tags already say what happens` closes
nothing. The test stays the same: would the rule look arbitrary, and is it easy to change
incorrectly?

A member with more than one failure channel, an exception beside a sentinel return, is not an
exception to that test. The tags state each outcome, and a maintainer reading them is expected to
keep them apart. A sentence explaining why an invalid argument throws rather than returning the
sentinel is the reason any reader would have assumed (measured: a maintainer who met such a sentence
in review called it common sense). Leave it out.

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
enforces it, and before what some *other* class does. A comment that opens with a neighboring class
forces the reader to reconstruct the rule from negative examples. State it positively, in one place,
first.

**When only one slot fits, keep the contract.** Rationale is the first slot to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

**Removing a bad explanation does not create an obligation to replace it.** A rationale slot emptied
by a cut stays empty until the finished contract, read on its own, turns out to need one. Start from
the contract, not from the gap.

**Make the obligated party the subject.** Obligations come in two shapes. A *stated* obligation
carries a *must*, *has to*, *may not*, or *should*, and whoever has to comply belongs in the
subject: not the thing acted on (`Every backend message must be read through readMessageLength`,
which names no one and lets `it` drift to the reader by the next clause), not the act (`relaxing a
protocol check must not be reachable`), and not a member that merely performs the act for someone
else (`markBroken must still fire` obliges `PGStream`). A named member in the subject is right only
where that member is itself what must comply: `readUntrackedLength must leave no envelope behind`.
The party need not be human, but it must act: a driver, a check, a reader. A mode constant or a
configured number complies with nothing.

A *census* is a rule for the next maintainer, written instead as a report on today's call sites:
`Every site that dispatches on a message type reads the tag through this method`, `CopyData is the
one such site`. It is flat indicative with no modal, so test it: **if a second such caller appeared
tomorrow, would this paragraph tell it that it is obliged?** Judge the paragraph, not the sentence;
an example may follow a law that is already correctly stated. Write the law, not the roll call.

Watch the intransitive modal, where the party hides best: `every constant has to appear in
HARDENED`, `an unknown value must fall back to FAIL`. Nothing appears or falls back on its own; name
what does it.

Out of reach of this rule: an imperative, which already addresses the party (`Call it where the
framed dialogue resumes`), including one that carries rationale (`so mirror that here`); a
constraint on a *value* (`must be ≤ MAX_MESSAGE_SIZE`), which bounds a number rather than behavior;
a field comment naming who writes or reads the field, which is the membership list §4 calls for; and
an inline comment whose next statement is the actor (`// Envelope must be fully consumed` above the
`endMessage()` that consumes it), after checking that the next line really is the actor and not test
setup standing between the comment and the call it constrains.

Most members need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots to
fill a template; an absent slot is not a gap.

**Size the comment to the member.** A doc comment longer than the member it documents is not
automatically wrong (an invariant can be worth ten lines over a one-line getter), but it is a signal
to re-read. When you check, the surplus is almost always rationale: keep at most two sentences of
it, and only for the part a reader would otherwise get wrong. The rest belongs in the commit
message. As a working size, a test-class comment is two to five sentences and a method comment fits
in one glance; past that you are describing the investigation, not the contract, so keep the rule
and the exception and move the rest.

## 3. The first sentence is a summary fragment

Javadoc extracts the first sentence into the class and member summary tables, where it appears with
**no surrounding context**. Write it to stand alone there.

- **Third person, subject omitted.** `Returns the backing map.` Not `Return…`, not `This method
  returns…`.
- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it, and the summary must be readable by
  someone who never reads paragraph two. The repair is rarely to define the term earlier: the field
  almost always has a word already, and `english-developer-style` §4a gives the test for telling a
  defined term from a coinage.
- **No self-description.** Drop `This class is responsible for…`, `Helper class that…`, `Utility
  for…`. Start with the verb.
- **Watch the terminating period.** The fragment ends at the first `.` followed by whitespace, so
  `e.g.`, `i.e.`, `vs.`, and `Dr.` truncate it. Rewrite, or pin the boundary with `{@summary …}`
  (JDK 10+).
- **One sentence.** If it takes two, the first one is not the summary.
- **A field or constant names itself first, with its unit.** `Largest declared length, in bytes,
  that this stream accepts for an encrypted packet.` The reason the bound has that value is slot 3,
  however interesting it is; a comment that opens with the upstream implementation it mirrors leaves
  the summary table saying nothing about the constant.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  fills the summary table with a word that states nothing about what the member does. Put the
  qualifier after the summary: `Rejects a message over its ceiling and breaks the connection. This
  is the default.`
- **A first sentence a reader could reconstruct from the identifier carries nothing.** A test method
  named `aFailingOutputCloseStillClosesTheInputAndTheSocket` does not need `Checks that a failing
  output close still closes the input stream and the socket.`; the report prints the name. Where the
  name states what the test establishes, the comment carries the reason, the construction the reader
  would not guess, or nothing. For a field or a getter the same rule leads to §7: where the name and
  the types are the whole contract, write no comment.

## 4. Genre notes

### Type (class, interface, enum, record)

The class comment carries the **invariant that spans the members**. Member comments specialize it
and do not carry it; a rule stated only on a private field is a rule the class comment is missing.

Name the collaborators the type is useless without, the threading model if there is one, and the
lifecycle if instances are not free-standing. Do not explain how a collaborator works internally;
link to it and let its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set (every check a mode governs, every method that writes a
field, every caller that must be updated) has transcribed a query. The list is stale from the first
refactor, and a reader who does not find their case in it concludes the wrong thing.

State the criterion instead: *every other check rejects a value that no conforming backend can send*
beats an eight-item list of those checks, because the reader can classify a check the list has never
heard of. The criterion has to let the reader name a member: "the ceilings whose error message
offers this as a remedy" is true by construction and states nothing the reader could not have
inferred. Where the honest criterion is circular, the list was the answer.

Two exceptions. A set the code itself declares (a test that partitions an enum into named sets, a
`switch` a reader must keep exhaustive) fails the build when it drifts, so there the list **is** the
contract. And a list the reader needs as vocabulary (the keys a map may hold, the tokens a property
accepts) stays, because the criterion alone ("whatever the server marks `GUC_REPORT`") lets nobody
write code. What goes in that case is the rot: the version label that freezes the list, and the
per-item annotations nobody maintained.

**One question decides it: can this set gain a member without anything forcing someone to edit this
comment?** If it can, write the criterion; no build, test, or review will report the stale list. If
it cannot, because the compiler or a test fails the moment the set changes, the list is the contract
and belongs here. The question is not about size (a three-item list nobody maintains rots faster
than a twenty-item one the build keeps honest) and not about origin in a standard (standards grow:
PostgreSQL adds message types, TLS adds versions). A *closed* set is safe, and the compiler check
detects exactly that.

**A trailing `...` is a confession, and where it belongs depends on what precedes it.** After a
stated criterion it is fine, because the items are illustration: *every wire-compatible backend
shares it (CockroachDB, YugabyteDB, Redshift, ...)* loses nothing if the reader has never heard of
the fourth. Where the list is itself the claim, *thrown by the higher layers (auth, cancel-key,
startup negotiation, ...)* reports that more members exist and gives no way to name one, so it is
neither a list nor a rule. Supply the criterion, or finish the list and accept the maintenance.

### Method

Slot 2 carries the work. State these, and only where the signature does not already:

- nullability of parameters and of the return, when not enforced by an annotation;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- ownership of a passed or returned mutable object: does the callee retain it, may the caller mutate
  it afterwards;
- side effects the name does not advertise, including I/O and state changes;
- idempotence, thread-safety, and ordering guarantees;
- whether the method may block, for how long, and what interrupting the thread or canceling the
  returned future does;
- error conditions, and which are checked versus programmer errors.

Every item on that list is a property of the value. Where the caller got the value is the caller's
sentence: `the caller computes this from the message header` describes one call path and ages the
day a second one appears (§1).

A method whose contract is exhausted by its name and types needs one line or nothing.

### Override

The reader has the inherited comment: an IDE shows it beside yours and a generated page inlines
it, so your comment is read as the delta. Write the delta and nothing else.

Three cases, and the inherited contract decides which one you are in. Read it before you write.

1. **The override obeys the inherited contract.** Write no comment. A bare `{@inheritDoc}` says the
   same thing and satisfies a checkstyle rule that demands one; it is not a slot to fill.
2. **The inherited contract leaves the behavior open, and this class picks one.** State the
   resulting contract as a rule of this class, in one positive sentence: `A count of zero or less
   skips nothing and returns {@code 0}.` The inherited freedom is not news, and a sentence spent on
   it is genealogy (§6). The same holds where the override narrows what the caller gets: `Returns
   an empty list rather than {@code null}.` A different result from the supertype's *own
   implementation* is this case too, not the next one: `InputStream.markSupported()` returns
   `false` and its contract says *if supported*, so an override returning `true` writes `Returns
   {@code true}; mark and reset are supported` and does not name the supertype.
3. **The override breaks the inherited contract.** A caller holding a supertype reference is about
   to be wrong, so the deviation is the reason this comment exists. Name it in the supertype's own
   terms, with the condition it happens under. Check first whether the contract really forbids the
   behavior: a contract that says *may* permits it, and case 2 applies. A deviation is also a defect
   report, so raise it rather than only documenting it.

The mechanism that forced the choice is rationale and earns its slot under §2. `The read position
indexes the buffer {@link #getBuffer()} returns` explains why a negative count cannot be honored,
and it stays only where a maintainer would otherwise relax the rule; a rule that matches what the
supertype itself does looks arbitrary to nobody.

### Field and constant

Document the unit, the range, the sentinel, and who may write it. A `private static final` set whose
membership rule is non-obvious needs that rule spelled out; a reader adding an entry has no other
source of truth. When the class comment already states the rule, the field comment shrinks to one
sentence plus a link.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence, positively, and
before any neighboring limit comes up: `This ceiling bounds only what the server sends.` A comment
that leaves the scope to be inferred from a contrast (`…which governs the direction this ceiling
does not`) makes the reader subtract one limit from another and reconstruct the missing verb. Both
halves are facts; state them separately, this one first.

A constant whose value is a size or a duration states both forms, and `{@value}` supplies the
digits: `1 MiB ({@value #MAX_CSTRING_LENGTH} bytes)`. The doclet renders the evaluated constant
without grouping (`1 << 20` and `8 + 8000` come out as `1048576` and `8008`), and the digits follow
the field when someone changes it. Only the unit can go stale, so it has to be exact (`64000000` is
`64 MB`, not `64 MiB`) or hedged in words: `about 1 GiB ({@value #MAX_MESSAGE_SIZE} bytes)`. The
form is `english-developer-style` §5.

### Inline comment

An inline comment states why this line, for a reader who can already see the line. Four failure
modes beyond narration:

- **Meta-commentary.** `…so say where the dialogue resumes instead` describes what the comment is
  doing. State the fact: `This is where the framed dialogue resumes.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` mark it.
- **Counterfactual.** See §1. `if … were`, `would`, `otherwise the` mark it. Name the source of the
  constraint; do not simulate the branch the guard prevents.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is cast to `short` belongs at the cast; repeating it inside the branch that rejects a
  negative value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone; rewording them changes behavior or destroys a record: `CHECKSTYLE:OFF` and its
siblings, `@formatter:off`, `//noinspection`, `$NON-NLS-`, `TODO` and `FIXME` markers, anything
citing an issue or a URL. The `@SuppressWarnings` annotation is not a comment at all; do not fold it
into one.

Two placement hazards when you restructure code around them:

- **`$NON-NLS-1$` counts string literals on its own line.** The suffix is an ordinal, so reflowing a
  line, splitting it, or reordering its literals silently retargets the suppression.
- **`@formatter:off` and `CHECKSTYLE:OFF` come in pairs.** Delete or move one half and the
  suppression runs to the end of the file, or ends where nobody intended.

### Test class

A test class is read in exactly one situation: it just went red. Write for that reader.

- **Summary = the firing condition**, not the subject matter. `Fails when a message type is added
  without a hardened reader` beats `Tests the message type inventory`. This is the class comment's
  shape. A test method's name already states what it establishes (below), so its comment, where it
  has one, carries the reason or the construction, not a `Fails when …` restatement of the name.
- **Contract = the rule the test guards**, stated positively and completely. The reader has to
  satisfy the rule, not reverse-engineer it from the assertion.
- **Use = what to do about the red build.** Which set to edit, which annotation to add, where the
  failure message states the rest.
- **State the rule as something you could assert.** `It has to stay quiet when the socket did go
  away the first time` leaves the reader guessing: not throw, not close twice, not log? Name the
  observable: `and it must not touch a socket that markBroken already closed.` If you cannot phrase
  the rule as an observation, the test probably cannot check it either.

Deliberate duplication between this class comment, a field comment, and the assertion message is
correct, because each reader meets exactly one of the three. It does not extend to production code,
where the class comment and the member comment have the same reader.

**A failing test should read as a bug report, and four things write it.** Decide what each one
carries before you write the next; the reader sees them together in one report.

- **The class name** carries what every method in it shares: the unit under test and the condition
  they all sit under. A fact true of every method belongs here rather than in each of them.
- **The method name** states what this one method establishes. `aNegativeCountIsRefused` is a
  finding; `testEnsureBytes` is a location that makes the reader open the file. One assertion per
  method keeps the name able to do this, and keeps the report readable when several methods fail at
  once.
- **The assertion prints the values.** `assertEquals(expected, actual, message)` renders both and
  opens a diff in an IDE; `assertTrue(expected == actual, message)` renders neither and leaves a
  stack trace to reverse-engineer. `assertThrows` prints the expected type the same way. Choose the
  assertion that already prints what the reader needs, rather than describing it in the message.
- **The message adds what the other three cannot.** In a parameterized test that is which invocation
  ran, so `ensureBytes(-2147483648)` is the whole message. Under a bare `assertTrue` it is the
  invariant, because nothing else states it. Where the values are arguments already, do not restate
  them; where the class or method name states the scenario, do not restate that either. A message
  read while someone scans a stack trace competes with the lines around it.

`fail()` with no message is that defect at its limit: it reports that something is wrong and nothing
else.

This does not contradict the duplication paragraph above. A name is printed in the report; a class
comment is read only once someone opens the file. Repeating a comment in a message is the useful
duplication; repeating a name is the one that costs.

### package-info.java

The entry point for the package: what it is for, which types are the way in, which are internal, and
any rule that holds across the package (naming, threading, immutability). The package's class list
is generated; a hand-written copy is the membership list all over again.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` are
invisible in rendered Javadoc, silently wrong after a reorder, and unchecked by any tool. Link the
member instead.

- `{@link Type#member}`: a reference the reader may want to follow. Doclint resolves it, so a rename
  that breaks the link is caught, but only where doclint runs, and many builds never reach it:
  `-Xdoclint:none` disables it outright, and a build that never generates javadoc never checks the
  links at all. Find out which yours does before you treat a green build as proof. Prefer `{@link}`
  to a bare `{@code}` name either way, because a reference a tool *can* check beats one nothing can.
- `{@code someExpression}`: an identifier, literal, or snippet the reader will not navigate to, or a
  target that cannot be linked (a member of another module, a method named only informally).
- `{@value #CONSTANT}`: inlines a constant's value; better than transcribing it.
- `@see`: related API the sentence does not need to name.

`{@link #PRIVATE_FIELD}` resolves in an IDE and under `-private`, but not in a published page. That
is fine for a test class or an internal type, and a defect for public API.

**An issue or PR number is an address, not a definition.** Name the phenomenon in the comment, then
give the number so a reader can find the history: `a length taken straight from the wire sizes the
allocation (issue #4015)`. The number must not carry the meaning: `the shape of issue #4015`, `the
same format as #1231`, `the bug #4015 fixed` count as content for someone who already knows the
ticket and as nothing for everyone else. The test: cover the number and read the sentence. If what
remains states no fact, the comment has none. A bare `see #4015` fails the same test from the other
end, and a published page reaches readers with no access to the tracker at all.

The number may open the sentence, as long as the phenomenon arrives in the same one. `The scenario
from issue #4015: a field claiming more bytes than the row envelope still holds` passes, because
covering the number leaves the failure named. The rule is about the number's role, not its position.

The same holds for a commit hash, a mailing-list thread, or a released version. It does **not** hold
for a normative source (an RFC, a protocol specification, a vendor's published documentation), which
may define a format the comment then need not restate.

**A ticket number is not a name.** `a #4015 hardening check` names nothing, and the check has a name
in the code. Use that name, and cite the number once, where the history belongs.

## 6. Tags

- **A fact that fits a tag goes in the tag.** `@return`, `@param`, and `@throws` are the first place
  a reader looks and the only place a tool renders in a parameter table. A body paragraph that
  restates one of them is dead weight: "a failure comes back as the return value rather than as a
  throw" belongs on the `@return` line, not above it.
- **`@param`, `@return`, and `@throws` earn their line by adding what the signature lacks**: a unit,
  a range, a null rule, a condition. `@param name the name` is noise, and a checkstyle rule that
  demands it produces noise at scale; report that rather than filling it in.
- **`@throws` for unchecked exceptions too**, when the caller can prevent them.
- **`@implSpec`** binds subclasses, **`@implNote`** binds nobody, **`@apiNote`** addresses the
  caller. Use them on API that will be extended; skip them elsewhere.
- **`{@inheritDoc}`** when you add to an inherited contract. Which case an override is in, and
  what its body may say, is §4's *Override* genre. What the supertype permits is not a fact of this
  member's contract and pays for nothing under §7a: `the interface permits null, but this
  implementation never returns it` spends a sentence on the genealogy of a guarantee the caller
  already has.
- **A tag you write on an override replaces the inherited one; it does not add to it.** So the first
  rule in this section reverses here: moving one special case into `@return` drops everything the
  inherited `@return` said about the ordinary case, and the reader ends up with a shorter return
  contract than they had. Keep the specialization in the body, where the inherited tag survives
  untouched, or write `@return {@inheritDoc} …` and add to the inherited text on purpose. The same
  holds for `@param` and `@throws`. Judge it by the complete tag the reader ends up with, not by the
  sentence you moved.
- **`@since`** on new public API. **`@deprecated`** must name the replacement and is paired with the
  `@Deprecated` annotation.
- Tag order: `@param`, `@return`, `@throws`, `@since`, `@see`, `@deprecated`.

Markup: `<p>` opens a paragraph and is not closed in traditional Javadoc; closing it is harmless and
some projects require it, so follow the file you are in. JDK 23+ supports Markdown doc comments
(`///`); use them only in a codebase that already has them.

## 6a. When the comment ships as documentation

A doc comment on a published library's public API reaches people through the generated javadoc
pages, and often through a second surface: an OpenAPI `description` that springdoc lifts out of it,
a generated client, a `--help` string.

**The reader changes, and that is the whole section.** They work against your API from the outside:
they cannot open the code, cannot read the private member you were thinking of, and have no `git
log`. Three rules follow.

1. **Know which surface the comment lands on, because the markup differs.** On a generated javadoc
   page `{@link}` is a working hyperlink and `<p>` is a paragraph. In a description a generator
   lifts into YAML or JSON, both arrive as literal text. Write plain sentences for the second case,
   and check what your generator does before assuming the first.
2. **A reference the reader cannot follow has to be spelled out.** `{@link #PRIVATE_FIELD}` and
   anything else that resolves only under `-private` (§5) points nowhere on a published page. Name
   the rule instead of linking to the thing that states it.
3. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a
   parameter accepts, the keys a map may hold: that list is the only source this reader has, so a
   criterion may replace it only when the reader can apply the criterion *without opening anything*.
   §4's own warning applies at full force: if the honest criterion is circular, the list was the
   answer, and the repair is to complete it and verify every member against the code in the same
   edit. An incomplete list shipped as documentation is worse than no list.

Where the generated output is committed (an OpenAPI spec in the repository, a checked-in client),
editing one of these is not a comment-only change. Regenerate and commit the result, or the drift
check fails. Because every edit costs that diff, the bar rises, but it rises for **rewording**, not
for **enriching**. A synonym or a smoother clause is churn that ships. A fact the description does
not carry and its reader needs is worth the diff every time, even when every sentence already there
is true. "It is correct as written" settles the first case and not the second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- a member whose name and types are the whole contract;
- an override that adds nothing to the inherited contract;
- a private helper whose single call site makes it obvious;
- anything the code states better, which is most narration.

The corollary: a public member with a non-obvious contract is not optional, however self-evident the
name looks to the person who just wrote it.

## 7a. Editing an existing comment

Most of the time you are rewriting a comment, not writing one. Different job, different failure
mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none takes one
away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry: a unit, a side effect, a nullability rule, an invariant. Name that fact
  to yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **A near-empty before-version makes the budget vacuous, not permissive.** `{@inheritDoc}`, a
  one-line stub, or no comment at all carries no facts, so everything in front of you is growth and
  none of it has been paid. Judge it as a comment written from scratch: every sentence earns its
  slot under §2, and on an override under §4's three cases. Where the branch under review wrote the
  paragraph an hour ago, its text carries no more authority than your own first draft.
- **A test is evidence, not a paying fact.** A test that pins the behavior establishes that it is
  intentional and stable enough to rely on; it does not make the behavior part of the contract,
  because a test pins implementation behavior just as readily. Name the fact a caller relies on and
  cite the test as support for it. `A test asserts it` pays for nothing on its own.
- **Decompression is paid growth.** A comment can be too dense to read while being too *short* to
  fix under the rule above, and the budget then blocks the only repair there is. Unpacking one of
  the over-compressed shapes `english-developer-style` §4 tabulates adds words and no fact, and it
  is not churn; the payment is the re-read it removes. Name the construction you unpacked instead of
  naming a fact. That skill owns which construction is which and how to unpack
  it; this bullet only states that the budget does not block it. The exemption is that narrow: it
  does not license explaining more, hedging, or a second sentence of rationale, which still need a
  fact.
- **Check every identifier the old comment names.** A comment written before a refactor cites modes,
  constants, and methods that no longer exist. `{@code warn}` for a mode that was deleted compiles,
  renders, and lies; `{@link #WARN}` would at least fail wherever doclint runs (§5). Grep each one,
  and convert what you verify.
- **When you lift a rule into the class comment, cut it from the member.** The member keeps the one
  sentence that specializes the rule, plus the link. Two full statements of the same rule is the
  most common outcome of a good structural edit and the easiest to miss, because each of the two
  reads well on its own.
- **Deleting is an edit, and every cut is reported.** A list of callers, a rejected alternative, a
  cost estimate, a reference to the PR that introduced the code: cutting these is usually the
  highest-value change in the diff, even though the result looks like less work. Delete sentence by
  sentence, and report each deleted sentence with the fact it carried and where that fact now lives:
  a tag, another member, the commit message, or nowhere, with the reason. A rationale sentence stays
  only where a maintainer reading the rule would ask why or would be tempted to relax it; the test
  is whether the sentence would come up as a question in code review. A rewrite that reads better and
  says less is the failure this rule exists to prevent.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule
  governs the body, not the first sentence. `Wrapper around X that implements some basic primitives`
  stays broken until someone rewrites it, and "I had no new fact to add" is not a reason to leave
  it.
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

One fact is one unit, one bound, one nullability rule, one side effect, one ordering or threading
constraint, one lifecycle obligation, one named collaborator, one link target, or one stated
default. A topic sentence is not a fact, and neither is a restatement of the signature. What the
supertype permits, and what another API does, is neither: it names nothing a caller of this member
relies on, so it takes a row as provenance and pays for no growth in step 3 (§6). Compare
facts, not sentences: at sentence granularity, merging two sentences looks like a loss and splitting
one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Four
defenses hold:

- the fact was wrong, which includes a claim the old text made and the code does not support;
- the fact moved to the class comment, and you can point at the sentence that now carries it;
- the fact moved into a `@param`, `@return`, or `@throws` tag, where §6 places it;
- the fact was rationale, the contract it explained is stated completely without it, and the
  rationale no longer earns a slot under §2.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is the sentence someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first sentence repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification. Where the old version carried no fact (`{@inheritDoc}`,
a stub, no comment at all), the budget measures nothing: judge every sentence of the new version on
whether it earns its slot under §2, and on an override under §4's three cases (§7a).

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
inside this package reaches the guard`, and supports nothing about who the guard is for. Design
intent traces to a comment, to a specification, or to the shape of the API itself, never to a count
of callers. This is §4's membership rule from the other end: a roll call of today's callers is not a
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

A comment something other than a human reads is out of scope for all of these; see §4 for the list
and for what moving one breaks.

**7. Prove the code did not move.**

A sweep that edits comments across many files is reviewable only if the claim "comments only" is
mechanical rather than asserted: parse each file before and after with comments discarded, and any
difference means the pass touched code. `natural-language-sweep` runs that oracle; for a single
edit, the diff is the proof.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it makes two people comparing the same pair reach
the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and convert it to `{@link}` (§5) |
| Duplicated rule | Cut the copy the class comment now carries (§7a) |
| Churn | Restore the old wording |
| Density kept | Unpack the stacked relative, the elliptical opener or the noun pile (§7a) |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Counterfactual | Cut the simulation; re-evaluate any rationale left standing under §2 |
| Unearned rationale | Cut the rationale; keep the complete contract (§2) |
| Superclass provenance | Cut it; keep the resulting contract (§6) |
| Stale inline comment | Rewrite it from the code |
| Reworded tool marker | Restore its exact text and position (§4) |

### The case this section exists for

**Before**, one line carrying two facts.

```java
/** Waits up to 30 seconds for the backend to acknowledge the cancel, then breaks the connection. */
```

**After**, the same comment restructured.

```java
/**
 * Waits for the backend to acknowledge the cancel request.
 *
 * <p>The connection is broken if the acknowledgment does not arrive.</p>
 */
```

The rewrite is better on every count §3 measures: the summary stands alone, the consequence gets its
own paragraph instead of trailing a comma, and the sentence no longer runs to two clauses. It also
dropped the timeout, and the new text carries no sign that one exists. Step 2 offers a defense here
(cite the property the value now comes from), and the rewrite takes none of them.

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Does the first sentence stand alone in a summary table, with no term this comment introduces?
- Does the first sentence terminate where you think it does, or does an `e.g.` cut it short?
- Could a reader reconstruct the first sentence from the member's name alone?
- In a regression test's comment: the rule first, the old defect in one past-tense sentence, and any
  equivalence with the old behavior kept (§1)?
- Is the contract stated positively and in one place, before any mechanism?
- Could a reader satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Is any rationale here PR-description material?
- Any sentence describing a previous version of the code: `now`, `no longer`, `used to`?
- Any sentence describing a code path this code does not have: what would happen if the rule were
  broken, rather than what the code does about it?
- Does the comment explain another class's internals instead of linking to it?
- Any positional reference: `below`, `above`, `the following`, `the other way`?
- Does a limit state what it bounds, rather than only what some neighboring limit bounds?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Any `{@code Foo}` that should be `{@link Foo}`?
- Does every `@param`, `@return`, and `@throws` add something the signature does not?
- On an override: which of §4's three cases is it in, and does any sentence describe the supertype's
  freedom rather than this method's rule?
- Does every term here have a definition outside this comment, and does every name match what the
  code calls the thing (`english-developer-style` §4a)?
- For each rationale sentence: would deleting just that sentence change what a caller may rely on,
  or leave a maintainer unable to see why a constraint is there? If not, delete it.
- Would deleting the whole comment lose anything?
- Is every `CHECKSTYLE:OFF`, `@formatter:off`, `//noinspection`, or `$NON-NLS-` marker still worded
  and placed exactly as it was?
- If the comment ships as documentation (§6a): can its reader follow every reference in it without
  opening the code, and did you regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the class comment, or on a `@return` or `@param` line?
- Any list that a criterion would replace, or that find-usages already provides? Can the set gain a
  member without anything forcing an edit here, and does a trailing `...` stand where no criterion
  precedes it?
- Does every name the old comment mentioned still exist?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first grows, because facts were
missing; the second shrinks, because they were not. Do not read either one as the target shape.

Both come from a real codebase, which makes them a hazard: an example you can recognize in the wild
is an example you will paste instead of derive. A rewrite that matches this file word for word
proves nothing about whether the rules were applied to the comment in front of you.

### A test class, where facts were missing

Both versions document a test that fails when a new backend message type is added without a hardened
reader. Abridged from pgjdbc PR #4016.

**Before**: opens with an invented term, then with a neighboring class; the rule it guards appears
nowhere; the reader is pointed at a source position.

```java
/**
 * Guards the inventory of backend messages the driver knows how to read.
 *
 * <p>{@link PGStream#receiveMessageType()} keeps every <em>existing</em> reader honest: a
 * reader that takes its length from a raw {@code receiveInteger4}, or that forgets
 * {@code endMessage()}, leaves the stream off a message boundary and fails the next read,
 * so any test that drives that message reports it. That only helps once a message is
 * exercised by a test. This test covers the gap ahead of it: adding a backend message to
 * {@link PgMessageType} fails here until the message is listed below, which is where the
 * author is told what the reader owes.</p>
 */
```

**After**: the summary is the firing condition; the contract is stated positively and first; the
neighboring class is compressed to its limitation; the reader is told what to do and where to look.

```java
/**
 * Fails when a backend message type is added without a hardened reader.
 *
 * <p>Every backend reader must declare a message envelope: take the length through
 * {@code PGStream.readMessageLength} (or {@code readFixedMessageLength} or
 * {@code readPreAuthMessageLength}), bound any length it reads from the wire, and close
 * the envelope with {@code endMessage}. A reader that skips this leaves the stream off a
 * message boundary, which is the desync class of bug that issue #4015 reported.</p>
 *
 * <p>{@link PGStream#receiveMessageType()} catches such a reader at run time, but only
 * after a test drives that message. A new message type with no test would slip through.
 * This test closes that gap. It lists every constant in {@link PgMessageType} in one of
 * two sets: {@link #HARDENED} for backend messages the driver reads, and {@link #FRONTEND}
 * for messages the driver only sends. Add a constant to {@link PgMessageType} and this
 * test fails until you classify it. The failure message states what a backend reader
 * owes.</p>
 */
```

What changed, slot by slot: the summary became a firing condition (§3); the contract moved to the
front and gained a positive, parallel statement of the three obligations (§2); the mechanism of
`PGStream` shrank to the one fact this comment needs (§4); `listed below` became `{@link #HARDENED}`
and `{@link #FRONTEND}` (§5); and a Use slot appeared, naming the action and the failure message
(§2). The issue number stayed, attached to a named class of bug (§5).

### A field, where the facts were already there

The example above grew. Most edits go the other way: nothing is missing, and the comment has
accreted a list that a tool serves better.

**Before**: enumerates the methods that touch the field. That list is find-usages transcribed by
hand, and it is wrong after the next refactor.

```java
  /**
   * Logical stream position of the byte at {@code buffer[0]}. The field is touched only when
   * the buffer is shifted, drained, or bypassed: {@link #moveBufferTo(byte[])} (the
   * compact/double path), the buffer-drain reset in {@link #readMore(int, boolean)},
   * {@link #read(byte[], int, int)}, and {@link #skip(long)}. The last two also bump
   * {@code position} for bytes they read or skip directly from the wrapped stream.
   */
```

**After**: states the invariant the list approximated, and the one consumer the field exists for.

```java
  /**
   * Bytes consumed before {@code buffer[0]}, counted since construction. The logical position is
   * {@code position + index}, so a read served out of the buffer advances it through
   * {@code index} alone. Never decreases; a skipped byte counts as consumed.
   *
   * <p>{@link PGStream} reads the position to record where a protocol message must end and to
   * verify that it ended there, which is why the count has to hold across a buffer refill.</p>
   */
```

Same number of lines, and the reader can now settle a question the list could not: what happens to
`position` in a method nobody has written yet (§4, the membership rule).
