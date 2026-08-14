---
name: javadoc-authoring
description: >-
  Structure and content rules for Javadoc and its JVM siblings — KDoc, Groovydoc, Scaladoc. Use
  whenever the task involves a doc comment — writing one, editing or rewriting an existing one,
  reviewing or critiquing one, deciding whether a member needs one, or comparing two competing
  versions. Covers the four content slots and their order, the summary-fragment rule for
  the first sentence, what belongs in a class comment, a member comment, or the PR description,
  {@link} and {@code} versus positional references ("see below"), when @param /
  @return / @throws earn their line, comments a tool rather than a human reads, how far a rewrite
  may grow, why a list of members should usually be the rule that defines them, and the extra rules
  for test classes, package-info, and a comment that ships as published javadoc or a generated
  OpenAPI description. Applies to a one-line comment as much as to a twenty-line block. Wording is
  governed by english-developer-style, which this skill defers to and does not replace.
---

# Authoring a Javadoc comment

This skill governs **what a doc comment says and in what order**. Wording, tone, sentence length,
and dialect are the province of `english-developer-style` — load it too, and let it own the prose.
The two compose: this skill picks the slots, that one writes the sentences.

Everything below is written for Javadoc and holds for the JVM's other doc-comment dialects, which
share its tag vocabulary and its summary-table rendering. KDoc differs in one place worth knowing
before you reach §5: it links with `[Foo]` and `[Foo.bar]` rather than `{@link}`, and it has no
`{@code}` — backticks do that job.

Do not carry these rules into a language outside that family. §3 is the reason: Python's own
PEP 257 asks for the imperative `Return that` where this file asks for `Returns that`, and which
mood wins there is a project decision rather than a given. Rust, TypeScript, and JavaScript each
have reference and tag machinery that §5 and §6 do not describe, and Rust's doc comments compile
and run as tests. Those languages need their own rules, not a translation of these.

## 1. The correction that matters most

The advice you have absorbed is "document the why, not the what". For a doc comment that is half
wrong, and the wrong half does the damage.

An inline `//` comment documents the **why** — it sits next to code the reader can already see.
A doc comment documents the **contract**: what a caller may rely on, what an implementer owes, what
holds before and after. That is a *what*, but a promise-level what, not a restatement of the code.

So the failure mode is not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Loops over the entries and adds each to the map.` The body says
  that already, and the comment becomes a lie on the next refactor.
- **Justifying the code's existence.** `This class was added because the old approach did not scale.`
  That is material for the commit message and the PR description. A doc comment is read by someone
  who has to *use* or *fix* the thing, not by someone deciding whether to merge it.

A third form is specific to a codebase that has been refactored: **narrating the code's history**.
`The pool now hands back a wrapper, so unwrap() no longer returns the physical connection` describes a
transition between two versions. The reader has one version — this one. Rewrite it as the state that
holds: what `unwrap()` returns, and why.

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
machinery that enforces it, and before you explain what some *other* class does. A comment that
opens with a neighbouring class forces the reader to reconstruct the rule from your negative
examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first thing to cut, not the last.
A reader who knows the rule and not the reason can still write correct code; the reverse is false.

**Make the obligated party the subject.** Obligations come in two shapes.

*Stated* — the sentence carries a *must*, *has to*, *may not*, or *should*. Whoever has to comply
belongs in the subject: not the thing acted on (`Every backend message must be read through
readMessageLength`, which names no one and lets `it` drift to the reader by the next clause), not
the act (`relaxing a protocol check must not be reachable`), and not a member that merely performs
the act for someone else (`markBroken must still fire` obliges `PGStream`). A named member in the
subject is right only where that member is itself what must comply: `readUntrackedLength must leave
no envelope behind`. The party need not be human, but it must be something that acts — a driver, a
check, a reader; a mode constant or a configured number complies with nothing.

*Census* — a rule for the next maintainer, written instead as a report on today's call sites:
`Every site that dispatches on a message type reads the tag through this method`, `CopyData is the
one such site`. Flat indicative, no modal, so ask: **if a second such caller appeared tomorrow,
would this paragraph tell it that it is obliged?** Judge the paragraph, not the sentence — an
example is allowed to follow a law that is already correctly stated. Write the law, not the roll
call.

Watch the intransitive modal, where the party hides best: `every constant has to appear in
HARDENED`, `an unknown value must fall back to FAIL`. Nothing appears or falls back of its own
accord; name what does it.

Out of reach: an imperative, which already addresses the party (`Call it where the framed dialogue
resumes`), including one carrying rationale (`so mirror that here`); a constraint on a *value*
(`must be ≤ MAX_MESSAGE_SIZE`), which bounds a number rather than behaviour; a field comment naming
who writes or reads the field, which is the membership list §4 asks for; and an inline comment whose
next statement is the actor — `// Envelope must be fully consumed` above the `endMessage()` that
consumes it, but check that the next line really is the actor and not test setup standing between
the comment and the call it constrains.

Most members need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots to
fill a template — an absent slot is not a gap.

**Size the comment to the member.** A doc comment longer than the member it documents is not
automatically wrong — an invariant can be worth ten lines over a one-line getter — but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two
sentences of it, and only for the part a reader would otherwise get wrong. Everything past that
belongs in the commit message.

## 3. The first sentence is a summary fragment

Javadoc extracts the first sentence into the class and member summary tables, where it appears with
**no surrounding context**. Write it to stand alone there.

- **Third person, subject omitted.** `Returns the backing map.` Not `Return…`, not `This method
  returns…`.
- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it. A summary must be readable by someone
  who will never read paragraph two.
- **No self-description.** Drop `This class is responsible for…`, `Helper class that…`,
  `Utility for…`. Start with the verb.
- **Watch the terminating period.** The fragment ends at the first `.` followed by whitespace, so
  `e.g.`, `i.e.`, `vs.`, and `Dr.` truncate it. Rewrite, or pin the boundary with `{@summary …}`
  (JDK 10+).
- **One sentence.** If it takes two, the first one is not the summary.
- **A field or constant names itself first, with its unit.** `Largest declared length in bytes this
  stream accepts for an encrypted packet.` The reason the bound has that value is slot 3, however
  interesting it is — a comment that opens with the upstream implementation it mirrors leaves the
  summary table saying nothing about the constant.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  fills the summary table with a word that answers no question. Put the qualifier after the summary:
  `Rejects a message over its ceiling and breaks the connection. This is the default.`

## 4. Genre notes

### Type (class, interface, enum, record)

The class comment carries the **invariant that spans the members**. Member comments specialize it;
they do not carry it. A rule stated only on a private field is a rule the class comment is missing.

Name the collaborators the type is useless without, the threading model if there is one, and the
lifecycle if instances are not free-standing. Do not explain how a collaborator works internally —
link to it and let its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set — every check a mode governs, every method that writes a
field, every caller that must be updated — has transcribed a query. The list looks authoritative and
is stale from the first refactor, and a reader who does not find their case in it concludes the
wrong thing.

State the criterion instead: *every other check rejects a value no conforming backend can send*
beats an eight-item list of those checks, because the reader can classify a check the list has never
heard of.

A criterion has to let the reader name a member. "The ceilings whose error message offers this as a
remedy" is true by construction and tells them nothing they could not have inferred; if the honest
criterion is circular, the list was the answer after all.

There are two exceptions. A set the code itself declares — a test that partitions an enum into named
sets, a `switch` a reader must keep exhaustive — is maintained because the build fails when it
drifts; there the list **is** the contract. And a list the reader needs as vocabulary — the keys a
map may hold, the tokens a property accepts — stays, because the criterion alone ("whatever the
server marks `GUC_REPORT`") does not let anyone write code. What goes in that case is the rot: the
version label that freezes the list, and the per-item annotations nobody maintained.

### Method

Slot 2 is where the work is. Reach for these, and only when the signature does not already say them:

- nullability of parameters and of the return, when not enforced by an annotation;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- ownership of a passed or returned mutable object — does the callee retain it, may the caller
  mutate it afterwards;
- side effects the name does not advertise, including I/O and state changes;
- idempotence, thread-safety, and ordering guarantees;
- whether the method may block, for how long, and what interrupting the thread or cancelling the
  returned future does;
- error conditions, and which are checked versus programmer errors.

A method whose contract is exhausted by its name and types needs one line or nothing.

### Field and constant

Document the unit, the range, the sentinel, and who may write it. A `private static final` set
whose membership rule is non-obvious needs that rule spelled out — a reader adding an entry has no
other source of truth. When the class comment already states the rule, the field comment shrinks to
one sentence plus a link, rather than repeating it.

A limit, ceiling, or timeout documents **what it bounds**, in its own sentence. Say it positively
and say it first, before any neighbouring limit comes up: `This ceiling bounds only what the server
sends.` A comment that leaves the scope to be inferred from a contrast — `…which governs the
direction this ceiling does not` — asks the reader to subtract one limit from another and to
reconstruct the verb it left out. Both halves are facts worth stating; state them separately, this
one first.

### Inline comment

Answers "why this line", for a reader who can already see the line. Three failure modes beyond
narration:

- **Meta-commentary.** `…so say where the dialogue resumes instead` describes what the comment is
  doing. State the fact: `This is where the framed dialogue resumes.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` are the tells.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is cast to `short` belongs at the cast; repeating it inside the branch that rejects a
  negative value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`CHECKSTYLE:OFF` and its siblings; `@formatter:off`; `//noinspection`; `$NON-NLS-`; `TODO` and
`FIXME` markers; anything citing an issue or a URL. The `@SuppressWarnings` annotation is not a
comment at all — do not fold it into one.

Two placement hazards when you restructure code around them:

- **`$NON-NLS-1$` counts string literals on its own line.** The suffix is an ordinal, so reflowing a
  line, splitting it, or reordering its literals silently retargets the suppression.
- **`@formatter:off` and `CHECKSTYLE:OFF` come in pairs.** Delete or move one half and the
  suppression runs to the end of the file, or ends where nobody intended.

### Test class

A test class is met in exactly one situation: it just went red. Write for that reader.

- **Summary = the firing condition**, not the test's subject matter. `Fails when a message type is
  added without a hardened reader` beats `Tests the message type inventory`.
- **Contract = the rule the test guards**, stated positively and completely. The reader has to
  satisfy the rule, not reverse-engineer it from the assertion.
- **Use = what to do about the red build.** Which set to edit, which annotation to add, where the
  failure message says the rest.
- **State the rule as something you could assert.** `It has to stay quiet when the socket did go
  away the first time` leaves the reader guessing: not throw, not close twice, not log? Name the
  observable: `and it must not touch a socket that markBroken already closed.` If you cannot phrase
  the rule as an observation, the test probably cannot check it either.

Deliberate duplication between this class comment, a field comment, and the assertion message is
correct — each reader meets exactly one of the three. It does not extend to production code, where
the class comment and the member comment have the same reader.

### package-info.java

The entry point for the package: what it is for, which types are the way in, which are internal, and
any rule that holds across the package (naming, threading, immutability). The package's class list is
generated; a hand-written copy is the membership list all over again.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` — all three
are invisible in rendered Javadoc, silently wrong after a reorder, and unchecked by any tool. Link
the member instead.

- `{@link Type#member}` — a reference the reader may want to follow. Doclint resolves it, so a
  rename that breaks the link is caught — but only where doclint runs, and many builds never reach
  it: `-Xdoclint:none` disables it outright, and a build that never generates javadoc never checks
  the links at all. Find out which yours does before you treat a green build as proof. Prefer
  `{@link}` to a bare `{@code}` name either way, because a reference a tool *can* check beats one
  nothing can.
- `{@code someExpression}` — an identifier, literal, or snippet the reader will not navigate to, or
  a target that cannot be linked (a member of another module, a method named only informally).
- `{@value #CONSTANT}` — inlines a constant's value; better than transcribing it.
- `@see` — related API the sentence does not need to name.

`{@link #PRIVATE_FIELD}` resolves in an IDE and under `-private`, but not in a published page. That
is fine for a test class or an internal type, and a defect for public API.

**An issue or PR number is an address, not a definition.** Name the phenomenon in the comment, then
give the number so a reader can find the history: `a length taken straight off the wire sizes the
allocation (issue #4015)`. The number must not carry the meaning — `the shape of issue #4015`, `the
same format as #1231`, `the bug #4015 fixed` all read as content to someone who already knows the
ticket and as nothing to everyone else. The test: cover the number and read the sentence. If what
remains states no fact, the comment has none. A bare `see #4015` fails the same test from the other
end, and a published page reaches readers with no access to the tracker at all.

The number may open the sentence, as long as the phenomenon arrives in the same one. `The scenario
from issue #4015: a field claiming more bytes than the row envelope still holds` passes, because
covering the number leaves the failure named. It is the number's role that the rule is about, not
its position.

The same holds for a commit hash, a mailing-list thread, or a released version. It does **not** hold
for a normative source — an RFC, a protocol specification, a vendor's published documentation — which
may define a format the comment then need not restate.

**A ticket number is not a name.** `a #4015 hardening check` names nothing, and the check has a name
in the code. Use that name, and cite the number once, where the history belongs.

## 6. Tags

- **A fact that fits a tag goes in the tag.** `@return`, `@param`, and `@throws` are the first place
  a reader looks and the only place a tool renders in a parameter table. A body paragraph that
  restates one of them is dead weight: "a failure comes back as the return value rather than as a
  throw" belongs on the `@return` line, not above it.
- **`@param` / `@return` / `@throws` earn their line by adding what the signature lacks** — a unit, a
  range, a null rule, a condition. `@param name the name` is noise, and a checkstyle rule that
  demands it produces noise at scale; say so rather than filling it in.
- **`@throws` for unchecked exceptions too**, when the caller can prevent them.
- **`@implSpec`** binds subclasses, **`@implNote`** binds nobody, **`@apiNote`** addresses the caller.
  Reach for them on API that will be extended; skip them elsewhere.
- **`{@inheritDoc}`** when you add to an inherited contract. An override that narrows or strengthens
  the contract must say so; an override that merely implements it needs no comment at all.
- **`@since`** on new public API. **`@deprecated`** must name the replacement and is paired with the
  `@Deprecated` annotation.
- Tag order: `@param`, `@return`, `@throws`, `@since`, `@see`, `@deprecated`.

Markup: `<p>` opens a paragraph and is not closed in traditional Javadoc, though closing it is
harmless and some projects require it — follow the file you are in. JDK 23+ supports Markdown doc
comments (`///`); use them only in a codebase that already has them.

## 6a. When the comment ships as documentation

A doc comment on a published library's public API is not just a comment. It reaches people through
the generated javadoc pages, and often through a second surface — an OpenAPI `description` that
springdoc lifts out of it, a generated client, a `--help` string.

**The reader changes, and that is the whole section.** They are working against your API from the
outside. They cannot open the code, cannot read the private member you were thinking of, and have
no `git log`. Three rules follow.

1. **Know which surface the comment lands on, because the markup differs.** On a generated javadoc
   page `{@link}` is a working hyperlink and `<p>` is a paragraph. In a description a generator
   lifts into YAML or JSON, both arrive as literal text. Write plain sentences for the second case,
   and check what your generator does before assuming the first.
2. **A reference the reader cannot follow has to be spelled out.** `{@link #PRIVATE_FIELD}` and
   anything else that resolves only under `-private` (§5) points nowhere on a published page. Name
   the rule instead of linking to the thing that states it.
3. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a
   parameter accepts, the keys a map may hold — that list is the only source this reader has, so
   replacing it with a criterion is allowed only when they can apply the criterion *without opening
   anything*. §4's own warning applies at full force: if the honest criterion is circular, the list
   was the answer, and the repair is to complete it and verify every member against the code in the
   same edit. An incomplete list shipped as documentation is worse than no list.

Where the generated output is committed — an OpenAPI spec in the repository, a checked-in client —
editing one of these is not a comment-only change. Regenerate and commit the result, or the drift
check fails. Because every edit costs that diff, the bar rises — but it rises for **rewording**,
not for **enriching**. A synonym or a smoother clause is churn that ships. A fact the description
does not carry and its reader needs is worth the diff every time, even when every sentence already
there is true. "It is correct as written" answers the first case and not the second.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one
by going stale. Skip it for:

- a member whose name and types are the whole contract;
- an override that adds nothing to the inherited contract;
- a private helper whose single call site makes it obvious;
- anything the code says better, which is most narration.

The corollary: a public member with a non-obvious contract is not optional, however self-evident the
name looks to the person who just wrote it.

## 7a. Editing an existing comment

Most of the time you are not writing a comment, you are rewriting one. Different job, different
failure mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old comment did not carry — a unit, a side effect, a nullability rule, an invariant. Name that
  fact to yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **Check every identifier the old comment names.** A comment written before a refactor cites modes,
  constants, and methods that no longer exist. `{@code warn}` for a mode that was deleted compiles,
  renders, and lies; `{@link #WARN}` would at least fail wherever doclint runs (§5). Grep each one,
  and convert what you verify.
- **When you lift a rule into the class comment, go and cut it from the member.** The member keeps
  the one sentence that specializes the rule, plus the link. Two full statements of the same rule
  is the most common outcome of a good structural edit and the easiest to miss, because each of the
  two reads well on its own.
- **Deleting is an edit.** A list of callers, a rejected alternative, a cost estimate, a reference
  to the PR that introduced the code — cutting these is usually the highest-value change in the
  diff, even though the result looks like less work.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule
  governs the body, not the first sentence. `Wrapper around X that implements some basic
  primitives` stays broken until someone rewrites it, and "I had no new fact to add" is not a
  reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot
  be verified as comment-only, and the verification is what makes a large sweep safe.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

Start from this. The new version will read better. It was written second, by someone who had just
finished understanding the code. Reading forward confirms that impression and finds nothing, because a
fact that vanished leaves no trace in the text that replaced it. So the work runs backwards: you read
the **old** version carefully first, and the verdict comes last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one nullability rule, one side effect, one ordering or threading
constraint, one lifecycle obligation, one named collaborator, one link target, or one stated default.
A topic sentence is not a fact, and neither is a restatement of the signature.

Compare facts, not sentences. At sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Three
defenses hold:

- the fact was wrong;
- the fact moved to the class comment, and you can point at the sentence that now carries it;
- the fact moved into a `@param`, `@return`, or `@throws` tag, where §6 says it belongs.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is what someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A first sentence repaired under §3 pays for itself and is exempt. Restructuring at
equal length is free and needs no justification at all.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the old comment, or to a contract it links to. A claim that traces
to none of the three is invented, however plausible it sounds, and plausible is the dangerous case: a
wrong invariant in a doc comment is a wrong invariant a caller will build on. The commit message is
not a source. It records what someone meant to do, and the comment has to describe what the code does.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer attention
now and costs the next reader a `git blame` later. §7a already says the old wording stays; here you go
looking for the places where it did not.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Three
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is
  the characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else.
  No build step catches this, which makes it the most valuable thing a comparison pass finds.

A comment something other than a human reads is out of scope for all three — see §4 for the list and
for what moving one breaks.

**7. Prove the code did not move.**

A sweep that edits comments across many files is only reviewable if the claim "comments only" is
mechanical rather than asserted. Parse each file before and after with comments discarded, and
compare the results:

```java
ParserConfiguration cfg = new ParserConfiguration().setAttributeComments(false);
CompilationUnit cu = new JavaParser(cfg).parse(src).getResult().orElseThrow();
String stripped = cu.toString();  // no comments to differ, so only code differences survive
```

Any difference means the pass touched code, and the pass is wrong until it is explained.

**8. Say which finding it is, not whether the comment got better.**

Each outcome names the repair it obliges. Naming it is what makes two people comparing the same pair
reach the same answer.

| Finding | Repair |
| --------- | -------- |
| Lost fact | Restore it, or defend the absence |
| Unpaid growth | Cut back to the old length, or name the fact |
| Unsupported claim | Verify it against the code, or delete it |
| Stale identifier | Fix what it names, and convert it to `{@link}` (§5) |
| Duplicated rule | Cut the copy the class comment now carries (§7a) |
| Churn | Restore the old wording |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Stale inline comment | Rewrite it from the code |
| Reworded tool marker | Restore its exact text and position (§4) |

### The case this section exists for

**Before** — one line, carrying two facts.

```java
/** Waits up to 30 seconds for the backend to acknowledge the cancel, then breaks the connection. */
```

**After** — the same comment, restructured.

```java
/**
 * Waits for the backend to acknowledge the cancel request.
 *
 * <p>The connection is broken if the acknowledgement does not arrive.</p>
 */
```

The rewrite is better on every count §3 measures. The summary stands alone, the consequence gets its
own paragraph instead of trailing a comma, and the sentence no longer runs to two clauses. It also
dropped the timeout, and nothing in the new text tells the reader that one exists. Step 2 offers a
defense here — cite the property the value now comes from — and the rewrite takes none of them.

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Does the first sentence stand alone in a summary table, with no term this comment introduces?
- Does the first sentence terminate where you think it does, or does an `e.g.` cut it short?
- Is the contract stated positively and in one place, before any mechanism?
- Could a reader satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Is any rationale here actually PR-description material?
- Any sentence describing a previous version of the code — `now`, `no longer`, `used to`?
- Does the comment explain another class's internals instead of linking to it?
- Any positional reference — `below`, `above`, `the following`, `the other way`?
- Does a limit say what it bounds, rather than only what some neighbouring limit bounds?
- Cover every issue, PR, or commit number: does each surrounding sentence still state a fact?
- Any `{@code Foo}` that should be `{@link Foo}`?
- Does every `@param` / `@return` / `@throws` add something the signature does not?
- Would deleting the whole comment lose anything?
- Is every `CHECKSTYLE:OFF`, `@formatter:off`, `//noinspection`, or `$NON-NLS-` marker still worded
  and placed exactly as it was?
- If the comment ships as documentation (§6a): can its reader follow every reference in it without
  opening the code, and did you regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the class comment, or on a `@return` / `@param` line?
- Any list that a criterion would replace, or that find-usages already answers?
- Does every name the old comment mentioned still exist?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first grows, because facts were
missing; the second shrinks, because they were not. Do not read either one as the target shape.

Both are lifted from a real codebase, which makes them a hazard: an example you can recognize in the
wild is an example you will paste instead of derive. A rewrite that matches this file word for word
says nothing about whether the rules were applied to the comment in front of you.

### A test class, where facts were missing

Both versions document a test that fails when a new backend message type is added without a hardened
reader. Abridged from pgjdbc PR #4016.

**Before** — opens with an invented term, then with a neighbouring class; the rule it guards appears
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

**After** — summary is the firing condition; the contract is stated positively and first; the
neighbouring class is compressed to its limitation; the reader is told what to do and where to look.

```java
/**
 * Fails when a backend message type is added without a hardened reader.
 *
 * <p>Every backend reader must declare a message envelope: take the length through
 * {@code PGStream.readMessageLength} (or {@code readFixedMessageLength} /
 * {@code readPreAuthMessageLength}), bound any length it reads from the wire, and close
 * the envelope with {@code endMessage}. A reader that skips this leaves the stream off a
 * message boundary, which is the desync class of bug issue #4015 reported.</p>
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

The example above grew. Most edits are the other way: nothing is missing, and the comment has
accreted a list that a tool answers better.

**Before** — enumerates the methods that touch the field. That list is find-usages, transcribed by
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

**After** — states the invariant the list was an approximation of, and the one consumer the field
exists for.

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

Same number of lines, and the reader can now answer a question the list could not: what happens to
`position` in a method nobody has written yet (§4, the membership rule).
