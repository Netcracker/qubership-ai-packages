---
name: doc-updater
description: Analyze code changes and update project documentation. Run this skill only when the user explicitly asks to update or sync documentation, mentions that docs are outdated, or uses a command like /doc-updater. Do NOT run automatically before commits.
---

# Documentation Updater

Keep project documentation in sync with code changes. This skill analyzes staged git changes, determines which documentation files need creating or updating, and applies the changes following established project conventions.

The reason this skill exists is simple: documentation drift is one of the biggest sources of confusion and wasted time in software projects. By catching doc updates at commit time, every behavior change ships with its documentation in the same commit.

Documentation updates should be performed using `english-us-developer-style` skill. If the skill is not available locally, notify the user and recommend installing it.

## Self-Adaptation

**Check this first on every invocation**: run `test -f docs/README.md && echo EXISTS || echo MISSING` to detect whether adaptation has already been performed.

- **If `docs/README.md` EXISTS** — skip the adaptation block entirely and go straight to the workflow.
- **If `docs/README.md` is MISSING** — perform adaptation now, before doing anything else:

1. Infer the repository layout from the filesystem: read `README.md` and run `ls` on the root directory. If `AGENTS.md` exists (`test -f AGENTS.md && echo EXISTS || echo MISSING`), read it as supplementary context only — it is **not** authoritative and may be out of date.
2. Run `find docs/ -type f -name '*.md' | sort` to enumerate actual doc files. If the output exceeds 120 files, note it to the user but use the full list.
3. Create `docs/README.md` — a navigable index of the project's documentation. Do **not** modify `references/analysis-guide.md` or `references/doc-conventions.md`. The file must contain:
   - **Navigation** section: a bulleted list with a clickable link to every doc file discovered in step 2, grouped by subdirectory (e.g., `docs/public/`, `docs/internal/`), with a one-line description for each file.
   - **Project layout** section: the doc-file tree (without links) derived from the `find` output and filesystem inspection, annotated with short descriptions.
4. After `docs/README.md` is created, continue with the normal workflow for this invocation.

---

## Workflow

1. **Discover** the project's doc structure
2. **Analyze** the staged diff and classify documentation impact
3. **Plan and confirm** (for major changes) or auto-apply (for small updates)
4. **Write** the documentation following existing conventions
5. **Verify** the result

---

## Step 1: Discover Project Structure

Read `docs/README.md` first — it is the primary source of truth for the documentation structure. It lists all doc files with descriptions and the project layout tree. Use it to understand which topics are already documented and what section names to use.

Then run the following commands **in parallel** to get the current filesystem state (to catch any files not yet reflected in `docs/README.md`):

```bash
# All doc files — verify against docs/README.md and catch any new additions
find docs/ -type f -name '*.md' | sort

# All Helm chart values files — primary source of new parameters
find . -path './.git' -prune -o -name 'values.yaml' -print | grep -v '.git'

# Operator API type files — CRD spec changes create new parameters
find . -path './.git' -prune -o -name '*_types.go' -print | grep -v '.git'
```

Then **read the Table of Contents** of `docs/public/installation.md` and `docs/public/architecture.md`. These tell you:

- Which components are already documented (so you know what section names to use when adding parameter rows)
- Which components exist architecturally (so you know where to add new ones)

Do not assume a fixed doc layout. Every project using this skill has a similar _shape_ (public docs, internal docs, installation params, architecture, monitoring, security) but different component names and feature files.

## Step 2: Analyze Changes

**Read `references/analysis-guide.md` now** — it contains the complete classification rules, file-pattern mapping table, and worked examples for this step. Apply those rules throughout Step 2.

First, determine the current branch:

```sh
git rev-parse --abbrev-ref HEAD
```

**If on a non-`main` branch**, gather two scopes of changes and union them:

1. **Branch scope** — all changes introduced by this branch since it diverged from `main`:
   ```sh
   git diff main...HEAD
   ```
2. **Staged scope** — changes staged for the current commit:
   ```sh
   git diff --cached
   ```

Use the union of both scopes for classification. This ensures the skill catches undocumented changes that were made earlier in the branch and not yet documented, not just the current staged diff. Also run `git status --short` to catch new untracked files that may be staged.

**If on `main`**, only analyze the staged scope:

```sh
git diff --cached
git status --short
```

If the diff exceeds ~500 lines, summarize by file group rather than line-by-line — focus on files matching the classification categories in `references/analysis-guide.md`.

Classify each changed file into documentation impact categories using the rules in `references/analysis-guide.md`.

### No Documentation Needed

After classifying all changed files, if none of them fall into a documentation-relevant category, **tell the user explicitly**: "I analyzed the diff — no documentation changes are required." Do not silently skip; the user should know you checked.

### Detecting Refactors

If the changes are purely internal — renaming private functions, restructuring code without changing behavior, updating dependencies without config changes — mention to the user that you detected a refactor and confirm no documentation updates are needed. Don't silently skip; the user should know you checked.

### Change Categories

**Helm chart parameters** — Changes to any `values.yaml` under `*/charts/helm/*/`, Helm templates introducing new parameters, CRD type definitions with new spec fields.

- Action: update parameter tables in `docs/public/installation.md` under the matching component section
- Read `references/doc-conventions.md` for exact table format

**New feature** — A substantial new capability: new controller, new CRD feature field, new service component, new integration.

- Action: create a new feature doc in `docs/public/<feature-name>.md`
- Cross-reference from `installation.md` if it has configurable parameters
- Cross-reference from `architecture.md` if it adds a new component

**Existing feature change** — Modifications to behavior, configuration options, or defaults of an existing feature.

- Action: update the corresponding file in `docs/public/`
- Also update `installation.md` parameter tables if params changed

**Metrics and monitoring** — Changes to Telegraf/Prometheus config, Grafana dashboard JSON/ConfigMaps in `monitoring/`, alert rules.

- Action: update `docs/public/monitoring.md` or `docs/public/alerts.md`

**Architecture** — New components, changed component interactions, new deployment schemes, CRD structure changes.

- Action: update `docs/public/architecture.md`

**Installation / Prerequisites** — New dependencies, changed versions, new permissions, changed install steps.

- Action: update relevant sections in `docs/public/installation.md`

**Troubleshooting / Maintenance** — New failure modes, changed recovery procedures, new maintenance operations.

- Action: update `docs/public/troubleshooting.md` or the relevant scenario doc in `docs/public/scenarios/`

**Security** — New auth mechanisms, TLS changes, new RBAC requirements.

- Action: update `docs/public/security.md` or the relevant file under `docs/public/security/`

**Removed or deprecated parameters** — Parameters removed from `values.yaml`, CRD fields removed or deprecated, features disabled or deleted.

- Action: remove or strike the parameter row from `installation.md`; if a feature doc exists, add a deprecation notice or remove the doc and clean up cross-references
- Do not silently leave stale rows — incorrect documentation is worse than no documentation

**Internal docs** — Changes to CI config, Makefile internals, operator development patterns, or dev workflows.

- Action: update `docs/internal/developing.md` or `docs/internal/operator-guide.md` as appropriate

**New or moved doc files** — A new `.md` file added under `docs/`, an existing doc file renamed or moved, or a doc file deleted.

- Action: update `docs/README.md` — add, rename, or remove the corresponding entry in both the Navigation section and the Project layout tree

### Handling Unknown Parameter Details

When you detect a new Helm parameter but can't determine its Type or Default from the code alone, ask the user for the missing information before adding the parameter row. Don't guess — incorrect parameter documentation is worse than no documentation.

## Step 3: Plan and Apply

Use a **hybrid approach** for confirmation:

- **Auto-apply** (no confirmation needed): adding 1–2 rows to an existing parameter table, fixing cross-references, updating ToC entries, minor wording adjustments to reflect changed defaults.
- **Confirm with the user** before: creating a new file, removing a section or parameter row, rewriting an existing section, making structural changes to existing docs, or adding 3 or more parameter rows at once.

For the confirmation case, present a concise plan:

- Which files will be **created** (with proposed filenames)
- Which files will be **updated** (with a summary of changes)
- Any cross-references to add

Wait for user approval before proceeding with those changes.

## Step 4: Write Documentation

Read `references/doc-conventions.md` before writing — it contains the exact table formats, templates, and style rules.

Key principles:

1. Invoke the `english-us-developer-style` skill before producing any prose.

2. **Match the existing style.** Always read the target file before editing. Preserve heading hierarchy, table column widths, link conventions, and note formatting.

3. **Always update the Table of Contents.** When adding new sections to a file, add corresponding ToC entries at the top of the file — whether or not the file already has a ToC.

4. **Parameter tables**: see `references/doc-conventions.md` for the exact column spec and formatting rules. Do not guess the format from memory.

5. **Feature docs**: use the feature documentation template defined in `references/doc-conventions.md` — do not invent structure from memory, as it is the single source of truth for templates and style.

6. **Use repo-root-relative links** for cross-references: `[Feature Name](/docs/public/feature-name.md)`.

7. **Image references**: `![Alt Text](/docs/public/images/path/to/image.png)`.

## Step 5: Verify

After applying changes:

- Read each modified file to confirm formatting is correct
- Check that parameter table column separators are consistent
- Verify cross-references point to existing files: for each internal link added or updated, confirm the target path exists with `find docs/ -name '<filename>'`
- If new feature files were created, confirm they're referenced from `installation.md` (if they have parameters)
- If any doc files were created, renamed, moved, or deleted, confirm `docs/README.md` reflects the current structure (Navigation links and Project layout tree)
- Run `git diff -- docs/` to show the user what changed

---

## Reference Files

- `docs/README.md` — Navigable index of the project's doc files with descriptions; created during adaptation.
- `references/doc-conventions.md` — Templates, table formats, and style rules. Read this before writing any doc.
- `references/analysis-guide.md` — How to classify changed files and map them to documentation updates. Read this during Step 2.
