---
name: troubleshooting-skill-creator
description: Use when the user asks to create, add, regenerate, or extend a repository-specific troubleshooting skill for the current checkout, a repository under `repos/`, or another named repository. This skill authors a skill; it does not diagnose a live incident.
---

# troubleshooting-skill-creator

## What you are building

One APM package inside the target repository:

```text
<target-repo>/
├─ agent-packages/
│  └─ troubleshoot-<topic>/
│     ├─ apm.yml
│     ├─ README.md
│     └─ .apm/skills/troubleshoot-<topic>/
│        ├─ SKILL.md
│        ├─ references/troubleshooting.md   ← canonical, the actual product
│        └─ scripts/show_cases.py
└─ docs/
   └─ troubleshooting.md                     → symlink into the package
```

Only two files carry repository-specific content: `references/troubleshooting.md` and the `SKILL.md` that reads it.
Everything else is fixed scaffolding. `references/package-template.md` holds the textual files verbatim, and
`scripts/show_cases.py` is the helper copied into every generated skill.

The reference is the product. A perfect skill wrapped around a thin reference diagnoses nothing, so most of the work
below is research, and the packaging at the end is mechanical. Resist the pull to scaffold first: an empty package
invites you to fill it with whatever you already know, which is exactly the failure mode this procedure exists to
prevent.

## Rules that hold across every phase

- **The repository outranks the internet.** Material already in the target repository was written by people who
  operated this deployment. Where it and an external source describe the same failure, the repository's wording wins,
  and its case survives into the new reference intact. Web research fills gaps; it never overrules local knowledge.
- **Every case is traceable and reachable here.** A case comes from repository material or a citable source, and the
  shipped code or configuration can produce its preconditions. External research does not prove that the failure has
  occurred on a real installation of this product. A case for a component this repository does not ship is a defect.
- **Never invent a log line.** Quote symptoms from real output — repository docs, issues, an upstream bug report. A
  reconstructed error string cannot be matched against what the reader has on screen, which is the one job symptoms do.
- **The format contract is not negotiable.** `references/troubleshooting-format.md` governs headings, labels, ordering,
  and the danger markers. Read it before writing the first case, and audit against it before handing off — the skill's
  whole retrieval strategy assumes it holds.

## Phase 1 — Understand the repository

Read the target repository deeply enough to name what can break in it. You are after the failure surface, not an
architecture summary.

Dispatch parallel subagents (they read a lot and you need only their conclusions), one per question:

1. **What does this repository ship?** Purpose, the artifact it produces (operator, exporter, installer, plugin,
   proxy), and the runtime it lands in. Record the canonical product name and every evidence-backed alias used in
   repository documentation, configuration, chart names, or supplied tickets, preserving spelling and capitalization.
   Format `<product-names>` as the canonical name followed by the aliases in parentheses. Read `README.md`, `docs/`,
   `charts/`, `Makefile`, CI workflows.
2. **What technologies does it stand on?** Languages and frameworks from the manifests (`go.mod`, `pom.xml`,
   `package.json`, `requirements.txt`); every external system it talks to (databases, brokers, storage backends,
   Kubernetes APIs); every image it deploys. Names *and* the roles they play — "Cassandra as the trace store" beats a
   dependency list, because storage backends fail differently from sidecars. Record which side of the Phase 3 research
   split each one sits on: a system the deployment operates separately — a database, a broker, the git server it
   clones from, the container runtime — fails in ways outsiders document. A library linked into the process — a DI
   container, a template engine, a parser — fails as this code's own misuse of it and is not documented anywhere but
   here. A CLI or a library repository often stands almost entirely on the second kind.
3. **How is it installed and configured?** Helm values, operator CRs, Ansible roles, environment variables, secrets,
   TLS, probes. Installation is where most reported failures happen, so this is not background reading.
4. **What does it already say about failure?** The next phase, run in parallel — see below.

Write the result to the workspace as a short inventory: components, technologies with roles, install path, config
surface. This inventory is what the research phase is built on; take it seriously.

## Phase 2 — Harvest what the repository already knows

Find every place the repository discusses failure. `docs/troubleshooting.md` is the obvious one and rarely the only
one. Search for `troubleshoot`, `known issue`, `FAQ`, `common problems`, `if it fails`, `error`, `debug` across `docs/`,
`README.md`, every nested `*/README.md`, chart notes, and issue templates.

Read what you find and extract each failure into a draft case. Preserve the operator's own words — their symptom
phrasing is what a colleague will search for. Where the source is loose about the format contract (a "Solution" heading
with no symptom, causes and fixes braided into a paragraph), restructure it into the case template without dropping the
technical content. Restructuring is translation, not rewriting: if you find yourself improving the engineering, stop —
you are guessing about a system you have not operated.

Also note what these documents *imply*: a page dense with Cassandra connection failures tells you where this deployment
actually hurts, and that is a research lead for Phase 4.

## Phase 3 — Assess coverage, and say so out loud

Compare the failure surface from Phase 1 against the cases from Phase 2. For each component, ask whether an operator
hitting a common failure would find it answered.

Expect large gaps. Most repositories document a handful of failures their maintainers happened to hit and nothing about
the technologies they embed, so a repository with no troubleshooting file at all is the normal starting point rather
than a surprise.

Split the gaps by where an answer could come from, because that decides the whole next phase. A failure has a
researchable third-party surface when it happens at a boundary someone outside this team operates and writes about — a
git server refusing credentials, a broker unreachable, the JVM out of heap, a container mount denied. Judge the
boundary, not the dependency: a library linked into the process — a DI container, a template engine, a parser, a
client hitting nothing but this code's own inputs — fails as this repository's misuse of it. External search returns
generic library docs rather than a case that fires here, so it lands on the first-party side even though it is not your
code. The service this repository itself implements is first-party for the same reason: no search covers its handlers,
its config parsing, or its own error strings, and an agent that searches anyway comes back with plausible inventions. A
dependency list is therefore not the split — on a CLI or a library repository most of the embedded dependencies land
first-party, and only a handful of operated boundaries remain to research.

A repository that leans this way has to hear it plainly: external research reaches only that handful of boundaries, and
the bulk of its failure surface is filled instead by tickets, maintainer-named problem classes, and the code itself.
See `references/deep-research-handoff.md`.

Report the gap to the user before spending research effort: components covered, components untouched, which of them
external sources can speak to, and where you intend to dig. This is a checkpoint — a maintainer often knows that a
component is out of scope, unused in practice, or about to be replaced, and thirty seconds of their attention here
saves an hour of research into a dead end.

Ask for a ticket or issue export at this checkpoint — a support-ticket dump, a Jira query, the GitHub issue list,
incident notes. It is the record of what operators actually hit, so it turns coverage from a guess about the code's
failure surface into a measurement against real requests: the failures that recur there are the ones the reference must
answer first. For a first-party-heavy repository it is also the primary source of cases, not only a yardstick for
coverage, so the earlier you have it the better Phase 4 goes — Phase 4 uses the same export as its first-party input.
Where no export exists, ask the maintainer to name the problem classes they see.

## Phase 4 — Research the failure modes

Now fill the gaps. Read `references/research-playbook.md` before starting — it holds the search strategy, the source
hierarchy, and the bar a case must clear to be included.

The short version: for each technology and each install step, find how it actually breaks in the field. Vendor
troubleshooting guides and upstream issue trackers give you mechanism; Stack Overflow, GitHub issues, and Reddit give
you the symptom in the words a person under pressure types into a search box. You need both — mechanism without the
verbatim symptom produces a case nobody finds, and a symptom without mechanism produces a case nobody can act on.

### Ask the user how to run this phase

Searching is the slowest part of this skill and the part that consumes the most context, so the user chooses where it
happens. Offer all three routes before any search starts, using the wording in
`references/deep-research-handoff.md`:

1. **Deep Research** — you print one prompt carrying the component inventory and the gap list, the user runs it and
   pastes the report back. Read `references/deep-research-handoff.md` and follow it: it holds the prompt template, what
   fills each placeholder, and the verification the report must pass before any case reaches the reference.
2. **This session** — you dispatch search subagents in parallel, one per technology or per install phase, each
   returning structured cases rather than a pile of links.
3. **Tickets or maintainer-named problem classes** — the only route for the repository's own code, where no external
   source exists. The user supplies the symptoms; you find the diagnosis and the fix in the code, quoting the service's
   error strings from the source rather than reconstructing them.

The options combine: a repository with both surfaces usually wants one of the first two for its dependencies and the
third for its own code. When Phase 3 found the repository leans first-party — few operated boundaries, most of the
surface in its own code — say so as you offer, and steer toward option 3: options 1 and 2 reach only that handful of
boundaries, so presenting Deep Research as the default route would send the effort where the failures are not. Wait for
the answer rather than starting to search while you ask.

Stop when every component in the inventory has its common failures covered and new searches stop turning up new
failures. Depth on the components this deployment leans on beats one shallow case per technology.

## Phase 5 — Compile the reference

Write `references/troubleshooting.md` against `references/troubleshooting-format.md`. Read the contract now, in full,
even if you read it earlier — the details it governs are exactly the ones that erode while you are concentrating on
content.

Order: repository-sourced cases first within each component, then researched ones. Group by component under `##`, in
the order a reader reaches them (install before runtime; the component that fails most first). Cases at `###`,
reference sections after the cases they belong with.

Three structural rules carry more weight than they look like they do, because the generated skill's retrieval depends
on them: every case sits at `###`, every `###` title is unique across the document, and each case's `**Symptoms:**`
label sits exactly two lines below its heading with nothing in between. The skill finds cases by pulling the whole
symptom catalog, then loads a section by its exact title. A duplicate title is ambiguous, and a case that opens with an
intro sentence is invisible; either defect prevents reliable retrieval.

### Judge the danger yourself

Sources will not do this for you. A vendor page prints `rm -rf` on a data directory as an ordinary step, a forum
answer says "just restart the pods", and neither mentions what it costs — the author knew, and assumed you did. You
are writing for someone whose system is already broken, at night, who will run what the page says.

So assess every step you write, in both directions:

- **Does it change the system?** Then it belongs under `**How to fix:**`. Anything under `**How to check:**` must be
  read-only, even when the source presented a restart as diagnosis. Move it; do not annotate it.
- **Does it destroy data, interrupt a service, remove a protection, resist reversal, or cost real time on a system
  already in trouble?** Then it opens with `**DANGEROUS — <consequence>.**`, before the instruction and before the
  command, naming what is lost in concrete terms. Add the marker on your own judgment: the absence of a warning
  upstream says nothing about the cost here.

Split any step that mixes a safe half with a destructive one — a marker cannot be honest about both. Put the safe fix
before the destructive one, and name the backup or reversal path in the same step as the dangerous action.

Then audit the file against the contract's own checklist — the section titled *Auditing a file against this format*.
Run it as a check, not as a memory exercise: a `**How to check:**` step that restarts a service is the one defect in
this document that breaks systems rather than annoying readers.

### Screen out the cases that will never fire

A troubleshooting reference fails quietly: a plausible but untraced case reads well, cites something, and matches no
incident anyone will ever have. It never fires, and it costs trust in the cases that do — a reader who catches one
invented claim starts discounting the whole file.

This audit runs once the reference is complete, and not by you. By now your context holds every source, draft, and
assumption the cases were written from, so you will read what you meant rather than what the file proves. Dispatch a
fresh subagent for a read-only audit:

1. Give it the compiled reference, `references/evidence-checklist.md`, and the target repository path — nothing
   else. Withholding your research notes is the point: every claim must be traceable from the file and the
   repository alone.
2. Have it verify each case only from repository sources, offline rendering, read-only validators, and supplied
   artifacts. It must not access a live system, start a component, reproduce a failure, apply a fix, or edit the target
   repository.
3. Have it report only claims it could not confirm, with the missing evidence for each one. Confirmed cases are omitted,
   and no grade or verification marker is written into `references/troubleshooting.md`.
4. Fix traceability gaps and re-dispatch. If a source-backed external case remains unverified against this deployment,
   keep its required sources and carry the limitation only into the final chat handoff. Delete a case that has neither
   deployment evidence nor a concrete path to confirmation.

## Phase 6 — Assemble the package

The generated package is the same in every repository. The consumer `SKILL.md` — the skill that reads the reference
and diagnoses one reported problem — differs only in its product name and component list, because the procedure it
performs (index the symptoms, match, read one case, report) does not vary by product. All the variation between
repositories lives in the reference you just compiled.

Before copying scaffolding, inspect the target repository for an existing generated package. Use this compatibility
checklist on both new and existing repositories:

- [ ] The package directory, package manifest, skill directory, and skill frontmatter use `troubleshoot-<topic>`.
- [ ] The generated skill description names the canonical product, every evidence-backed alias, and its components.
- [ ] The generated skill contains `scripts/show_cases.py`, copied unchanged from this creator skill.
- [ ] With only the catalog path, the helper prints every case heading and complete `**Symptoms:**` block.
- [ ] With a section title after the catalog path, the helper prints that complete `###` section.
- [ ] Every `###` title is unique across the canonical reference.
- [ ] The consumer contains no inline Python, `rg`, or `grep`.
- [ ] The consumer defers final output, actionability, and user interaction to an enclosing assessment contract.
- [ ] The consumer retains its standalone output when no enclosing contract exists.
- [ ] The canonical `references/troubleshooting.md` exists, and `docs/troubleshooting.md` points to it with Git mode
  `120000`.
- [ ] Active manifests, documentation, and tests refer to `troubleshoot-<topic>`, not the legacy package name.

The legacy generated name is `<topic>-troubleshooting`. If only that package exists, migrate the package and skill
directories to `troubleshoot-<topic>`, then refresh `apm.yml`, `README.md`, and the consumer `SKILL.md` from the current
template, and copy the current `scripts/show_cases.py` helper into the generated skill. Move the canonical
`references/troubleshooting.md` with its directory; preserve its bytes and case structure unless the user separately
requested a catalog content change. Retarget the verified legacy documentation symlink to the new canonical path, and
find active repository references to the exact legacy package name and update them to `troubleshoot-<topic>`. Preserve
an existing package version instead of resetting it to the template's `1.0.0`. If both legacy and current package
paths exist, a symlink points anywhere else, or a scaffold file contains non-placeholder custom behavior, stop and ask
the user which copy or behavior is authoritative.

After the check, copy `apm.yml`, `README.md`, and the consumer `SKILL.md` from
`references/package-template.md` verbatim and substitute the placeholders. Copy this creator skill's
`scripts/show_cases.py` into the generated skill's `scripts/` directory without modification. Do not
reword the hard rules, procedure, contract integration, or standalone output format to fit this product better: they
keep a diagnosis bound to the reference and the enclosing assessment policy. For an existing package, retaining its
current version is the only exception to copying the `apm.yml` template value.

Naming: `troubleshoot-<topic>`, where the topic is what an operator calls the thing, not the repository slug. For
example, use `troubleshoot-jaeger` rather than prefixing it with an organization or repository name. The package
directory, the `name:` in `apm.yml`, the skill directory, and the skill's `name:` all carry that same string.

Then wire the human-facing copy. The canonical file stays in the package, next to the skill that reads it. Resolve
`<target-repo>` to an absolute path before running commands.

First inspect `docs/troubleshooting.md` and `docs/troubleshooting.superseded.md`. When the troubleshooting document is
an existing regular file, migrate all of its cases, ensure the superseded path is free, rename the document there, and
add the pointer header shown below. Do this before creating the symlink. When the path is already a symlink to the
current canonical reference, leave it unchanged. When it points to the verified legacy canonical reference being
migrated, retarget it as required by the compatibility checklist. For any other symlink target or an occupied
superseded path, stop and ask the user before replacing anything.

Once `docs/troubleshooting.md` is free, create the relative symlink:

```bash
mkdir -p "<absolute-target-repo>/docs"
cd "<absolute-target-repo>/docs"
ln -s ../agent-packages/troubleshoot-<topic>/.apm/skills/troubleshoot-<topic>/references/troubleshooting.md \
  troubleshooting.md
git -C "<absolute-target-repo>" add docs/troubleshooting.md
git -C "<absolute-target-repo>" ls-files -s -- docs/troubleshooting.md
```

The last command must report mode `120000`. The symlink takes the path the repository's existing troubleshooting
document already occupied, so existing links keep resolving. Open the renamed review copy with this pointer header:

```markdown
> Superseded by [docs/troubleshooting.md](troubleshooting.md), which carries every case from this file.
> Kept for review of this change; delete once the new document is merged.
```

Its cases must already be in the new reference by then — the rename is bookkeeping for the reviewer, not a way to park
content you have not migrated. Say plainly in the handoff which cases moved where.

## Phase 7 — Verify with evals

Test the generated skill with the available skill-evaluation workflow rather than by reading it and judging that it
looks right. Ask the user how far to take it: three cases as a smoke test, or the full loop with baselines, grading, and
a benchmark. When no eval harness is available, run the same scenarios manually and capture the prompts and outputs.

Test cases are a pasted symptom in an operator's own words — not the case title from the reference, or you are testing
string matching instead of diagnosis. Cover: a symptom that maps cleanly onto a case, a symptom whose wording differs
from the reference's, and a symptom no case covers (the skill must say so rather than improvise).

Also run one discovery scenario in which the ticket uses only an alias from `<product-names>`. The generated skill must
be selected before its diagnostic procedure can pass the scenario.

Store every eval artifact under `tests/agent_skills/evals/<skill-name>/` in the target repository, replacing
`<skill-name>` with the generated skill's name. Keep prompts, outputs, grading, and benchmark data there, outside the
skill package at `agent-packages/<skill-name>/`. These are internal testing artifacts: do not ship them in the APM
package or commit them unless the user explicitly asks.

## Phase 8 — Hand off

Give the user the reference and the eval results. Report verification by exception: list only what remains unconfirmed
or incomplete.

- The reference itself (path, case count, coverage per component).
- Claims whose sources, deployment applicability, checks, or fixes could not be confirmed, plus the artifact or
  maintainer input needed to resolve each gap.
- Externally researched cases that have not been verified against a real installation of this product.
- The eval result summary and the path under `tests/agent_skills/evals/<skill-name>/`, when evals ran.

Omit confirmed cases from the handoff. Do not add confidence ratings, evidence grades, or verification markers to the
troubleshooting reference or other user-facing documents.

## References

- `references/troubleshooting-format.md` — the format contract for the reference. Read before Phase 5.
- `references/evidence-checklist.md` — what a case may assert and the proof each assertion needs. Dispatched to a
  fresh subagent once the reference is compiled (Phase 5); the author does not audit their own file.
- `references/research-playbook.md` — search strategy, source hierarchy, inclusion bar. Read before Phase 4.
- `references/deep-research-handoff.md` — the Deep Research prompt and how to verify what comes back. Read at Phase 4
  when the user picks Deep Research.
- `references/package-template.md` — verbatim scaffolding for the generated package. Read at Phase 6.
- `scripts/show_cases.py` — fixed symptom-catalog and section reader. Copy unchanged at Phase 6.
