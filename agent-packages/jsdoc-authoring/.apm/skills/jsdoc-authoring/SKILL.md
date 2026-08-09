---
name: jsdoc-authoring
description: >-
  Structure and content rules for JSDoc and TSDoc comments and the inline comments beside them, in
  JavaScript and TypeScript. Use whenever the task involves such a comment — writing one, editing or
  rewriting an existing one, reviewing or critiquing one, deciding whether a declaration needs one,
  or comparing two versions. Covers the four content slots and their order, where the summary
  section ends, the one rule that inverts between TypeScript and checked JavaScript (a type in a tag
  is noise in one and code in the other), {@link} and what actually checks it, which tags earn their
  line, comments a tool rather than a human reads (@ts-expect-error, eslint-disable-next-line,
  #__PURE__, release tags), how far a rewrite may grow, why a list of members should usually be the
  rule that defines them, and the extra rules for tests, module docs, and a comment that ships in a
  .d.ts. A one-line comment is in scope. Wording is governed by english-developer-style, which this
  skill defers to and does not replace.
---

# Authoring a JSDoc or TSDoc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect are the province of `english-developer-style` — load it too, and let it own the prose. The
two compose: this skill picks the slots, that one writes the sentences.

It covers both languages, because they share one comment syntax, one tag vocabulary, one Markdown
body, and one language service behind the editor hover most readers actually meet the comment in.
TSDoc is the standardized subset that API Extractor and TypeDoc read; JSDoc is the older, looser
superset. Where a rule differs between the two dialects, this file says so. Where a rule differs
between a `.ts` file and a checked `.js` file — which happens exactly once, and it inverts — that is
§3a, and it is the most important section here for an agent that writes both.

Conventions carried in from another language's doc comments go wrong in three specific places, so do
not translate them in your head: the summary ends at the first block tag rather than at the first
period (§3), Markdown is the markup (§5), and a tag that states a type is either redundant or
load-bearing depending on the file it sits in (§3a, §6).

**The formatter does not own the layout.** Measured on Prettier 3.9.6, a doc comment is re-indented
to a single leading `*` column and otherwise left alone — prose is not reflowed, inner runs of
spaces are not collapsed, and a line past `--print-width` is not wrapped. Every line break inside a
doc comment is your decision, and it survives every format run, including the stale ones.

## 1. The correction that matters most

The advice you have absorbed is "document the why, not the what". For a doc comment that is half
wrong, and the wrong half does the damage.

An inline `//` comment documents the **why** — it sits next to code the reader can already see. A
doc comment documents the **contract**: what a caller may rely on, what an implementer owes, what
holds before and after. That is a *what*, but a promise-level what, not a restatement of the code.

So the failure mode is not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Maps over the entries and pushes each into the result array.`
  The body says that already, and the comment becomes a lie on the next refactor.
- **Justifying the code's existence.** `This hook was extracted because three components repeated
  the same effect.` That is material for the commit message and the pull request. A doc comment is
  read by someone who has to *use* or *fix* the thing, not by someone deciding whether to merge it.

A third form is specific to a codebase that has been refactored: **narrating the code's history**.
`This now returns a Promise, so callers no longer get the value synchronously` describes a
transition between two versions. The reader has one version — this one. Rewrite it as the state that
holds: what the function returns, and when the value is available.

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
opens with a neighbouring class forces the reader to reconstruct the rule from your negative
examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first thing to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

Most declarations need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots
to fill a template — an absent slot is not a gap.

**Size the comment to the declaration.** A doc comment longer than the function it documents is not
automatically wrong — an invariant can be worth ten lines over a one-line accessor — but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two
sentences of it, and only for the part a reader would otherwise get wrong. Everything past that
belongs in the commit message.

## 3. The first sentence, and where the summary ends

Write the first sentence in the third person with the subject omitted: `Returns the backing map.`
Not `Return…`, not `This function returns…`, and not `parseHeaders returns…`. The name is already on
the line below and in every listing that renders the comment.

**The summary is a section, not a sentence.** Everything before the first block tag is the summary,
and `@remarks` is the tag that ends it deliberately. Tooling that builds an index of many API items
shows the summary and nothing else, so the boundary you care about is the first block tag, not the
first period. Two consequences, and a first-sentence habit predicts the opposite of both:

- `e.g.` and `i.e.` do **not** truncate anything. Leave them alone.
- A four-paragraph comment with no block tag is a four-paragraph summary, and every index page in
  the generated docs carries all four. Keep the summary to one sentence and push the rest behind
  `@remarks`.

JSDoc's vocabulary spells the same idea the other way round: the whole prose block is the
description, and `@summary` is the tag that marks the short line an index should show. Use whichever
one the repository already uses (§6), but do not leave four paragraphs unmarked in either.

The rest of the summary rule carries over unchanged:

- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it. A summary must be readable by someone
  who will never read paragraph two.
- **No self-description.** Drop `This class is responsible for…`, `Helper that…`, `Utility for…`.
  Start with the verb.
- **One sentence.** If it takes two, the first one is not the summary.
- **A property or constant names its unit, not its type.** `Largest payload this stream accepts, in
  bytes.` The type is already in the signature; the unit never is. The reason the bound has that
  value is slot 3, however interesting it is.
- **A qualifier is not a summary.** `Internal.`, `Deprecated.`, `Default.` as the opening sentence
  fills every index page with a word that answers no question. Put the qualifier after the summary,
  or in the tag that exists for it.

## 3a. The rule that inverts: a type in a tag

This is the one place where the same comment is correct in one file and wrong in the next, and the
file extension decides, not taste.

**In TypeScript, a type in a tag is noise.** `@param {string} name` and `@returns {number}` restate
the signature the reader is already looking at, and nothing checks them. Measured on TypeScript
5.9.3 and 7.0.2: a `.ts` file whose `@param` names a parameter that does not exist compiles clean,
and so does an invented `@nosuchtag`. Write `@param name - what the caller must pass that the type
does not say`, and let the type be the type.

**In JavaScript with `checkJs` (or a `// @ts-check` pragma), a type in a tag is code.** The same
compiler reads `@param {string}`, `@returns`, `@type`, and `@typedef` as the file's type
annotations. Measured on the same two compilers, in a `.js` file: `len(42)` against
`@param {string} name` is `error TS2345`, and a `@param` whose name no longer matches the parameter
is `error TS8024`.

Three things follow, and they are the reason this section is not a footnote:

1. **Editing a type tag in a checked `.js` file is a code change.** It is not covered by "comments
   only", it does not belong in a comment sweep, and §7b's proof does not see it (step 7).
2. **The tag that is noise in `.ts` is the contract in `.js`.** Deleting `@param {string}` from a
   checked `.js` file deletes a type. Do not carry a TypeScript habit into a `.js` file without
   checking whether the project checks it — `checkJs` in `tsconfig.json`, or `// @ts-check` at the
   top of the file.
3. **In `.ts`, an identifier in a tag rots in silence.** Nothing tells you. §7a's instruction to
   grep every name the old comment mentions applies at full force there, and only in `.js` do you
   get a compiler that does part of it for you.

## 4. Genre notes

### Class, interface, and type alias

The type's comment carries the **invariant that spans the members**. Member comments specialize it;
they do not carry it. A rule stated only on a private field is a rule the type's comment is missing.

Name the collaborators the type is useless without, the concurrency or reentrancy model if there is
one, and the lifecycle if instances are not free-standing: which factory constructs it, whether
`new` is allowed, whether it must be disposed, and what using it after disposal does.

Do not explain how a collaborator works internally — link to it and let its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set — every event a component emits, every function that
writes a field, every caller that must be updated — has transcribed a query. The list looks
authoritative and is stale from the first refactor, and a reader who does not find their case in it
concludes the wrong thing.

State the criterion instead: *every other status rejects a request no conforming server can answer*
beats an eight-item list of those statuses, because the reader can classify a status the list has
never heard of.

A criterion has to let the reader name a member. "The options whose error message offers this as a
remedy" is true by construction and tells them nothing they could not have inferred; if the honest
criterion is circular, the list was the answer after all.

There are two exceptions. A set the code itself declares — a union type, a `const` object the code
derives a type from, a `switch` a reader must keep exhaustive — is maintained because the build
fails when it drifts; there the list **is** the contract, and duplicating it in prose is the defect.
And a list the reader needs as vocabulary — the keys an options object accepts, the values an
environment variable takes — stays, because the criterion alone does not let anyone write code. What
goes in that case is the rot: the version label that freezes the list, and the per-item annotations
nobody maintained.

### Function and method

Slot 2 is where the work is, and the types answer much of it on their own, so the bar for a sentence
is high: reach for these, and only when the signature does not already say them.

- whether a returned array, object, or `Map` is a live view or a copy, and whether the caller may
  mutate it;
- whether an argument is retained after the call, and whether the callee mutates it;
- what `undefined` means where the type allows it, and how it differs from an absent property;
- whether the function throws synchronously or returns a rejected promise, and which errors a caller
  is expected to match — by `instanceof`, by a `code` property, or through `error.cause`;
- whether a callback runs synchronously or on a later tick, and how many times;
- whether the method may be detached from its receiver and passed as a callback, or needs its
  `this`;
- what an `AbortSignal` does: whether abort rejects, resolves, or only stops future work;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- idempotence and ordering guarantees, and whether a returned iterable may be consumed more than
  once;
- side effects the name does not advertise, including I/O, storage, and module-level state.

A function whose contract is exhausted by its name and types needs one line or nothing.

**Overloads document themselves separately.** In TypeScript each overload signature carries its own
doc comment and the implementation signature's comment is not shown to callers — a contract written
only above the implementation reaches nobody. In JavaScript the same shape is `@overload` blocks.

### Property, field, and constant

Document the unit, the range, the sentinel, and who may write it. A module-level constant whose
membership rule is non-obvious needs that rule spelled out — a reader adding an entry has no other
source of truth. When the type's comment already states the rule, the property comment shrinks to
one sentence plus a link, rather than repeating it.

State a default with `@defaultValue` (`@default` in JSDoc) rather than in prose, so the tooling can
render it in the same table as the type.

### Inline comment

Answers "why this line", for a reader who can already see the line. Three failure modes beyond
narration:

- **Meta-commentary.** `…so check the flag here instead` describes what the comment is doing. State
  the fact: `the flag is only settled after hydration.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` are the tells.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is coerced with `Number()` belongs at the coercion; repeating it inside the branch that
  rejects `NaN` splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording, reflowing, or moving them changes behavior or destroys a record:

`// @ts-check`, `// @ts-nocheck`, `// @ts-ignore`, `// @ts-expect-error`; `/* eslint-disable */`,
`// eslint-disable-next-line <rule>`, `// biome-ignore lint/<rule>: <reason>`; `// prettier-ignore`;
`/* istanbul ignore next */`, `/* v8 ignore next */`; `/*#__PURE__*/`;
`/* webpackChunkName: "…" */` and `/* @vite-ignore */`; `/// <reference types="…" />`;
`/** @jsx … */` and `/** @jsxImportSource … */`; `//# sourceMappingURL=`; `/** @type {…} */` on a
config export; `// Code generated … DO NOT EDIT.`; `TODO` and `FIXME` markers; anything citing an
issue or a URL.

Four placement hazards when you restructure code around them:

- **A directive applies to the next line, so reflowing retargets it.** Splitting a call across lines
  moves the reported position; inserting anything between the directive and its statement orphans
  it. `// @ts-expect-error` at least fails loudly when it stops covering an error — measured, that
  is `error TS2578: Unused '@ts-expect-error' directive`. `// @ts-ignore` never reports anything,
  and an unused `// eslint-disable-next-line` is caught only where
  `linterOptions.reportUnusedDisableDirectives` is left on.
- **`/*#__PURE__*/` annotates the call expression, not the statement.** It has to sit immediately
  before the call. Moving it to its own line above the statement is the natural thing to do while
  tidying, and it silently drops the tree-shaking hint that kept the call out of the bundle.
- **A `/** @type {…} */` cast belongs to the parenthesized expression that follows it.** Detach it
  and it becomes an ordinary doc comment on the statement — in a checked file, the cast is gone and
  the types change (§3a).
- **A blank line does not detach a doc comment.** Measured on TypeScript 5.9.3 and 7.0.2,
  declaration emit kept a doc comment that was separated from its declaration by a blank line. Do
  not "repair" such a gap on the theory that it is broken, and do not introduce one either: it reads
  as detached to every human who opens the file.

### Test file

A test is met in exactly one situation: it just went red. Write for that reader.

- **Summary = the rule the test guards**, stated positively and completely, as something you could
  assert. `It has to stay quiet when the socket did go away` leaves the reader guessing: not throw,
  not retry, not log? Name the observable. If you cannot phrase the rule as an observation, the test
  probably cannot check it either.
- **Use = what to do about the red build.** Which fixture to edit, which case to add, where the
  failure message says the rest.
- **The `describe` and `it` strings are the comment.** They are what the reader sees in the failure
  output, before any file is opened, so they name the condition rather than the subject:
  `it('rejects with AbortError when the signal fires mid-flight')` beats `it('handles abort')`, and
  both beat `it('works')`. A doc comment above a test that repeats its `it` string has said
  everything twice and nothing once.

Deliberate duplication between a test's comment, a helper's comment, and the failure message is
correct — each reader meets exactly one of the three. It does not extend to production code, where
the type's comment and the member's comment have the same reader.

### Module documentation

One comment per entry point, at the top of the file, tagged `@packageDocumentation` for TSDoc or
`@module` for JSDoc. Without the tag it is read as documentation for whatever declaration happens to
follow it.

It is the entry point: what the module is for, which exports are the way in, which are internal, and
any rule that holds across the module (naming, error conventions, what must be disposed). The export
list is generated; a hand-written copy is the membership list all over again.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following options` — all three
are invisible in a rendered page and in an editor hover, silently wrong after a reorder, and
unchecked by most toolchains. Name the target instead.

| Form | Refers to |
| --- | --- |
| `` `identifier` `` | code the reader will not navigate to: a literal, a CLI flag, a JSON key |
| `{@link Thing}` | a declaration the reader may want to follow |
| `{@link Thing.member}` | a member of a declaration |
| `{@link Thing.member \| custom text}` | the same, with the sentence's own wording (TSDoc spelling) |
| `{@link https://example.com \| the spec}` | an external page |

Markdown is the markup: backticks for inline code, a blank `*` line for a paragraph break, a fenced
block for a sample. There is no `{@code}` and no `<p>`, and writing either one ships the tag itself
to the reader. JSDoc's older link spellings (`{@link Thing|text}` with no spaces, and
`{@link Thing text}`) still parse in many tools; follow the file you are in rather than converting a
codebase mid-edit.

**Know what checks your links, because it is not the compiler.** Measured on TypeScript 5.9.3 and
7.0.2, `{@link NoSuchThing}` compiles clean and emits nothing. What does check:

- **TypeDoc** warns through `validation.invalidLink`, which is on by default, and fails the build
  only under `treatValidationWarningsAsErrors`.
- **API Extractor** reports `ae-unresolved-link` for a declaration reference it cannot resolve.
- **Your editor** resolves the link in the hover, which is where most readers meet it — and a broken
  one shows as literal text there.

None of these runs unless your build runs it. Find out which of the three your project has before
you treat a green build as proof, and prefer a `{@link}` to a bare backticked name either way,
because a reference something *can* check beats one nothing can.

Cite an issue only alongside the name of the phenomenon: `the desync class of bug that #4015 fixed`
survives the tracker; a bare `see #4015` does not.

## 6. Tags

**Pick one vocabulary per repository and stay in it.** TSDoc is the small standardized set that
API Extractor and TypeDoc agree on, and `eslint-plugin-tsdoc` enforces its syntax. JSDoc is the
larger, looser one that `eslint-plugin-jsdoc` checks. They overlap but disagree on spellings
(`@returns` versus `@return`, `@defaultValue` versus `@default`, `@typeParam` versus `@template`),
and a file that mixes them renders wrong somewhere.

- **A tag earns its line by adding what the signature lacks.** `@param value - The value` is noise
  in any language and worse here, because the type sits three characters away in the same hover.
  A lint rule that demands a tag per parameter produces that noise at scale; say so rather than
  filling it in.
- **`@param name - description`.** The hyphen is TSDoc's separator between the name and the prose,
  and the generators expect it.
- **`@returns` when the summary does not already say it.** `Returns the backing map.` followed by
  `@returns the backing map` is one sentence billed twice.
- **`@throws`** is not in TSDoc's standard set but is widely rendered; use it to say what a caller
  matches on, not merely that something can fail. In an async function, say whether the failure
  arrives as a rejection.
- **`@remarks`** ends the summary section (§3). Everything the index page should not carry goes
  after it.
- **`@example`** earns its place on published API and almost nowhere else. It is a fenced code
  block, and it goes stale like any other code that nothing compiles.
- **`@deprecated`** must name the replacement. Editors strike through every call site, which makes
  it one of the few tags a machine acts on.
- **`@typeParam T - …`** (`@template` in JSDoc) when a type parameter has a constraint the reader
  must satisfy that the `extends` clause does not express.
- **`@inheritDoc`** when you add nothing to an inherited contract. An override that narrows or
  strengthens one must say so instead.
- **Release tags** — `@public`, `@beta`, `@alpha`, `@internal` — are build inputs, not notes (§6a).
- Tag order: summary, `@remarks`, `@typeParam`, `@param`, `@returns`, `@throws`, `@example`,
  `@defaultValue`, `@see`, `@deprecated`, release tag last.

Two syntax hazards that have nothing to do with content:

- **A line that starts with `@` is read as a block tag.** A scoped package name or an email address
  at the start of a line becomes a bogus tag and swallows the paragraph under it. Wrap it in
  backticks, or move it off the line start.
- **`*/` ends the comment, wherever it appears.** A glob, a regular expression, or a code sample
  containing `*/` terminates the doc comment early and turns the rest of it into a syntax error, or
  worse, into code.

## 6a. When the comment ships as documentation

A doc comment on an exported declaration is not just a comment. Declaration emit copies it verbatim
into the `.d.ts` that ships in the package — measured on TypeScript 5.9.3 and 7.0.2 — and for most
consumers that hover **is** the documentation, whether or not you also publish a site. The same text
may reach a second surface: a TypeDoc page, an API Extractor report, an OpenAPI or JSON Schema
`description` a generator lifts out of it, a `--help` string.

**The reader changes, and that is the whole section.** They are working against your API from the
outside. They cannot open the code, cannot resolve a link to something you did not export, and have
no `git log`. Three rules follow.

1. **Know which surface the comment lands on, because the markup differs.** In an editor hover and
   on a TypeDoc page, Markdown renders and `{@link}` is a hyperlink. In a `description` a generator
   lifts into YAML or JSON, backticks, pipes, and `{@link}` all arrive as literal text. Write plain
   sentences for the second case, and check what your generator does before assuming the first.
2. **A reference the reader cannot follow has to be spelled out.** A `{@link}` to a declaration the
   package does not export resolves in your editor and points nowhere for them; API Extractor names
   the related defect `ae-forgotten-export` when such a type leaks into the public signature. Name
   the rule instead of linking to the thing that states it.
3. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values an
   option accepts, the keys a result object may hold — that list is the only source this reader has,
   so replacing it with a criterion is allowed only when they can apply the criterion *without
   opening anything*. §4's own warning applies at full force: if the honest criterion is circular,
   the list was the answer, and the repair is to complete it and verify every member against the
   code in the same edit. An incomplete list shipped as documentation is worse than no list.

Then the mechanics, and here the two dialects part company sharply.

**A release tag is a build switch.** Measured on TypeScript 5.9.3 and 7.0.2, `--stripInternal`
removes an `@internal` declaration from the emitted `.d.ts` entirely — not its comment, the whole
declaration. API Extractor keys its trimmed rollups and its checked-in `.api.md` report off the same
tags. Adding or removing one is an API change that happens to be spelled as a comment edit, and it
belongs in its own commit with the regenerated output.

**Prose is cheaper than a release tag, but not free.** An `.api.md` report is designed to diff only
on contractual change, so rewording a summary does not touch it. A committed OpenAPI spec or JSON
Schema generated from the same comments does diff on every word. Where the generated output is
committed, regenerate and commit it, or the drift check fails.

Because some edits cost that diff, the bar rises — but it rises for **rewording**, not for
**enriching**. A synonym or a smoother clause is churn that ships. A fact the description does not
carry and its reader needs is worth the diff every time, even when every sentence already there is
true. "It is correct as written" answers the first case and not the second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- a declaration whose name and types are the whole contract — which in TypeScript is more
  declarations than in a language with weaker types, because the reader sees the types in the same
  hover;
- an override or implementation that adds nothing to the documented contract;
- a component prop whose name and type say it;
- a non-exported helper whose single call site makes it obvious;
- anything the code says better, which is most narration.

The corollary: an exported declaration with a non-obvious contract is not optional, however
self-evident the name looks to the person who just wrote it.

A rule that demands a doc comment on everything — `jsdoc/require-jsdoc`, or TypeDoc's
`validation.notDocumented` pointed at every reflection — manufactures exactly the comments this
section exists to prevent. Scope it to the public API or turn it off; do not satisfy it.

## 7a. Editing an existing comment

Most of the time you are not writing a comment, you are rewriting one. Different job, different
failure mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry — a unit, a side effect, a mutation rule, an invariant. Name that fact
  to yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **Check every identifier the old comment names.** A comment written before a refactor cites
  options, constants, and methods that no longer exist. In a `.ts` file nothing tells you: a stale
  name in prose, in backticks, or in a `{@link}` compiles and renders (§3a, §5). Grep each one, and
  convert what you verify into a `{@link}`, so the next reader at least gets a link that visibly
  fails.
- **When you lift a rule into the type's comment, go and cut it from the member.** The member keeps
  the one sentence that specializes the rule, plus the link. Two full statements of the same rule is
  the most common outcome of a good structural edit and the easiest to miss, because each of the two
  reads well on its own.
- **Deleting is an edit.** A list of callers, a rejected alternative, a benchmark number, a
  reference to the pull request that introduced the code — cutting these is usually the
  highest-value change in the diff, even though the result looks like less work.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule
  governs the body, not the first sentence. A four-paragraph summary with no `@remarks`, or one that
  opens `This function is a wrapper around X`, stays broken until someone rewrites it, and "I had no
  new fact to add" is not a reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot
  be verified as comment-only, and the verification is what makes a large sweep safe. In a checked
  `.js` file, editing a type tag is moving code (§3a).

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

Start from this. The new version will read better. It was written second, by someone who had just
finished understanding the code. Reading forward confirms that impression and finds nothing, because
a fact that vanished leaves no trace in the text that replaced it. So the work runs backwards: you
read the **old** version carefully first, and the verdict comes last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one mutation or ownership rule, one side effect, one ordering or
timing constraint, one lifecycle obligation, one named collaborator, one link target, or one stated
default. A topic sentence is not a fact, and neither is a restatement of the signature.

Compare facts, not sentences. At sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Three
defenses hold:

- the fact was wrong;
- the fact moved to the type's comment or the module comment, and you can point at the sentence that
  now carries it;
- the fact moved into a tag where §6 says it belongs, or into the signature itself — a narrowed
  type, a renamed parameter, a default the declaration now states.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is what someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first sentence repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification at all.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the old comment, or to a contract it links to. A claim that
traces to none of the three is invented, however plausible it sounds, and plausible is the dangerous
case: a wrong invariant in a doc comment is a wrong invariant a caller will build on. The commit
message is not a source. It records what someone meant to do, and the comment has to describe what
the code does.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer
attention now and costs the next reader a `git blame` later. §7a already says the old wording stays;
here you go looking for the places where it did not. Where the comment feeds a committed generated
file (§6a), the churn arrives with that file's diff attached.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Three
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is
  the characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something
  else. No build step catches this, which makes it the most valuable thing a comparison pass finds.

A comment something other than a human reads is out of scope for all three — see §4 for the list and
for what moving one breaks.

**7. Prove the code did not move — and in `.js`, prove the types did not either.**

A sweep that edits comments across many files is only reviewable if the claim "comments only" is
mechanical rather than asserted. Parse each file before and after and re-print it without comments:

```javascript
const ts = require("typescript");
const src = require("node:fs").readFileSync(path, "utf8");
const sf = ts.createSourceFile(path, src, ts.ScriptTarget.Latest, false);
// identical output before and after means no executable code moved
process.stdout.write(ts.createPrinter({ removeComments: true }).printFile(sf));
```

Any difference means the pass touched code, and the pass is wrong until it is explained.

**This proof is complete for `.ts` and incomplete for checked `.js`.** The printer discards exactly
what §3a says is load-bearing there: run it over a `.js` file and `@param {string}` and
`/** @type {…} */` vanish, so a sweep that changed both would still print identically. The second
leg is a diagnostic comparison — `tsc --noEmit` before and after must report the same set. Without
it, the strip-and-compare result is evidence about the wrong file type.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it is what makes two people comparing the same pair
reach the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and make it a `{@link}` (§5) |
| Duplicated rule | Cut the copy the type's comment now carries (§7a) |
| Churn | Restore the old wording |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Stale inline comment | Rewrite it from the code |
| Summary with no `@remarks` boundary | Cut it to one sentence and move the rest (§3) |
| Retargeted directive | Put it back adjacent to the line it suppresses (§4) |
| Type tag changed in a checked `.js` file | Treat it as a code change and review it as one (§3a) |
| Release tag added or removed | Regenerate the shipped output and split the commit (§6a) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the first sentence third person with the subject omitted, standing alone, with no term this
  comment introduces?
- Does the summary end where you meant it to, or does a missing `@remarks` push four paragraphs onto
  every index page?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Is any rationale here actually commit-message material?
- Any sentence describing a previous version of the code — `now`, `no longer`, `used to`?
- Does the comment explain another module's internals instead of linking to it?
- Any positional reference — `below`, `above`, `the following`?
- Any backticked name that should be a `{@link}`, and does anything in this build check the links?
- Does every tag add something the signature does not — and in a `.ts` file, does any tag carry a
  type that the signature already states?
- If this is a `.js` file: is `checkJs` or `// @ts-check` on, and did this edit change a type (§3a)?
- Would deleting the whole comment lose anything?
- Is every `@ts-expect-error`, `eslint-disable-next-line`, `/*#__PURE__*/`, and `@type` cast still
  worded and placed exactly as it was?
- If the comment ships as documentation (§6a): can its reader follow every reference without opening
  the code, and did you regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the type's comment or on a `@param` line?
- Any list that a criterion would replace, or that the reader's editor already answers?
- Does every name the old comment mentioned still exist?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the facts were
already there. The second grows, because they were missing. Do not read either one as the target
shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a
sweeper can recognize in the wild is an example it will paste instead of derive, and a rewrite that
matches this file word for word tells you nothing about whether the rules were applied.

### A TypeScript method, where the tags restated the types

**Before** — four tags, no contract. Every one of them is readable off the signature, and the one
thing a caller can get wrong is not stated anywhere.

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

**After** — the summary carries what the tags were spending four lines on, and the body carries the
two facts the signature cannot: the case rule and the ownership of the returned array.

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

What changed, slot by slot: the summary stopped restating the method name and gained the ordering
guarantee (§3); `@param` and `@returns` went, because a type is not a fact in TypeScript (§3a, §6);
the `{string[]}` in `@returns` went with them; and slot 2 appeared, carrying case-insensitivity,
aliasing, and the empty-versus-`undefined` rule (§4). Two lines longer, and every added line names a
fact the reader would otherwise discover by breaking something.

### A checked JavaScript function, where the failure contract was missing

The file below is `.js` under `checkJs`, so its type tags are the signature (§3a). Watch them come
through the rewrite untouched: they are code, and this is a comment edit.

**Before** — narrates the implementation, and leaves out everything a caller has to handle.

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

**After** — states what the caller may rely on, what reaches them on failure, and what abort does.

```javascript
/**
 * Sends a GET request, retrying a failed attempt with exponential backoff.
 *
 * Only a network failure and a 5xx response are retried; a 4xx comes back as-is on the first
 * attempt, because replaying it would ask the same question and get the same answer. Every failure
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

The rewrite grew by six lines and paid for them with four facts the original did not carry: which
responses are retried and why, that failures arrive as rejections with a `cause` chain, what abort
does to a pending backoff, and that `attempts` counts tries rather than retries — the off-by-one a
reader gets wrong precisely because the name reads either way. `Loops over the attempts` went,
because the body already said it (§1).

The three tag lines are the ones to check twice in review. Their prose grew, which is an ordinary
comment edit; their braces did not change, which is what makes the diff safe to read as one. Had a
`{number}` become a `{number | string}` in the same pass, that would be a signature change wearing a
comment's clothes, and §7b's strip-and-compare proof would not have caught it.
