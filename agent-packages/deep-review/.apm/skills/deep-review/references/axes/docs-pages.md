# Axis: documentation pages

Finding prefix: `DOCP`.

Can the reader of each user-facing documentation page find what they came for and act on it, and is every promise
the page makes true of the code? The pages are the user guide, feature and how-to pages, administration and
installation guides, the configuration reference, hand-written API reference prose, troubleshooting pages, and the
docs site that serves them. Their reader holds one question and arrives mid-page from a search, a link, or an error.
If the only user documentation is the README and a getting-started page, say so and stop: `docs-onboarding` owns them.

The rubric is the `docs-page-authoring` skill, at the path your prompt gives. Read §1–§7 before starting and cite
findings by section number. Do not apply §7a, §7b, or §8: they review an edit, and this axis reviews the pages as they
stand.

**Do not review style.** Wording, tone, sentence length, dialect, heading case, and anything markdownlint enforces are
not findings, however much better a rewrite would read. A wording problem is a finding only when it misleads or blocks
the reader: a paraphrased error text that a search cannot match, a name that differs from the code's spelling, a
sentence whose missing condition makes it false for a case the reader is in.

## What counts as a finding

Each shape names its expectation source. A gap with no source is a preference.

- **A promise the code contradicts** (§6). A default, unit, range, limit, or accepted form on the page that differs
  from the code; `64 MB` beside `67108864` counts. Also an option, flag, key, or env var the code does not read, or
  reads under another spelling, and an error text the code does not emit. The code, read at the version the page
  claims to describe, is the source. Wrong rates higher than missing. The same shape covers an entry for something
  the code no longer has (a removed option with no removal marker, an error the code stopped emitting) and, under
  §1, implementation stated as a promise once it is false or names a symbol the reader cannot set.
- **An item the code has and the pages lack** (§7). An option, flag, env var, config key, chart value an admin guide
  relies on, user-visible error or error code, or supported version or platform, with no entry or row a reader can
  find. The source is the §7 table: the promise exists in the code, so the page owes it.
- **An option entry missing a slot the reader needs** (§2). Missing default, unit, valid values, scope, or behavior at
  the limit, where the reader must read the source to configure the option safely. The source is §2's slot table.
  Report the slot by name ("no unit: `timeout: 30` could be seconds or milliseconds; the code reads milliseconds").
  A missing rationale or "when to change it" slot is a finding only when the default is unsafe for a realistic
  deployment.
- **An interaction stated on one side only** (§2, slot 6). The reader of the other entry configures it wrongly.
  Name both entries and the configuration that fails.
- **A fenced example that does not run or validate** (§6). It fails to parse, fails the schema, names a key that does
  not exist, or uses a removed command or endpoint. Executed evidence only: run it, or validate it, then report.
- **A reader who cannot land** (§3, §5). An error D5 will search for, an option D4 will search for, or a task D3 will
  search for, with no heading, row, or list entry carrying its name. A link or fragment that resolves to nothing,
  including a renamed heading whose old anchor other pages still use, a nav entry pointing at a missing page, and a
  page reachable from no nav or link while it holds the only copy of a fact the reader needs.
- **A copy that contradicts its record** (§4). Two pages state different defaults or semantics for one item. Name the
  record (§4: the most detailed copy) and the copy that disagrees with it.
- **A section whose purpose blocks its reader** (§4, §3). A troubleshooting entry that explains the mechanism and
  never names the fix, a how-to that stops at a concept, a reference entry whose first paragraph never states what the
  item controls. Report only when you, as that reader, failed the task on it; name the task.

## What is not a finding

- Style, wording, and structure that a rewrite would improve while the reader still gets the answer.
- A page that mixes genres (§4 says mixtures are normal), and duplicate copies that agree.
- A missing heading or `Since X.Y` marker that nobody would search for, on a project that supports one release line.
- History narration (§1) that does not misstate the current behavior.
- Missing documentation for internal or unreleased items: package-private config, test-only flags, feature flags the
  project marks experimental and undocumented on purpose (check the marker).
- Doc comments, generated API reference, design documents, ADRs, contributor docs: see *Ownership*.
- The absence of a link checker or a doctest harness, unless this run found rot that the tool would have caught.
  Then report it once, inside the finding about the rot.

## Method

Cheapest decisive checks first. Keep every extracted list and every command output under the dossier's `work/`.

1. **Map the pages.** Find the docs toolchain by its configuration (`mkdocs.yml`, `docusaurus.config.*`, `hugo.toml`,
   `antora.yml`, `conf.py`, a chart `README.md.gotmpl`) and build the site if it builds offline. Record which docs
   version each page claims to describe, and docs that live outside the repository, if the profile names them. List
   every page with its genre and reader from §1 and §4. Mark the pages on the onboarding drill path (README,
   getting started, first tutorial): `docs-onboarding` owns them.
2. **Inventory the code's knobs.** Extract mechanically, never from memory: env var reads (`os.Getenv`, `getenv`,
   `process.env`, `@Value`, `envconfig`/`mapstructure`/`yaml` struct tags, viper and Spring bindings), flag
   definitions, config schema files, the env and args of deploy artifacts (Helm templates, Compose, `.env.example`),
   user-visible error texts and error-code enums, and supported versions (CI matrix, `engines`, `kubeVersion`,
   compatibility constants). Record each item's default as a value with its unit.
3. **Diff both ways.** Grep the pages for each inventory item: missing, stale, or mismatched. Then extract every
   identifier the pages state (code spans, keys in fenced config, flags in commands) and grep the code for each: names
   that resolve to nothing are stale. The result is the required inventory table below.
4. **Validate the fences.** Skip fences a doctest harness already runs, and say which. Parse JSON and YAML; validate
   config snippets against the schema the code ships (`values.schema.json`, a JSON Schema, an OpenAPI document); run
   CLI examples with `--help` or a dry run; compile code snippets where the toolchain is in `00-commands.md`; send API
   examples only to a local instance you started. Never point an example at a shared system.
5. **Check links and anchors.** Run the site's strict build or a link checker offline for internal links. Compute
   heading slugs by the generator's rules and resolve every fragment. Probe external links sparingly; a dead external
   link is a finding only when the reader needs the target.
6. **Read from each reader's seat.** From the profile, pick at least two realistic tasks each for D3, D4, and D5 (for
   D5, take literal error strings from step 2 and search the built site or the Markdown for them), and one for D6 if
   the project ships a migration guide. Enter each where a search would land you, read one paragraph per §3, and
   record whether you could act without reading the source. That transcript is the evidence for every §3 and §4
   finding.

**Coverage** names the pages read and the pages skipped, the inventory sources grepped, the fences validated and the
fences left unchecked with the reason, and the reader tasks run. **In a slice**, inventory only the component's knobs
and read only its pages; a shared page, such as a global configuration reference, is checked only for that
component's entries. The slice named `site`, or the first slice where none is, also owns the docs site build, links,
anchors, and nav, and the copies that contradict their record across pages (§4).

## Required section: Inventory diff

One row per inventory item with a defect, plus a count of the items that matched:

| Item | Kind | Defined at (`path:line`) | Code default | Documented at | Documented default | Status |
| --- | --- | --- | --- | --- | --- | --- |

`Status` is one of `missing`, `stale`, `mismatch`, `slot missing: <slot>`. Group a cluster of rows with one cause
into one finding (for example, a whole subsystem's env vars absent from the reference), not one finding per row. An
item documented correctly only on a drill-path page counts as documented; a mismatch on such a page goes under
*Cross-axis notes* for `docs-onboarding`.

## Severity

Rate by what the reader does after following the page. `HIGH` is reserved for a page that leads a competent reader into
a harmful action: a troubleshooting entry that prescribes the wrong fix for an error the system emits, or a limit stated
higher than the code enforces, so the reader sizes a deployment that fails under load. A wrong default or name that
produces a failing configuration the reader can diagnose is `MEDIUM`. A missing entry the reader needs for a realistic
task is `MEDIUM`; one only an edge case needs is `LOW`. Findability, anchors, and missing slots are `LOW` unless a task
in step 6 failed on them.

## Ownership

| Concern | Owner axis |
| --- | --- |
| README, getting-started, and first-tutorial pages: the drill from nothing to a first working result, and every claim on those pages | `docs-onboarding` |
| Agreement of README, `--help`, completions, agent snippet, MCP registration, where a surface pack routes it | `docs-onboarding` (the pack wins) |
| Every other user-facing page; the inventory diff across all pages; troubleshooting and runbook pages and their coverage of errors and terminal states; links, anchors, and nav of the docs site | `docs-pages` |
| Names of options and APIs, shape of the API, doc comments in code, generated API reference, OpenAPI and tool descriptions, chart value documentation in `values.yaml` comments and the schema (per `surfaces/helm.md`) | `api-ux` |
| Code that contradicts a page whose promise is what the user would reasonably expect | `least-surprise`, or `correctness` when a specification states it |
| Executing a documented install procedure | `deployment-config` |
| Executing a documented upgrade procedure or migration runbook | `upgrade-migration` |
| A break with no migration or deprecation note; a deprecation with no replacement | `api-compatibility` |
| Changelog and release notes; a docs site that fails to build; generated README drift | `build-release` |
| Wording and shape of the error message itself | `error-model` |
| The signals an operator reads (logs, metrics, status) | `observability-operability` |
| A page that tells the reader to configure something insecurely | `security` |

When a page and the code disagree, the owner is the side the fix must change, the rule `least-surprise.md` also
states. When the page is the only statement of the behavior and the product's other words (labels, help, option
names) agree with the code, or the code holds the intended contract (a test pins it, a changelog announced it, the
page predates the change), the page is the defect and this axis reports it. When the product's other words agree with
the page, or the page describes the safe behavior and the code destroys or exposes data, the behavior must change:
record one line under *Cross-axis notes* for the owner above. When the evidence does not say which side is intended,
report it here, say so under *Open questions*, and name the other axis.
