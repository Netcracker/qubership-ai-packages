# Surface pack: command-line interface

Apply this pack when the repository ships something invoked by arguments: a CLI tool, a plugin for another CLI, a build
or migration tool, a `main` with a flag parser, or a binary whose primary caller is a script or an agent. It does not
apply to a server that only reads a config file and one `--config` flag — say so in the profile and spend the budget
elsewhere.

The caller here is a human at a terminal, a script in CI, and increasingly an AI agent, and the three fail differently.
The human googles the error. The script reads the exit code and nothing else. The agent reads `--help`, guesses by
analogy with every other CLI it has seen, pays for every byte of output twice, and has no way to ask a question. Design
that survives all three is the subject of this pack.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what** — stay inside your
row of the table below and leave the rest alone. A concern raised twice in two vocabularies costs the reader more
than it costs you.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Command and subcommand naming, the verb vocabulary, tree depth; flag names and their consistency across subcommands; placeholder (metavariable) vocabulary; `--help` completeness and per-subcommand visibility of inherited flags; defaults, units, and allowed values in help text; output volume and shape; machine-readable mode; empty states; next-step hints | `api-ux` |
| Stream discipline (what goes to stdout versus stderr); exit-code taxonomy, its documentation and stability; behavior on an unknown command, flag, or enum value, and whether a suggestion is offered; message shape; structured errors under `--json`; interactive prompts; partial success in batch operations | `error-model` |
| Renaming or removing a command, flag, alias, or `--json` field; changing a default, a meaning, or the exit code for an existing condition; tightening validation; moving a command under a new parent; the stability policy for human-readable output; deprecation windows | `api-compatibility` |
| Drift between the help text and the parser; flag, environment, and config precedence; repeated flags and the `--` terminator; idempotency of mutating commands; `--dry-run` fidelity; behavior on signals and partial writes | `correctness` |
| Secrets in `argv`, in verbose output, or in error text; permissions on files the tool writes; confirmation gates and what bypasses them; shell injection where the tool builds subprocess commands | `security` |
| Verbosity levels and where logs go; progress reporting under a non-TTY; timeouts; exit on `SIGINT`; update checks and telemetry that phone home on every invocation | `observability-operability` |
| Agreement between `README`, manpage, shell completions, and `--help`; a documented exit-code table and environment-variable list; the agent-facing snippet — whether one exists at all, what it costs per session, whether it routes rather than enumerates, and whether it agrees with the parser | `docs-onboarding` |
| Golden snapshots of the help tree; a test per documented exit code; tests that run the tool with stdout piped | `tests` |
| Startup latency per invocation and runtime dependencies — an agent pays that cost on every call | `build-release` |

## Normative sources

Fetch these rather than recalling them; the expectation in a finding must cite a section, not a memory.

- **POSIX Utility Conventions**, XBD sections 12.1 and 12.2 — option syntax, the `--` terminator, operand ordering.
- **GNU Coding Standards**, "Standards for Command Line Interfaces" — long options, `--help`, `--version`, and the
  `--file=FILE` metavariable convention.
- **Command Line Interface Guidelines** (`clig.dev`) — the closest thing to a modern consensus on help output,
  subcommand consistency, stdout versus stderr, `--json` and `--plain`, and standard flag names.
- **`sysexits.h`** for the 64–78 range, and the shell's reserved codes: 126, 127, 128+N, and 130 for `SIGINT`.
- **AXI** (`axi.md`) — measured evidence, over 915 runs, that token-efficient output, minimal default schemas,
  pre-computed aggregates, definitive empty states, and contextual next-step suggestions cut both cost and turn count
  against the same underlying tool. Cite the principle number when you use it.
- **`no-color.org`** for `NO_COLOR`.
- **The parser framework's own documentation** — cobra, clap, picocli, argparse, urfave/cli, oclif. What the help
  renderer inherits from a parent command differs per framework, and half the findings in this pack live in that gap.

Where the project states its own convention in `AGENTS.md`, `CLAUDE.md`, or a design document, that wins over the
upstream convention — cite the local rule and note the divergence rather than reporting it as a defect.

## `api-ux` — the argument surface is the API

- **One grammar, chosen once.** Either `noun verb` (`issue list`) or `verb noun` (`list issues`), everywhere. Mixed
  grammar is the defect an agent pays for on every guess.
- **Predictable verbs.** An agent guesses by analogy: `list`, `get`, `create`, `delete`, `update`, `run`. A house
  synonym as the canonical name (`show`, `new`, `nuke`) costs a failed invocation per caller; the same word as an alias
  costs nothing. Depth costs too — a three-level path the caller must discover is one turn per level.
- **Uniform construction.** Enumerate every flag in the tree and group by name. The same concept carries the same flag
  name, the same short form, and the same value type on every subcommand that has it (`--namespace`, `--output`,
  `--timeout`). One name meaning two things across two subcommands is the most expensive defect on this surface.
- **Placeholders are types, not hints.** `<file>` is a path that must exist; `<id>` is one kind of identifier
  throughout. Same placeholder, same syntax and same validation everywhere; two different things, two different
  placeholders. Mixing conventions (`FILE`, `<file>`, `[file]`) inside one help output makes the reader guess which of
  them is optional. In suggested next-step lines the placeholder stays literal; a fabricated example value gets
  copied verbatim by an agent (AXI 9).
- **Help on every node.** `--help` and `-h` work on the root and on every subcommand at every level, exit 0, and write
  to stdout. Bare `<tool> help <subcommand>` reaches the same text.
- **Every accepted option appears in the help of the subcommand that accepts it.** This is where frameworks betray the
  design: a parent flag is accepted after the subcommand but printed only at the top level, so the option exists,
  works, and is undiscoverable where it is used. Do not reason about it — extract the flags from each subcommand's
  help, extract the flags its parser accepts, and diff. The diff is the finding list, in both directions.
- **Each option states its default, its unit, and its allowed values.** An enum flag whose help omits the values forces
  trial and error, and the error message is then the only documentation (see `error-model`).
- **Find the agent-facing contract wherever it lives, and hold `--help` to it.** A tool aimed at agents often ships a
  second documentation surface the reviewer will not find by reading `--help`: a snippet an installer writes into
  `AGENTS.md`, a bundled skill, or the descriptions in an MCP wrapper. What is yours here is the gap — an exit-code
  table, a stream contract, or a default cap that exists only in the snippet serves the caller who installed the tool
  and abandons the one who typed `--help`, which is the same defect as an option documented only at the top level.
  The snippet's own quality belongs to `docs-onboarding` below.
- **Output volume is a first-class cost.** The default schema carries the 3–4 fields a caller needs (AXI 2); anything
  long is truncated with a size hint and the flag that lifts it (AXI 3); totals and counts are pre-computed so nobody
  needs a second call to get them (AXI 4); an empty result says so explicitly, because empty output is
  indistinguishable from a crash (AXI 5). Banners, ASCII art, update-check nags, spinners, ANSI escapes on a
  non-TTY, and a closing `Done!` are pure cost. Measure it: bytes and tokens for the ten most likely invocations.
- **A machine-readable mode that is documented and stable.** `--json` (or the project's equivalent) is the contract;
  the human table is not. Its absence on any command that returns data is a finding.
- **Size the machine-readable mode against its audience, and settle the audience first.** For a `jq` filter in a
  pipeline, verbosity is nearly free and schema stability is everything — do not report bytes there. The question
  changes the moment the tool points an agent at that mode: a `--help` line, an `AGENTS.md` snippet, a skill, or an
  MCP wrapper saying "use `--json`" makes the size part of the contract, because the agent pays it in context on
  every call. Then measure it against the text mode and against the raw material the command summarizes. A structured
  mode that costs several times the text mode, or more than reading the input file, cancels the reason the caller
  reached for the tool — and where the docs quote a compression ratio, check it on the input that stresses it, not on
  the average one.
- **The program calls itself by one name.** The name in `Usage:` comes from `argv[0]` in most frameworks and from a
  hard-coded string on the paths a framework does not render. Where those disagree, one help screen teaches the caller
  a command that may not be on their `PATH`.

## `error-model` — what the caller branches on

- **Streams.** Data on stdout, everything else on stderr. The falsifiable rule is separation, not preference: a caller
  that runs `<tool> list --json 2>/dev/null | jq` must get parseable JSON, and a caller that discards stdout must still
  see the failure. Both are broken by mixing.
- **Exit codes.** Zero on success; distinct, documented, stable codes for at least usage error versus runtime failure.
  Stay below 126 for your own meanings — 126, 127, 128+N and 130 belong to the shell and to signals. Enumerate every
  `exit` call in the source, map each to the condition that reaches it, and compare against the documented table. That
  gap list is the most useful artifact this surface produces on this axis.
- **`exit 0` on failure is the most expensive defect on this surface.** CI, `set -e`, and every agent read it as
  success, so the failure surfaces later as something else. The same applies to a status swallowed by a pipeline or a
  `|| true` in a wrapper script the project ships.
- **Unknown input fails loudly and helpfully.** An unknown command, an unknown flag, or an out-of-range enum value
  exits non-zero and prints the valid values, or the nearest matches. Suggestion is not substitution: the absence of
  "did you mean `apply`?" is a finding, and *running* `apply` because the caller typed `aply`, or resolving `--ver`
  to `--verbose` by prefix, is a worse one, because a typo then silently does work. Do not stop at "suggestions
  exist": type a realistic typo of the most-used command and read what comes back. An edit-distance matcher that
  offers three commands and omits the intended one has spent the caller's turn to point away from the answer.
- **Message shape.** Reason, action, consequence, naming the offending token and where it came from: the flag, the
  environment variable, or the config file and line. Error identity lives in the exit code and in the structured
  `code` field, never in the prose, which is free to change.
- **Structured errors under `--json`**: a stable `code`, a human `message`, and where the tool knows one, a
  `remediation`. An error that reverts to a bare stack trace when `--json` was requested is a finding.
- **No prompt without a TTY.** A confirmation that blocks on a non-TTY hangs CI and agents until something times out.
  There must be a non-interactive path (`--yes`, `--no-input`, or an environment variable), and it must be documented.
- **Partial success.** For anything batched, the caller must be able to tell which items succeeded, and the exit code
  must not read as total success.

## `api-compatibility` — a shipped CLI is a frozen contract

Breaking, on this surface, means an invocation that worked stops working, or a consumer parsing the output gets
something it cannot handle. Concretely — renaming or removing a command, subcommand, flag, or alias; changing a flag's
default or meaning; changing the exit code for a condition that already had one; removing or renaming a field in the
machine-readable output; tightening validation that previously passed; moving a command under a different parent;
changing which format is the default.

Additive is safe, and the docs should say so: new commands, new flags whose default preserves the old behavior, new
fields in `--json` that consumers are told to tolerate.

Two questions this axis must settle explicitly. **Is the human-readable output a contract?** If nothing says
otherwise, people grep it and it is one in practice; the fix is a documented stable mode, not a promise never to touch
the table. And **is there a deprecation path at all** — a warning on stderr, for at least one release, before anything
disappears? Shipped shell completions and manpages from the previous version are part of the same contract.

## `correctness` — the parser versus the help

Drift in both directions: documented but not accepted, and accepted but not documented. Precedence between flag,
environment variable, config file, and default — stated, and actually implemented in that order. Repeated flags (last
wins, or accumulate?). The `--` terminator. A flag placed after a positional argument. For mutating commands: a re-run
that is idempotent, and a `--dry-run` that exercises the same code path as the real run — a dry-run computed by a
separate branch drifts from the real one and eventually lies about it.

One check belongs here and is easy to miss: `<tool> delete <id> --help` must print help and delete nothing.

## `security`

Secrets passed in `argv` are visible in `ps` and in shell history on a shared host; a flag that takes a token, where an
environment variable, a file, or stdin would do, is a finding. Check verbose and debug modes for echoed `Authorization`
headers and connection strings, the permissions on files the tool writes, and what a `--force` reaching the tool from a
script bypasses that a human would have been asked about.

## `docs-onboarding` — the agent-facing prompt

A subcommand that prints the snippet an agent should carry — `prompt`, `instructions`, `skill`, `agent-info` — is good
practice, and on a tool that expects agent callers its absence is a finding on its own. The argument for it is
versioning: whatever an installer wrote into someone's `AGENTS.md` is a snapshot, and the binary has moved since, so
a copy that has drifted is indistinguishable from one that has not. A subcommand prints what *this build* contracts
to do. It can be refreshed in one call, and CI can diff it against the parser.

It is not free. The snippet is loaded into every session that uses the tool, so its length is a standing tax rather
than a per-call one — measure it, and judge the content against that number. For scale, `sb prompt` costs about 12 KB
(roughly 3,100 tokens) to route 25 commands, against 18 KB for the full help tree it replaces.

- **Only what the model does not already know.** No bash, no git, no `jq`, no explanation of globbing or of what JSON
  is. Every line is a fact about this tool that a competent model would otherwise get wrong. Falsify each one: delete
  it, and does the model now make a mistake? If not, it is rent, and it is charged on every session.
- **No duplication — inside the snippet, and against `--help`.** A snippet that restates the option list adds nothing
  `--help` would not answer on demand, and the second copy drifts, after which nobody can say which one the build
  honors. What belongs here is what a help renderer structurally cannot say: which command answers which question, in
  what order, and when to stop. Routing, not enumeration.
- **The traps, which are the reason the file exists.** The default that changes the answer, the cap that makes a
  truncated result look complete, the argument that looks like a path and is not, the quoting the shell eats before
  the tool sees it, the zero that means "your filter was wrong" rather than "there is nothing there". A snippet
  without these is a table of contents. A snippet that is mostly these is doing its job, and it is the cheapest
  defect-prevention surface the tool has.
- **Every claim in it is executable.** Run each example, and check each number it quotes — a compression ratio, a
  default cap, a schema name — on an input that stresses it rather than on the average one. A model trusts this file
  more than it trusts `--help`, so an example that no longer works costs more than a missing one.
- **One contract, not three.** Where the tool also ships an MCP wrapper or a skill, the snippet, the tool
  descriptions, and `--help` are three renderings of one contract. Diff them; the pairs that disagree are the finding.

## `tests`

A golden snapshot of `--help` for every command in the tree, so a rename shows up in review rather than in a user's
script. A test per documented exit code. A test that runs the tool with stdout piped rather than attached to a
terminal, asserting the machine-readable output is byte-identical either way.

## Tooling

Crawl the help tree first — it is the inventory every check below reads from. Do it in a throwaway directory, and
never against a real endpoint: the crawler appends `--help`, and a parser that validates positionals before
short-circuiting will happily run the command instead.

```bash
<tool> --help >/tmp/h.out 2>/tmp/h.err; echo "exit=$?"; wc -c /tmp/h.out /tmp/h.err   # 0, stdout, empty stderr
<tool> nosuchcmd >/dev/null; echo "exit=$?"                     # non-zero, message on stderr, valid values listed
<tool> list --bogus-flag >/dev/null; echo "exit=$?"             # same, and distinguishable from a runtime failure
<tool> list --output json | jq .                                # machine mode still parses when piped
NO_COLOR=1 TERM=dumb <tool> list | cat -v | head                # no ANSI escapes, no spinner, on a non-TTY
timeout 10 <tool> delete <id> </dev/null; echo "exit=$?"        # must not block waiting for a prompt
<tool> list --output json 2>/dev/null | jq .                    # survives a caller that discards stderr
```

Then two measurements that turn opinion into evidence. **Size**: `wc -c` the ten most likely invocations, and convert
to tokens; a default listing that costs thousands of tokens is a finding with a number attached. **A transcript**:
give a fresh agent, or yourself with the source unread, three realistic tasks and nothing but `--help`. Record
every wrong guess, every extra turn, and every place the output had to be re-read. That transcript is the strongest
evidence this surface can produce, and it is the one thing no amount of reading the parser will give you.

Prefer `executed` over `traced` here more than on any other surface: every claim in this pack can be settled by running
the binary, so a finding that reasons about the flag parser without invoking it should not have been written that way.

## Where the sources disagree

Do not report a project for picking the other side of a live disagreement. Report it for having no rule.

- **Errors on stderr or on stdout.** `clig.dev` and Unix practice say stderr. AXI 6 says the opposite — "reserve
  stdout for structured data and stderr for debug/log output" — and gives no rationale for it: the page states it as a
  design prescription, and the benchmarks behind AXI measure task success, cost, duration, and turns, none of which
  separate the two streams. The sources are therefore not equally weighted here. Expect stderr, which pipelines, CI,
  and `2>/dev/null` callers all depend on. A documented, consistent choice of stdout with clean separation is a
  `convention` rejection, not a defect. Mixing the two in one invocation is a defect either way.
- **What a bare invocation prints.** `clig.dev` says concise help; AXI 8 says live data plus a one-line description of
  what the tool is. Both beat a wall of full help. Judge consistency and the exit code, not the choice.
- **JSON or something denser.** `--json` is the interoperable baseline and its absence on a data-returning command is a
  finding. A token-optimized default such as TOON (AXI 1, around 40% fewer tokens) is worth proposing, but it is a
  recommendation, not a defect — unless the project itself claims to target agents.
- **Exit-code numbering.** `sysexits.h` (64–78), the short ladders (1 general, 2 usage, 3 auth, 4 not found), and
  per-project schemes all have adherents; no consensus exists. The requirement is a documented, stable taxonomy that
  separates usage error from runtime failure. Report the missing table, not the chosen numbers.
- **Typo handling.** Arcjet argues for hard failure with no suggestions at all; usability guidance argues for "did you
  mean". They agree on the part that matters, which is the only part to report: never act on the guess.

## Severity guidance

`exit 0` on a failed operation, and a destructive command that proceeds on input it could not resolve, are the two
paths to `CRITICAL` here — both end in a caller acting on a success that did not happen. A secret in `argv`, or a
prompt that blocks on a non-TTY, is `HIGH`. A flag whose meaning differs between two subcommands, and an option
documented only at the top level, are `MEDIUM`: they cost every caller a failed attempt. Output noise is `LOW` on its
own; it earns `MEDIUM` only with a measured cost across the commands a caller actually runs.

## Architectural questions this surface raises

For the `architecture` distiller, not for the evidence axes:

- Does the command tree model the domain, or the source layout that happened to produce it?
- Should this be a CLI, a library, and an MCP server over one shared core — and where several exist already, is the
  contract shared or re-implemented per entry point, with the drift that follows?
- Does a realistic task require running three commands and feeding one's output into the next by hand? Each hand-off is
  a turn, a parsing risk, and a place where a human's judgment was silently assumed.
- What does one invocation cost in startup time, and does the interface force one process per item where a batch flag
  would do?
- Who owns the stability promise for the argument surface, and does anything in CI enforce it?
