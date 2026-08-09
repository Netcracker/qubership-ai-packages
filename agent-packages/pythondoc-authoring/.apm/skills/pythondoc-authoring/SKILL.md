---
name: pythondoc-authoring
description: >-
  Structure and content rules for Python docstrings and inline comments. Use whenever the task
  involves a comment in Python source — writing a new docstring, editing or rewriting an existing
  one, reviewing or critiquing one, deciding whether an object needs one at all, or comparing two
  competing versions. Covers the four content slots and their order, the one-line summary and the
  imperative-versus-descriptive mood dispute, why the docstring must be the first statement, what
  the annotations already say so the docstring must not, the three section dialects
  (reStructuredText, Google, NumPy), cross-references nothing checks, doctest examples that run as
  tests, comments a tool rather than a human reads (# type:, # noqa, # fmt:, # pragma), how far a
  rewrite may grow, and the extra rules for tests, packages, and a docstring that ships as --help
  text or an OpenAPI description. A one-line comment is in scope. Wording is governed by
  english-developer-style, which this skill defers to and does not replace.
---

# Authoring a Python docstring

This skill governs **what a comment says and in what order**. Wording, tone, sentence length, and
dialect are the province of `english-developer-style` — load it too, and let it own the prose. The
two compose: this skill picks the slots, that one writes the sentences.

Two facts about Python change the job at the root, and both come back in later sections.

**A docstring is a runtime object, not source text.** It is `__doc__`; `help()` renders it,
`doctest` executes the examples in it, a CLI framework can print it as `--help`, and `python -OO`
deletes it outright. Every one of those is a surface an edit reaches.

**No formatter owns its prose.** `black` and `ruff format` re-indent a docstring's body and strip its
trailing whitespace, but they never rewrap it — measured on ruff 0.14. The line breaks are yours to
place, and `E501` counts them.

## 1. The correction that matters most

The advice you have absorbed is "document the why, not the what". For a docstring that is half
wrong, and the wrong half does the damage.

An inline `#` comment documents the **why** — it sits next to code the reader can already see. A
docstring documents the **contract**: what a caller may rely on, what an implementer owes, what
holds before and after. That is a *what*, but a promise-level what, not a restatement of the code.

So the failure mode is not "explains what the code does". It is either of these:

- **Narrating the implementation.** `Loops over the rows and adds each to the index.` The body says
  that already, and the docstring becomes a lie on the next refactor.
- **Justifying the code's existence.** `This helper centralizes the retry logic every client
  copied.` That is material for the commit message and the pull request. A docstring is read by
  someone who has to *use* or *fix* the thing, not by someone deciding whether to merge it.

A third is Python's own: **restating the annotations**. `Args: timeout (float): the timeout in
seconds.` on `def fetch(timeout: float)` carries one fact, the unit, and pays for it with a line the
reader has to sift. Annotations are the signature; §6 says what a parameter line has to add before it
earns its place.

A fourth is specific to a codebase that has been refactored: **narrating the code's history.**
`The session now returns a copy, so callers can no longer mutate the cached row` describes a
transition between two versions. The reader has one version — this one. Rewrite it as the state that
holds: what the session returns, and what the caller may do with it.

## 2. The four slots

A docstring has at most four slots, and they go in this order.

| # | Slot | Answers | Skip when |
| --- | ------ | --------- | ----------- |
| 1 | **Summary** | What is this, or when does it fire? | Never — always present |
| 2 | **Contract** | What may a caller rely on? What does an implementer owe? | The signature genuinely says all of it |
| 3 | **Rationale** | Why is it this way, when the way is surprising? | Nothing is surprising |
| 4 | **Use** | What does the reader do next? | The contract already implies the action |

Two rules govern the order.

**Contract before mechanism.** State the rule the reader must satisfy before you explain the
machinery that enforces it, and before you explain what some *other* module does. A docstring that
opens with a neighbouring class forces the reader to reconstruct the rule from your negative
examples. State it positively, in one place, first.

**When only one slot fits, keep the contract.** Rationale is the first thing to cut, not the last. A
reader who knows the rule and not the reason can still write correct code; the reverse is false.

Most objects need slots 1 and 2 only. A property needs slot 1. Do not manufacture the other slots to
fill a template — an absent slot is not a gap, and a `Returns:` section that repeats the summary is
the commonest way one gets manufactured.

**Size the docstring to the object.** A docstring longer than the function it documents is not
automatically wrong — an invariant can be worth ten lines over a three-line method — but it is a
signal to re-read. When you check, the surplus is almost always rationale: keep at most two sentences
of it, and only for the part a reader would otherwise get wrong. Everything past that belongs in the
commit message.

## 3. The first line

PEP 257 puts the summary on **one physical line**, ending in a period, and the linters enforce that
shape: `D200`, `D205`, `D400`, and `D415` between them require a one-line summary, a period, and a
blank line before the body. So the length limit is not advice. A summary that does not fit on one
line inside the project's line budget is a summary that is doing too much.

Whether that line sits beside the opening quotes or on the line below is the project's business.
Ruff's `D212` and `D213` take opposite sides and cannot both be on; the `google` convention selects
`D212`, and `numpy` and `pep257` select neither — measured on ruff 0.14.

### The mood is a project decision, not yours

Python's two most-cited guides contradict each other here, and both are live:

- **PEP 257** prescribes the imperative: `Return the rows matching the query.` Not `Returns…`.
- **Google's Python style guide** prescribes the descriptive third person: `Returns the rows
  matching the query.`

Tooling takes sides. Ruff's `D401` flags a descriptive summary under the default `pep257`
convention, and `convention = "google"` switches `D401` off — measured on ruff 0.14, where the same
`Fetches rows from a table.` docstring fails under `pep257` and passes under `google`.

Decide in this order, and never mix moods inside a project:

1. the `convention` in `pyproject.toml` (`[tool.ruff.lint.pydocstyle]`, `[tool.pydocstyle]`), if
   there is one;
1. the docstrings already in the file, if they agree with each other;
1. PEP 257's imperative, which is both the language's own document and pydocstyle's default.

### The rest of the summary rule

- **No term this docstring invents.** `Guards the inventory of backend messages` fails, because
  "inventory" means nothing until the body defines it. A summary must be readable by someone who
  will never read the body — which is what `help()` and an API index show them.
- **No self-description.** Drop `This function…`, `Helper that…`, `Utility for…`. Start with the
  verb.
- **One sentence.** If it takes two, the first one is not the summary.
- **A property, an attribute, or a constant is a noun phrase, with its unit.** `Largest encrypted
  packet this stream accepts, in bytes.` A property is documented as the value it exposes, not as
  the method that computes it. The reason the bound has that value is slot 3, however interesting.
- **A qualifier is not a summary.** `Internal.`, `Deprecated.`, `Default.` as the opening line
  answers no question. Put the qualifier after the summary.

### The first-statement rule, and three ways to lose the docstring

A docstring is the **first statement** of a module, class, or function. Nothing warns when it stops
being one:

- **An f-string is not a docstring.** `f"""Fetch {name}."""` in the docstring position leaves
  `__doc__` as `None` — measured on CPython 3.9 and 3.13. Interpolate nothing; a docstring is a
  constant.
- **Anything above it demotes it.** A comment is fine — comments are not statements — but an
  assignment, an import, or a `from __future__ import annotations` above the docstring means the
  module has no docstring at all. The future import goes *after* it.
- **`python -OO` deletes every docstring in the process.** Never make one load-bearing: a CLI whose
  `--help` comes from `__doc__` prints nothing under `-OO`, and `inspect.getdoc` returns `None`
  where it would otherwise have inherited a parent's text.

One more mechanical trap: a docstring containing a backslash needs a raw string, opened with `r"""`.
Without it, `"""Match \d+."""` raises `SyntaxWarning: invalid escape sequence '\d'` on Python 3.12
and later. Regexes, Windows paths, and LaTeX in a NumPy-style docstring are where this bites.

## 4. Genre notes

### Module

First statement of the file, before the imports. It is the entry point: what the module is for,
which objects are the way in, which are private, and any rule that holds across the file (naming,
concurrency, error conventions). A hand-written list of the module's own functions is the membership
list all over again — `__all__` and the generated API page both answer it better.

A module that is also a script documents the invocation: what it does, its arguments, its
environment variables, its exit codes. There the vocabulary exception below applies in full.

### Package (`__init__.py`)

One docstring for the package, in `__init__.py`: what the package is for, which submodule a reader
starts with, and which are internal. Resist restating each submodule's own docstring — the reader
who needs that detail is one import away from it.

### Class

The class docstring carries the **invariant that spans the attributes and methods**. Method
docstrings specialize it; they do not carry it. A rule stated only on a private attribute is a rule
the class docstring is missing.

Name the collaborators the class is useless without, the concurrency model if there is one, and the
lifecycle if an instance is not usable straight after construction. Do not explain how a
collaborator works internally — reference it and let its own docstring do that job.

**Constructor arguments go in one place, and the project picks which.** The class docstring or
`__init__`, never both: Sphinx's `autoclass_content` and mkdocstrings' `merge_init_into_class` each
decide which one reaches the rendered page, so the copy in the other place is invisible there and
stale everywhere. Follow the file.

A dataclass, an attrs class, or a Pydantic model documents its fields where the project already
does — an `Attributes:` section, or an attribute docstring under each field (see below). Picking the
second style for one model in a package that uses the first produces a page with half its fields
described.

### The membership rule, not the membership list

A docstring that lists the members of a set — every exception a call may raise, every function that
writes an attribute, every caller that must be updated — has transcribed a query. The list looks
authoritative and is stale from the first refactor, and a reader who does not find their case in it
concludes the wrong thing.

State the criterion instead: *every other check rejects a value no conforming client can send* beats
an eight-item list of those checks, because the reader can classify a check the list has never heard
of.

A criterion has to let the reader name a member. "The limits whose error message offers this as a
remedy" is true by construction and tells them nothing they could not have inferred; if the honest
criterion is circular, the list was the answer after all.

There are two exceptions. A set the code itself declares — an `__all__`, a `match` a reader must
keep exhaustive, a test that partitions an `Enum` — is maintained because the build or the test
fails when it drifts; there the list **is** the contract. And a list the reader needs as
vocabulary — the environment variables a command reads, the keys a payload may hold — stays, because
the criterion alone does not let anyone write code. What goes in that case is the rot: the version
label that freezes the list, and the per-item annotations nobody maintained.

The exception is wider for a docstring that ships as documentation (§6a), because that reader cannot
open the code to enumerate the set themselves. It is not unlimited: an incomplete list shipped as
documentation is worse than no list, so if you keep one, verify every member against the code in the
same edit.

### Function and method

Slot 2 is where the work is. Reach for these, and only when the signature and its annotations do not
already say them:

- what a `None` return means, and whether a returned container is a live view of internal state or a
  copy the caller owns;
- whether an argument is mutated, and whether the callee keeps a reference to it after returning;
- units, ranges, encodings, time bases (`seconds`, `UTF-8 bytes`, `0-based`), and `bytes` versus
  `str` where the annotation is `str | bytes`;
- side effects the name does not advertise, including I/O, global state, and anything that happens at
  import time;
- **laziness**, which annotations hide: a function returning `Iterator[Row]` may have done nothing
  yet, may be single-pass, and may hold a connection open until it is exhausted;
- idempotence, thread-safety, and ordering guarantees;
- whether the call blocks, whether an `async def` blocks the event loop anyway, and what cancelling
  the task does;
- resource obligations: what the caller must close, and whether the object is meant to be used as a
  context manager;
- which exceptions a caller is expected to catch — nothing in Python declares them, so the docstring
  is the only record (§6).

Either name a parameter in prose, spelled exactly as in the signature, at the point where its
contract matters — `body is encoded as JSON when it is not None` — or use the project's section
dialect (§6). Do not walk the parameter list in order restating annotations; that is the signature,
transcribed.

A function whose contract is exhausted by its name and annotations needs one line or nothing.

### Generator, coroutine, and context manager

Three contracts the signature will not carry. A generator says whether it is single-pass, what
closing it early does, and what it holds open while suspended. A coroutine says what cancellation
leaves behind — a half-written file, an open connection, a released lock. A context manager says
what `__exit__` does with an exception: suppress it, roll back, or let it through.

### Attribute, property, and constant

Document the unit, the range, the sentinel, and who may write it. A module-level constant whose
invariant is non-obvious needs that invariant spelled out — a reader adding a value has no other
source of truth.

An **attribute docstring** — a bare string literal on the line after an assignment — is read by
Sphinx autodoc, by mkdocstrings, and by Pydantic when `use_attribute_docstrings` is on. The
interpreter is not among them: a variable has no `__doc__`, so `help()` and `inspect.getdoc` never
show it. Use it where the project's renderer reads it, and do not expect it at runtime.

A block of related constants takes one docstring above the block and short ones inside it, not the
same sentence eight times.

### Exception class

Document the situation that raises it and the attributes a handler reads off it — "Raised when the
broker rejects the frame; `code` carries the broker's reason" is the whole job. A subclass that adds
no attribute and no new situation needs no docstring; the base class's arrives through
`inspect.getdoc` (§7).

### Inline comment

Answers "why this line", for a reader who can already see the line. PEP 8 owns the shape: `#` then
one space, and at least two spaces before an inline `#` on a statement line. Three failure modes
beyond narration:

- **Meta-commentary.** `…so check the flag first instead` describes what the comment is doing. State
  the fact: `the flag is the only signal that survives a reconnect.`
- **History.** See §1. `now`, `no longer`, `used to`, `instead of the old` are the tells.
- **Placement.** The comment goes where the surprise is, not where the consequence lands. The reason
  a value is coerced to `int` belongs at the coercion; repeating it inside the branch that rejects a
  negative value splits one thought across two places.

### Comments a tool reads, not a human

Leave these alone. Rewording them changes behavior or destroys a record:

`# type:` and `# type: ignore[…]`; `# noqa: …`; `# pragma: no cover`; `# fmt: off` / `# fmt: on`;
`# isort: skip` and `# isort: off`; `# pylint: disable=…`; `# mypy: …` and `# ruff: noqa` file
directives; `# doctest: +ELLIPSIS` and its siblings; the shebang and any `# -*- coding: -*-` line;
`TODO` and `FIXME` markers; anything citing an issue or a URL.

Three Python-specific hazards when you restructure a file that contains them:

- **A file-wide `# type: ignore` must precede every statement, including the module docstring.**
  Measured on mypy 1.18: with `# type: ignore` on line 1 the file is silenced; insert a module
  docstring above it and mypy reports the file's errors again. Nothing warns. If a file needs both,
  the ignore comes first and the docstring follows it — or use a `# mypy: ignore-errors` comment,
  which is not position-sensitive in the same way.
- **`# noqa` and `# type: ignore` are scoped to their physical line.** Rewrapping a call across two
  lines, or splitting one statement into two, moves the suppression off the line that needed it and
  onto one that did not.
- **`# fmt: off` and `# fmt: on` come in pairs.** Delete or move one half and the suppressed region
  runs to the end of the file, or ends where nobody intended.

### Test file

A test is met in exactly one situation: it just went red. Write for that reader.

pytest's progress line and its short summary print the node id and nothing else, so **the test's name
is its summary** — `test_retry_preserves_caller_headers`, not `test_headers_2`. The docstring is not
wasted, though: pytest prints the failing function's source in the traceback, docstring included, so
it is the first prose the reader meets after the assertion.

- **Docstring = the rule the test guards**, stated positively and completely, as something you could
  assert. `It has to stay quiet when the socket did go away` leaves the reader guessing: not raise,
  not close twice, not log? Name the observable. If you cannot phrase the rule as an observation, the
  test probably cannot check it either.
- **Use = what to do about the red build.** Which fixture to look at, which case to add, where the
  assertion message says the rest.
- **A `pytest.mark.parametrize` `ids=` entry is a comment.** It is the string the reader sees in the
  node id, so it names the case's condition, not its ordinal.
- **An assertion message is read before either.** Put the observable there; the docstring carries the
  rule behind it.

Deliberate duplication between the test's docstring, a fixture's docstring, and the assertion message
is correct — each reader meets exactly one of the three. It does not extend to production code, where
the class docstring and the method docstring have the same reader.

## 5. References

**Never point at a position.** `see below`, `the list above`, `the following constants` — all three
are invisible in a rendered page, silently wrong after a reorder, and unchecked by any tool. Name the
object instead.

Python has no cross-reference syntax of its own. The renderer supplies one, so **find out which
renderer the project uses before you write a reference**:

- **Sphinx** — RST, and Google or NumPy sections through napoleon. A role such as `:func:`, `:meth:`,
  `:class:`, `:attr:`, `:mod:`, `:exc:`, or `:data:`, followed by the target in single backticks. A
  leading `~` shortens the displayed name to its last segment.
- **mkdocstrings**, on MkDocs — `[Client.send][pkg.client.Client.send]`.
- **No renderer at all** — read in an editor and through `help()`, where backticks are backticks and
  a role is a pair of stray colons in front of them.

**Nothing checks any of them by default.** Sphinx reports an unresolved reference only in nitpicky
mode (`-n`, or `nitpicky = True`), which many projects never switch on, and a docstring nobody
renders is checked by nobody at all. A role pointing at a method that was renamed two releases ago
renders as unlinked text and lies quietly. The verification burden of §7a sits entirely on you.

Use a cross-reference for something the reader may want to follow. For an identifier they will not
navigate to — a JSON key, a literal, a shell command, a symbol in a service you do not import —
plain text is correct. Set off a longer snippet as a code block in the project's markup.

Cite an issue only alongside the name of the phenomenon: `the desync class of bug that #4015 fixed`
survives the tracker; a bare `see #4015` does not.

## 6. Sections

Python has three **section dialects**, and a project holds exactly one:

| Dialect | Parameter section | Parsed by |
| --- | --- | --- |
| reStructuredText / Sphinx | `:param body:` … `:raises ValueError:` | Sphinx, natively |
| Google | `Args:` … `Raises:` | napoleon, mkdocstrings, ruff |
| NumPy | `Parameters` under a `----------` rule | napoleon, numpydoc, ruff |

Mixing them is the failure this section exists to prevent, and it is silent: an `Args:` header in a
Sphinx-only project renders as an ordinary paragraph with a colon, and nobody's build goes red. Ruff
enforces one dialect through `convention` in `[tool.ruff.lint.pydocstyle]` — set it, and let the
linter hold the line. Section names are a fixed vocabulary in every dialect: `Arg:` for `Args:`
silently becomes prose.

Whichever dialect the project uses, the content rules are the same:

- **A parameter line earns its place by adding what the annotation lacks** — a unit, a range, a
  `None` rule, a condition, an ownership statement. `timeout (float): the timeout` is noise, and a
  lint rule that demands one line per parameter produces noise at scale; say so rather than filling
  it in.
- **Do not restate the type.** The annotation is the type. A `(float)` beside `timeout: float` is a
  second copy that a signature change desynchronizes, and Sphinx's `autodoc_typehints` prints the
  annotation for you.
- **`Returns:` is skippable when the summary already said it.** Google's own guide allows omitting
  the section when the summary describes the return value. Keep it when the return is a tuple, a
  sentinel, or a container whose ownership needs a sentence.
- **`Raises:` is the only record a caller has.** No annotation carries it and no checker derives it.
  List the exceptions a caller can act on, not every one that could escape; a `KeyError` from a
  misspelled config key is a bug report, not a contract.
- **`Yields:` for a generator**, and it is the place to say single-pass (§4).
- **Deprecation has a machine-readable form, and prose is not it.** `warnings.warn(…,
  DeprecationWarning, stacklevel=2)` reaches the caller at run time, and `@deprecated` (PEP 702,
  `typing_extensions` or `typing` on 3.13+) reaches them in a type checker. A line that only says
  "deprecated" in the docstring is read by nobody who has not already opened it. Whichever you use,
  name the replacement.
- **An `Examples:` block with `>>>` in it is executable.** `doctest` and `pytest --doctest-modules`
  run it, so editing the prompt, the expected output, or a `# doctest:` directive is a test change.
  Run the doctests after the edit.

Markup belongs to the renderer, not to the docstring: RST directives in a Markdown-rendered project
and Markdown in a Sphinx one both arrive as literal characters.

## 6a. When the docstring ships as documentation

Python has several of these surfaces, and they are easy to miss because the docstring looks like an
ordinary comment in the file:

- a CLI framework prints a command function's docstring as its `--help` text (Click, Typer), and an
  `argparse` parser is conventionally built with `description=__doc__`;
- FastAPI turns a path operation's docstring into the OpenAPI `description`, which Swagger UI renders
  as Markdown;
- a published package's API pages, on Read the Docs or GitHub Pages, are its docstrings;
- `help()` at an interactive prompt.

**The reader changes, and that is the whole section.** This text is read by someone working against
your interface from the outside. They cannot open the code, cannot follow a cross-reference, cannot
find out what a name refers to, and have no `git log`. Three rules follow, and they are about what
the text says, not about the build:

1. **Every reference has to be spelled out.** "See the client" points nowhere. A Sphinx role reaches
   a `--help` string as its own raw colons and backticks. If the sentence names something, it has to
   define it in the same breath or not name it at all.
1. **§4's vocabulary exception is wider here, and the criterion test is stricter.** The values a
   parameter accepts, the keys a payload may hold — that list is the only source this reader has, so
   replacing it with a criterion is allowed only when they can apply the criterion *without opening
   anything*. §4's own warning applies at full force: if the honest criterion is circular, the list
   was the answer, and the repair is to complete it and verify every member against the code in the
   same edit.
1. **Write for the markup the surface actually renders.** Swagger renders Markdown; a terminal
   renders nothing; Sphinx renders RST. The same docstring reaching two of them has to be plain
   enough for the poorer one.

Then the mechanics. Where the generated output is committed — an OpenAPI spec in the repository, a
generated client, a `--help` snapshot test — editing the docstring is not a comment-only change:
regenerate and commit the result, or the drift check fails. Because every edit costs that diff, the
bar rises — but it rises for **rewording**, not for **enriching**, and confusing the two is how this
section does damage. A synonym or a smoother clause is churn that ships. A fact the description does
not carry and its reader needs is worth the diff every time, even when every sentence already there
is true. "It is correct as written" answers the first case and not the second.

One Python-only caveat for this section: every surface above reads `__doc__`, and `python -OO`
deletes it (§3). A blank `--help` under `-OO` is a curiosity, because almost nobody starts a CLI
that way. A docstring your code *parses* — for defaults, for a schema, for a routing table — is a
program that stops working under a flag, and belongs in a constant instead.

## 7. When to write nothing

A docstring that would not confuse a future reader by its absence is a docstring that will mislead
one by going stale. Skip it for:

- an object whose name and annotations are the whole contract;
- an override that adds nothing to the inherited contract — `inspect.getdoc` walks the MRO on Python
  3.9 and later, so `help()` shows the parent's text, and a `"""See base class."""` replaces that
  text with nothing;
- a private helper whose single call site makes it obvious;
- anything the code says better, which is most narration.

The corollary: a public object with a non-obvious contract is not optional, however self-evident the
name looks to the person who just wrote it.

A lint rule that demands a docstring everywhere (`D100`–`D107`) fights this section and wins on
volume: it produces `"""Initialize."""` at scale, which is narration with a linter's blessing. Argue
about the rule's configuration rather than filling it in — and where the project has settled the
argument, a one-line summary that says something is still the job.

## 7a. Editing an existing docstring

Most of the time you are not writing a docstring, you are rewriting one. Different job, different
failure mode: a rewrite drifts longer, because every restructuring pass adds a sentence and none
takes one away.

- **Budget the net delta at zero.** Restructuring is free. Growth has to be paid for by a fact the
  old docstring did not carry — a unit, a side effect, a `None` rule, an invariant. Name that fact to
  yourself; if you cannot, you are re-phrasing, and the old wording stays.
- **Check every identifier the old docstring names.** A docstring written before a refactor cites
  parameters, attributes, and functions that no longer exist. Python will not tell you: an identifier
  in prose runs, renders, and lies, and so does a cross-reference outside nitpicky mode (§5). Grep
  each one, and convert what you verify into the project's reference form.
- **Delete a parameter section that the annotations made redundant.** This is the commonest unpaid
  line in a Python docstring, and cutting it is the edit most likely to shrink the file.
- **When you lift a rule into the class docstring, go and cut it from the method.** The method keeps
  the one sentence that specializes the rule, plus the reference. Two full statements of the same
  rule is the most common outcome of a good structural edit and the easiest to miss, because each of
  the two reads well on its own.
- **Deleting is an edit.** A list of callers, a rejected alternative, a cost estimate, a reference to
  the change that introduced the code — cutting these is usually the highest-value change in the
  diff, even though the result looks like less work.
- **A summary that breaks §3 is itself the fact that pays for a rewrite.** The net-delta rule governs
  the body, not the first line. A docstring that opens with `This function is a wrapper around X`
  stays broken until someone rewrites it, and "I had no new fact to add" is not a reason to leave it.
- **Run what the docstring runs.** If it contains a `>>>` block, run the doctests. If it feeds a
  committed artifact (§6a), regenerate.
- **Do not move code.** A docstring edit that also renames a variable or reorders a statement cannot
  be verified as comment-only, and the verification is what makes a large sweep safe. Python sharpens
  this: the docstring *is* a statement, so an edit that lets anything precede it deletes it (§3).

## 7b. Comparing two versions

§7a governs how far your own rewrite may grow. This section is for the moment you hold both versions
and have to establish what actually changed: reviewing someone else's edit, checking your own before
you commit it, or judging a machine-generated one.

Start from this. The new version will read better. It was written second, by someone who had just
finished understanding the code. Reading forward confirms that impression and finds nothing, because
a fact that vanished leaves no trace in the text that replaced it. So the work runs backwards: you
read the **old** version carefully first, and the verdict comes last.

**1. List the old version's facts before you read the new one.**

One fact is one unit, one bound, one `None` rule, one side effect, one ordering or concurrency
constraint, one lifecycle obligation, one named collaborator, one reference target, one raised
exception, or one stated default. A topic sentence is not a fact, and neither is a restatement of the
signature or of an annotation.

Compare facts, not sentences. At sentence granularity, merging two sentences looks like a loss and
splitting one looks like growth, and both readings are wrong.

**2. Mark each fact present, restated, or absent.**

Restated is the ordinary case and needs no defense. Absent needs one, in words, for each fact. Three
defenses hold:

- the fact was wrong;
- the fact moved to the class or module docstring, and you can point at the sentence that now carries
  it;
- the fact moved into the signature — a new annotation, a renamed parameter, a keyword-only argument,
  a return type that now says what a sentence used to.

Three do not: *the code implies it*, *the new wording covers it*, *it was obvious anyway*. Each of
those is what someone writes when they cannot find the fact and would rather not look again.

**3. Only now count the delta.**

Apply §7a's budget to the body: growth is paid for by a fact the old version did not carry, and you
name the fact. A summary repaired under §3 pays for itself and is exempt, and so does a parameter
section deleted because the annotations already said it. Restructuring at equal length is free and
needs no justification at all.

**4. Check what the new version asserts without support.**

Every claim traces to the code, to the old docstring, or to a contract it references. A claim that
traces to none of the three is invented, however plausible it sounds, and plausible is the dangerous
case: a wrong invariant in a docstring is a wrong invariant a caller will build on. `Raises:` is
where this lands hardest, because nothing in Python can contradict it. The commit message is not a
source either. It records what someone meant to do, and the docstring has to describe what the code
does.

**5. Name the changes that bought nothing.**

A sentence reworded with no new fact and no §3 defect repaired is churn. It costs a reviewer
attention now and costs the next reader a `git blame` later. §7a already says the old wording stays;
here you go looking for the places where it did not. Where the docstring ships (§6a) the cost is
higher, because the churn arrives with a regenerated artifact attached.

**6. Inline comments run on a different rubric.**

A new `#` comment has no earlier version, so steps 1 through 3 have nothing to work on. Three
failures replace them:

- **Narration.** The comment restates the statement below it. §1 names this for docstrings; it is the
  characteristic failure of inline ones.
- **History.** The comment describes the change that produced the code rather than the code. §1.
- **Staleness.** The comment survived a change to the code under it and now describes something else.
  No build step catches this, which makes it the most valuable thing a comparison pass finds.

A comment something other than a human reads is out of scope for all three — see §4 for the list and
for what moving one breaks.

**7. Prove the code did not move.**

A sweep that edits docstrings across many files is only reviewable if the claim "comments only" is
mechanical rather than asserted. Comments never reach the AST, but docstrings do, so they have to be
dropped before the comparison:

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

Dropping every bare string statement, rather than only what `ast.get_docstring` returns, is what
makes attribute docstrings (§4) come out too. Any difference between the two dumps means the pass
touched code, and the pass is wrong until it is explained.

**8. Say which finding it is, not whether the docstring got better.**

Each outcome names the repair it obliges. Naming it is what makes two people comparing the same pair
reach the same answer.

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
| Narration | Delete the comment |
| History narration | Rewrite as the state that holds now |
| Stale inline comment | Rewrite it from the code |
| Mixed section dialect | Convert to the project's dialect (§6) |
| Displaced tool comment | Restore its exact text and line (§4) |
| Broken doctest | Run it, and fix the example or the expectation |

## 8. Review checklist

Run this over a comment you wrote or one you are reviewing.

- Is the summary one line, ending in a period, and does it stand alone with no term the docstring
  introduces?
- Is its mood the one the rest of the project uses (§3)?
- Is the docstring still the first statement, and is it a plain string rather than an f-string?
- Is the contract stated positively and in one place, before any mechanism?
- Could a caller satisfy the contract without opening the code, or a maintainer fix a failing test
  from the docstring alone?
- Does any parameter line say more than the annotation already does?
- Does `Raises:` list what a caller can act on, and can the code actually raise each entry?
- For anything returning an iterator: is laziness, single-pass, and what it holds open stated?
- Is any rationale here actually commit-message material?
- Any sentence describing a previous version of the code — `now`, `no longer`, `used to`?
- Does the docstring explain another module's internals instead of naming it?
- Any positional reference — `below`, `above`, `the following`?
- Are the sections in the project's one dialect, spelled exactly (§6)?
- Does every cross-reference still resolve, in the form this project's renderer reads?
- Is every `# type:`, `# noqa`, `# pragma`, or `# fmt:` comment still on the exact line it governs?
- Would deleting the whole docstring lose anything, given that `inspect.getdoc` inherits?
- If it contains `>>>`: did you run the doctests?
- If it ships as documentation (§6a): can its reader follow every reference without opening the
  code, and did you regenerate whatever it feeds?
- If this is a rewrite: did you list the old version's facts before you read the new one (§7b)?
- If this is a rewrite: what fact does each added sentence carry that the old docstring did not?
- Does any statement here also appear in the class or module docstring?
- Any list that a criterion would replace, or that the reader's editor already answers?

## 9. Worked examples

The two examples pull in opposite directions on purpose. The first shrinks, because the template was
carrying the annotations. The second grows, because a fact was missing. Do not read either one as the
target shape.

Both are constructed rather than lifted from a real codebase, and deliberately so: an example a
sweeper can recognize in the wild is an example it will paste instead of derive, and a rewrite that
matches this file word for word tells you nothing about whether the rules were applied.

Both also sit in a project that has settled on the Google convention — descriptive summaries, Google
sections. In a PEP 257 project the summaries would be imperative and the sections would be
reStructuredText fields, and nothing else in either rewrite would change (§3, §6).

### A docstring the annotations had already outgrown

**Before** — eleven lines, of which two carry a fact. The rest is the signature, transcribed into a
Google-style template.

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

**After** — the two facts, and the one the reader would otherwise get wrong.

```python
def merge_labels(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    """Merges into a new dict, with overrides winning on a key both sides set.

    Neither argument is modified. A key whose override value is empty is dropped from the
    result, which is how a caller removes an inherited label.
    """
```

Fact ledger: *overrides win* — new, and the only thing the old summary left the reader to guess.
*Neither argument is mutated* — new. *The empty-string convention* — new, and it is the behavior a
caller cannot infer from the name. Everything cut was a type the annotation already states (§6), so
by §7b step 3 the deletion needs no defense and the three added facts pay for the two lines they
cost.

### A generator whose laziness was never stated

**Before** — accurate, and it describes a function that returns a list.

```python
def failed_rows(report_path: Path) -> Iterator[Row]:
    """Returns the rows the ingest run rejected."""
```

**After** — the summary keeps its shape and picks up the ordering; the body carries what the
annotation hides.

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

The rewrite grew from one line to nine and paid for them with four facts the one-liner did not
carry: the ordering, the point at which the file is opened, the single-pass rule, and — the one that
costs a caller a debugging session — that the exception surfaces at the first `next()` rather than
at the call. The last is a property of every generator, and a surprise to anyone who read the
signature and expected a list.
