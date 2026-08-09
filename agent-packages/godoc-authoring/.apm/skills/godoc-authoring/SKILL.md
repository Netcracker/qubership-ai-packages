---
name: godoc-authoring
description: >-
  Structure and content rules for Go doc comments and inline comments. Use whenever the task
  involves a comment in Go source — writing a new one, editing or rewriting an existing one,
  reviewing or critiquing one, deciding whether a declaration needs one at all, or comparing two
  competing versions. Covers the four content slots and their order, why the first sentence names
  the thing it documents, the exception Kubernetes API types make to that rule, doc links versus
  bare names, what stands in for tags Go does not have, why a list of members should usually be the rule that
  defines them, how far a rewrite may grow, comments that a tool rather than a human reads
  (//go:, //nolint, +kubebuilder), and the extra rules for tests, package comments, and CRD field
  descriptions that ship to users. Applies to a one-line comment as much as to a twenty-line block.
  Language and wording are governed by english-developer-style, which this skill defers to and does
  not replace.
---

# Authoring a Go doc comment

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect are the province of `english-developer-style` — load it too, and let it own the prose. The
two compose: this skill picks the slots, that one writes the sentences.

Everything here is written for Go. Conventions carried in from another language's doc comments go
wrong in three specific places, so do not translate them in your head: Go puts the identifier's name
in the first sentence (§3), its references are an unchecked bracket syntax (§5), and it has no tags
at all (§6).

`gofmt` owns the *layout* of a doc comment (indentation of code blocks, list markers, blank-line
normalization) and rewrites it on every save. Never hand-align a doc comment; write the content and
let the formatter place it.

## 1. The correction that matters most

The advice you have absorbed is "document the why, not the what". For a doc comment that is half
wrong, and the wrong half does the damage.

An inline `//` comment inside a function documents the **why** — it sits next to code the reader can
already see. A doc comment on a declaration documents the **contract**: what a caller may rely on,
what an implementer owes, what holds before and after. That is a *what*, but a promise-level what,
not a restatement of the code.

So the failure mode is not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Loops over the entries and adds each to the map.` The body says
  that already, and the comment becomes a lie on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the boilerplate every endpoint
  shared.` That is material for the commit message and the pull request. A doc comment is read by
  someone who has to *use* or *fix* the thing, not by someone deciding whether to merge it.

A third form is specific to a codebase that has been refactored: **narrating the code's history**.
`Successful reconciles now carry a RequeueAfter, so the delay can no longer distinguish done from
retrying` describes a transition between two versions. The reader has one version — this one.
Rewrite it as the state that holds: what the delay cannot do, and why.

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
machinery that enforces it, and before you explain what some *other* package does. A comment that
opens with a neighbouring type forces the reader to reconstruct the rule from your negative
examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first thing to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

Most declarations need slots 1 and 2 only. A getter needs slot 1. Do not manufacture the other slots
to fill a template — an absent slot is not a gap.

**Size the comment to the declaration.** A doc comment longer than the function it documents is not
automatically wrong — an invariant can be worth ten lines over a three-line method — but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two sentences
of it, and only for the part a reader would otherwise get wrong. Everything past that belongs in the
commit message.

## 3. The first sentence names the thing it documents

Go's convention is unusually specific, and it is the rule most often lost when a comment is written
from habit: **a doc comment begins with the name being declared.**

```go
// SetCredentials atomically replaces the Basic Auth credentials used for all
// subsequent requests. Safe for concurrent use.
func (c *AggregatorClient) SetCredentials(username, password string) { … }
```

Not `Atomically replaces…` and not `This method replaces…`. The name leads, followed by a
present-tense third-person verb.

- **Package comment**: `// Package client provides an HTTP client for the dbaas-aggregator REST API.`
- **Command** (`package main`): the binary's name leads — `// Aggregator-mock emulates the
  dbaas-aggregator endpoints the operator calls.`
- **Test function**: the exception — see the test genre note in §4.
- **Blank identifier** (`var _ Interface = (*T)(nil)`): nothing to lead with; state the assertion.

The rest of the summary rule:

- **No term this comment invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until paragraph two defines it. A summary must be readable by someone who
  will never read paragraph two.
- **No self-description.** Drop `Helper type that…`, `Utility for…`. The name, then the verb.
- **Watch the terminating period — on a package-level declaration.** Tooling extracts the first
  sentence of a package, func, type, const, or var as a one-line summary: package listings,
  `go list -f {{.Doc}}`, pkg.go.dev search results. `go/doc.Synopsis` ends that sentence at the first
  `.` followed by a space, so `e.g.`, `i.e.`, and `vs.` truncate it. Nothing lets you pin the
  boundary — rewrite instead.

  **A struct field is exempt.** Nothing extracts a synopsis from one: `go doc` prints a field comment
  whole, and so do pkg.go.dev and a generated CRD description. Moving an `e.g.` out of a field
  comment's first sentence fixes nothing, and on a field that ships as a CRD description it is churn
  that ships (§6a).
- **One sentence.** If it takes two, the first one is not the summary.
- **A constant or variable names itself first, with its unit.** `maxPacketLen is the largest
  encrypted packet this stream accepts, in bytes.` The reason the bound has that value is slot 3,
  however interesting it is.
- **A qualifier is not a summary.** `Default.`, `Internal.`, `Deprecated.` as the opening sentence
  answers no question. Put the qualifier after the summary.

### The Kubernetes API exception

In a type whose fields are serialized into an API — a CRD spec or status, or any type a client reads
through `kubectl explain` — the field comment opens with the **JSON name**, not the Go name:

```go
    // observedGeneration reflects the .metadata.generation that was last processed.
    ObservedGeneration int64 `json:"observedGeneration,omitempty"`
```

The Kubernetes API conventions require this, and it is the right call: the comment is rendered to
someone writing YAML, who has never seen `ObservedGeneration`. Follow the file. Go-visible
declarations in the same package — exported constants, functions, interfaces — keep the Go name.

## 4. Genre notes

### Type (struct, interface, named type)

The type comment carries the **invariant that spans the fields and methods**. Member comments
specialize it; they do not carry it. A rule stated only on an unexported field is a rule the type
comment is missing.

Name the collaborators the type is useless without, the concurrency model if there is one, and the
lifecycle if the zero value is not ready to use. "The zero value is ready to use" is itself a
contract worth one clause when it holds. Do not explain how a collaborator works internally — link to
it and let its own comment do that job.

### The membership rule, not the membership list

A comment that lists the members of a set — every reason a condition may carry, every function that
writes a field, every caller that must be updated — has transcribed a query. The list looks
authoritative and is stale from the first refactor, and a reader who does not find their case in it
concludes the wrong thing.

State the criterion instead: *every other check rejects a value no conforming backend can send* beats
an eight-item list of those checks, because the reader can classify a check the list has never heard
of.

A criterion has to let the reader name a member. "The ceilings whose error message offers this as a
remedy" is true by construction and tells them nothing they could not have inferred; if the honest
criterion is circular, the list was the answer after all.

There are two exceptions. A set the code itself declares — a `switch` a reader must keep exhaustive,
a test that partitions a set of constants — is maintained because the build or the test fails when it
drifts; there the list **is** the contract. And a list the reader needs as vocabulary — the
environment variables a command reads, the keys a map may hold — stays, because the criterion alone
does not let anyone write code. What goes in that case is the rot: the version label that freezes the
list, and the per-item annotations nobody maintained.

The exception is wider for a comment that ships as API documentation (§6a), because that reader
cannot open the code to enumerate the set themselves. It is not unlimited: an incomplete list shipped
as documentation is worse than no list, so if you keep one, verify every member against the code in
the same edit.

### Function and method

Slot 2 is where the work is. Reach for these, and only when the signature does not already say them:

- whether a returned pointer, slice, or map may be nil, and what nil means;
- whether a nil argument is accepted;
- units, ranges, encodings, time bases (`milliseconds since the epoch`, `UTF-8 bytes`, `0-based`);
- ownership of a passed or returned mutable value — does the callee retain it, may the caller mutate
  it afterwards;
- side effects the name does not advertise, including I/O and state changes;
- idempotence, goroutine-safety, and ordering guarantees;
- whether the function may block, and what cancelling `ctx` does;
- which errors a caller is expected to match with `errors.Is` / `errors.As`, and which are
  programmer errors that panic.

There is no tag for a parameter. Name it in prose, spelled exactly as in the signature, at the point
where its contract matters: `body is marshaled as JSON when non-nil`. Do not walk the parameter list
in order restating types — that is the signature, transcribed.

Nor is there one for a result. Named results are the closest equivalent and often do the job outright:
`func CreateDatabase(…) (pending bool, err error)` needs one clause about what `pending` means, not a
paragraph. Reach for named results when a bare `(bool, error)` would force the comment to explain
which is which.

A function whose contract is exhausted by its name and types needs one line or nothing.

### Field, constant, and variable

Document the unit, the range, the sentinel, and who may write it. An unexported package-level
variable whose invariant is non-obvious needs that invariant spelled out — a reader adding a write
has no other source of truth. When the type comment already states the rule, the field comment
shrinks to one sentence plus a link, rather than repeating it.

A `const` block with a shared rule takes one comment above the block and short ones inside it, not
the same sentence eight times.

### Inline comment

Answers "why this line", for a reader who can already see the line. Three failure modes beyond
narration:

- **Meta-commentary.** `…so gate on the conditions instead` describes what the comment is doing.
  State the fact: `the conditions identify a terminal state; the requeue delay does not.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` are the tells.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is converted to `int32` belongs at the conversion; repeating it inside the branch that
  rejects a negative value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`//go:build`, `//go:generate`, `//go:embed`, `//go:noinline` and the rest of the `//go:` family;
`//nolint:…`; `// +kubebuilder:…`, `// +optional`, `// +listType`, `// +groupName` and other
controller-gen markers; `// +kubebuilder:scaffold:…` injection points; `// Code generated … DO NOT
EDIT.`; `TODO` and `FIXME` markers; anything citing an issue or a URL.

Two Go-specific hazards when you restructure a comment that contains them:

- **A field's markers must stay in the same comment group as the field.** controller-gen reads the
  doc-comment group immediately above a struct field. Insert a blank line — even a bare `//` — between
  a `// +kubebuilder:validation:…` marker and the field, and the whole group detaches: measured on
  controller-gen 0.20.1, a blank line above `Type string` dropped `minLength`, the `XValidation` rule,
  **and the field's description** from the generated CRD, and nothing failed. Markers go at the end of
  the block, adjacent to the field.

  Type-level markers are the opposite case and look alarming for no reason. `+kubebuilder:object:root`,
  `+kubebuilder:printcolumn`, `+kubebuilder:resource`, and a root `XValidation` conventionally sit in
  their own group *above* the doc comment, separated by a blank line, and controller-gen picks them up
  from there. Do not "fix" that separation.
- **A directive in the doc position becomes the doc.** `go/doc` strips the `//go:` family, but not
  `//nolint:`. A `//nolint:gocyclo` line directly above `func main` is that function's entire
  rendered documentation. Put it on its own after the prose, or accept that the declaration has no
  doc comment.

### Test file

A test is met in exactly one situation: it just went red. Write for that reader.

Test functions are not rendered by `go doc` or pkg.go.dev, so the name-first rule of §3 has no tooling
behind it here and the firing condition wins:

```go
// A header the caller set by hand must survive the retry unchanged.
func TestClient_RetryPreservesCallerHeaders(t *testing.T) { … }
```

- **Summary = the rule the test guards**, stated positively and completely, as something you could
  assert. `It has to stay quiet when the socket did go away` leaves the reader guessing: not panic,
  not close twice, not log? Name the observable. If you cannot phrase the rule as an observation, the
  test probably cannot check it either.
- **Use = what to do about the red build.** Which set to edit, which case to add, where the failure
  message says the rest.
- **A table-driven case's `name` field is a comment.** It is the string the reader sees in the
  failure output, so it names the case's condition, not its ordinal.

Deliberate duplication between the test's comment, a helper's comment, and the failure message is
correct — each reader meets exactly one of the three. It does not extend to production code, where
the type comment and the method comment have the same reader.

### Package comment

One per package, in the file that carries it — a `doc.go` when the text is long enough to crowd out
code, or the package's principal file when it is not. Two files with package comments in one package
is a defect no compiler catches.

It is the entry point: what the package is for, which types are the way in, which are internal, and
any rule that holds across the package (naming, concurrency, error conventions). The package's
declaration list is generated; a hand-written copy is the membership list all over again.

A command's package comment is user documentation: what the binary does, its flags, its environment
variables, its exit codes. There the vocabulary exception of §4 applies in full.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` — all three
are invisible in rendered documentation, silently wrong after a reorder, and unchecked by any tool.
Name the identifier instead.

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
text `[Foo]`, and neither `go vet` nor a stock `golangci-lint` run reports it. Nothing you can switch
on will, so the verification burden of §7a sits entirely on you.

Use a doc link for a reference the reader may want to follow. For an identifier they will not
navigate to — a JSON field name, a literal, a shell command, a symbol in a service you do not import
— plain text is correct; Go doc comments have no inline code markup, and backticks render as
backticks. Set off a longer snippet as an indented block instead.

Cite an issue only alongside the name of the phenomenon: `the desync class of bug that #4015 fixed`
survives the tracker; a bare `see #4015` does not.

## 6. Structure

Go has no tags at all. §4 covers what stands in for documenting a parameter and a result. The rest:

- **`Deprecated:`** starts its own paragraph, at the end of the comment, and must name the
  replacement. Tooling reads it: `staticcheck` SA1019 and editors flag callers. Nothing else in a Go
  doc comment is machine-interpreted this way, so do not invent siblings for it.
- **Errors** go in prose, naming the sentinel or type a caller matches: `Returns an
  *AggregatorError for any non-2xx response.` A panic is worth a sentence when the caller can
  prevent it.
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

1. **Every reference has to be spelled out.** "See the controller" points nowhere. A doc link renders
   as literal brackets. A symbol name is a word they cannot look up. If the sentence names something,
   it has to define it in the same breath or not name it at all.
2. **§4's vocabulary exception is wider here, and the criterion test is stricter.** A list of the
   values a field may hold, the reasons a condition may carry, the keys a map accepts — that list is
   the only source this reader has, so replacing it with a criterion is only allowed when they can
   apply the criterion *without opening anything*. "Reason names the outcome for this kind of
   resource" fails that test: it is true, it is circular, and it leaves the reader with nothing.
   §4's own warning applies at full force — if the honest criterion is circular, the list was the
   answer, and the repair is to complete the list and verify every member against the code in the
   same edit.
3. **No markup.** Go doc comments have no inline code syntax, so backticks, `<p>`, and Markdown all
   reach the user as themselves, inside a YAML string. Write plain sentences.

Then, and only then, the mechanics: **editing one of these is not a comment-only change.** Regenerate
(`make manifests generate` in a stock kubebuilder project, plus whatever target syncs the Helm
chart's CRDs) and commit the result, or the drift check in CI fails. Plan it as its own commit;
mixing it with prose-only edits buries a two-line rewrite in sixteen files of generated YAML.

Because every edit costs that diff, the bar rises — but it rises for **rewording**, not for
**enriching**, and confusing the two is how this section does damage. A dash swapped for an em dash,
a synonym, a smoother clause: churn that ships, and the diff is the argument against it. A fact this
description does not carry and its reader needs: worth the diff every time, even when every sentence
already there is true. "It is correct as written" answers the first case and not the second, so when
you catch yourself declining an edit on cost grounds, say which one it is. A description that is
accurate and thin is still a description that sends someone to read the controller.

The same reasoning applies to any comment a generator turns into published output: an OpenAPI
description, a generated client, a flag's help text.

## 7. When to write nothing

A comment that would not confuse a future reader by its absence is a comment that will mislead one by
going stale. Skip it for:

- a declaration whose name and types are the whole contract;
- a method that adds nothing to the interface's documented contract;
- an unexported helper whose single call site makes it obvious;
- anything the code says better, which is most narration.

The corollary: an exported declaration with a non-obvious contract is not optional, however
self-evident the name looks to the person who just wrote it. Go's convention is that every exported
declaration has a doc comment; that convention buys nothing when the comment restates the name.

## 7a. Editing an existing comment

Most of the time you are not writing a comment, you are rewriting one. Different job, different
failure mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the old
  comment did not carry — a unit, a side effect, a nil rule, an invariant. Name that fact to
  yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **Check every identifier the old comment names.** A comment written before a refactor cites
  constants, fields, and functions that no longer exist. Go will not tell you: an identifier in prose
  compiles, renders, and lies, and so does a doc link (§5). Grep each one. Convert what you verify
  into a doc link, so the next reader at least gets a hyperlink that visibly fails.
- **When you lift a rule into the type comment, go and cut it from the member.** The member keeps the
  one sentence that specializes the rule, plus the link. Two full statements of the same rule is the
  most common outcome of a good structural edit and the easiest to miss, because each of the two
  reads well on its own.
- **Deleting is an edit.** A list of callers, a rejected alternative, a cost estimate, a reference to
  the change that introduced the code — cutting these is usually the highest-value change in the
  diff, even though the result looks like less work.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule governs
  the body, not the first sentence. A comment that opens with `This function is a wrapper around X`
  stays broken until someone rewrites it, and "I had no new fact to add" is not a reason to leave it.
- **Do not move code.** A comment edit that also renames a variable or reorders a statement cannot be
  verified as comment-only, and the verification is what makes a large sweep safe.

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

Start from this. The new version will read better. It was written second, by someone who had just
finished understanding the code. Reading forward confirms that impression and finds nothing, because a
fact that vanished leaves no trace in the text that replaced it. So the work runs backwards: you read
the **old** version carefully first, and the verdict comes last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one nil rule, one side effect, one ordering or concurrency
constraint, one lifecycle obligation, one named collaborator, one link target, or one stated default.
A topic sentence is not a fact, and neither is a restatement of the signature.

Compare facts, not sentences. At sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Three
defenses hold:

- the fact was wrong;
- the fact moved to the type or package comment, and you can point at the sentence that now carries
  it;
- the fact moved to the declaration itself — a named result, a renamed parameter, a sentinel error
  the signature now exposes.

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
looking for the places where it did not. In a file that regenerates (§6a) the cost is higher, because
the churn arrives with a YAML diff attached.

**6. Inline comments run on a different rubric.**

A new `//` comment has no earlier version, so steps 1 through 3 have nothing to work on. Three
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for doc comments; it is
  the characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else.
  No build step catches this, which makes it the most valuable thing a comparison pass finds.

**7. Prove the code did not move.**

A sweep that edits comments across many files is only reviewable if the claim "comments only" is
mechanical rather than asserted. Parse each file before and after without comments and compare:

```go
fset := token.NewFileSet()
f, _ := parser.ParseFile(fset, path, src, 0) // no ParseComments: comments are dropped
printer.Fprint(&buf, fset, f)
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
| Stale identifier | Fix what it names, and make it a doc link (§5) |
| Duplicated rule | Cut the copy the type comment now carries (§7a) |
| Churn | Restore the old wording |
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Stale inline comment | Rewrite it from the code |
| Detached marker | Move it back into the declaration's comment group (§4) |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Does the first sentence begin with the name of the declaration — or, for an API field, its JSON
  name?
- Does the first sentence stand alone, with no term this comment introduces, and does it terminate
  where you think it does, or does an `e.g.` cut it short?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the comment alone?
- Is any rationale here actually commit-message material?
- Any sentence describing a previous version of the code — `now`, `no longer`, `used to`?
- Does the comment explain another package's internals instead of naming it?
- Any positional reference — `below`, `above`, `the following`?
- Any bare name that should be a doc link, and does every doc link still resolve?
- Does every parameter named in prose still exist, spelled that way?
- Would deleting the whole comment lose anything?
- Is every `//go:`, `//nolint`, or `+kubebuilder` marker still in the comment group it needs to be in?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old comment did not?
- Does any statement here also appear in the type or package comment?
- Any list that a criterion would replace, or that the reader's editor already answers?
- If the file generates output (§6a): did you regenerate, and is the edit worth the regeneration diff?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the facts were
already there. The second grows, because one was missing. Do not read either one as the target shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a
sweeper can recognize in the wild is an example it will paste instead of derive, and a rewrite that
matches this file word for word tells you nothing about whether the rules were applied.

### An inline comment that narrated the code's history

**Before** — the rule is in there, wrapped in an account of what changed.

```go
    // Reset the budget on success only. Failures used to reset it too, which meant
    // a flapping backend could never exhaust its retries; we now let the budget
    // drain and refill it only when a call actually goes through.
    if err == nil {
        budget.reset()
    }
```

**After** — same rule, stated as what holds.

```go
    // The budget refills on success alone, so a flapping backend drains it instead
    // of holding it topped up.
    if err == nil {
        budget.reset()
    }
```

Fact ledger: *the budget resets only on success* — present. *A backend that keeps failing must be able
to exhaust it* — present, and now stated as a property of the code rather than as a change to it.
Nothing absent, one line shorter, and `used to` / `we now` are gone.

### A set whose membership rule was missing

**Before** — names the set and stops. A reader deciding whether to add `409 Conflict` has nothing to
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

**After** — states the criterion the five entries are an instance of.

```go
// retryableStatus holds the statuses where replaying the identical request can
// still succeed: the server rejected the attempt, not its content. A status that
// answers something about the request itself — 400, 404, 409, 422 — never belongs
// here, however transient its cause looks, because the retry would ask the same
// question and get the same answer.
//
// [Client.Do] returns [ErrGivenUp] once the attempt budget is spent, whatever
// status ended the last try.
var retryableStatus = map[int]struct{}{ … }
```

The rewrite grew by six lines and paid for them with two facts the one-liner did not carry: the
criterion, which lets a reader classify a status the list has never heard of, and the sentinel a
caller matches when the retries run out. `409` earns its place in the exclusion list because it is
the case a reader gets wrong — it looks transient and is not.
