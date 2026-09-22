---
name: deep-review
description: Run a multi-axis adversarial review of a repository, a microservice, or a system of interacting components — profile the target, agree the focus with the user in a questions file, then fan out independent review axes (tests, correctness, error model, concurrency, API compatibility, API/agent UX, protocol conformance, security, operability, architecture and others), refute every finding before it is reported, and consolidate the survivors into one ranked report. Use when the user asks for a deep, adversarial, architecture, or multi-axis review of a repository, a service, an operator, a library, or a system of services, or runs /deep-review. Not for anything smaller than a repository or a deployable — a pull request, a diff, a class, a file, or a package. For those use adversarial-code-review (a pull request or merge request), codex-review (a branch diff or a commit), or a direct review. Runs only in Claude Code, through its Workflow tool.
---

# Deep review

A review of a repository, a microservice, or a system of components, run as several independent axes rather than one
pass. Each axis has its own filter for what counts as a finding, every finding is refuted before it survives, and the
`architecture` axis is driven by a prompt distilled from what the evidence axes actually found — not from a generic
template.

**This skill runs only in Claude Code with dynamic workflows enabled.** The pipeline is a workflow script that the
session starts with the `Workflow` tool. An agent without that tool cannot run the pipeline: stop before creating a
dossier, say that the skill needs Claude Code, and offer a direct review instead.

**The smallest target is a repository or a deployable.** A class, a file, a package, a pull request, or a diff has no
archetype to classify and no surface to profile, and the pipeline would spend a dozen agents on it. For those, use
`adversarial-code-review` (a pull request or merge request), `codex-review` (a branch diff or a commit), or review the
code directly. A large target is handled by coarsening the review, never by narrowing it to a subtree: fewer axes,
contract-level findings, `depth: coarse` (the default). `depth: deep` adds unit-level work (reproduction tests,
mutation runs, stress tests) and is worth its cost on a library or a component whose correctness is the question.

**A system review names its components.** Several repositories, or several deployables of one monorepo, reviewed
together: the profile lists each component with its checkout and revision, the focus file carries the questions about
their interactions, and every axis receives the whole list. What the pipeline supports and what it does not is stated
in step 3.

The unit of work is a **dossier**: a directory holding the profile, the agreed focus, the generated prompts, the
per-axis reports, and a normalized findings file. Nothing is passed between stages as chat text. Everything is a file,
so any stage can be re-run on its own.

## Procedure

### 1. Profile the repository

Read enough to fill in a profile — do not review anything yet. This step is reading and a commands file, not an audit:
the reading is short, and the commands file takes as long as running the commands takes.

- Build files, `README`, `AGENTS.md` / `CLAUDE.md`, `docs/`, `CHANGELOG`, CI workflows.
- The public surface: `sb surface` where a structural-search CLI is installed and the language has a resolver,
  otherwise read the exported declarations of the source roots.
- Size and shape: `git ls-files | wc -l`, languages, module layout, test layout, dependency cycles between modules.
- Who consumes it, and what stability has been promised (semver? published artifact? internal only?).

Then classify the archetype against `references/archetypes.md`. The archetype selects the axes; get it right or the
review will answer questions nobody asked.

**For a system, profile each component and then the system.** Write a components table into `00-profile.md` — one row
per component: name, checkout path, revision, archetype, what it exposes, what it consumes — and after it the
interactions: which component calls which, over what (a REST API, a topic, a shared schema, a CRD), and what each side
assumes about the other. The interactions are the subject of a system review; a component's internals are reviewed
only as far as they carry an interaction. Every component's checkout has to exist locally before step 3, at the
revision the table names, because the axes read files, not URLs.

**Then list the surfaces** — the forms in which this repository exposes an API. One repository often has several:
a Kubernetes operator has `kubernetes` and usually `code-library`; a service may have `rest-http`, `events-messaging`,
and a `cli`. Each form has its own naming conventions, its own definition of a breaking change, and its own normative
source, and none of that can be derived from general principles. Available packs live in `references/surfaces/`; if a
form has no pack yet, say so in the profile rather than pretending the generic axis covers it — then write the pack
when the review proves what it needs to contain.

Create the dossier:

```bash
${CLAUDE_SKILL_DIR}/scripts/new-dossier.sh <repo-path>
```

It prints the dossier path — use it everywhere below. For a system, pass the checkout that hosts the dossier (the
primary component, or a directory you created for the review); the other components stay where they are. Write
`00-profile.md` into it: archetype, languages, public surface, consumers, stability commitments, notable prior art in
the repo (existing review reports, ADRs), and anything that looks load-bearing.

**The profile carries a technology inventory.** One row per language, runtime, library, framework, storage, or
external component the system cannot run without. It is a fact table, written before any opinion is formed, and every
axis reads it. The columns, one row per technology:

| Column | Contents |
| --- | --- |
| Technology | The name, as its own documentation spells it |
| Designed for | Quoted from its own documentation, with the URL |
| Stated non-goals and limits | Quoted the same way |
| Role here | `path:line` |
| Authors | Who writes artifacts on it here; who it was designed for |
| Distinctive features in use | The features it is chosen for that this system uses |
| Size | Lines on it, lines around it |
| What is lost if it leaves this role | One sentence |

Fill "designed for" from the upstream documentation, never from memory, and quote it: the first paragraph of the
project's README, its "what is X" page, its "when not to use X" section where one exists. "What is lost" is one
sentence per row and the cheapest question in the table; where the honest answer is "nothing but the runtime", write
that. Judging the rows is the `architecture` axis's job, in its "check the grain" step. The profiler only records.

Measured on a real run, a policy engine had been embedded to interpret the syntax tree of a foreign rule language: the
policy program was fixed, never changed with the policies, and unrolled recursion by hand because the language has
none. Five confirmed correctness defects sat in the interpreter file, one of them a constant where the language has no
recursion for the recursive check the operator needs, and a sixth was found two weeks later by hand: the tree is
unrolled to depth two, so a condition that nests three levels is denied. No report named the choice, because no stage
had asked what the engine was designed to do. The inventory row would have read: designed for declarative policies
written by policy owners; used as a fixed interpreter over an AST stored in `data`; written by the core team only;
lost if removed: nothing but the runtime. Two signals from the grain step in `axes/architecture.md` were measurable
on that row alone, an interpreter inside the interpreter and the emulation of a stated non-goal, so the threshold for
a finding was met before any defect count.

Then write `00-commands.md` — **the commands that actually work, having run each one yourself.** Without it, every
agent re-derives the build incantation, several get it wrong, and one reports a broken build that is only a missing
flag. Most repositories do not document this correctly; a few have it in `AGENTS.md`, and where they do, verify it
rather than copying it.

Cover: build, unit tests, a single test, lint, coverage, and whatever else the axes will need. For each, give the
exact command, the working directory, the expected wall-clock time, and — this is the part that saves the agents —
every non-obvious flag with one line on why it is needed. Record the toolchain you used (JDK, Go, Node, Python
version) and any version constraint you hit. Where a command does not work at all, say so explicitly, so an agent
does not spend its budget rediscovering the failure.

A command in this file that turns out to be wrong is worse than an absent one. Run every line before you write it —
and record the exit status the way the axes will read it. **Never take `$?` from the end of a pipeline**: it is the
last command's status, so `lint … | tail; echo $?` reports `tail` succeeding and turns a failing gate into a green
one in the file every agent trusts. Redirect to a file and check the status of the command itself. The same care
applies to any wrapper that swallows a status — `|| true`, a `set +e` block, a `make` target that ends in `echo`.
This exact mistake was made on a real run and an axis built a recommendation on the false "lint is green".

**Where a tool is missing, do not accept the gap — close it.** A review that reports "helm is not installed, so the
chart was not rendered" has spent a full agent to produce nothing. Work out what the axes will need from the
repository's own build files: `helm`, `helmfile`, `kustomize`, `controller-gen`, `kubeconform`, `kind`, `terraform`,
`vals`, `sops`, a JDK of a particular major version, a coverage or mutation plugin, a language server, a fuzzer, a
protocol reference implementation. Then, in the questions file, list what is missing, what each unlocks, and how you
would install it — and install the approved ones **before** the workflow starts, never from inside an axis. An agent
that installs a toolchain mid-run burns its budget on setup, and a second agent installing the same thing
concurrently is a race nobody debugs.

**Probe for a runtime; never assert its absence.** The most damaging thing this file can say is "no cluster / no
database / no device is available", because every axis then falls back to a simulator and qualifies its conclusions
accordingly. On a measured run the profiler wrote exactly that and had never checked: there was a live cluster with
the relevant CRDs already installed, and three axes went on to report a defect that only the fake client can produce
while a verifier wrongly refuted a real one the fake could not see. Run the probe, whatever the archetype implies —
`kubectl config current-context` and `kubectl get nodes`, `kind get clusters`, `docker ps`, a connection to the
database the tests expect — and record what answered. If a runtime does exist, say what it is, what is already
installed on it, and the rules for using it: create and delete your own namespace or schema, change nothing shared,
and never install or upgrade something the user depends on.

Two things stay true regardless. Install into a user-scoped location (`GOBIN=~/go/bin`, a Homebrew formula, a
`bin/` inside your throwaway worktree) rather than anywhere that changes the machine for other work; and pin the
version the repository asks for, since a newer `controller-gen` or `kubeconform` will report drift that is the
tool's, not the code's. Record in `00-commands.md` what you installed, at which version, and what it made possible.

Where the user declines an install, say so in `00-focus.md` and name the axis that will be weaker for it — that is a
coverage limitation, and the report must carry it rather than quietly omitting a section.

**Find the configuration where it actually lives, not where it ought to be.** A glob over the repository root is how
you conclude that a project has no lint configuration while CI has been enforcing one for a year — a mistake made on
a real run of this pipeline, in the one file every agent trusts. Three habits prevent it:

- **Ask the tool, not the filesystem.** `golangci-lint config path`, `npm config list`, `mvn help:effective-pom`,
  `helm template --debug`, `pytest --co -q` with the config echoed. The tool knows which file it will read; a
  directory listing only tells you which files exist. The two answers differ more often than you would think — in
  the case above, `.github/linters/.golangci.yml` existed *and* the tool ignored it, because it searches the working
  directory and its parents.
- **Search the whole tree.** Configuration hides in `.github/`, `.github/linters/`, `build/`, `ci/`, `hack/`,
  `config/`, tool-specific directories, and inside the build file itself (a `pom.xml` plugin block, a Gradle
  convention plugin, a `package.json` key).
- **Follow the configuration out of the repository.** CI routinely loads it from elsewhere: a checkout of an
  organization-level `.github` repository, a reusable workflow referenced as `uses: org/repo/.github/workflows/x@ref`,
  a shared chart, a base image, an organization Renovate or Dependabot preset. Fetch those and read them — they
  decide what actually runs on a pull request. Record where each configuration came from and **at which ref**: a
  shared config pinned to a moving `main` is a supply-chain fact worth a finding on its own, and it means the rules
  can change without a commit in this repository.

When local and CI configuration differ, say so explicitly in `00-commands.md` and name both. An axis told "there is
no configuration" will report the absence as a defect, and it will be wrong in a way that is expensive to unpick.

The file is yours alone: agents read it and never write to it. When one of them finds a correction, it writes
`work/commands-<axis>.md` instead, and later axes read those alongside the baseline. Fold the worthwhile ones back
into `00-commands.md` during the post-mortem — that is how the next review of this repository starts ahead of this
one. Do not let agents append to a shared file: several axes run concurrently, and one read-and-rewrite discards the
others' lines.

### 2. Agree the focus in a questions file

Write `questions.md` into the dossier. **Pre-fill every answer with your recommendation**, so the user can accept the
whole file by saying so and only edit what they disagree with. Structure:

```markdown
## 1. Archetype
<your classification and why>
**Answer:** protocol library

## 2. Axes to run
| Axis | Run? | Why |
| --- | --- | --- |
| protocol-conformance | yes | the point of the library |
| deployment-config | no | nothing is deployed |
**Answer:** as above

## 3. Where does it hurt today?
...
**Answer:** <your guess, or "unknown">
```

Cover, at minimum: archetype; surfaces; axes in and out with a one-line reason each; known pain points and past
incidents; what is explicitly out of scope; the stability contract (may the API change?); the depth — `coarse`
(contracts, boundaries, deployables; executes only what already exists) or `deep` (adds reproduction tests, mutation
runs, stress tests), which step 3 passes to every axis as `args.depth`; models per phase; whether to include a second
opinion on the top findings. For a system, also: which interactions matter most, and which components are in scope
only as far as they carry an interaction.

**And a runtime section, always — even when you found nothing.** Probing (step 1) tells you what exists; only the
user can tell you what may be touched, and the two questions have different answers far more often than not. Report
what the probe found, **what is already living in it**, and then ask:

| | |
| --- | --- |
| A runtime exists and is empty or clearly disposable | May the axes use it? State the rules you propose — own namespace, own schema, deleted afterwards, nothing shared modified. |
| A runtime exists and is somebody's working environment | Say so plainly and recommend **against** using it. A cluster running real workloads is not a test bed, and an axis given permission will happily install a CRD into it. Offer a disposable one instead. |
| No runtime exists | May one be created — `kind create cluster`, a compose file, a container, testcontainers? For an operator or a service this is usually the highest-value item in the whole questions file. |

Never let "no runtime" survive as an unexamined premise: it is the caveat that quietly degrades every axis at once,
because each falls back to a simulator whose behavior differs from the real thing in ways it will not notice.

Then stop and ask the user to edit the file inline and say when it is ready. Do not use `AskUserQuestion` for this —
the questions are interdependent and the user needs to see them together. Use `AskUserQuestion` only if the user's
edited file leaves a genuine contradiction.

When the user is done, read the file back and write `00-focus.md`: the resolved decisions only, no questions. That file
is what every agent reads.

#### Directed questions get exactly one owner

A directed question is a specific thing you want established — carried over from the user, from a design document, or
from something you noticed while profiling. It is the highest-value content in the focus file, and it is also the
easiest thing to lose, because it does not belong to any axis by default.

**Address each one to exactly one axis, by key, and never to two.** A question addressed to two axes jointly is
answered by neither: each reads it, assumes the other owns it, and neither reports its absence. Measured on a real
run, a question marked "for `correctness` and `security` jointly" produced zero occurrences of its subject in either
report, and the defect it pointed at turned out to be the most severe finding of the whole review — raised afterwards,
by hand, from a single grep.

Write them into `00-focus.md` under a `## Directed questions` heading (the consolidator reads that heading in that
file), one subsection per question, each headed with the owning axis:

```markdown
### For `correctness` — what the MVP deliberately dropped
<the question, what would settle it, and what makes the answer severe>
```

Where a question genuinely spans two axes, split it into two questions with different subjects, or give it to the one
that can execute the check and let the other read the answer. Do not hedge with "jointly", "and", or "either of".

An axis that cannot answer its question must say so under a "Направленные вопросы" heading in its report, with what it
tried. Silence is the failure mode this rule exists to prevent, and the consolidator is told to look for it.

#### An owner's constraint on a technology fixes how it is used, not whether

"We do not fork X", "X stays", "X is the standard here" are legitimate constraints and go into the focus file as such.
They settle how X may be used. They do not settle whether X belongs in the role it has, and a focus file that carries
the constraint without the question makes every axis treat the role as given. On a real run the constraint "the
engine is not forked" was agreed in the topology decision after the axes had run, the alternatives were compared only
inside "the engine executes everything", and no report named the misfit of the engine to its role. For each such
constraint, add one directed question for `architecture`: is X the right technology for the role the inventory row
records, and what force in the domain justifies it if not.

### 3. Run the pipeline

```js
Workflow({
  scriptPath: "${CLAUDE_SKILL_DIR}/workflow/deep-review.js",
  args: { dossier, repo, skill: "${CLAUDE_SKILL_DIR}", depth: "coarse", surfaces: [...], surfacesWithoutPack: [...],
          components: [...], axes: [...], models: {...}, completenessCritic: true }
})
```

`args.skill` is required and must be an absolute path; the script throws otherwise. Every axis prompt points its agent
at reference packs under that directory, and an agent that cannot resolve them reviews from memory instead. Claude
Code substitutes `${CLAUDE_SKILL_DIR}` before you read this file, so the value you pass is already the path.

`depth` is `coarse` (the default) or `deep`, from the questions file. The workflow puts the chosen depth into every
axis and verifier prompt: at `coarse`, an axis executes only what already exists and reports at the level of contracts
and boundaries; at `deep`, the unit-level work the axis files describe is in scope.

`surfaces` holds the forms from step 1 that have a pack in `references/surfaces/`: `cli`, `gitops-argocd`, `helm`,
`helm-qubership`, `kubernetes`, `mcp`. The script refuses any other name. Every axis is told to read those packs and to
obey the ownership table inside them; the distiller additionally carries their architectural questions into the
synthesis prompt. Leave it out only when the repository genuinely exposes no API — which is rarer than it looks.

`surfacesWithoutPack` holds the other forms from step 1, e.g. `["code-library", "rest-http"]` for a service that serves
a REST API and also publishes a client library. The workflow names these forms to every axis as reviewed by the
form-independent rules, so the gap shows up in coverage instead of disappearing.

`components` is for a system review, one entry per row of the profile's components table:

```json
{ "name": "orders", "repo": "/abs/path/orders", "ref": "v2.3.0", "role": "owns the order schema; publishes order.created" }
```

`repo` stays the checkout that hosts the dossier. With `components` set, every axis receives the list, every write-access
axis makes a worktree per component, the sweep in step 4a covers every component, and each finding carries a
`component` field. What the pipeline does not do: it does not clone or check out anything (step 1 did), it does not
select axes per component (one axis list covers the system, and the focus file says which components each axis reads
closely), and a surface list applies to the system as a whole. A system review that needs different axes per component
is two reviews: one dossier per component, then a system dossier whose focus file names the component reports as
prior art.

Build `args.axes` from the focus file. Each entry:

```json
{ "key": "concurrency-lifecycle", "phase": "evidence", "needsWriteAccess": true, "agentType": null, "model": null }
```

The script refuses an entry without a `key` and an entry whose `phase` is not `scout`, `evidence`, or `synthesis`,
because a misspelled phase would otherwise drop the axis from the run and from the failure list alike. Optional per
axis: `refuteModel` (the verifier's model, over `models.refute`), `effort`, `attempt` (see step 5), and
`distill: false` for a synthesis axis that reads the verified findings directly instead of a distilled prompt
(`runtime-verification` is the one that does).

Set `needsWriteAccess: true` for any axis that has to change the project to measure it — `tests` (coverage plugin,
mutation run), `correctness` (reproduction tests), `performance` (benchmark harness), `protocol-conformance` (fuzzer),
`api-compatibility` (building against the previous release). Axes that only read leave it off. At `depth: coarse`
the unit-level measurements are off, so only an axis that has to edit the project to render or run an existing
artifact (a coverage plugin for `tests`, a build against the previous release for `api-compatibility`) needs it.

**Also pass `sessionRepoIsTarget: true` when, and only when, this session's own repository is the one under review.**
Harness worktree isolation copies the *session's* repository, so on a cross-repository review it drops the agent into
an unrelated checkout. With the flag absent, the workflow skips harness isolation and instructs each write-access axis
to create its own worktree of the target repository under `work/<axis>-wt` instead. Getting this wrong is not a
cosmetic problem: an agent either reviews the wrong codebase or silently writes into the user's real working tree.

`phase` is one of three:

- `scout` — cheap and broad, runs first behind a barrier because the others read its output. `tests` and
  `dependencies` belong here.
- `evidence` — the main axes. They run concurrently and each is refuted as soon as it finishes.
- `synthesis` — `architecture`; `api-ux` when there is review history to distill from; `runtime-verification`, which
  settles the verified findings of the other axes against a running system. For `architecture` and `api-ux` a
  distiller agent writes `prompts/<axis>.md` from the evidence reports first, then the axis runs on that prompt.
  `runtime-verification` is passed with `distill: false` and reads `work/findings-<axis>.jsonl` directly.

Order inside a phase does not matter. Every axis that reports at least one finding is followed by an adversarial
verifier that writes `work/findings-<axis>.jsonl` (moving an earlier version into `work/history/`) and moves refuted
findings into a closing section of the report rather than deleting them. An axis that reports nothing gets no verifier;
the workflow tells the consolidator which axes were clean and which lost their verifier, so neither reads as a failed
run and a failed run never reads as clean.

**Leave `agentType` unset.** The specialized reviewers (`security-reviewer`, `protocol-compatibility-reviewer`,
`backward-compatibility-reviewer` and the rest) are built for reviewing a diff and their system prompts fight the
axis instructions: measured on this pipeline, `protocol-compatibility-reviewer` failed twice — once refusing over a
working-directory mismatch the other axes worked around, once emitting a placeholder structured output as its second
action, which ends the agent with an empty result that looks like "ran, found nothing". Use the default workflow
subagent unless you have evidence a specialist does better on a whole-repository axis.

Models: default everything to `sonnet` while debugging the pipeline. For a real run:

```json
{ "default": "opus", "refute": "opus", "consolidate": "opus", "critic": "opus" }
```

`models` also takes a key per phase (`scout`, `evidence`, `synthesis`), which an axis's own `model` overrides.

with `"model": "fable"` on `correctness`, `concurrency-lifecycle`, `protocol-conformance`, and `architecture`;
`"model": "opus"` on `security` (fable declines vulnerability work); `"model": "sonnet"` on the tool-driving axes —
`tests`, `dependencies`, `docs-onboarding`, `build-release`.

`models.refute` deserves its own thought. Measured on a 12-axis run, the verifiers cost 35% of the whole budget and
returned zero rejections and two downgrades out of 128 findings, because half of them "verified" by re-reading the
lines the finding already quoted. Buying a stronger model does not fix that — the confidence rule below does. Keep
verification on `opus` and watch the executed-versus-read rate the consolidator reports; if it stays near zero, the
prompt is still wrong and no model will save it.

**Confidence is assigned by the verifier, never by the axis that raised the finding.** An axis reports `method`
(`executed` / `traced` / `inferred`) and its `evidence`; the verifier may stamp `CONFIRMED` only when it executed
something itself. That is what makes the label mean anything, and it is also the verifier's one unambiguous job — it
can always decide whether it ran something, whereas "is this finding wrong" invites agreement.

The workflow writes `reports/<axis>.md`, `prompts/<axis>.md` for the distilled synthesis axes, `findings.jsonl`, and
`synthesis.md`.
It returns counts only — read the files.

### 4. Triage

Read `synthesis.md`, then the reports behind anything that matters. For each finding, set `verdict` and, when
rejecting, a typed `rejection_reason` in `findings.jsonl`:

| `rejection_reason` | Meaning | Where the fix goes |
| --- | --- | --- |
| `convention` | A rule that lives outside the code: platform guarantee, CI behavior, deliberate team decision | `AGENTS.md` / `CLAUDE.md` |
| `guard-missed` | The code does handle it; the reviewer missed the guard | A comment next to the guard |
| `out-of-scope` | Real, but not this review's question | The axis file or `common-rules.md` |
| `model-error` | Fabrication | Nowhere |
| `accepted-debt` | Correct, and not being fixed | An ADR |

### 4a. Sweep after every run

An agent that dies mid-run — a dropped API connection, a timeout, a kill — never reaches its own teardown, so
anything it created outlives it. Harness-managed worktrees are cleaned up for you; everything an agent made itself is
not. After each pass, check and clean:

```bash
git -C <repo> worktree list          # remove any under <dossier>/work/
git -C <repo> status --porcelain     # must be empty
kind get clusters                    # and the equivalent for any other runtime
docker ps -a                         # containers a test harness started
```

On a system review, run the two `git` lines against every component's checkout.

Do this before re-running, too: an axis that retries will try to create the worktree or the cluster it already
created and fail on a name collision, which then looks like a second, different failure.

### 5. Re-run what was wrong, not everything

A bad axis costs one stage, not the run. Resume caches every agent call on its prompt text, and the prompts carry only
the *paths* of the axis file and of `prompts/<axis>.md`, so editing those files changes no prompt and a plain resume
returns the old result. To re-run one axis after fixing its file or its distilled prompt, set `attempt: 2` on that
axis entry and re-invoke with `{ scriptPath, resumeFromRunId, args }` otherwise unchanged. The attempt number is part
of the prompt. Resume returns the longest unchanged prefix of agent calls from cache and runs everything from the first
changed call on, so the axes sequenced before the bumped one come back from cache, and the bumped axis, its verifier,
every axis sequenced after it, the distillers, the consolidator, and the critic run again. A re-run of an early axis
therefore costs most of the run; a re-run of a synthesis axis costs little.

To re-run one axis in a fresh run instead, pass only that axis in `axes` and the keys of every other axis whose report
is already in the dossier in `priorAxes`; the consolidator then covers all of them. Without `priorAxes`, a fresh run
consolidates the one axis it ran and writes a `synthesis.md` that covers nothing else.

### 6. Post-mortem

Group the `convention` rejections and propose a concrete diff to the project's `AGENTS.md`. Phrase each rule as a fact
with its reason, never as an instruction to suppress findings, and give it a falsification hook: *"X is guaranteed by
the platform, so callers do not validate it — but a path that forwards X into a URL before canonicalization is still a
bug."* A rule that only says "do not report this" will hide the real defect when it eventually arrives.

Rules that need a paragraph go into a linked document, not into `AGENTS.md` itself, which is loaded into every session
and has a context budget. Group `out-of-scope` rejections separately and fix the axis files — that is how the skill
gets better.

Then read the technology inventory against the findings that survived refutation. Every finding whose `tool_limit`
(the `Tool limit:` line of its report) names a technology should point at an inventory row; a technology that several
findings name and the inventory lacks was missed at profiling, so fix the profile step rather than the axis. Where
`architecture` produced no `FIT` finding and no "checked and sound" line for a row with two or more such findings, the
grain step did not run on that row.

## Files

- `references/common-rules.md` — evidence bar, falsification, confidence labels, severity ladder. Every axis prompt
  includes it verbatim.
- `references/report-format.md` — the report and finding block shape. Also included verbatim.
- `references/archetypes.md` — archetype to axis mapping.
- `references/axes/<key>.md` — one file per axis: its filter, its questions, its rejection rules.
- `references/surfaces/<form>.md` — one file per API form: the normative source where one exists, the form-specific
  checks, what counts as a breaking change there, the tooling, and an ownership table routing each concern to the axis
  that owns it. Cross-cutting by design: several axes read the same pack. Adding a pack means adding its name to
  `KNOWN_PACKS` in the workflow as well.
- `workflow/deep-review.js` — the pipeline.
- `scripts/new-dossier.sh` — dossier layout.

## Rules for this skill itself

- The target is a repository, a deployable, or a system of them. When the request names a class, a file, a package, a
  pull request, or a diff, stop before creating a dossier and name the skill that fits (`adversarial-code-review`,
  `codex-review`, or a direct review).
- Never run an axis whose file does not exist. Adding an axis means writing its file first.
- Never skip the questions file. A review with the wrong focus is more expensive than no review: it produces a long
  document that has to be read before it can be discarded.
- The dossier lives at `<repo>/.review/<date>/` and is gitignored by the setup script. Do not put it in a session
  scratchpad — the point is that it outlives the session.
- Report honestly what did not run. If an axis produced nothing because the agent failed, say so; do not let a missing
  section read as a clean bill of health.
