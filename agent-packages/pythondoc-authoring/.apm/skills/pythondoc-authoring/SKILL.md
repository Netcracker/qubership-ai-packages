---
name: pythondoc-authoring
description: >-
  Load before writing, editing, or reviewing a docstring or inline comment in Python: the docstring on a new or changed
  function or class, a `Raises:` or `Yields:` section for behavior that just changed, a docstring that ships as `--help`
  text or an OpenAPI description, a doctest the test run executes, the docstring on a test just added, a regression test
  that names the old defect, an override that departs from the inherited contract, a `#` comment beside a new check, a
  `# noqa` or `# type: ignore` line. In a coding task on a Python codebase ("fix the bug", "add the method") load it as
  soon as the change touches a docstring or comment, before writing it. Also load to decide whether an object needs a
  docstring at all, or to compare two versions of one. Governs what the docstring says and in which order: the one-line
  summary and its mood, contract before rationale, sections and references, when to write nothing, how far a rewrite may
  grow. Wording is english-developer-style's; load both.
---

# Authoring a Python docstring

This skill governs **what a docstring says and in what order**. Wording, tone, sentence length, and dialect belong to
`english-developer-style`: load it too, and defer to it on the prose. The two compose: this skill picks the slots; that
one writes the sentences.

Two facts about Python change the job at the root, and both come back in later sections.

**A docstring is a runtime object, not source text.** It is `__doc__`: `help()` renders it, `doctest` executes the
examples in it, a CLI framework can print it as `--help`, and `python -OO` deletes it. Every one of those is a surface
an edit reaches.

**No formatter owns its prose.** `black` and `ruff format` re-indent a docstring's body and strip its trailing
whitespace, but they never rewrap it (measured on ruff 0.14). You place the line breaks, and `E501` counts them.

Conventions carried in from another language's doc comments go wrong in three places, so do not translate them in your
head. The summary is one physical line whose mood the project picks, not a first sentence fixed in the third person
(§3). References have no syntax of their own, so the form depends on the renderer and nothing checks it by default (§5).
The section headings belong to a dialect the project has already chosen, not to the language (§6).

## 1. The correction that matters most

"Document the why, not the what" is half wrong for a docstring, and the wrong half does the damage.

An inline `#` comment documents the **why**; it sits next to code the reader can already see. A docstring documents the
**contract**: what a caller may rely on, what an implementer must guarantee, what holds before and after. That is a
*what* at the level of a promise, not a restatement of the code.

The failure mode is therefore not "explains what the code does". It is one of these:

- **Narrating the implementation.** `Loops over the rows and adds each to the index.` The body already states it, and
  the docstring becomes false on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the retry logic every client copied.` That belongs in
  the commit message and the pull request description. A docstring's reader has to *use* or *fix* the thing, not decide
  whether to merge it.
- **Restating the annotations**, which is Python's own. `Args: timeout (float): the timeout in seconds.` on
  `def fetch(timeout: float)` carries one fact, the unit, and pays for it with a line the reader has to sift. The
  annotations are the signature; §6 says what a parameter line has to add before it earns its place.

**The test is the refactor, not the reader.** Rewrite the body so it behaves identically and reads differently: a loop
becomes a comprehension, a helper is inlined, an attribute is renamed. Every sentence you would then have to edit was
implementation, whatever it sounded like. This is the operative rule, because it settles cases that "specification, not
details" argues about forever, and it does not soften with visibility: a `_private` function's docstring goes stale on
that refactor exactly as a public one's does, and the cost of a docstring that lies is the same either way.

**The caller substitutes too, and catches what the refactor cannot.** Imagine a new legitimate caller supplying the same
argument for a different reason. A sentence that then describes only the old call path is caller context, not this
function's contract. `A negative size is refused before any byte is read` survives the substitution; `because a size
taken from a length the server declared can be negative` does not.

Cutting is not the whole repair, because the rationale slot can be open and merely filled wrong. Where a value came from
does not explain why the function behaves as it does; a local reason, where one exists, is a property of this function's
own contract. Look for the local reason before concluding that the slot was never open, then ask §2's question of it:
does the rule look arbitrary without it, or would a maintainer relax it incorrectly? A reason any reader would have
assumed fails that question and stays out, however true it is.

Provenance crosses into a callee's docstring where it is that function's own contract: a protocol method whose parameter
*is* the declared length minus the header documents its own layer rather than borrowing the one above it. **State the
local rule at the lowest-level API, and the scenario at the layer where the scenario exists.** A guard found through one
concrete call path does not carry that path's scenario.

**Sufficiency** scales with visibility: how much the docstring may leave to the code beside it. Python marks visibility
by convention rather than by keyword: a name listed in `__all__` or spelled without a leading underscore is public, and
a `_name` is private (PEP 8).

| Where | What the docstring must carry |
| --- | --- |
| public name | Complete without the code. A subclasser is a caller, so a method written to be overridden is public API here (§6a) |
| `_private` name | May be elliptical and lean on the body beside it. Often there is no contract distinct from the implementation at all, and §7's "the name and annotations are the whole contract" usually applies |
| inline `#` | Nothing about the contract. The reader has the code |

For an inline comment the bar is negative: **a competent reader is looking at this code and understanding it correctly;
write the comment only where they would not.** A reason that surprises, a bound that looks arbitrary, an order that
looks swappable, a branch that looks dead. Where their expectation and the code agree, the comment is noise, and later
stale noise.

A further failure, specific to a codebase that has been refactored, is **narrating the code's history**. `The session
now returns a copy, so callers can no longer mutate the cached row` describes a transition between two versions, and the
reader has only this one. Rewrite it as the state that holds: what the session returns, and what the caller may do with
it.

One exception. **The docstring on a regression test may tell history, and an equivalence is not history.** The defect is
what the test guards, so it belongs in the docstring: state the rule the test asserts first, then the defect in one
past-tense sentence with the exception class: `A negative count used to be reported as available, and the caller then
failed with IndexError.` A docstring that opens with the defect makes the reader reconstruct the broken version to
understand the fixed one (measured on one branch: a blind reader ranked the version that opened with `used to` fourth of
five on that ground alone). Do not narrate the old mechanism in the present tense, and do not recast it as a chain of
`would` clauses. History narration, which this section forbids, is a sentence whose only content is that the code
changed. A sentence that argues the new behavior is safe **because it is identical to the old one** is rationale, and
the old behavior is its comparison term. Keep the comparison; it is the whole argument.

- *Keep:* `a reader that has not yet observed the write behaves exactly as every reader did before this attribute was
  added: it reads from the buffer and the wrapped stream as if nothing were closed`
- *Wrong repair:* `a reader on another thread may not observe the write and may still read from the buffer` (the
  equivalence, which is the reason the unsynchronized attribute is safe, is gone)

The last failure is the mirror image of history narration: **narrating the branch that does not exist**, what the code
would do on an input it refuses, or under a rule it does not implement. History narration gives the reader a past
version of the code; this gives them a version that never existed. `If uppercase names were allowed, the label built
from this name would be rejected downstream and the deployment would never start` describes a path no build of this code
can take. No refactor can make it false and no reader can check it, so it survives every review.

This does not ban consequences. What the code does when the contract is broken (which exception, which return value,
what state the object is left in) is contract, and the `Raises:` section or `:raises:` field (§6) carries it. Cut the
simulation of the branch the guard prevents.

**The test: could a reader falsify the sentence by reading this repository?**

- `Raises ValueError when the name contains an uppercase letter`: contract. It names a path this code has.
- `The name becomes a Kubernetes label, and a label admits no uppercase letter`: eligible. It names the *source* of the
  constraint, the shape rationale takes when it earns a slot at all. It still has to earn it.
- `Otherwise the deployment would be rejected and never start`: cut. Nothing here produces that, and the system that
  would is one the reader cannot see and you do not control.

**Where the reason belongs in the docstring at all, name the source of the constraint rather than the disaster it
averts.** Cutting a counterfactual obliges you to put nothing in its place. §2 fills the empty rationale slot only where
the rule would otherwise look arbitrary or be easy to change incorrectly, never merely because a source exists and is
true.

A source the reader cannot infer from the code is the likeliest to earn its sentence, but reachability is evidence, not
the test. `The size must be a power of two because indexing masks with size - 1` earns its place with the masking five
lines below: the restriction looks arbitrary without it and the next maintainer will relax it. `RFC 1234 permits three
encodings` earns nothing when no caller needs to know why this one was chosen.

Where the constraint is *enforced*, an earned sentence belongs inline beside the guard: the reader sees the `raise` and
cannot see why the value is unacceptable. Where the constraint is only *stated*, in a docstring, ask the question again
from scratch. Completeness does not settle it: a contract states itself completely by definition, so `the sections
already say what happens` closes nothing. The test stays the same: would the rule look arbitrary, and is it easy to
change incorrectly?

A function with more than one failure channel, a raised exception beside a sentinel `None` return, does not escape that
test. The `Raises:` and `Returns:` sections state each outcome, and a maintainer reading them is expected to keep them
apart. A sentence explaining why an invalid argument raises rather than returning `None` is the reason any reader would
have assumed (measured: a maintainer who met such a sentence in review called it common sense). Leave it out.

## 2. The four slots

A docstring has at most four slots, in this order.

| # | Slot | Answers | Skip when |
| --- | ------ | --------- | ----------- |
| 1 | **Summary** | What is this, or when does it fire? | Never; always present |
| 2 | **Contract** | What may a caller rely on? What must an implementer guarantee? | The signature genuinely says all of it |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader do next? | The contract already implies the action |

Two rules govern the order.

**Contract before mechanism.** State the rule the reader must satisfy before the machinery that enforces it, and before
what some *other* module does. A docstring that opens with a neighboring class forces the reader to reconstruct the rule
from negative examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first slot to cut, not the last. A reader who knows the
rule and not the reason can still write correct code; the reverse is false.

**Removing a bad explanation does not create an obligation to replace it.** A rationale slot emptied by a cut stays
empty until the finished contract, read on its own, turns out to need one. Start from the contract, not from the gap.

**Make the obligated party the subject.** Obligations come in two shapes. A *stated* obligation carries a *must*, *has
to*, *may not*, or *should*, and whoever has to comply belongs in the subject: not the thing acted on (`The lock must be
released before returning`, which names no one and lets `it` drift to the reader by the next clause), not the act
(`reopening the session must not be reachable after close`), and not an object that merely performs the act for someone
else (`close must still run` obliges the caller). A named object in the subject is right only where that object is
itself what must comply: `close must be safe to call twice`. The party need not be human, but it must act: the caller,
the loop, a subclass. An enum member or a configured limit complies with nothing.

The summary line is exempt. PEP 257 fixes it as an imperative (`Return the decoded payload.`), which addresses the
reader directly and so already names the party. The rule applies to the body, where an obligation stated without a
subject is easy to write and impossible to act on.

A *census* is a rule for the next maintainer, written instead as a report on today's call sites: `Called from __aexit__
once the transport is idle`, `connect is the only caller`. It is flat indicative with no modal, so test it: **if a
second such caller appeared tomorrow, would this paragraph tell it that it is obliged?** Judge the paragraph, not the
sentence; an example may follow a law that is already correctly stated. Write the law, not the roll call.

Watch the intransitive modal, where the party hides best: `every codec has to appear in _REGISTRY`, `an unknown value
must fall back to Mode.FAIL`. Nothing appears or falls back on its own; name what does it.

Out of reach of this rule: an imperative in the body, which already addresses the reader (`Call this before the first
await`), including one that carries rationale (`so mirror the asyncio behavior here`); a constraint on a *value* (`must
be ≤ sys.maxsize`), which bounds a number rather than behavior; a docstring naming who writes or reads an attribute,
which is the membership rule §4 calls for; and a `#` comment whose next statement is the actor (`# Buffer must be
drained` above the `drain()` that drains it), after checking that the next line really is the actor and not test setup
standing between the comment and the call it constrains.

Most objects need slots 1 and 2 only. A property needs slot 1. Do not manufacture the other slots to fill a template; an
absent slot is not a gap, and a `Returns:` section that repeats the summary is the commonest way one gets manufactured.

**Size the docstring to the object.** A docstring longer than the function it documents is not automatically wrong (an
invariant can be worth ten lines over a three-line method), but it is a signal to re-read. When you check, the surplus
is almost always rationale: keep at most two sentences of it, and only for the part a reader would otherwise get wrong.
The rest belongs in the commit message. As a working size, a test module's docstring is two to five sentences and a
function's docstring fits in one glance; past that you are describing the investigation, not the contract, so keep the
rule and the exception and move the rest.

## 3. The first line

PEP 257 puts the summary on **one physical line**, ending in a period, and the linters enforce that shape: `D200`,
`D205`, `D400`, and `D415` between them require a one-line summary, a period, and a blank line before the body. So the
length limit is not advice. A summary that does not fit on one line inside the project's line budget is doing too much.

Whether that line sits beside the opening quotes or on the line below is the project's business. Ruff's `D212` and
`D213` take opposite sides and cannot both be on; the `google` convention selects `D212`, and `numpy` and `pep257`
select neither (measured on ruff 0.14).

### The mood is a project decision, not yours

Python's two most-cited guides contradict each other here, and both are live:

- **PEP 257** prescribes the imperative: `Return the rows matching the query.` Not `Returns…`.
- **Google's Python style guide** prescribes the descriptive third person: `Returns the rows matching the query.`

Tooling takes sides. Ruff's `D401` flags a descriptive summary under the default `pep257` convention, and
`convention = "google"` switches `D401` off (measured on ruff 0.14, where the same `Fetches rows from a table.`
docstring fails under `pep257` and passes under `google`).

Decide in this order, and never mix moods inside a project:

1. the `convention` in `pyproject.toml` (`[tool.ruff.lint.pydocstyle]`, `[tool.pydocstyle]`), if there is one;
2. the docstrings already in the file, if they agree with each other;
3. PEP 257's imperative, which is both the language's own document and pydocstyle's default.

### The rest of the summary rule

- **No term this docstring invents.** `Guards the inventory of backend messages` fails, because "inventory" means
  nothing until the body defines it, and the summary must be readable by someone who never reads the body, which is
  what `help()` and an API index show them. The repair is rarely to define the term earlier: the field almost always
  has a word already, and `english-developer-style` §4a gives the test for telling a defined term from a coinage.
- **No self-description.** Drop `This function…`, `Helper that…`, `Utility for…`. Start with the verb.
- **One sentence.** If it takes two, the first one is not the summary.
- **A property, an attribute, or a constant is a noun phrase, with its unit.** `Largest encrypted packet this stream
  accepts, in bytes.` A property is documented as the value it exposes, not as the method that computes it. The reason
  the bound has that value is slot 3, however interesting it is.
- **A qualifier is not a summary.** `Internal.`, `Deprecated.`, `Default.` as the opening line fills the index with a
  word that states nothing about what the object does. Put the qualifier after the summary: `Rejects a frame over its
  ceiling and closes the connection. This is the default.`
- **A first sentence a reader could reconstruct from the identifier carries nothing.** A test named
  `test_failing_output_close_still_closes_input_and_socket` does not need `"""Check that a failing output close still
  closes the input and the socket."""`; the report prints the name. Where the name states what the test establishes,
  the docstring carries the reason, the construction the reader would not guess, or nothing. For an attribute or a
  property the same rule leads to §7: where the name and the annotation are the whole contract, write no docstring.

### The first-statement rule, and three ways to lose the docstring

A docstring is the **first statement** of a module, class, or function. Nothing warns when it stops being one:

- **An f-string is not a docstring.** `f"""Fetch {name}."""` in the docstring position leaves `__doc__` as `None`
  (measured on CPython 3.9 and 3.13). Interpolate nothing; a docstring is a constant.
- **Anything above it demotes it.** A comment is fine, because comments are not statements, but an assignment, an
  import, or a `from __future__ import annotations` above the docstring means the module has no docstring at all. The
  future import goes *after* it.
- **`python -OO` deletes every docstring in the process.** Never make a program depend on one: a CLI whose `--help`
  comes from `__doc__` prints nothing under `-OO`, and `inspect.getdoc` returns `None` where it would otherwise have
  inherited a parent's text.

One more mechanical trap: a docstring containing a backslash needs a raw string, opened with `r"""`. Without it,
`"""Match \d+."""` raises `SyntaxWarning: invalid escape sequence '\d'` on Python 3.12 and later. Regexes, Windows
paths, and LaTeX in a NumPy-style docstring are the usual cases.

## 4. Genre notes

### Module

First statement of the file, before the imports. It is the entry point: what the module is for, which objects are the
way in, which are private, and any rule that holds across the file (naming, concurrency, error conventions). A
hand-written list of the module's own functions is the membership list all over again; `__all__` and the generated API
page both answer it better.

A module that is also a script documents the invocation: what it does, its arguments, its environment variables, its
exit codes. There the vocabulary exception below applies in full.

### Package (`__init__.py`)

One docstring for the package, in `__init__.py`: what the package is for, which submodule a reader starts with, and
which are internal. Do not restate each submodule's own docstring; the reader who needs that detail is one import away
from it.

### Class

The class docstring carries the **invariant that spans the attributes and methods**. Method docstrings specialize it and
do not carry it; a rule stated only on a private attribute is a rule the class docstring is missing.

Name the collaborators the class is useless without, the concurrency model if there is one, and the lifecycle if an
instance is not usable straight after construction. Do not explain how a collaborator works internally; reference it and
let its own docstring do that job.

**Constructor arguments go in one place, and the project picks which.** The class docstring or `__init__`, never both:
Sphinx's `autoclass_content` and mkdocstrings' `merge_init_into_class` each decide which one reaches the rendered page,
so the copy in the other place is invisible there and stale everywhere. Follow the file.

A dataclass, an attrs class, or a Pydantic model documents its fields where the project already does: an `Attributes:`
section, or an attribute docstring under each field (see below). Picking the second style for one model in a package
that uses the first produces a page with half its fields described.

### The membership rule, not the membership list

A docstring that lists the members of a set (every exception a call may raise, every function that writes an attribute,
every caller that must be updated) has transcribed a query. The list is stale from the first refactor, and a reader who
does not find their case in it concludes the wrong thing.

State the criterion instead: *every other check rejects a value no conforming client can send* beats an eight-item list
of those checks, because the reader can classify a check the list has never heard of. The criterion has to let the
reader name a member: "the limits whose error message offers this as a remedy" is true by construction and states
nothing the reader could not have inferred. Where the honest criterion is circular, the list was the answer.

Two exceptions. A set the code itself declares (an `__all__`, a `match` a reader must keep exhaustive, a test that
partitions an `Enum`) fails the build or the test when it drifts, so there the list **is** the contract. And a list the
reader needs as vocabulary (the environment variables a command reads, the keys a payload may hold) stays, because the
criterion alone lets nobody write code. What goes in that case is the rot: the version label that freezes the list, and
the per-item annotations nobody maintained.

**One question decides it: can this set gain a member without anything forcing someone to edit this docstring?** If it
can, write the criterion; no build, test, or review will report the stale list. If it cannot, because a test or a type
checker fails the moment the set changes, the list is the contract and belongs here. The question is not about size (a
three-item list nobody maintains rots faster than a twenty-item one the test suite keeps honest) and not about origin in
a standard (standards grow: PostgreSQL adds message types, TLS adds versions). A *closed* set is safe, and an exhaustive
`match` checked by the type checker detects exactly that.

**A trailing `...` admits the list is incomplete, and where it belongs depends on what precedes it.** After a stated
criterion it is fine, because the items are illustration: *every wire-compatible backend shares it (CockroachDB,
YugabyteDB, Redshift, ...)* loses nothing if the reader has never heard of the fourth. Where the list is itself the
claim, *raised by the higher layers (auth, cancel-key, startup negotiation, ...)* reports that more members exist and
gives no way to name one, so it is neither a list nor a rule. Supply the criterion, or finish the list and accept the
maintenance.

The vocabulary exception is wider for a docstring that ships as documentation (§6a), because that reader cannot open
the code to enumerate the set themselves. It is not unlimited: an incomplete list shipped as documentation is worse than
no list, so if you keep one, verify every member against the code in the same edit.

### Function and method

Slot 2 carries the work. State these, and only where the signature and its annotations do not already:

- what a `None` return means, and whether a returned container is a live view of internal state or a copy the caller
  owns;
- whether an argument is mutated, and whether the callee keeps a reference to it after returning;
- units, ranges, encodings, time bases (`seconds`, `UTF-8 bytes`, `0-based`), and `bytes` versus `str` where the
  annotation is `str | bytes`;
- side effects the name does not advertise, including I/O, global state, and anything that happens at import time;
- **laziness**, which annotations hide: a function returning `Iterator[Row]` may have done nothing yet, may be
  single-pass, and may hold a connection open until it is exhausted;
- idempotence, thread-safety, and ordering guarantees;
- whether the call blocks, whether an `async def` blocks the event loop anyway, and what canceling the task does;
- resource obligations: what the caller must close, and whether the object is meant to be used as a context manager;
- which exceptions a caller is expected to catch; nothing in Python declares them, so the docstring is the only record
  (§6).

Every item on that list is a property of the value. Where the caller got the value is the caller's sentence: `the
caller computes this from the message header` describes one call path and ages the day a second one appears (§1).

Either name a parameter in prose, spelled exactly as in the signature, at the point where its contract matters (`body is
encoded as JSON when it is not None`), or use the project's section dialect (§6). Do not walk the parameter list in
order restating annotations; that is the signature, transcribed.

A function whose contract is exhausted by its name and annotations needs one line or nothing.

### Generator, coroutine, and context manager

Three contracts the signature will not carry. A generator says whether it is single-pass, what closing it early does,
and what it holds open while suspended. A coroutine says what cancellation leaves behind: a half-written file, an open
connection, a released lock. A context manager says what `__exit__` does with an exception: suppress it, roll back, or
let it through.

### Override

A subclass method that overrides a base method, or implements an abstract one, has the inherited docstring beside it
only where a tool puts it there, and the tools differ. Python copies nothing: the override's own `__doc__` is `None`
until you write one. `inspect.getdoc` walks the MRO and returns the base
method's text, and `help()` prints that text under the override's own signature (measured on CPython 3.9, 3.12, and
3.13 for a class defined at module level; for a class defined inside a function the walk finds nothing and both return
`None`). Sphinx documents `autodoc_inherit_docstrings` as on by default, so an override with no docstring gets the base
docstring on the generated page. Write your docstring as the delta from the inherited text, and nothing else; a reader
whose tool shows no inherited text follows the class to the base.

Three cases, and the inherited contract decides which one you are in. Read it before you write.

1. **The override obeys the inherited contract.** Write no docstring. `"""See base class."""` is not a substitute: it
   replaces the inherited text with four words wherever `inspect.getdoc` is the reader (§7), and pydocstyle's
   documentation lists `D102` as satisfied by any docstring, so the stub silences the rule while carrying nothing.
2. **The inherited contract leaves the behavior open, and this class picks one.** State the resulting contract as a
   rule of this class, in one positive sentence: `A size of zero or less reads nothing and returns b"".` The inherited
   freedom is not news, and a sentence spent on it is provenance (§6). The same holds where the override narrows what
   the caller gets: `Returns an empty list rather than None.` A different result from the base class's *own
   implementation* is this case too, not the next one: `io.IOBase.seekable()` returns `False`, and a stream that
   supports random access overrides it with `Returns True; seek() and tell() are supported.` without naming the base
   class.
3. **The override breaks the inherited contract.** A caller holding a base-class reference is about to be wrong, so the
   deviation is the reason this docstring exists. Name it in the base class's own terms, with the condition it happens
   under. Check first whether the contract really forbids the behavior: a contract that says *may* permits it, and case
   2 applies. A deviation is also a defect report, so raise it rather than only documenting it.

An implementation of an `@abstractmethod` is the same three cases, with the contract on the abstract method's
docstring; `inspect.getdoc` reaches it from the implementation the same way (measured on the same versions).

The mechanism that forced the choice is rationale and earns its slot under §2. `The read position indexes the buffer
that getbuffer() returns` explains why a negative size cannot be honored, and it stays only where a maintainer would
otherwise relax the rule; a rule that matches what the base class itself does looks arbitrary to nobody.

### Attribute, property, and constant

Document the unit, the range, the sentinel, and who may write it. A module-level constant whose invariant is non-obvious
needs that invariant spelled out; a reader adding a value has no other source of truth.

An **attribute docstring**, a bare string literal on the line after an assignment, is read by Sphinx autodoc, by
mkdocstrings, and by Pydantic when `use_attribute_docstrings` is on. The interpreter is not among them: a variable has
no `__doc__`, so `help()` and `inspect.getdoc` never show it. Use it where the project's renderer reads it, and do not
expect it at runtime.

A block of related constants takes one docstring above the block and short ones inside it, not the same sentence eight
times.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence, positively, and before any neighboring
limit comes up: `This ceiling bounds only what the server sends.` A docstring that leaves the scope to be inferred from
a contrast (`…which governs the direction this ceiling does not`) makes the reader subtract one limit from another and
reconstruct the missing verb. Both halves are facts; state them separately, this one first.

A constant whose value is a size or a duration states both forms: `1 MiB (1048576 bytes)`. The docstring text carries
the digits by hand: nothing in Python substitutes the constant's value into its own docstring, so check the digits on
every edit to the constant. A generated page may show the value beside the text (Sphinx documents `autodata` as
rendering it), and that does not update the digits in the docstring. The unit has to be exact (`64000000` is `64 MB`,
not `64 MiB`) or hedged in words: `about 1 GiB (1073741823 bytes)`. The form is `english-developer-style` §5.

### Exception class

Document the situation that raises it and the attributes a handler reads off it: `Raised when the broker rejects the
frame; code carries the broker's reason.` is the whole job. A subclass that adds no attribute and no new situation needs
no docstring; the base class's arrives through `inspect.getdoc` (§7).

### Inline comment

An inline comment states why this line, for a reader who can already see the line. PEP 8 owns the shape: `#` then one
space, and at least two spaces before an inline `#` on a statement line. Four failure modes beyond narration:

- **Meta-commentary.** `…so check the flag first instead` describes what the comment is doing. State the fact: `the
  flag is the only signal that survives a reconnect.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` mark it.
- **Counterfactual.** See §1. `if … were`, `would`, `otherwise the` mark it. Name the source of the constraint; do not
  simulate the branch the guard prevents.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason a value is coerced
  to `int` belongs at the coercion; repeating it inside the branch that rejects a negative value splits one thought
  across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`# type:` and `# type: ignore[…]`; `# noqa: …`; `# pragma: no cover`; `# fmt: off` and `# fmt: on`; `# isort: skip` and
`# isort: off`; `# pylint: disable=…`; `# mypy: …` and `# ruff: noqa` file directives; `# doctest: +ELLIPSIS` and its
siblings; the shebang and any `# -*- coding: -*-` line; `TODO` and `FIXME` markers; anything citing an issue or a URL.

Three Python-specific hazards when you restructure a file that contains them:

- **A file-wide `# type: ignore` must precede every statement, including the module docstring.** Measured on mypy 1.18:
  with `# type: ignore` on line 1 the file is silenced; insert a module docstring above it and mypy reports the file's
  errors again. Nothing warns. If a file needs both, the ignore comes first and the docstring follows it, or use a
  `# mypy: ignore-errors` comment, which is not position-sensitive in the same way.
- **`# noqa` and `# type: ignore` are scoped to their physical line.** Rewrapping a call across two lines, or splitting
  one statement into two, moves the suppression off the line that needed it and onto one that did not.
- **`# fmt: off` and `# fmt: on` come in pairs.** Delete or move one half and the suppressed region runs to the end of
  the file, or ends where nobody intended.

### Test file

A test is read in exactly one situation: it just went red. Write for that reader.

pytest's progress line and its short summary print the node id and nothing else, so **the test's name is its summary**:
`test_retry_preserves_caller_headers`, not `test_headers_2`. The docstring still has a reader: pytest prints the failing
function's source in the traceback, docstring included, so it is the first prose the reader meets after the assertion.

- **Docstring = the rule the test guards**, stated positively and completely, as something you could assert. `It has to
  stay quiet when the socket did go away` leaves the reader guessing: not raise, not close twice, not log? Name the
  observable. If you cannot phrase the rule as an observation, the test probably cannot check it either.
- **Use = what to do about the red build.** Which fixture to look at, which case to add, where the assertion message
  states the rest.
- **A `pytest.mark.parametrize` `ids=` entry is a comment.** It is the string the reader sees in the node id, so it
  names the case's condition, not its ordinal.
- **An assertion message is read before either.** Put the observable there; the docstring carries the rule behind it.

Deliberate duplication between the test's docstring, a fixture's docstring, and the assertion message is correct,
because each reader meets exactly one of the three. It does not extend to production code, where the class docstring and
the method docstring have the same reader.

**A failing test should read as a bug report, and four things write it.** Decide what each one carries before you write
the next; the reader sees them together in one report.

- **The module and class name** carry what every test in them shares: the unit under test and the condition they all
  sit under. pytest prints them as the prefix of the node id (`test_stream.py::TestEnsureBytes::`), so a fact true of
  every test belongs there rather than in each of them.
- **The function name** states what this one test establishes. `test_negative_count_is_refused` is a finding;
  `test_ensure_bytes` is a location that makes the reader open the file. One assertion per test keeps the name able to
  do this, and keeps the report readable when several tests fail at once.
- **The assertion prints the values.** pytest rewrites a bare `assert actual == expected` to print both operands
  (`assert -1 == 0`) and, where an operand is a call, the call that produced it; `assert ok` on a boolean computed one
  line earlier prints `assert False` and nothing else, and `pytest.fail()` with no reason prints `Failed` (measured on
  pytest 8.4.2). `pytest.raises(ValueError)` names the expected type the same way. Choose the assertion that already
  prints what the reader needs, rather than describing it in the message.
- **The message adds what the other three cannot.** Under a bare `assert ok` it is the invariant, because nothing else
  states it. In a parametrized test the `ids=` entry already sits in the node id, so the message does not repeat the
  parameter; where the class or function name states the scenario, do not restate that either. A message read while
  someone scans a traceback competes with the lines around it.

This does not contradict the duplication paragraph above. A name is printed in the report; a docstring is read only once
someone opens the file. Repeating a docstring's rule in a message is the useful duplication; repeating a name is the one
that costs.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` are invisible in a rendered
page, silently wrong after a reorder, and unchecked by any tool. Name the object instead.

Python has no cross-reference syntax of its own. The renderer supplies one, so **find out which renderer the project
uses before you write a reference**:

- **Sphinx**: RST, and Google or NumPy sections through napoleon. A role such as `:func:`, `:meth:`, `:class:`,
  `:attr:`, `:mod:`, `:exc:`, or `:data:`, followed by the target in single backticks. A leading `~` shortens the
  displayed name to its last segment.
- **mkdocstrings**, on MkDocs: `[Client.send][pkg.client.Client.send]`.
- **No renderer at all**: read in an editor and through `help()`, where backticks are backticks and a role is a pair of
  stray colons in front of them.

**Nothing checks any of them by default.** Sphinx reports an unresolved reference only in nitpicky mode (`-n`, or
`nitpicky = True`), which many projects never switch on, and a docstring nobody renders is checked by nobody at all. A
role pointing at a method that was renamed two releases ago renders as unlinked text, and no build goes red. The
verification burden of §7a sits entirely on you.

Use a cross-reference for something the reader may want to follow. For an identifier they will not navigate to (a JSON
key, a literal, a shell command, a symbol in a service you do not import) plain text is correct. Set off a longer
snippet as a code block in the project's markup.

**An issue or PR number is an address, not a definition.** Name the phenomenon in the comment, then give the number so a
reader can find the history: `a length taken straight from the wire sizes the allocation (issue #4015)`. The number
must not carry the meaning: `the shape of issue #4015`, `the same format as #1231`, `the bug #4015 fixed` count as
content for someone who already knows the ticket and as nothing for everyone else. The test: cover the number and read
the sentence. If what remains states no fact, the comment has none. A bare `see #4015` fails the same test from the
other end, and a rendered Sphinx page reaches readers with no access to the tracker at all.

The number may open the sentence, as long as the phenomenon arrives in the same one. `The scenario from issue #4015: a
field claiming more bytes than the row envelope still holds` passes, because covering the number leaves the failure
named. The rule is about the number's role, not its position.

The same holds for a commit hash, a mailing-list thread, or a released version. It does **not** hold for a normative
source (an RFC, a protocol specification, a vendor's published documentation), which may define a format the comment
then need not restate.

**A ticket number is not a name.** `a #4015 hardening check` names nothing, and the check has a name in the code. Use
that name, and cite the number once, where the history belongs.

## 6. Sections

Python has three **section dialects**, and a project holds exactly one:

| Dialect | Parameter section | Parsed by |
| --- | --- | --- |
| reStructuredText / Sphinx | `:param body:` … `:raises ValueError:` | Sphinx, natively |
| Google | `Args:` … `Raises:` | napoleon, mkdocstrings, ruff |
| NumPy | `Parameters` under a `----------` rule | napoleon, numpydoc, ruff |

This section exists to prevent mixing them, and the mixing is silent: an `Args:` header in a Sphinx-only project renders
as an ordinary paragraph with a colon, and nobody's build goes red. Ruff enforces one dialect through `convention` in
`[tool.ruff.lint.pydocstyle]`; set it, and the linter enforces it from then on. Section names are a fixed vocabulary in
every dialect: `Arg:` for `Args:` silently becomes prose.

Whichever dialect the project uses, the content rules are the same:

- **A parameter line earns its place by adding what the annotation lacks**: a unit, a range, a `None` rule, a
  condition, an ownership statement. `timeout (float): the timeout` is noise, and a lint rule that demands one line per
  parameter produces noise at scale; report that rather than filling it in.
- **Do not restate the type.** The annotation is the type. A `(float)` beside `timeout: float` is a second copy that a
  signature change desynchronizes, and Sphinx's `autodoc_typehints` prints the annotation for you.
- **`Returns:` is skippable when the summary already said it.** Google's own guide allows omitting the section when the
  summary describes the return value. Keep it when the return is a tuple, a sentinel, or a container whose ownership
  needs a sentence.
- **`Raises:` is the only record a caller has.** No annotation carries it and no checker derives it. List the exceptions
  a caller can act on, not every one that could escape; a `KeyError` from a misspelled config key is a bug report, not a
  contract.
- **`Yields:` for a generator**, and it is the place to say single-pass (§4).
- **What the base class permits is not a fact of this method's contract**, and it pays for nothing under §7a: `the
  base class allows None here, but this implementation never returns it` spends a sentence on the provenance of a
  guarantee the caller already has. Which case an override is in, and what its body may say, is §4's *Override* genre.
- **A docstring you write on an override replaces the inherited one whole; it does not add to it.** `inspect.getdoc`
  returns the base docstring only when the override has none, so a section written on the override to state one special
  case (a `Raises:` entry for the one new exception) leaves the reader with no `Args:` and none of the base's other
  `Raises:` entries (measured on CPython 3.9, 3.12, and 3.13: an override whose docstring is `"""See base class."""`
  returns exactly those words). Sphinx documents `autodoc_inherit_docstrings` as copying the base text only into an
  override that has none, so the page behaves the same way. Neither the standard library nor Sphinx has a marker that
  splices the inherited sections back in (a third-party docstring-inheritance package may). Either write no docstring
  (§4, case 1), or write the complete contract this method has, sections included. Judge it by the complete docstring
  the reader ends up with, not by the sentence you added.
- **Deprecation has a machine-readable form, and prose is not it.** `warnings.warn(…, DeprecationWarning, stacklevel=2)`
  reaches the caller at run time, and `@deprecated` (PEP 702, `typing_extensions` or `typing` on 3.13+) reaches them in
  a type checker. A line that only says "deprecated" in the docstring is read by nobody who has not already opened it.
  Whichever you use, name the replacement.
- **An `Examples:` block with `>>>` in it is executable.** `doctest` and `pytest --doctest-modules` run it, so editing
  the prompt, the expected output, or a `# doctest:` directive is a test change. Run the doctests after the edit.

Markup belongs to the renderer, not to the docstring: RST directives in a Markdown-rendered project and Markdown in a
Sphinx one both arrive as literal characters.

## 6a. When the docstring ships as documentation

Python has several of these surfaces, and they are easy to miss because the docstring looks like an ordinary comment in
the file:

- a CLI framework prints a command function's docstring as its `--help` text (Click, Typer), and an `argparse` parser
  is conventionally built with `description=__doc__`;
- FastAPI turns a path operation's docstring into the OpenAPI `description`, which Swagger UI renders as Markdown;
- a published package's API pages, on Read the Docs or GitHub Pages, are its docstrings;
- `help()` at an interactive prompt.

**The reader changes, and that is the whole section.** They work against your interface from the outside: they cannot
open the code, cannot follow a cross-reference, cannot find out what a name refers to, and have no `git log`. Three
rules follow, and they are about what the text says, not about the build.

1. **Every reference has to be spelled out.** "See the client" points nowhere. A Sphinx role reaches a `--help` string
   as its own raw colons and backticks. If the sentence names something, it has to define it in the same sentence or
   not name it at all.
2. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a parameter accepts, the
   keys a payload may hold: that list is the only source this reader has, so a criterion may replace it only when the
   reader can apply the criterion *without opening anything*. §4's own warning applies at full force: if the honest
   criterion is circular, the list was the answer, and the repair is to complete it and verify every member against the
   code in the same edit.
3. **Write for the markup the surface actually renders.** Swagger renders Markdown; a terminal renders nothing; Sphinx
   renders RST. The same docstring reaching two of them has to be plain enough for the poorer one.

Then the mechanics. Where the generated output is committed (an OpenAPI spec in the repository, a generated client, a
`--help` snapshot test), editing the docstring is not a comment-only change: regenerate and commit the result, or the
drift check fails. Because every edit costs that diff, the bar rises, but it rises for **rewording**, not for
**enriching**, and the two are easy to confuse. A synonym or a smoother clause is churn that ships. A fact the
description does not carry and its reader needs is worth the diff every time, even when every sentence already there is
true. "It is correct as written" settles the first case and not the second.

One Python-only caveat for this section: every surface above reads `__doc__`, and `python -OO` deletes it (§3). A blank
`--help` under `-OO` is a curiosity, because almost nobody starts a CLI that way. A docstring your code *parses* (for
defaults, for a schema, for a routing table) is a program that stops working under a flag, and belongs in a constant
instead.

## 7. When to write nothing

A docstring that would not confuse a future reader by its absence is a docstring that will mislead one by going stale.
Skip it for:

- an object whose name and annotations are the whole contract;
- an override that adds nothing to the inherited contract: `inspect.getdoc` walks the MRO on Python 3.9 and later, so
  `help()` shows the parent's text, and a `"""See base class."""` replaces that text with nothing (§4, *Override*);
- a private helper whose single call site makes it obvious;
- anything the code states better, which is most narration.

The corollary: a public object with a non-obvious contract is not optional, however self-evident the name looks to the
person who just wrote it.

A lint rule that demands a docstring everywhere (`D100`–`D107`) fights this section and wins on volume: it produces
`"""Initialize."""` at scale, which is narration with a linter's blessing. Argue about the rule's configuration rather
than filling it in, and where the project has settled the argument, a one-line summary that says something is still the
job.

## 7a. Editing an existing docstring

Most of the time you are rewriting a docstring, not writing one. Different job, different failure mode: a rewrite drifts
longer, because every restructuring pass adds a sentence and none takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the old docstring did not
  carry: a unit, a side effect, a `None` rule, an invariant. Name that fact to yourself; if you cannot, you are
  re-phrasing, and the old wording stays.
- **A near-empty before-version makes the budget vacuous, not permissive.** `"""See base class."""`,
  `"""Initialize."""`, or no docstring at all carries no facts, so everything in front of you is growth and none of it
  has been paid. Judge it as a docstring written from scratch: every sentence earns its slot under §2, and on an
  override under §4's three cases. Where the branch under review wrote the paragraph an hour ago, its text carries no
  more authority than your own first draft.
- **A test is evidence, not a paying fact.** A test that pins the behavior establishes that it is intentional and stable
  enough to rely on; it does not make the behavior part of the contract, because a test pins implementation behavior
  just as readily. Name the fact a caller relies on and cite the test as support for it. `A test asserts it` pays for
  nothing on its own.
- **Decompression is paid growth.** A docstring can be too dense to read while being too *short* to fix under the rule
  above, and the budget then blocks the only repair there is. Unpacking one of the over-compressed shapes
  `english-developer-style` §4 tabulates adds words and no fact, and it is not churn; the payment is the re-read it
  removes. Name the construction you unpacked instead of naming a fact. That skill owns which construction is which and
  how to unpack it; this bullet only states that the budget does not block it. The exemption is that narrow: it does not
  license explaining more, hedging, or a second sentence of rationale, which still need a fact.
- **Check every identifier the old docstring names.** A docstring written before a refactor cites parameters,
  attributes, and functions that no longer exist. Python will not tell you: an identifier in prose runs, renders, and
  lies, and so does a cross-reference outside nitpicky mode (§5). Grep each one, and convert what you verify into the
  project's reference form.
- **Delete a parameter section that the annotations made redundant.** This is the commonest unpaid line in a Python
  docstring, and cutting it is the edit most likely to shrink the file.
- **When you lift a rule into the class docstring, cut it from the method.** The method keeps the one sentence that
  specializes the rule, plus the reference. Two full statements of the same rule is the most common outcome of a good
  structural edit and the easiest to miss, because each of the two reads well on its own.
- **Deleting is an edit, and every cut is reported.** A list of callers, a rejected alternative, a cost estimate, a
  reference to the change that introduced the code: cutting these is usually the highest-value change in the diff, even
  though the result looks like less work. Delete sentence by sentence, and report each deleted sentence with the fact it
  carried and where that fact now lives: a section, another object, the commit message, or nowhere, with the reason. A
  rationale sentence stays only where a maintainer reading the rule would ask why or would be tempted to relax it; the
  test is whether the sentence would come up as a question in code review. A rewrite that reads better and says less has
  lost a fact, and this rule catches it.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule governs the body, not the
  first line. A docstring that opens with `This function is a wrapper around X` stays broken until someone rewrites it,
  and "I had no new fact to add" is not a reason to leave it.
- **Run what the docstring runs.** If it contains a `>>>` block, run the doctests. If it feeds a committed artifact
  (§6a), regenerate.
- **Do not move code.** A docstring edit that also renames a variable or reorders a statement cannot be verified as
  comment-only, and that verification makes a large sweep safe. Python adds a hazard: the docstring *is* a statement, so
  an edit that lets anything precede it deletes it (§3).

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions and have to
establish what actually changed: reviewing someone else's edit, checking your own before you commit it, or judging a
machine-generated one.

The new version will read better. It was written second, by someone who had just finished understanding the code, and a
fact that vanished leaves no trace in the text that replaced it, so reading forward confirms that impression and finds
nothing. The work therefore runs backwards: read the **old** version carefully first, and form the verdict last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one `None` rule, one side effect, one ordering or concurrency constraint, one lifecycle
obligation, one named collaborator, one reference target, one raised exception, or one stated default. A topic sentence
is not a fact, and neither is a restatement of the signature or of an annotation. What the base class permits, and what
another API does, is neither: it names nothing a caller of this method relies on, so it takes a row as provenance and
pays for no growth in step 3 (§6). Compare facts, not sentences: at sentence granularity, merging two sentences looks
like a loss and splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Four defenses hold:

- the fact was wrong, which includes a claim the old text made and the code does not support;
- the fact moved to the class or module docstring, and you can point at the sentence that now carries it;
- the fact moved into the signature: a new annotation, a renamed parameter, a keyword-only argument, a return type that
  now says what a sentence used to;
- the fact was rationale, the contract it explained is stated completely without it, and the rationale no longer earns
  a slot under §2.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of those is the sentence
someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you name the fact. A
summary repaired under §3 pays for itself and is exempt, and so does a parameter section deleted because the
annotations already said it. Restructuring at equal length is free and needs no justification. Where the old version
carried no fact (`"""See base class."""`, a stub, no docstring at all), the budget measures nothing: judge every
sentence of the new version on whether it earns its slot under §2, and on an override under §4's three cases (§7a).

Two more exemptions, both from §7a. A stacked relative, an elliptical nominal opener, or a noun pile unpacked into a
finite clause is paid growth: the payment is the re-read it removes, and the rewrite names the construction rather than
a fact. And growth is not the only failure: a rewrite that keeps the old version's density while changing its words has
bought nothing and belongs in step 5.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the tests, or to a contract it references. **The old docstring is provenance, not
evidence.** That it made the claim shows the claim was made, not that it holds, so a claim carried over unchanged is
checked like any other. A claim that traces to none of those sources is invented, however plausible it sounds, and
plausible is the dangerous case: a wrong invariant in a docstring is a wrong invariant a caller will build on, and an
inherited one is worse, because it has outlived every pass that did not check it. `Raises:` is the most exposed place,
because nothing in Python can contradict it. The commit message is not a source either. It records what someone meant
to do; the docstring has to describe what the code does.

**An inference from the code is not the code.** A census of call sites establishes what is true today, not why the code
is the way it is. `No caller passes a negative value` supports `nothing inside this package reaches the guard`, and
supports nothing about who the guard is for. Design intent traces to a docstring, to a specification, or to the shape of
the API itself, never to a count of callers. This is §4's membership rule from the other end: a roll call of today's
callers is not a law about tomorrow's.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer attention now and costs the
next reader a `git blame` later. §7a has already settled that the old wording stays; here you look for the places where
it did not. Where the docstring ships (§6a) the cost is higher, because the churn arrives with a regenerated artifact
attached.

**6. Inline comments run on a different rubric.**

A new `#` comment has no earlier version, so steps 1 through 3 have nothing to work on. Four failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for docstrings; it is the characteristic
  failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Counterfactual.** The comment describes what would happen on a path this code rules out, rather than what it does.
  §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else. No build step
  catches this, so it is the most valuable thing a comparison pass finds.

A comment something other than a human reads is out of scope for all of these; see §4 for the list and for what moving
one breaks.

**7. Prove the code did not move.**

A sweep that edits docstrings across many files is reviewable only if the claim "comments only" is mechanical rather
than asserted. Comments never reach the AST, but docstrings do, so they have to be dropped before the comparison:

```python
import ast


def code_only(src: str) -> str:
    """Return a dump of the module's code with every bare string statement removed."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        node.body = [
            stmt
            for stmt in body
            if not (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            )
        ] or [ast.Pass()]
    return ast.dump(tree)
```

Dropping every bare string statement, rather than only what `ast.get_docstring` returns, also removes the attribute
docstrings (§4). Any difference between the two dumps means the pass touched code, and the pass is wrong until it is
explained.

**8. Say which finding it is, not whether the docstring got better.**

Each outcome names the repair it obliges. Naming it makes two people comparing the same pair reach the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Invented `Raises:` entry | Check that the code can raise it, or cut the line |
| Stale identifier | Fix what it names, and make it a reference (§5) |
| Restated annotation | Cut the type, keep whatever the line added |
| Duplicated rule | Cut the copy the class docstring now carries (§7a) |
| Churn | Restore the old wording |
| Density kept | Unpack the stacked relative, the elliptical opener, or the noun pile (§7a) |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Counterfactual | Cut the simulation; re-evaluate any rationale left standing under §2 |
| Unearned rationale | Cut the rationale; keep the complete contract (§2) |
| Base-class provenance | Cut it; keep the resulting contract (§6) |
| Stale inline comment | Rewrite it from the code |
| Mixed section dialect | Convert to the project's dialect (§6) |
| Displaced tool comment | Restore its exact text and line (§4) |
| Broken doctest | Run it, and fix the example or the expectation |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the summary one line, ending in a period, and does it stand alone with no term the docstring introduces?
- Is its mood the one the rest of the project uses (§3)?
- Could a reader reconstruct the summary from the object's name alone?
- Is the docstring still the first statement, and is it a plain string rather than an f-string?
- In a regression test's docstring: the rule first, the old defect in one past-tense sentence, and any equivalence with
  the old behavior kept (§1)?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test from the docstring
  alone?
- Does any parameter line say more than the annotation already does?
- Does `Raises:` list what a caller can act on, and can the code actually raise each entry?
- For anything returning an iterator: is laziness, single-pass, and what it holds open stated?
- Is any rationale here commit-message material?
- Any sentence describing a previous version of the code: `now`, `no longer`, `used to`?
- Any sentence describing a code path this code does not have: what would happen if the rule were broken, rather than
  what the code does about it?
- Does the docstring explain another module's internals instead of naming it?
- Any positional reference: `below`, `above`, `the following`, `the other way`?
- Does a limit state what it bounds, rather than only what some neighboring limit bounds?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Are the sections in the project's one dialect, spelled exactly (§6)?
- Does every cross-reference still resolve, in the form this project's renderer reads?
- On an override: which of §4's three cases is it in, does any sentence describe the base class's freedom rather than
  this method's rule, and does the docstring you wrote carry every section the inherited one did (§6)?
- Does every term here have a definition outside this docstring, and does every name match what the code calls the
  thing (`english-developer-style` §4a)?
- For each rationale sentence: would deleting just that sentence change what a caller may rely on, or leave a
  maintainer unable to see why a constraint is there? If not, delete it.
- Is every `# type:`, `# noqa`, `# pragma`, or `# fmt:` comment still on the exact line it governs?
- Would deleting the whole docstring lose anything, given that `inspect.getdoc` inherits?
- If it contains `>>>`: did you run the doctests?
- If it ships as documentation (§6a): can its reader follow every reference without opening the code, and did you
  regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old docstring did not?
- Does any statement here also appear in the class or module docstring?
- Any list that a criterion would replace, or that the reader's editor already answers? Can the set gain a member
  without anything forcing an edit here, and does a trailing `...` stand where no criterion precedes it?
- Does every name the old docstring mentioned still exist?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the template was carrying the
annotations. The second grows, because a fact was missing. Do not read either one as the target shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a sweeper can recognize in
the wild is an example it will paste instead of derive, and a rewrite that matches this file word for word proves
nothing about whether the rules were applied.

Both also sit in a project that has settled on the Google convention: descriptive summaries, Google sections. In a PEP
257 project the summaries would be imperative and the sections would be reStructuredText fields, and nothing else in
either rewrite would change (§3, §6).

### A docstring the annotations had already outgrown

**Before**: eleven lines, of which two carry a fact. The rest is the signature, transcribed into a Google-style
template.

```python
def merge_labels(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    """Merges two label dictionaries.

    Args:
        base: dict[str, str]. The base labels.
        overrides: dict[str, str]. The overriding labels.

    Returns:
        dict[str, str]: The merged labels.
    """
```

**After**: the two facts, and the one the reader would otherwise get wrong.

```python
def merge_labels(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    """Merges into a new dict, with overrides winning on a key both sides set.

    Neither argument is modified. A key whose override value is empty is dropped from the
    result, so a caller removes an inherited label by overriding it with the empty string.
    """
```

Fact ledger: *overrides win* is new, and the only thing the old summary left the reader to guess. *Neither argument is
mutated* is new. *The empty-string convention* is new, and it is the behavior a caller cannot infer from the name.
Everything cut was a type the annotation already states (§6), so by §7b step 3 the deletion needs no defense and the
three added facts pay for the two lines they cost.

### A generator whose laziness was never stated

**Before**: accurate, and it describes a function that returns a list.

```python
def failed_rows(report_path: Path) -> Iterator[Row]:
    """Returns the rows the ingest run rejected."""
```

**After**: the summary keeps its shape and picks up the ordering; the body carries what the annotation hides.

```python
def failed_rows(report_path: Path) -> Iterator[Row]:
    """Returns the rows the ingest run rejected, in the order the report lists them.

    The file is opened on the first ``next()`` and stays open until the iterator is
    exhausted or closed, so consume it inside a ``with contextlib.closing(...)`` block if
    you may abandon it early. Single-pass: a second iteration yields nothing.

    Raises:
        FileNotFoundError: on the first ``next()``, not at the call, if the report is
            missing.
    """
```

The rewrite grew from one line to nine and paid for them with four facts the one-liner did not carry: the ordering, the
point at which the file is opened, the single-pass rule, and the one that costs a caller a debugging session, that the
exception is raised at the first `next()` rather than at the call. The last is a property of every generator, and a
surprise to anyone who read the signature and expected a list.
