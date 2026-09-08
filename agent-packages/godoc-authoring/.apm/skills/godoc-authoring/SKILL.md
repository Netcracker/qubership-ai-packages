---
name: godoc-authoring
description: >-
  Load before writing, editing, or reviewing a doc comment or inline comment in Go: the comment on
  a new or changed function, method, type, or package, a method that implements an interface, a
  //go:, //nolint, or +kubebuilder line, a regression test that names the old defect, a subtest
  name or a failure message, a CRD field description that reaches users through kubectl explain.
  Inside a coding task on a Go codebase ("fix the bug", "add the handler") load it as soon as the
  change touches a comment, before writing it. Also load to decide whether a declaration needs a
  comment at all, or to compare two versions of one. Governs what the comment says and in which
  order: the first sentence that names the thing, contract before rationale, doc links, errors and
  deprecation stated in prose, when to write nothing, how far a rewrite may grow. Wording is
  english-developer-style's; load both.
---

# Authoring a Go doc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect belong to `english-developer-style`: load it too, and defer to it on the prose. The two
compose: this skill picks the slots; that one writes the sentences.

It is the Go sibling of `javadoc-authoring` and keeps its section numbering, so a review that cites
"§7b" means the same rubric in either language. Read this one for Go; do not translate the Java one
in your head. The slot model transfers unchanged, but §3, §5, and §6 do not: Go puts the
identifier's name in the first sentence, replaces `{@link}` with an unchecked bracket syntax, and
has no tags at all.

`gofmt` owns the *layout* of a doc comment (indentation of code blocks, list markers, blank-line
normalization) and rewrites it on every save. Never hand-align a doc comment; write the content and
let the formatter place it.

## 1. The correction that matters most

"Document the why, not the what" is half wrong for a doc comment, and the wrong half does the
damage.

An inline `//` comment inside a function documents the **why**; it sits next to code the reader can
already see. A doc comment on a declaration documents the **contract**: what a caller may rely on,
what an implementer must guarantee, what holds before and after. That is a *what* at the level of a
promise, not a restatement of the code.

The failure mode is therefore not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Loops over the entries and adds each to the map.` The body
  already states it, and the comment becomes false on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the boilerplate every endpoint
  shared.` That belongs in the commit message and the pull request description. A doc comment's
  reader has to *use* or *fix* the thing, not decide whether to merge it.

**The test is the refactor, not the reader.** Rewrite the body so it behaves identically and reads
differently: a loop becomes a call into `slices`, a helper is inlined, a field is renamed. Every
sentence you would then have to edit was implementation, whatever it sounded like. This is the
operative rule, because it settles cases that "specification, not details" argues about forever,
and it does not soften with visibility: an unexported function's comment goes stale on that
refactor exactly as an exported one's does, and the cost of a comment that lies is the same either
way.

**The caller substitutes too, and catches what the refactor cannot.** Imagine a new legitimate
caller supplying the same argument for a different reason. A sentence that then describes only the
old call path is caller context, not this declaration's contract. `A negative n is refused before
any byte is read` survives the substitution; `because a count taken from a length the backend
declared can be negative` does not.

Cutting is not the whole repair, because the rationale slot can be open and merely filled wrong.
Where a value came from does not explain why the declaration behaves as it does; a local reason,
where one exists, is a property of this declaration's own contract. Look for the local reason
before concluding that the slot was never open, then ask §2's question of it: does the rule look
arbitrary without it, or would a maintainer relax it incorrectly? A reason any reader would have
assumed fails that question and stays out, however true it is.

Provenance crosses into a callee's comment where it is that declaration's own contract: a protocol
function whose parameter *is* the declared length minus the header documents its own layer rather
than borrowing the one above it. **State the local rule at the lowest-level API, and the scenario
at the layer where the scenario exists.** A guard found through one concrete call path does not
thereby own that path's story.

**Sufficiency** scales with visibility: how much the comment may leave to the code beside it.

| Where | What the comment must carry |
| --- | --- |
| exported | Complete without the code. An exported method on an unexported type is reachable through every exported function or interface that yields the type, so it is exported API here. A field that ships as a CRD description has a further reader (§6a) |
| unexported | May be elliptical and lean on the body beside it. Often there is no contract distinct from the implementation at all, and §7's "the name and types are the whole contract" usually applies |
| inline | Nothing about the contract. The reader has the code |

For an inline comment the bar is negative: **a competent reader is looking at this code and
understanding it correctly; write the comment only where they would not.** A reason that surprises,
a bound that looks arbitrary, an order that looks swappable, a branch that looks dead. Where their
expectation and the code agree, the comment is noise, and later stale noise.

A third failure, specific to a codebase that has been refactored, is **narrating the code's
history**. `Successful reconciles now carry a RequeueAfter, so the delay can no longer distinguish
done from retrying` describes a transition between two versions, and the reader has only this one.
Rewrite it as the state that holds: what the delay cannot do, and why.

One exception. **The comment on a regression test may tell history, and an equivalence is not
history.** The test guards the defect, so the defect belongs in the comment: state the rule the
test asserts first, then the defect in one past-tense sentence with the error or the panic: `A
negative n used to be reported as available, and the caller then panicked with a slice bounds out
of range.` A comment that opens with the defect makes the reader reconstruct the broken version to
understand the fixed one (measured on one branch: a blind reader ranked the version that opened
with `used to` fourth of five on that ground alone). Do not narrate the old mechanism in the present
tense, and do not recast it as a chain of `would` clauses. History narration, which this section
forbids, is a sentence whose only content is that the code changed. A sentence that argues the new
behavior is safe **because it is identical to the old one** is rationale, and the old behavior is
its comparison term. Keep the comparison; it is the whole argument.

- *Keep:* `a reader whose closed.Load() runs before Close stores true behaves exactly as every
  reader did before the atomic.Bool was added: it reads from the buffer and the wrapped reader as
  if nothing were closed`
- *Wrong repair:* `a concurrent reader may not have observed the store yet and may still read from
  the buffer` (the equivalence, which is the reason an atomic.Bool with no lock around it is
  enough, is gone)

A fourth is the third one turned sideways: **narrating the branch that does not exist**, what the
code would do on an input it refuses, or under a rule it does not implement. History narration gives
the reader a past version of the code; this gives them a version that never existed. `If uppercase
names were allowed, the label built from this name would be rejected downstream and the deployment
would never start` describes a path no build of this code can take. No refactor can make it false
and no reader can check it, so it survives every review.

This does not ban consequences. What the code does when the contract is broken (which error it
returns, what it wraps, what state the value is left in) is contract, and the sentence that names
the error (§6) carries it. Cut the simulation of the branch the guard prevents.

**The test: could a reader falsify the sentence by reading this repository?**

- `Returns an error when the name contains an uppercase letter`: contract. It names a path this
  code has.
- `The name becomes a Kubernetes label, and a label admits no uppercase letter`: eligible. It names
  the *source* of the constraint, the shape rationale takes when it earns a slot at all. It still
  has to earn it.
- `Otherwise the deployment would be rejected and never start`: cut. Nothing here produces that,
  and the system that would is one the reader cannot see and you do not control.

**Where the reason belongs in the comment at all, name the source of the constraint rather than the
disaster it averts.** Cutting a counterfactual obliges you to put nothing in its place. §2 fills
the empty rationale slot only where the rule would otherwise look arbitrary or be easy to change
incorrectly, never merely because a source exists and is true.

A source the reader cannot infer from the code is the likeliest to earn its sentence, but
reachability is evidence, not the test. `The size must be a power of two because indexing masks
with size - 1` earns its place with the masking five lines below: the restriction looks arbitrary
without it and the next maintainer will relax it. `RFC 1234 permits three encodings` earns nothing
when no caller needs to know why this one was chosen.

Where the constraint is *enforced*, an earned sentence belongs inline beside the guard: the reader
sees the `return err` and cannot see why the value is unacceptable. Where the constraint is only
*stated*, in a doc comment, ask the question again from scratch. Completeness does not settle it: a
contract states itself completely by definition, so `the error sentence already says what happens`
closes nothing. The test stays the same: would the rule look arbitrary, and is it easy to change
incorrectly?

A function with more than one failure channel, an error beside a sentinel result such as `false` or
`-1`, is not an exception to that test. The comment states each outcome, and a maintainer reading
them is expected to keep them apart. A sentence explaining why an invalid argument returns an error
rather than the sentinel is the reason any reader would have assumed (measured: a maintainer who
met such a sentence in review called it common sense). Leave it out.

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
enforces it, and before what some *other* package does. A comment that opens with a neighboring
type forces the reader to reconstruct the rule from negative examples. State it positively, in one
place, first.

**When only one slot fits, keep the contract.** Rationale is the first slot to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

**Removing a bad explanation does not create an obligation to replace it.** A rationale slot emptied
by a cut stays empty until the finished contract, read on its own, turns out to need one. Start from
the contract, not from the gap.

**Make the obligated party the subject.** Obligations come in two shapes. A *stated* obligation
carries a *must*, *has to*, *may not*, or *should*, and whoever has to comply belongs in the
subject: not the thing acted on (`Every backend message must be read through readMessageLength`,
which names no one and lets `it` drift to the reader by the next clause), not the act (`relaxing a
protocol check must not be reachable`), and not a declaration that merely performs the act for
someone else (`markBroken must still be called` obliges the `Conn` that calls it). A named
declaration in the subject is right only where that declaration is itself what must comply:
`readUntrackedLength must leave no envelope behind`. The party need not be human, but it must act: a
client, a check, a reader. A mode constant or a configured number complies with nothing.

A *census* is a rule for the next maintainer, written instead as a report on today's call sites:
`Every site that dispatches on a message type reads the tag through this method`, `CopyData is the
one such site`. It is flat indicative with no modal, so test it: **if a second such caller appeared
tomorrow, would this paragraph tell it that it is obliged?** Judge the paragraph, not the sentence;
an example may follow a law that is already correctly stated. Write the law, not the roll call.

Watch the intransitive modal, where the party hides best: `every constant has to appear in
hardened`, `an unknown value must fall back to ModeFail`. Nothing appears or falls back on its own;
name what does it.

Out of reach of this rule: an imperative, which already addresses the party (`Call it where the
framed dialogue resumes`), including one that carries rationale (`so mirror that here`); a
constraint on a *value* (`must be <= maxMessageSize`), which bounds a number rather than behavior;
a field comment naming who writes or reads the field, which is the membership list §4 calls for;
and an inline comment whose next statement is the actor (`// The envelope must be fully consumed`
above the `c.endMessage()` that consumes it), after checking that the next line really is the actor
and not test setup standing between the comment and the call it constrains.

Most declarations need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots
to fill a template; an absent slot is not a gap.

**Size the comment to the declaration.** A doc comment longer than the function it documents is not
automatically wrong (an invariant can be worth ten lines over a three-line method), but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two
sentences of it, and only for the part a reader would otherwise get wrong. The rest belongs in the
commit message. As a working size, a test function's comment is two to five sentences and a
function comment fits in one glance; past that you are describing the investigation, not the
contract, so keep the rule and the exception and move the rest.

## 3. The first sentence names the thing it documents

Go's convention is unusually specific, and it is the rule most often lost when Javadoc habits are
carried across: **a doc comment begins with the name being declared.**

```go
// SetCredentials atomically replaces the Basic Auth credentials used for all
// subsequent requests. Safe for concurrent use.
func (c *AggregatorClient) SetCredentials(username, password string) { … }
```

Not `Atomically replaces…` (the Javadoc form) and not `This method replaces…`. The name leads,
followed by a present-tense third-person verb.

- **Package comment**: `// Package client provides an HTTP client for the dbaas-aggregator REST
  API.`
- **Command** (`package main`): the binary's name leads: `// Aggregator-mock emulates the
  dbaas-aggregator endpoints the operator calls.`
- **Test function**: the exception; see the test genre note in §4.
- **Blank identifier** (`var _ Interface = (*T)(nil)`): nothing to lead with; state the assertion.

The rest of the summary rule carries over from Javadoc unchanged:

- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it, and the summary must be readable by
  someone who never reads paragraph two. The repair is rarely to define the term earlier: the field
  almost always has a word already, and `english-developer-style` §4a gives the test for telling a
  defined term from a coinage.
- **No self-description.** Drop `Helper type that…`, `Utility for…`. The name, then the verb.
- **Watch the terminating period on a package-level declaration.** Tooling extracts the first
  sentence of a package, func, type, const, or var as a one-line summary: package listings,
  `go list -f {{.Doc}}`, pkg.go.dev search results. `go/doc.Synopsis` ends that sentence at the
  first `.` followed by a space, so `e.g.`, `i.e.`, and `vs.` truncate it, and Go has no
  `{@summary}` escape hatch. Rewrite instead.

  **A struct field is exempt.** Nothing extracts a synopsis from one: `go doc` prints a field
  comment whole, and so do pkg.go.dev and a generated CRD description. Moving an `e.g.` out of a
  field comment's first sentence fixes nothing, and on a field that ships as a CRD description it
  is churn that ships (§6a).
- **One sentence.** If it takes two, the first one is not the summary.
- **A constant or variable names itself first, with its unit.** `maxPacketLen is the largest
  encrypted packet that this stream accepts, in bytes.` The reason the bound has that value is slot
  3, however interesting it is; a comment that opens with the upstream implementation it mirrors
  leaves the summary saying nothing about the constant.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  fills the summary with a word that states nothing about what the declaration does. Put the
  qualifier after the summary: `ModeFail rejects a message over its limit and closes the connection.
  It is the default.`
- **A first sentence a reader could reconstruct from the identifier carries nothing.** A test
  named `TestClient_RetryPreservesCallerHeaders` does not need `Checks that a header the caller set
  survives the retry.`; `go test` prints the name. Where the name states what the test establishes,
  the comment carries the reason, the construction the reader would not guess, or nothing. For a
  field or a getter the same rule leads to §7: where the name and the types are the whole contract,
  write no comment.

### The Kubernetes API exception

In a type whose fields are serialized into an API (a CRD spec or status, or any type a client reads
through `kubectl explain`) the field comment opens with the **JSON name**, not the Go name:

```go
    // observedGeneration reflects the .metadata.generation that was last processed.
    ObservedGeneration int64 `json:"observedGeneration,omitempty"`
```

The Kubernetes API conventions require this, and the requirement is right: the comment is rendered
to someone writing YAML, who has never seen `ObservedGeneration`. Follow the file. Go-visible
declarations in the same package (exported constants, functions, interfaces) keep the Go name.

## 4. Genre notes

### Type (struct, interface, named type)

The type comment carries the **invariant that spans the fields and methods**. Member comments
specialize it and do not carry it; a rule stated only on an unexported field is a rule the type
comment is missing.

Name the collaborators the type is useless without, the concurrency model if there is one, and the
lifecycle if the zero value is not ready to use. "The zero value is ready to use" is itself a
contract worth one clause when it holds. Do not explain how a collaborator works internally; link
to it and let its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set (every reason a condition may carry, every function that
writes a field, every caller that must be updated) has transcribed a query. The list is stale from
the first refactor, and a reader who does not find their case in it concludes the wrong thing.

State the criterion instead: *every other check rejects a value that no conforming backend can
send* beats an eight-item list of those checks, because the reader can classify a check the list
has never heard of. The criterion has to let the reader name a member: "the ceilings whose error
message offers this as a remedy" is true by construction and states nothing the reader could not
have inferred. Where the honest criterion is circular, the list was the answer.

Two exceptions. A set the code itself declares and a check enforces (a test that partitions a set
of constants into named sets, a `switch` that an exhaustiveness linter covers) fails the build when
it drifts, so there the list **is** the contract. The compiler does not check a `switch` for
exhaustiveness on its own; without a linter or a test behind it, a `switch` is a list like any
other. And a list the reader needs as vocabulary (the environment variables a command reads, the
keys a map may hold) stays, because the criterion alone lets nobody write code. What goes in that
case is the part that rots: the version label that freezes the list, and the per-item annotations
nobody maintained.

The exception is wider for a comment that ships as API documentation (§6a), because that reader
cannot open the code to enumerate the set themselves. It is not unlimited: an incomplete list
shipped as documentation is worse than no list, so if you keep one, verify every member against the
code in the same edit.

**One question decides it: can this set gain a member without anything forcing someone to edit this
comment?** If it can, write the criterion; no build, test, or review will report the stale list. If
it cannot, because a test or a linter fails the moment the set changes, the list is the contract
and belongs here. The question is not about size (a three-item list nobody maintains rots faster
than a twenty-item one a test keeps honest) and not about origin in a standard (standards grow:
PostgreSQL adds message types, TLS adds versions). A *closed* set is safe, and the check detects
exactly that.

**A trailing `...` admits that the list is incomplete, and where it belongs depends on what
precedes it.** After a stated criterion it is fine, because the items are illustration: *every
wire-compatible backend shares it (CockroachDB, YugabyteDB, Redshift, ...)* loses nothing if the
reader has never heard of the fourth. Where the list is itself the claim, *returned by the higher
layers (auth, cancel-key, startup negotiation, ...)* reports that more members exist and gives no
way to name one, so it is neither a list nor a rule. Supply the criterion, or finish the list and
accept the maintenance.

### Function and method

Slot 2 carries the work. State these, and only where the signature does not already:

- whether a returned pointer, slice, or map may be nil, and what nil means;
- whether a nil argument is accepted;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- ownership of a passed or returned mutable value: does the callee retain it, may the caller mutate
  it afterwards;
- side effects the name does not advertise, including I/O and state changes;
- idempotence, goroutine-safety, and ordering guarantees;
- whether the function may block, and what canceling `ctx` does;
- which errors a caller is expected to match with `errors.Is` or `errors.As`, and which are
  programmer errors that panic.

Go has no `@param`. Name a parameter in prose, spelled exactly as in the signature, at the point
where its contract matters: `body is marshaled as JSON when non-nil`. Do not walk the parameter
list in order restating types; that is the signature, transcribed.

Go has no `@return` either. Named results are the closest equivalent and often do the job outright:
`func CreateDatabase(…) (pending bool, err error)` needs one clause about what `pending` means,
not a paragraph. Use named results when a bare `(bool, error)` would force the comment to explain
which is which.

Every item on that list is a property of the value. Where the caller got the value is the caller's
sentence: `the caller computes this from the message header` describes one call path and ages the
day a second one appears (§1).

A function whose contract is exhausted by its name and types needs one line or nothing.

### Method that implements an interface

Go has no override and inherits no comment. A type satisfies an interface by having the methods,
and nothing ties a method's comment to the interface's: pkg.go.dev shows the interface's method
comments on the interface's own page, and an editor shows the method's own comment on hover, so the
reader reaches the interface's contract only by navigating to the interface. Whatever you write
beside the method is the whole of what they see there. Read the interface's comment before you
write.

Three cases, and the interface's contract decides which one you are in.

1. **The method obeys the interface's contract.** Write a single line that names the contract, and
   nothing else: `Close implements [io.Closer].` The line satisfies §3, and its doc link is the
   only thing beside the method that gets the reader to the contract they rely on. A second
   sentence that restates that contract is the duplicate §7a cuts.
2. **The interface leaves the behavior open, and this type picks one.** State the resulting
   contract as a rule of this type, in one positive sentence: `Read returns the final bytes
   together with [io.EOF], not on the following call.` The freedom the interface granted is not
   news, and a sentence spent on it is provenance (§6). The same holds where the method narrows
   what the caller gets: `Entries returns an empty slice, never nil.` A method that shadows a
   promoted method of an embedded type is this case too, where the embedded type's comment leaves
   the behavior open: state this type's rule and do not name the embedded type.
3. **The method breaks the interface's contract.** A caller holding the interface value is about to
   be wrong, so the deviation is the reason this comment exists. Name it in the interface's own
   terms, with the condition it happens under: a `Read` that keeps a reference to `p` after it
   returns breaks a sentence `io.Reader` states outright. Check first whether the contract really
   forbids the behavior: a contract that says *may* permits it, and case 2 applies. A deviation is
   also a defect report, so raise it rather than only documenting it.

The mechanism that forced the choice is rationale and earns its slot under §2. `The offset indexes
the buffer that [Buffer.Bytes] returns` explains why a negative offset is refused, and it stays only
where a maintainer would otherwise relax the rule; a rule that matches what the interface's own
documentation prescribes looks arbitrary to nobody.

### Field, constant, and variable

Document the unit, the range, the sentinel, and who may write it. An unexported package-level
variable whose invariant is non-obvious needs that invariant spelled out; a reader adding a write
has no other source of truth. When the type comment already states the rule, the field comment
shrinks to one sentence plus a link.

A `const` block with a shared rule takes one comment above the block and short ones inside it, not
the same sentence eight times.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence, positively, and
before any neighboring limit comes up: `maxServerMessage bounds only what the server sends.` A
comment that leaves the scope to be inferred from a contrast (`…which governs the direction this
limit does not`) makes the reader subtract one limit from another and reconstruct the missing verb.
Both halves are facts; state them separately, this one first.

A constant whose value is a size or a duration states both forms: `1 MiB (1048576 bytes)`. Nothing
in Go substitutes the value into the comment: `go doc` and pkg.go.dev print the declaration as
written, so a reader of `MaxCStringLength = 1 << 20` sees the expression, not the digits. The
digits in the comment are hand-written, so re-check them whenever the value changes, and keep the
unit exact (`64000000` is `64 MB`, not `64 MiB`) or hedged in words: `about 1 GiB (1073741823
bytes)`. The form is `english-developer-style` §5.

### Inline comment

An inline comment states why this line, for a reader who can already see the line. Four failure
modes beyond narration:

- **Meta-commentary.** `…so gate on the conditions instead` describes what the comment is doing.
  State the fact: `the conditions identify a terminal state; the requeue delay does not.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` mark it.
- **Counterfactual.** See §1. `if … were`, `would`, `otherwise the` mark it. Name the source of
  the constraint; do not simulate the branch the guard prevents.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is converted to `int32` belongs at the conversion; repeating it inside the branch that
  rejects a negative value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`//go:build`, `//go:generate`, `//go:embed`, `//go:noinline` and the rest of the `//go:` family;
`//nolint:…`; `// +kubebuilder:…`, `// +optional`, `// +listType`, `// +groupName` and other
controller-gen markers; `// +kubebuilder:scaffold:…` injection points;
`// Code generated … DO NOT EDIT.`; `TODO` and `FIXME` markers; anything citing an issue or a
URL.

Two Go-specific hazards when you restructure a comment that contains them:

- **A field's markers must stay in the same comment group as the field.** controller-gen reads the
  doc-comment group immediately above a struct field. Insert a blank line, or even a bare `//`,
  between a `// +kubebuilder:validation:…` marker and the field, and the whole group detaches:
  measured on controller-gen 0.20.1, a blank line above `Type string` dropped `minLength`, the
  `XValidation` rule, **and the field's description** from the generated CRD, and nothing failed.
  Markers go at the end of the block, adjacent to the field.

  Type-level markers are the opposite case and look alarming for no reason.
  `+kubebuilder:object:root`, `+kubebuilder:printcolumn`, `+kubebuilder:resource`, and a root
  `XValidation` conventionally sit in their own group *above* the doc comment, separated by a blank
  line, and controller-gen picks them up from there. Do not "fix" that separation.
- **A directive in the doc position becomes the doc.** `go/doc` strips the `//go:` family, but not
  `//nolint:`. A `//nolint:gocyclo` line directly above `func main` is that function's entire
  rendered documentation. Put it on its own after the prose, or accept that the declaration has no
  doc comment.

### Test file

A test is read in exactly one situation: it just went red. Write for that reader.

Test functions are not rendered by `go doc` or pkg.go.dev, so the name-first rule of §3 has no
tooling behind it here. `go test` prints the name, so the name states what the test establishes,
and the comment, where the function has one, carries what the name cannot:

```go
// Only headers the caller set are compared; a header the transport adds on its
// own, such as Content-Length, may differ between attempts.
func TestClient_RetryPreservesCallerHeaders(t *testing.T) { … }
```

- **The rule the test guards** goes in the comment where the name cannot hold it whole, stated
  positively and completely, as something you could assert. `It has to stay quiet when the socket
  did go away` leaves the reader guessing: not panic, not close twice, not log? Name the
  observable. If you cannot phrase the rule as an observation, the test probably cannot check it
  either.
- **What to do about the red build** goes in the comment as well: which set to edit, which case to
  add, where the failure message states the rest.
- **A table-driven case's `name` field is a comment.** It is the string the reader sees in the
  failure output, so it names the case's condition, not its ordinal.

Deliberate duplication between the test's comment, a helper's comment, and the failure message is
correct, because each reader meets exactly one of the three. It does not extend to production code,
where the type comment and the method comment have the same reader.

**A failing test should read as a bug report, and four things write it.** Decide what each one
carries before you write the next; the reader sees them together in one `--- FAIL` block.

- **The test function's name** carries what every subtest in it shares: the unit under test and
  the condition they all sit under. A fact true of every case belongs here rather than in each of
  them.
- **The subtest's name**, the `name` field that `t.Run` receives, states what this one case
  establishes. `negative count is refused` is a finding; `case 3` is a location that makes the
  reader open the file. One assertion per case keeps the name able to do this, and keeps the
  report readable when several cases fail at once.
- **The failure call prints the values.** `t.Errorf("got %v, want %v", got, want)` renders both;
  `if got != want { t.Fatal("mismatch") }` renders neither and leaves the reader to rerun under a
  debugger. An assertion library's `Equal(t, want, got)` prints both the same way, and its
  `True(t, got == want)` prints neither. Choose the form that already prints what the reader needs,
  rather than describing it in the message.
- **The message adds what the other three cannot.** `go test` prints the file and line before the
  message, so the message never says where. In a table-driven test the subtest name states which
  case ran, so the message states the invariant or nothing. Under a bare `t.Fatal` it is the
  invariant, because nothing else states it. Where the values are in the format arguments already,
  do not restate them; where the function or subtest name states the scenario, do not restate that
  either.

`t.Fatal("failed")` is that defect at its limit: it reports that something is wrong and nothing
else.

This does not contradict the duplication paragraph above. A name is printed in the report; a test's
comment is read only once someone opens the file. Repeating a comment in a message is the useful
duplication; repeating a name is the one that costs.

### Package comment

One per package, in the file that carries it: a `doc.go` when the text is long enough to crowd out
code, or the package's principal file when it is not. Two files with package comments in one
package is a defect no compiler catches.

It is the entry point: what the package is for, which types a caller starts from, which are
internal, and any rule that holds across the package (naming, concurrency, error conventions). The
package's declaration list is generated; a hand-written copy is the membership list all over again.

A command's package comment is user documentation: what the binary does, its flags, its environment
variables, its exit codes. There the vocabulary exception of §4 applies in full.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` are
invisible in rendered documentation, silently wrong after a reorder, and unchecked by any tool. Name
the identifier instead.

Go 1.19 and later support **doc links**, which render as hyperlinks on pkg.go.dev and in editors:

| Form | Refers to |
| --- | --- |
| `[Classifier]` | a declaration in this package |
| `[AggregatorClient.SetCredentials]` | a method or field of a type in this package |
| `[client.AggregatorClient]` | a declaration in an imported package |
| `[*client.AggregatorClient]` | the same, as a pointer |
| `[net/http.Client]` | a package the file does not import |

A doc link only resolves if the target exists and, for another package, that package is imported by
the file. **Nothing fails the build when it does not.** An unresolved `[Foo]` renders as the literal
text `[Foo]`, and neither `go vet` nor a stock `golangci-lint` run reports it. Javadoc at least has
doclint, which catches a broken `{@link}` wherever it is switched on; Go has no equivalent to switch
on, so the verification burden of §7a sits entirely on you.

Use a doc link for a reference the reader may want to follow. For an identifier they will not
navigate to (a JSON field name, a literal, a shell command, a symbol in a service you do not import)
plain text is correct; Go doc comments have no inline code markup, and backticks render as
backticks. Set off a longer snippet as an indented block instead.

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

## 6. Structure, where Javadoc has tags

Go has no `@param`, `@return`, `@throws`, `@since`, or `@see`. §4 covers what replaces the first
two. The rest:

- **`Deprecated:`** starts its own paragraph, at the end of the comment, and must name the
  replacement. Tooling reads it: `staticcheck` SA1019 and editors flag callers. Nothing else in a Go
  doc comment is machine-interpreted this way, so do not invent siblings for it.
- **Errors** go in prose, naming the sentinel or type a caller matches: `Do returns an
  *AggregatorError for any non-2xx response.` A panic is worth a sentence when the caller can
  prevent it.
- **Nothing is inherited.** A method's comment is all that is displayed beside it: pkg.go.dev shows
  the interface's method comments on the interface's page, and an editor hover shows the method's
  own comment. A comment on an implementing method that states one special case and nothing else
  therefore leaves the reader with a shorter contract than the interface gives them. Name the
  interface in a doc link (§4, *Method that implements an interface*) so the reader can reach the
  rest, and judge the comment by the complete contract they end up with. What the interface permits
  is not a fact of this method's contract and pays for nothing under §7a: `the interface permits
  nil, but this implementation never returns it` spends a sentence on the provenance of a guarantee
  the caller already has.
- **Code blocks** are indented one tab. Use them for a command the reader runs or a payload shape,
  not for pseudo-code that restates the function.
- **Lists** are lines beginning with two spaces, a hyphen, and a space. `gofmt` normalizes the
  marker and the indentation.
- **Headings** are `# Heading` at the start of a line. They earn their place in a long package
  comment and nowhere else.
- **Blank `//` lines** separate paragraphs. There is no `<p>`.

Since Go 1.19 `gofmt` reflows all of the above. If your formatting survives `gofmt` unchanged, it
was already canonical; if it does not, the formatter is right.

## 6a. When the comment ships as documentation

In a kubebuilder project a doc comment on an exported API-type field is not just a comment. It
becomes the `description` in the generated CRD, which reaches users through `kubectl explain`, ships
in the generated CRD manifests, and is copied into the Helm chart's CRD templates.

**The reader changes, and that is the whole section.** This comment is read by someone writing YAML
against an API. They cannot open the code, cannot follow a doc link, cannot find out what a name
refers to, and have no `git log`. Three rules follow, and they are about what the text says, not
about the build:

1. **Every reference has to be spelled out.** "See the controller" points nowhere. A doc link
   renders as literal brackets. A symbol name is a word they cannot look up. If the sentence names
   something, it has to define it in the same sentence or not name it at all.
2. **§4's vocabulary exception is wider here, and the criterion test is stricter.** A list of the
   values a field may hold, the reasons a condition may carry, the keys a map accepts: that list is
   the only source this reader has, so a criterion may replace it only when they can apply the
   criterion *without opening anything*. "Reason names the outcome for this kind of resource" fails
   that test: it is true, it is circular, and it leaves the reader with nothing. §4's own warning
   applies at full force: if the honest criterion is circular, the list was the answer, and the
   repair is to complete the list and verify every member against the code in the same edit.
3. **No markup.** Go doc comments have no inline code syntax, so backticks, `<p>`, and Markdown all
   reach the user as themselves, inside a YAML string. Write plain sentences.

Then, and only then, the mechanics: **editing one of these is not a comment-only change.**
Regenerate (`make manifests generate` in a stock kubebuilder project, plus whatever target syncs
the Helm chart's CRDs) and commit the result, or the drift check in CI fails. Plan it as its own
commit; mixing it with prose-only edits buries a two-line rewrite in sixteen files of generated
YAML.

Because every edit costs that diff, the bar rises, but it rises for **rewording**, not for
**enriching**, and this section does damage when the two are confused. A hyphen swapped for a dash,
a synonym, a smoother clause: each is churn that ships, and the diff is the argument against it. A
fact this description does not carry and its reader needs is worth the diff every time, even when
every sentence already there is true. "It is correct as written" settles the first case and not the
second, so when you decline an edit on cost grounds, say which one it is. A description that is
accurate and thin still sends someone to read the controller.

The same reasoning applies to any comment a generator turns into published output: an OpenAPI
description, a generated client, a flag's help text.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- a declaration whose name and types are the whole contract;
- a method that adds nothing to the interface's documented contract, beyond a single line that
  names the interface (§4);
- an unexported helper whose single call site makes it obvious;
- anything the code states better, which is most narration.

The corollary: an exported declaration with a non-obvious contract is not optional, however
self-evident the name looks to the person who just wrote it. Go's convention is that every exported
declaration has a doc comment; that convention buys nothing when the comment restates the name.

## 7a. Editing an existing comment

Most of the time you are rewriting a comment, not writing one. Different job, different failure
mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none takes one
away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry: a unit, a side effect, a nil rule, an invariant. Name that fact to
  yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **A near-empty before-version makes the budget vacuous, not permissive.** A one-line `Close
  implements io.Closer.`, a stub, or no comment at all carries no facts, so everything in front of
  you is growth and none of it has been paid. Judge it as a comment written from scratch: every
  sentence earns its slot under §2, and on an implementing method under §4's three cases. Where
  the branch under review wrote the paragraph an hour ago, its text carries no more authority than
  your own first draft.
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
- **Check every identifier the old comment names.** A comment written before a refactor cites
  constants, fields, and functions that no longer exist. Go will not tell you: an identifier in
  prose compiles, renders, and lies, and so does a doc link (§5). Grep each one. Convert what you
  verify into a doc link, so the next reader at least gets a hyperlink that visibly fails.
- **When you lift a rule into the type comment, cut it from the member.** The member keeps the one
  sentence that specializes the rule, plus the link. Two full statements of the same rule is the
  most common outcome of a good structural edit and the easiest to miss, because each of the two
  reads well on its own.
- **Deleting is an edit, and every cut is reported.** A list of callers, a rejected alternative, a
  cost estimate, a reference to the change that introduced the code: cutting these is usually the
  highest-value change in the diff, even though the result looks like less work. Delete sentence by
  sentence, and report each deleted sentence with the fact it carried and where that fact now
  lives: another declaration, the type comment, the commit message, or nowhere, with the reason. A
  rationale sentence stays only where a maintainer reading the rule would ask why or would be
  tempted to relax it; the test is whether the sentence would come up as a question in code review.
  A rewrite that reads better and says less is the failure this rule exists to prevent.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule
  governs the body, not the first sentence. A comment that opens with `This function is a wrapper
  around X` stays broken until someone rewrites it, and "I had no new fact to add" is not a reason
  to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot
  be verified as comment-only, and that verification makes a large sweep safe.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both
versions and have to establish what actually changed: reviewing someone else's edit, checking your
own before you commit it, or judging a machine-generated one.

The new version will read better. It was written second, by someone who had just finished
understanding the code, and a fact that vanished leaves no trace in the text that replaced it, so
reading forward confirms that impression and finds nothing. The work therefore runs backwards: read
the **old** version carefully first, and form the verdict last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one nil rule, one side effect, one ordering or concurrency
constraint, one lifecycle obligation, one named collaborator, one link target, or one stated
default. A topic sentence is not a fact, and neither is a restatement of the signature. What the
interface permits, and what another API does, is neither: it names nothing a caller of this method
relies on, so it takes a row as provenance and pays for no growth in step 3 (§6). Compare facts,
not sentences: at sentence granularity, merging two sentences looks like a loss and splitting one
looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Four
defenses hold:

- the fact was wrong, which includes a claim the old text made and the code does not support;
- the fact moved to the type or package comment, and you can point at the sentence that now carries
  it;
- the fact moved to the declaration itself: a named result, a renamed parameter, a sentinel error
  the signature now exposes;
- the fact was rationale, the contract it explained is stated completely without it, and the
  rationale no longer earns a slot under §2.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is the sentence someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first sentence repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification. Where the old version carried no fact (a one-line
`implements` comment, a stub, no comment at all), the budget measures nothing: judge every sentence
of the new version on whether it earns its slot under §2, and on an implementing method under §4's
three cases (§7a).

Two more exemptions, both from §7a. A stacked relative, an elliptical nominal opener, or a noun
pile unpacked into a finite clause is paid growth: the payment is the re-read it removes, and the
rewrite names the construction rather than a fact. And growth is not the only failure: a rewrite
that keeps the old version's density while changing its words has bought nothing and belongs in
step 5.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the tests, or to a contract it links to. **The old comment is
provenance, not evidence.** That it made the claim shows the claim was made, not that it holds, so a
claim carried over unchanged is checked like any other. A claim that traces to none of those sources
is invented, however plausible it sounds, and plausible is the dangerous case: a wrong invariant in
a doc comment is a wrong invariant a caller will build on, and an inherited one is worse, because
it has outlived every pass that did not check it. The commit message is not a source either. It
records what someone meant to do; the comment has to describe what the code does.

**An inference from the code is not the code.** A census of call sites establishes what is true
today, not why the code is the way it is. `No caller passes a negative value` supports `nothing
inside this package reaches the guard`, and supports nothing about who the guard is for. Design
intent traces to a comment, to a specification, or to the shape of the API itself, never to a count
of callers. This is §4's membership rule from the other end: a roll call of today's callers is not
a law about tomorrow's.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer
attention now and costs the next reader a `git blame` later. §7a has already settled that the old
wording stays; here you look for the places where it did not. In a file that regenerates (§6a) the
cost is higher, because the churn arrives with a YAML diff attached.

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

**7. Prove the code did not move.**

A sweep that edits comments across many files is reviewable only if the claim "comments only" is
mechanical rather than asserted. Parse each file before and after without comments and compare:

```go
fset := token.NewFileSet()
f, _ := parser.ParseFile(fset, path, src, 0) // no ParseComments: comments are dropped
printer.Fprint(&buf, fset, f)
```

Any difference means the pass touched code, and the pass is wrong until it is explained.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it makes two people comparing the same pair reach
the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and make it a doc link (§5) |
| Duplicated rule | Cut the copy the type comment now carries (§7a) |
| Churn | Restore the old wording |
| Density kept | Unpack the stacked relative, the elliptical opener, or the noun pile (§7a) |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Counterfactual | Cut the simulation; re-evaluate any rationale left standing under §2 |
| Unearned rationale | Cut the rationale; keep the complete contract (§2) |
| Interface provenance | Cut it; keep the resulting contract (§6) |
| Stale inline comment | Rewrite it from the code |
| Detached marker | Move it back into the declaration's comment group (§4) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Does the first sentence begin with the name of the declaration, or, for an API field, its JSON
  name?
- Does the first sentence stand alone, with no term this comment introduces, and does it terminate
  where you think it does, or does an `e.g.` cut it short?
- Could a reader reconstruct the first sentence from the declaration's name alone?
- In a regression test's comment: the rule first, the old defect in one past-tense sentence, and any
  equivalence with the old behavior kept (§1)?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Is any rationale here commit-message material?
- Any sentence describing a previous version of the code: `now`, `no longer`, `used to`?
- Any sentence describing a code path this code does not have: what would happen if the rule were
  broken, rather than what the code does about it?
- Does the comment explain another package's internals instead of naming it?
- Any positional reference: `below`, `above`, `the following`?
- Does a limit state what it bounds, rather than only what some neighboring limit bounds?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Any bare name that should be a doc link, and does every doc link still resolve?
- Does every parameter named in prose still exist, spelled that way?
- On a method that implements an interface: which of §4's three cases is it in, and does any
  sentence describe the interface's freedom rather than this method's rule?
- Does every term here have a definition outside this comment, and does every name match what the
  code calls the thing (`english-developer-style` §4a)?
- For each rationale sentence: would deleting just that sentence change what a caller may rely on,
  or leave a maintainer unable to see why a constraint is there? If not, delete it.
- Would deleting the whole comment lose anything?
- Is every `//go:`, `//nolint`, or `+kubebuilder` marker still in the comment group it needs to be
  in, worded exactly as it was?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the type or package comment?
- Any list that a criterion would replace, or that the reader's editor already answers? Can the set
  gain a member without anything forcing an edit here, and does a trailing `...` stand where no
  criterion precedes it?
- If the file generates output (§6a): did you regenerate, and is the edit worth the regeneration
  diff?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the facts were
already there. The second grows, because one was missing. Do not read either one as the target
shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a
sweeper can recognize in the wild is an example it will paste instead of derive, and a rewrite that
matches this file word for word proves nothing about whether the rules were applied.

### An inline comment that narrated the code's history

**Before**: the rule is in there, wrapped in an account of what changed.

```go
    // Reset the budget on success only. Failures used to reset it too, which meant
    // a flapping backend could never exhaust its retries; we now let the budget
    // drain and refill it only when a call actually goes through.
    if err == nil {
        budget.reset()
    }
```

**After**: the same rule, stated as what holds.

```go
    // The budget refills on success alone, so a flapping backend drains it instead
    // of holding it topped up.
    if err == nil {
        budget.reset()
    }
```

Fact ledger: *the budget resets only on success*, present. *A backend that keeps failing must be
able to exhaust it*, present, and now stated as a property of the code rather than as a change to
it. Nothing absent, one line shorter, and both `used to` and `we now` are gone.

### A set whose membership rule was missing

**Before**: names the set and stops. A reader deciding whether to add `409 Conflict` has nothing to
decide with, and the list will not tell them.

```go
// retryableStatus lists the HTTP statuses the client retries.
var retryableStatus = map[int]struct{}{
    http.StatusRequestTimeout:     {},
    http.StatusTooManyRequests:    {},
    http.StatusBadGateway:         {},
    http.StatusServiceUnavailable: {},
    http.StatusGatewayTimeout:     {},
}
```

**After**: states the criterion the five entries are an instance of.

```go
// retryableStatus holds the statuses where replaying the identical request can
// still succeed: the server refused the attempt rather than its content. A status
// that describes the request itself (400, 404, 409, 422) never belongs here,
// however transient its cause looks, because a retry sends the same request and
// receives the same status.
//
// [Client.Do] returns [ErrGivenUp] once the attempt budget is spent, whatever
// status ended the last try.
var retryableStatus = map[int]struct{}{ … }
```

The rewrite grew by six lines and paid for them with two facts the one-liner did not carry: the
criterion, which lets a reader classify a status the list has never heard of, and the sentinel a
caller matches when the retries run out. `409` earns its place in the exclusion list because it is
the case a reader gets wrong: it looks transient and is not.
