---
name: rustdoc-authoring
description: >-
  Structure and content rules for Rust doc comments and inline comments. Use whenever the task
  involves a comment in Rust source — writing a new one, editing or rewriting an existing one,
  reviewing one, deciding whether an item needs one, or comparing two versions. Covers the four
  content slots and their order, why the first paragraph rather than the first sentence is the
  summary, what the signature already says so the comment need not, the headings that stand in for
  tags (# Errors, # Panics, # Safety, # Examples), intra-doc links and the lints that
  check them, doc examples that compile and run as tests and the blocks that become one by
  accident, // SAFETY: comments, how far a rewrite may grow, and the extra rules for traits, unsafe
  code, tests, module and crate comments, and docs that ship to docs.rs. Applies to a one-line
  comment as much as to a twenty-line block. Language and wording are governed by
  english-developer-style, which this skill defers to and does not replace.
---

# Authoring a Rust doc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect are the province of `english-developer-style` — load it too, and let it own the prose. The
two compose: this skill picks the slots, that one writes the sentences.

Everything here is written for Rust. Habits carried in from another language's doc comments go wrong
in three specific places, so do not translate them in your head:

- **Rust's type system states in the signature what elsewhere goes in prose.** `Option` is the
  nullability rule, `Result` is the error list, ownership and `&mut` are the aliasing contract,
  `Send` and `Sync` are the threading model. §4 is mostly about what is *left*.
- **A doc example compiles and runs.** The code in a doc comment is a test the build executes, so
  the strongest thing a Rust comment can say is a checked assertion rather than a claim (§6).
- **Nothing formats a doc comment for you.** Measured on rustfmt 1.8.0, stable rustfmt leaves doc
  comments byte for byte alone: it does not reflow a 180-column line, does not normalize a list
  marker, does not fix indentation. `wrap_comments` and `format_code_in_doc_comments` are
  nightly-only and off. You own the layout — match the wrapping width the file already uses.

Everything measured below was measured on rustc, cargo 1.92.0, clippy 0.1.92, and rustfmt 1.8.0.

## 1. The correction that matters most

The advice you have absorbed is "document the why, not the what". For a doc comment that is half
wrong, and the wrong half does the damage.

An inline `//` comment inside a function documents the **why** — it sits next to code the reader can
already see. A doc comment on an item documents the **contract**: what a caller may rely on, what an
implementer owes, what holds before and after. That is a *what*, but a promise-level what, not a
restatement of the code.

So the failure mode is not "explains what the code does". It is any of these:

- **Narrating the implementation.** `Iterates the entries and inserts each into the map.` The body
  says that already, and the comment becomes a lie on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the boilerplate every handler
  shared.` That is material for the commit message and the pull request. A doc comment is read by
  someone who has to *use* or *fix* the thing, not by someone deciding whether to merge it.
- **Restating the signature.** This is the Rust-specific one and it is the most common.
  `Returns None when the key is absent. Takes ownership of the buffer. The error type is
  io::Error.` The reader has `Option<&V>`, `buf: Vec<u8>`, and `io::Result<_>` on the screen. A
  comment that spends its first paragraph re-typing the signature in English has spent the reader's
  attention on the one part they did not need.

A fourth form is specific to a codebase that has been refactored: **narrating the code's history**.
`Poll now returns Pending instead of blocking, so callers no longer need their own timeout`
describes a transition between two versions. The reader has one version — this one. Rewrite it as
the state that holds: what `poll` returns, and what the caller owes.

**Deleting the narration is not deleting the finding.** A comment that carries a measured number —
`a floor of 100 over top_k * 5 only moved the coupling past k = 20`, `the outline splits into 12
chunks over 473 KB` — carries a fact, and usually the fact that decided the code. Change its tense
and cut the account of how it was discovered; keep the number and what it measures. §7b step 2
counts a dropped measurement as a lost fact, not as a trim, and a tuned constant whose measurement
is gone is a constant the next reader will change back.

## 2. The four slots

A doc comment has at most four slots, and they go in this order.

| # | Slot | Answers | Skip when |
| --- | ------ | --------- | ----------- |
| 1 | **Summary** | What is this, or when does it fire? | Never — always present |
| 2 | **Contract** | What may a caller rely on? What does an implementer owe? | The signature genuinely says all of it |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader do next? | The contract already implies the action |

Two rules govern the order.

**Contract before mechanism.** State the rule the reader must satisfy before you explain the
machinery that enforces it, and before you explain what some *other* module does. A comment that
opens with a neighbouring type forces the reader to reconstruct the rule from your negative
examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first thing to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

**Make the obligated party the subject.** Obligations come in two shapes.

*Stated* — the sentence carries a *must*, *has to*, *may not*, or *should*. Whoever has to comply
belongs in the subject: not the thing acted on (`The guard must be held for the whole write`, which
names no one), not the act (`aliasing the buffer must not be reachable from safe code`), and not an
item that merely performs the act for someone else (`drop must still run` obliges the caller). A
named item in the subject is right only where that item is itself what must comply: `try_reserve
must leave the capacity untouched when it fails`. The party need not be human, but it must be
something that acts — the caller, the allocator, an implementor; a variant or a configured limit
complies with nothing.

*Census* — a rule for the next maintainer, written instead as a report on today's call sites:
`Called from poll_next once the waker is registered`, `Vec is the only implementor`. Flat
indicative, no modal, so ask: **if a second such caller appeared tomorrow, would this paragraph tell
it that it is obliged?** Judge the paragraph, not the sentence — an example is allowed to follow a
law that is already correctly stated. Write the law, not the roll call.

`# Safety` is where this matters most: the whole section is one obligation, and the party is the
caller of the `unsafe fn`, never the function itself. `The pointer must be valid for reads` leaves
the reader to infer who guarantees it; `The caller must guarantee that ptr is valid for reads of
len bytes` is the contract `unsafe` actually rests on. The same goes for the `# Panics` and
`# Errors` sections when they state what a caller has to avoid rather than what the function does.

Watch the intransitive modal, where the party hides best: `every variant has to appear in
FROM_STR`, `an unknown value must fall back to Mode::Fail`. Nothing appears or falls back of its own
accord; name what does it.

Out of reach: an imperative, which already addresses the party (`Call this before the first poll`),
including one carrying rationale (`so mirror the std behaviour here`); a constraint on a *value*
(`must be ≤ isize::MAX`), which bounds a number rather than behaviour; a doc comment naming who
writes or reads a field, which is the membership rule §4 asks for; and an inline comment whose next
statement is the actor — a `// SAFETY:` note above the `unsafe` block it justifies, but check that
the next line really is the actor and not test setup standing between the comment and the call it
constrains.

Slot 4 has a Rust-specific form: the `# Examples` block. It is the Use slot written as code the
build runs, which makes it the only slot that cannot silently go stale. Prefer it to a prose
paragraph describing how to call the thing (§6).

Most items need slots 1 and 2 only. An accessor needs slot 1. Do not manufacture the other slots to
fill a template — an absent slot is not a gap.

**Size the comment to the item.** A doc comment longer than the function it documents is not
automatically wrong — an invariant can be worth ten lines over a three-line method — but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two
sentences of it, and only for the part a reader would otherwise get wrong. Everything past that
belongs in the commit message.

A measurement does not count against that budget. `k = 20`, `473 KB`, `eight of thirty queries` are
facts under §1, and the two-sentence cap governs the prose around them — cut the story, keep the
number.

## 3. The first paragraph is the summary

Rustdoc lifts the opening of a doc comment into the item table on the parent module's page and into
the search index, where it appears with **no surrounding context**. Write it to stand alone there.

The boundary is a **blank `///` line, not a period**, which is the opposite of what a sentence-based
convention would lead you to expect. Measured on rustc 1.92, a comment opening `/// Returns a thing,
e.g. a widget. Second sentence stays on the same line.` puts *both* sentences in the item table, and
the paragraph after the blank line in neither. So `e.g.` costs nothing here, and a second sentence
you meant as detail costs the whole table row.

- **One sentence, then a blank `///` line.** If the summary takes two sentences, the first one is
  not the summary.
- **Third person, subject omitted.** `Returns the backing map.` Not `Return…`, not `This function
  returns…`. The item's own name does **not** lead: rustdoc prints the name beside the summary
  already, so `parse parses the input` is a stutter.
- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it. A summary must be readable by someone
  who will never read paragraph two.
- **No self-description.** Drop `Helper type that…`, `Utility for…`. The verb leads.
- **A `const` or `static` names its unit.** `Largest encrypted packet this stream accepts, in
  bytes.` The reason the bound has that value is slot 3, however interesting it is.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  answers no question. Put the qualifier after the summary.
- **A field of a `pub` struct gets the same treatment as a function.** It is a public item with a
  contract, not a label.

## 4. Genre notes

### What the signature already says

Rust encodes in types much of what elsewhere goes in prose. Before you write slot 2, cross off
everything the reader can see:

| The signature already says | So do not write |
| --- | --- |
| `Option<T>` | "returns `None` if absent" — unless what `None` *means* here is non-obvious |
| `Result<T, E>` | "may fail" — say which `E` values arise and what a caller does about each |
| `&mut self`, `self` by value | "mutates the receiver", "consumes the value" |
| `&'a T` tied to a parameter | "the result borrows from `input`" |
| `T: Send + Sync` | "safe to share between threads" |
| `impl Iterator<Item = …>` | "returns an iterator" |

What is left is the work:

- **Panics**, with the exact condition, and whether the caller can test for it first.
- **What each error means**, beyond its type: which are the caller's fault, which are transient,
  which a retry can fix. `Result<_, io::Error>` names a type, not a taxonomy.
- **Units, ranges, encodings, time bases** — `milliseconds since the epoch`, `UTF-8 bytes`,
  `0-based`, `inclusive of both endpoints`.
- **Complexity and allocation**, where a caller would guess wrong. std documents `O(n)` for a reason:
  nothing in the signature distinguishes a lookup from a scan.
- **Laziness.** An iterator, a builder, or a future that does nothing until it is consumed or awaited
  needs one sentence saying so, because the type does not.
- **Cancellation safety** for an `async fn`: what state is lost if the future is dropped mid-poll.
  This has no encoding in the type system at all, and getting it wrong corrupts data at run time.
- **Blocking.** A synchronous call inside an async context is a defect the compiler will not catch.
- **What `Drop` does**, and whether the value must be explicitly closed, flushed, or awaited first.
- **Invariants a `pub` field must keep**, since anyone can write it.
- **Platform differences** behind a `#[cfg]`.

Name a parameter in prose, spelled exactly as in the signature, at the point where its contract
matters: `body is serialized as JSON when non-empty`. Do not walk the parameter list in order
restating types — that is the signature, transcribed. Rust has no `@param`, and it does not need one.

A function whose contract is exhausted by its name and types needs one line or nothing.

### The membership rule, not the membership list

A comment that lists the members of a set — every variant a match must handle, every function that
writes a field, every caller that must be updated — has transcribed a query. The list looks
authoritative and is stale from the first refactor, and a reader who does not find their case in it
concludes the wrong thing.

State the criterion instead: *every other check rejects a value no conforming peer can send* beats
an eight-item list of those checks, because the reader can classify a check the list has never heard
of.

A criterion has to let the reader name a member. "The limits whose error message offers this as a
remedy" is true by construction and tells them nothing they could not have inferred; if the honest
criterion is circular, the list was the answer after all.

There are two exceptions. A set the code itself declares — an exhaustive `match` the compiler keeps
honest, a test that partitions a set of constants — is maintained because the build or the test fails
when it drifts; there the list **is** the contract. And a list the reader needs as vocabulary — the
environment variables a binary reads, the Cargo features that change behavior — stays, because the
criterion alone does not let anyone write code. What goes in that case is the rot: the version label
that freezes the list, and the per-item annotations nobody maintained.

`#[non_exhaustive]` cuts the other way. It tells a downstream reader that the list they can see is
not the list that will exist, so a comment enumerating the variants of a `#[non_exhaustive]` enum
contradicts the attribute. State the criterion; that is what the attribute was for.

The exception is wider for a comment that ships to docs.rs (§6a), because that reader cannot open
the code to enumerate the set themselves.

### Type (struct, enum, type alias)

The type comment carries the **invariant that spans the fields and methods**. Member comments
specialize it; they do not carry it. A rule stated only on a private field is a rule the type
comment is missing.

Name the collaborators the type is useless without, and the lifecycle if the value is not free
standing. `Default` being meaningful is itself a contract worth one clause when it holds. Where the
type upholds an invariant its fields could violate — a sorted vector, a validated string, a handle
that must outlive its parent — say what the invariant is, because that is the reason the fields are
private and the reason the constructor exists.

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

A provided method's comment says what an override must preserve. A required method's comment is the
obligation itself.

An `unsafe trait` gets a `# Safety` section, and it points the opposite way from an `unsafe fn`
(§6): it states what an **implementer** guarantees, because that is who writes `unsafe impl`.

### Field, constant, and static

Document the unit, the range, the sentinel, and who may write it. A private `static` whose invariant
is non-obvious needs that invariant spelled out — a reader adding a write has no other source of
truth. When the type comment already states the rule, the field comment shrinks to one sentence plus
a link, rather than repeating it.

A run of constants with a shared rule takes one comment on the enclosing module or block and short
ones on each, not the same sentence eight times.

### `unsafe fn` and `# Safety`

An `unsafe fn` moves an obligation from the compiler to the caller, and the `# Safety` section is
where that obligation is written down. It is the only doc section in Rust that is load-bearing:
without it the caller has no way to know what makes a call sound, and `unsafe` becomes a wish.

- **Write conditions the caller can check**, in the caller's vocabulary: `ptr must be non-null,
  aligned for T, and valid for reads of len * size_of::<T>() bytes`. Not "the caller must use this
  correctly".
- **State every condition.** A `# Safety` section that lists three of four requirements is more
  dangerous than none, because it reads as complete.
- **Do not explain the implementation there.** Why the function is sound given those conditions is
  rationale; the conditions themselves are the contract.

`clippy::missing_safety_doc` warns by default (verified on clippy 0.1.92) for a public `unsafe fn`
with no `# Safety` section, so this one rule has a tool behind it. Nothing checks that the section
is *correct*, or that it is complete.

### `// SAFETY:` comments

The inverse of the section above. An `unsafe` block consumes someone else's `# Safety` contract, and
the `// SAFETY:` comment above it is the argument that this call site satisfies it.

```rust
    // SAFETY: `idx < self.len` was checked above, and `self.ptr` is valid for
    // `self.len` initialized elements for as long as `&self` is held.
    unsafe { &*self.ptr.add(idx) }
```

It answers the callee's conditions one by one, in the caller's own terms. "This is fine because the
index is in range" is not an argument if the callee also required alignment and initialization.
`clippy::undocumented_unsafe_blocks` finds the missing ones, but it is a restriction lint and off by
default (verified), so in most crates nothing asks for these but review.

### Inline comment

Answers "why this line", for a reader who can already see the line. Three failure modes beyond
narration:

- **Meta-commentary.** `…so check the length first instead` describes what the comment is doing.
  State the fact: `a shorter frame cannot carry a header, so the parse below would read past the
  end.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` are the tells.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is narrowed to `u32` belongs at the conversion; repeating it inside the branch that
  rejects an oversized value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`// SAFETY:` (read by `clippy::undocumented_unsafe_blocks`); `// TODO` and `// FIXME` markers;
`#[rustfmt::skip]` and `// rustfmt::skip`; `// @generated` and `// Code generated … DO NOT EDIT.`;
anything citing an issue or a URL. `#[allow]`, `#[expect]`, `#[deprecated]`, and `#[doc(hidden)]`
are attributes rather than comments — do not fold one into prose, and do not delete one because it
looks like a note.

Three Rust-specific hazards, all of them compile errors or silent behavior changes:

- **A doc comment must be followed by an item.** `///` is sugar for `#[doc = "…"]`, so a doc comment
  with nothing after it is `error: expected item after doc comment` — a hard build failure, not a
  lint. A comment orphaned by a deleted item therefore cannot survive into the repository, and a
  "comment-only" edit can fail the build — compile before you claim the sweep was harmless.
- **`//!` may only appear before items.** Moving an inner doc comment below the first item in a file
  is `error[E0753]: expected outer doc comment`, plus the error above. A module comment stays at the
  top.
- **A doc comment is part of the item's attributes**, so it interacts with `#[cfg]` and
  `#[cfg_attr(docsrs, doc(cfg(…)))]`. Reordering attributes around a doc comment is safe; splitting
  a `#[doc]` group is not.

### Test module

A test is met in exactly one situation: it just went red. Write for that reader.

Rustdoc does not render `#[cfg(test)]` code at all, so no tooling reads these and the firing
condition wins over every other consideration:

```rust
    /// A header the caller set by hand survives the retry unchanged.
    #[test]
    fn retry_preserves_caller_headers() { … }
```

- **Summary = the rule the test guards**, lifted out of the body rather than invented. The rule is
  already in the assertions and nowhere else; the comment says it once, above them, so a reader
  meeting a red build does not have to reconstruct it from four `assert_eq!` calls and a fixture.
  State it positively and completely, as something you could assert. `It has to stay quiet when the
  socket did go away` leaves the reader guessing: not panic, not close twice, not log? Name the
  observable. If you cannot phrase the rule as an observation, the test probably cannot check it
  either.
- **Use = what to do about the red build.** Which set to edit, which case to add, where the failure
  message says the rest.
- **The test's name is a comment.** It is the string in the failure output, and often the only one
  the reader sees. A table-driven case's label is the same thing: it names the case's condition, not
  its ordinal.
- **The `assert!` message is a comment too**, and it is the one that reaches the reader first. Put
  the expected rule there, not `assertion failed`.

Deliberate duplication between the test's comment, a helper's comment, and the failure message is
correct — each reader meets exactly one of the three. It does not extend to production code, where
the type comment and the method comment have the same reader.

### Module and crate comment

`//!` at the top of the file, before any item. One per module; a `mod.rs` or the module's principal
file carries it.

The crate comment in `lib.rs` is the entry point and the docs.rs landing page: what the crate is
for, which types are the way in, the Cargo features and what each turns on, the minimum supported
Rust version if the crate promises one, and any rule that holds across the crate (error conventions,
panics policy, async runtime assumptions). The item list is generated; a hand-written copy is the
membership list all over again.

`#![doc = include_str!("../README.md")]` makes the README the crate documentation, which is a good
default and has one sharp edge: **every fenced block in that README becomes a doc test**. Measured
on rustc 1.92, an untagged block containing `cargo add mycrate` fails `cargo test --doc`, and the
failure is reported against `src/lib.rs` at the line of the attribute, with no mention of the README.
Tag the README's non-Rust blocks (§6) before wiring this up.

A binary crate's module comment is user documentation: what the binary does, its flags, its
environment variables, its exit codes. There the vocabulary exception of §4 applies in full.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` — all three
are invisible in rendered documentation, silently wrong after a reorder, and unchecked by any tool.
Name the item instead.

Rust has **intra-doc links**, which render as hyperlinks on docs.rs and in editors:

| Form | Refers to |
| --- | --- |
| `[Classifier]` | an item in scope, resolved by Rust's own name resolution |
| ``[`Vec`]`` | the same, rendered as code — the usual form for a type |
| `[Client::send]` | an associated function, method, or field |
| `[crate::codec::Frame]` | an item by path from the crate root |
| `[std::io::Read]` | an item in another crate, imported or not |
| `[the sender](Client::send)` | the same target under different link text |
| `[struct@Frame]`, `[fn@frame]`, `[macro@frame]`, `[prim@u8]` | a name that is several things at once |

The disambiguators matter more in Rust than the table suggests: a struct and a function may share a
name in the same module, and `[frame]` then resolves to whichever the resolver reaches first.

**A broken link is caught.** `rustdoc::broken_intra_doc_links` is warn-by-default
(verified on rustc 1.92): `cargo doc` reports `unresolved link to 'NoSuchItem'` and points at the
column. Two limits on that guarantee. It is a warning, so it fails nothing unless the crate denies
it or CI runs with `RUSTDOCFLAGS="-D warnings"`; and it only fires where `cargo doc` runs at all.
The unresolved link still renders as the literal text `[NoSuchItem]`, so the reader sees nothing
unusual and only your build tells you.

Two more lints worth knowing, both warn-by-default:

- **`rustdoc::invalid_html_tags`.** Rust doc comments are Markdown, so raw HTML passes through. `///
  Takes a Vec<T>` emits a literal `<T>` into the page, which the browser parses as an unknown tag
  and drops: the reader sees "Takes a Vec". Backtick every type that carries angle brackets.
- **`rustdoc::bare_urls`.** A bare URL is not auto-linked; wrap it in `<…>` or make it a Markdown
  link.

`clippy::doc_markdown` wants backticks around every identifier-shaped word, but it is a pedantic
lint and off by default (verified). Backtick identifiers anyway — it costs two characters and it is
what distinguishes a type name from an English noun.

Repeated links go in reference definitions at the end of the comment, which keeps the prose
readable:

```rust
/// Wraps [`Frame`] for transport and hands it to [`Sink::send`].
///
/// [`Frame`]: crate::codec::Frame
/// [`Sink::send`]: futures::Sink::send
```

`rustdoc::private_intra_doc_links` warns when a public item's docs link to a private one: the link
resolves for you and points nowhere on docs.rs (§6a).

Cite an issue only alongside the name of the phenomenon: `the desync class of bug that #4015 fixed`
survives the tracker; a bare `see #4015` does not.

## 6. Sections and examples

Rust has no tags. §4 covers what stands in for documenting a parameter and a result. The rest is
conventional Markdown headings, written as `#` and rendered by rustdoc as subheadings of the item:

| Heading | Carries | Lint behind it |
| --- | --- | --- |
| `# Errors` | what each error value means, and what the caller does about it | `missing_errors_doc`, pedantic, off |
| `# Panics` | the exact condition, and how the caller avoids it | `missing_panics_doc`, pedantic, off |
| `# Safety` | the caller's obligations (§4), or a trait implementer's | `missing_safety_doc`, **warn by default** |
| `# Examples` | working code the build compiles and runs | none, and it is still worth writing |

The lint names are clippy's, and the three levels were verified on clippy 0.1.92. Only `# Safety`
has a lint on by default; the other two fire under `-W clippy::pedantic` and nothing at all asks for
an example.

std's order is `# Errors`, `# Panics`, `# Safety`, then `# Examples` last, and matching it means a
reader who knows std can skim yours. A heading with one sentence under it is fine; a heading with
nothing under it is a template being filled in.

`# Deprecated` is not one of these. Deprecation in Rust is `#[deprecated(since = "…", note = "…")]`,
an attribute rather than a section: the compiler warns at every call site and prints the `note`
there. Name the replacement in the `note`, not in a paragraph a caller has to go looking for.

Other markup: paragraphs are separated by a blank `///` line, `**bold**` and `` `code` `` work,
tables and lists work, `#` headings are demoted by rustdoc so `#` is the right level to write.

### Examples are tests, and accidental examples are too

This is the section with no counterpart in the sibling skills. Every fenced block in a doc comment
is compiled and run by `cargo test`, which is what makes an example the most durable thing in a
comment — and what makes several ordinary formatting habits into build failures.

**A fenced block with no language tag is Rust.** Measured on rustc 1.92, a block containing `cargo
build --release` fails with `expected one of '!' or '::', found 'build'`. Tag every non-Rust block:
`text`, `console`, `sh`, `toml`, `json`.

**A four-space-indented block is also an untagged code block**, because the comment is Markdown.
Indentation is how you show a command in some other languages' doc comments; here it is how you hand
`this is not rust` to the compiler. Verified — the failure is identical to the untagged-fence one.
Use a tagged fence, always.

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

**A hidden line — `#` and a space — is for setup the reader does not need to see**, and for nothing
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
silently and takes the reader's trust with it. Reach for `no_run` or `text` instead; if neither
fits, the example is prose and should be written as prose.

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
often a second surface — a README assembled from the crate docs, a `--help` string, a generated
client.

**The reader changes, and that is the whole section.** They are working against your API from the
outside, on a page in a browser, with no repository checked out and no `git log`. Four rules follow.

1. **Links they can follow are a strength here.** Rustdoc renders an intra-doc link as a real
   hyperlink on docs.rs, so ``[`Frame`]`` costs the reader nothing and saves them a search. Prefer
   a link to a reference spelled out in prose — this reader can click it, and a rendered page is
   the one surface where that holds.
2. **A link this reader cannot follow has to be spelled out.** A link to a private item or a
   `#[doc(hidden)]` one resolves in your editor and points nowhere on the published page;
   `rustdoc::private_intra_doc_links` catches the first case. Name the rule instead of linking to
   the thing that states it.
3. **Say which Cargo feature an item needs.** docs.rs builds with the feature set the crate's
   metadata names, so a reader sees items their own build does not have.
   `#[cfg_attr(docsrs, doc(cfg(feature = "tls")))]` puts the badge on the page; without it the
   reader hits a missing symbol and blames the version.
4. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a
   parameter accepts, the keys a map may hold, the errors a call can produce — that list is the only
   source this reader has, so replacing it with a criterion is allowed only when they can apply the
   criterion *without opening anything*. §4's own warning applies at full force: if the honest
   criterion is circular, the list was the answer, and the repair is to complete it and verify every
   member against the code in the same edit. An incomplete list shipped as documentation is worse
   than no list.

The example carries more weight on this surface than anywhere else: it is the first thing a reader
scrolls to and the thing they paste. Make it complete enough to compile in their crate — visible
imports, no hidden line they need — and keep it to the one call the item is for.

Because a published comment reaches people who cannot see a correction until the next release, the
bar rises — but it rises for **rewording**, not for **enriching**. A synonym or a smoother clause is
churn that ships. A fact the page does not carry and its reader needs is worth the release every
time, even when every sentence already there is true. "It is correct as written" answers the first
case and not the second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- an item whose name and types are the whole contract;
- a trait implementation that adds nothing to the trait's documented contract;
- a private helper whose single call site makes it obvious;
- anything the code says better, which is most narration.

Nothing forces the issue: `missing_docs` is allow-by-default (verified), so an undocumented `pub`
item builds clean. The corollary is the same as in the sibling languages, and here it has no lint
behind it: a public item with a non-obvious contract is not optional, however self-evident the name
looks to the person who just wrote it. A crate that publishes to crates.io should turn
`#![warn(missing_docs)]` on and then write comments worth the warning, not comments that restate the
name.

## 7a. Editing an existing comment

Most of the time you are not writing a comment, you are rewriting one. Different job, different
failure mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry — a unit, a panic condition, a cancellation rule, an invariant. Name
  that fact to yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **Check every identifier the old comment names.** A comment written before a refactor cites types,
  fields, and functions that no longer exist. A bare name in prose compiles, renders, and lies.
  Convert what you verify into an intra-doc link, because that is the one form `cargo doc` will
  check for the next reader (§5).
- **A doc-comment edit can break the build.** Adding or editing an example changes code the test
  suite runs, and a stray indent or an untagged fence turns prose into a failing test (§6). Run
  `cargo test --doc` on any comment edit that touches a fenced or indented block. It is the rule
  most often skipped, because nothing about the edit looks like a code change.
- **When you lift a rule into the type or trait comment, go and cut it from the member.** The member
  keeps the one sentence that specializes the rule, plus the link. Two full statements of the same
  rule is the most common outcome of a good structural edit and the easiest to miss, because each of
  the two reads well on its own.
- **Deleting is an edit.** A list of callers, a rejected alternative, a benchmark number, a
  reference to the change that introduced the code — cutting these is usually the highest-value
  change in the diff, even though the result looks like less work.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule governs
  the body, not the first paragraph. A comment whose summary runs to three sentences stays broken
  until someone rewrites it, and "I had no new fact to add" is not a reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot be
  verified as comment-only, and the verification is what makes a large sweep safe.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

Start from this. The new version will read better. It was written second, by someone who had just
finished understanding the code. Reading forward confirms that impression and finds nothing, because
a fact that vanished leaves no trace in the text that replaced it. So the work runs backwards: you
read the **old** version carefully first, and the verdict comes last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one panic condition, one error meaning, one ordering or
cancellation constraint, one lifecycle obligation, one named collaborator, one link target, one
safety requirement, or one stated default. A topic sentence is not a fact, and neither is a
restatement of the signature.

Compare facts, not sentences. At sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Three
defenses hold:

- the fact was wrong;
- the fact moved to the type, trait, or module comment, and you can point at the sentence that now
  carries it;
- the fact moved into the code — a stricter type, a named error variant, an `assert_eq!` in the
  example that now checks what a sentence used to claim.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is what someone writes when they cannot find the fact and would rather not look again.

A `# Safety` requirement is the one fact class where absence has no acceptable defense short of the
first. Dropping a condition from a `# Safety` section is an unsound-call-site generator, and it
looks exactly like tightening the prose.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first paragraph repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification at all.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the old comment, or to a contract it links to. A claim that traces
to none of the three is invented, however plausible it sounds, and plausible is the dangerous case: a
wrong invariant in a doc comment is a wrong invariant a caller will build on. The commit message is
not a source. It records what someone meant to do, and the comment has to describe what the code
does.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer
attention now and costs the next reader a `git blame` later. §7a already says the old wording stays;
here you go looking for the places where it did not.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Three
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is
  the characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else.
  No build step catches this, which makes it the most valuable thing a comparison pass finds.

A `// SAFETY:` comment is the exception within the exception: it is an argument about the code below
it, so a change to that code invalidates the argument even when the comment still parses as true.
Re-derive it rather than re-reading it.

**7. Prove the code did not move, and prove the tests still run.**

Rust needs both halves, because a doc comment holds executable code.

For the first half, start with the check that costs one command and no dependency — read the diff
and delete every line that is a comment:

```sh
git diff <base>..HEAD -- '*.rs' | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | grep -vE '^[+-]\s*//'
```

Whatever it prints is a non-comment line the pass changed, and on a comment-only sweep it prints
nothing. Run it before you read the diff yourself: it answers in a second, and on a sweep spanning
hundreds of lines it is the only reading that is not subject to fatigue. Its limits are the limits
of text — it cannot tell a moved line from a rewritten one, it does not see a `/* */` block, and a
re-wrapped comment counts as a change on both sides.

The precise version parses instead of matching, so re-wrapping and reordering cannot fool it. `syn`
discards `//` comments outright and turns `///` and `//!` into `#[doc]` attributes, so removing
those leaves only code:

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

For the second half, run `cargo test --doc`. Neither check above can see inside a doc example — to
`grep` it is a comment and to `syn` it is a string — so a sweep that rewrote an example is
comment-only by both proofs and can still have broken the build.

A test that stopped running is the failure this step is really for, and it is quieter than a test
that fails. It is not silent, though: a function in a `#[cfg(test)] mod tests` that loses its
`#[test]` stops being called, and `dead_code` warns by default (verified) — clippy adds
`duplicated attribute` when the lost attribute landed on a neighbour. Do not lean on that. A warning
in a build that already prints warnings is a warning nobody reads, whereas the diff check names the
file and the line. Compare the test count across the sweep as well; it costs one number.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it is what makes two people comparing the same pair
reach the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Lost safety condition | Restore it; no other defense applies (§7b step 2) |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and make it an intra-doc link (§5) |
| Duplicated rule | Cut the copy the type or trait comment now carries (§7a) |
| Churn | Restore the old wording |
| Narration | Delete the comment |
| Signature restated in prose | Delete the restatement (§4) |
| History narration | Rewrite as the state that holds now |
| Stale inline comment | Rewrite it from the code |
| Stale `// SAFETY:` argument | Re-derive it against the callee's current contract |
| Untagged or indented block | Make it a tagged fence, before the build compiles it as Rust (§6) |
| `ignore`d example | Convert to `no_run` or `text`, or delete it (§6) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the first paragraph one sentence, followed by a blank `///` line?
- Does it stand alone, with no term this comment introduces, and does it avoid repeating the item's
  own name?
- Does any sentence restate what `Option`, `Result`, `&mut`, or a trait bound already says?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Does a function that can panic have a `# Panics` section naming the condition?
- Does every `unsafe fn` have a `# Safety` section, and is every condition in it checkable by the
  caller?
- Does every `unsafe` block have a `// SAFETY:` comment that answers the callee's conditions?
- Does a trait comment state the laws an implementer owes, not only what the methods do?
- Is every fenced block tagged, and is there any four-space-indented block that will be compiled as
  Rust?
- Does the example assert what the prose claims, and does it compile without a hidden line the reader
  needs?
- Any `ignore` attribute that should be `no_run` or `text`?
- Any positional reference — `below`, `above`, `the following`?
- Any bare name that should be an intra-doc link, and does `cargo doc` report no unresolved link?
- Any type with angle brackets outside backticks?
- Is any rationale here actually commit-message material?
- Any sentence describing a previous version of the code — `now`, `no longer`, `used to`?
- Would deleting the whole comment lose anything?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- If this is a rewrite: did every measured number in the old version survive it (§1)?
- If this is a rewrite touching a fenced block: did `cargo test --doc` pass?
- If this is a sweep across files: does the diff check print nothing, and does the test count match
  (§7b step 7)?
- Does any statement here also appear in the type, trait, or module comment?
- Any list that a criterion would replace, or that the reader's editor already answers?
- If the comment ships to docs.rs (§6a): can its reader follow every link, and is a feature gate
  named?

## 9. Worked examples

The two examples pull in opposite directions on purpose. In the first the prose shrinks, because it
was restating the signature, while the comment grows an example. In the second everything grows,
because a fact was missing. Do not read either one as the target shape.

Both are constructed rather than lifted from a real crate, and deliberately so: an example a sweeper
can recognize in the wild is an example it will paste instead of derive, and a rewrite that matches
this file word for word tells you nothing about whether the rules were applied.

### A comment that re-typed the signature

**Before** — four sentences, three of which the reader can see in the declaration. The one fact the
signature does not carry, the meaning of an empty result, is buried in the last clause.

```rust
/// Parses a frame from the buffer.
///
/// This method takes a shared reference to the buffer and returns an `Option`
/// containing the parsed `Frame`, or `None`. It does not modify the buffer. The
/// caller owns the returned value, and `None` is returned when the buffer holds
/// fewer bytes than a complete frame.
pub fn parse(buf: &[u8]) -> Option<Frame> { … }
```

**After** — the summary keeps its one sentence, `None` gets the only sentence it needs, and the
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
*the caller owns the result* — all four absent, all four defended by step 2's third defense, since
each is in the signature. *`None` when the buffer is short* — present, and now distinguished from
the malformed case, which is the fact the old comment did not carry.

The comment as a whole is seven lines longer, and every one of those lines is the example. That is
the trade this section is for: the prose lost four sentences that the declaration already made, and
the growth bought the one claim in the comment that `cargo test` will keep honest. Count prose
against §7a's budget and count an example separately, or the budget will talk you out of the example
every time.

### An `unsafe fn` whose obligations were not written down

**Before** — a summary and a reason. The reason is real and the comment is still unusable, because
nothing here tells a caller what makes a call sound.

```rust
/// Returns the element at `idx` without a bounds check.
///
/// Skipping the check matters in the decode loop, where the index is already
/// known to be in range and the branch showed up in profiles.
pub unsafe fn get_unchecked(&self, idx: usize) -> &T { … }
```

**After** — the obligations, stated as conditions the caller can check, plus the counterpart the
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
/// while it is alive — including [`Self::push`], which may reallocate and leave
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
no debug-build safety net, which is what a reader assumes wrongly), and the aliasing rule the
returned lifetime enforces but does not explain. The performance rationale went to the commit
message under §2 — a caller who knows the rule and not the reason can still write sound code. The
example's `// SAFETY:` line is doing double duty: it is the checked demonstration of the contract,
and it shows the caller the shape of the argument they owe at their own call site.
