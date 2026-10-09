---
name: doc-updater
description: Update a repository's documentation to match the code changes on the current branch and in the staging area. Classify each change, map it to the page that documents it, and edit that page in the format the page already uses. Use only when the user asks to update or sync the documentation, says the docs are out of date, or invokes doc-updater by name. Do not run it automatically before a commit.
---

# Documentation updater

Bring a repository's documentation in line with the code changes on the current branch. Find the documentation the
repository already has, map each change to the page that documents it, and edit that page in its own format.

No documentation path is fixed in this skill. Every page you read or edit comes from the documentation map you build
in step 1, so the skill works the same in a repository with `docs/public/installation.md`, one with
`docs/installation.md`, and one with only a root `README.md`.

Write all prose with the repository's English style skill (`english-us-developer-style` or
`english-uk-developer-style`). If neither is installed, tell the user and recommend installing one.

## Step 1. Build the documentation map

The map assigns each documentation role to the page, section, or directory that plays it in this repository:

| Role | What it holds |
| --- | --- |
| `index` | The page that lists every documentation page |
| `parameters` | The reference table of Helm values or other configuration parameters |
| `installation` | Prerequisites, install, upgrade, and rollback procedures |
| `architecture` | Components, how they interact, deployment schemes |
| `features` | One page per feature, usually a directory |
| `monitoring` | Metrics and dashboards |
| `alerts` | Alert rules |
| `troubleshooting` | Failure modes and recovery procedures |
| `security` | TLS, authentication, authorization, RBAC |
| `developer` | Build, CI, and development workflow for contributors |
| `images` | Screenshots and diagrams |

A role can map to a section of a page (parameters often live in the installation page), to several pages, or to
nothing. Build the map from the repository every time; do not carry one over from another repository.

1. List the documentation and the sources that most often need it:

   ```bash
   # Every tracked or new Markdown page, outside vendored and generated trees
   { git ls-files '*.md'; git ls-files --others --exclude-standard '*.md'; } \
     | grep -vE '(^|/)(node_modules|vendor|apm_modules|\.github|\.claude|\.cursor|\.codex|\.agents)/' | sort -u

   # Helm values files and operator API types, the usual source of new parameters
   git ls-files '*values.yaml' '*_types.go'
   ```

1. If an `index` page exists (a `README.md` in the documentation root that links the other pages, or a site config
   such as `mkdocs.yml`), read it first.
1. For each candidate page, read its headings (`grep -n '^#' <page>`) and assign it to every role it plays. Decide
   by content, not by file name alone: a `README.md` with a parameters table plays `parameters`.
1. Show the map to the user in the plan (step 4), with the roles that map to nothing.

When a change needs a role that maps to nothing, do not invent a path. Propose a page next to the existing
documentation, named in the style the repository already uses, and treat it as a new file that needs confirmation in
step 4. In a repository with no documentation directory, propose the section of the root `README.md` that fits, or a
new page beside it.

## Step 2. Gather the changes

Find the default branch, then collect the changes this branch introduces plus the changes staged for the next commit:

```bash
base=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
git rev-parse --abbrev-ref HEAD
```

If `base` is empty because `origin/HEAD` is not set, use `main` or `master` when exactly one of `origin/main` and
`origin/master` exists (`git rev-parse --verify --quiet origin/<name>`). Otherwise ask the user for the base branch.

- On a branch other than the base, take the union of both scopes:

  ```bash
  git diff "$base"...HEAD
  git diff --cached
  git status --short
  ```

- On the base branch, take only the staged scope and `git status --short`.

`git status --short` lists untracked files, which neither diff shows. Read the new files it lists that match the
categories in the analysis guide. If the combined diff exceeds about 500 lines, summarize it by file group and read in
full only the files that match a category.

## Step 3. Classify the changes

Read `references/analysis-guide.md` now and apply it to every changed file. It maps each kind of change to a
documentation role, and step 1 maps each role to a page.

Tell the user what you found even when the result is empty:

- No change matches a category: say "I analyzed the diff; no documentation changes are required."
- The changes are an internal refactor (renamed private code, restructured code with the same behavior, dependency
  bumps without configuration changes): say that you found a refactor and that it needs no documentation.

When a new parameter's type or default cannot be read from the code, ask the user before you add its row. A wrong
parameter row is worse than a missing one.

## Step 4. Plan and confirm

Apply small edits without asking:

- adding one or two rows to an existing parameter table;
- fixing a cross-reference or a table-of-contents entry;
- rewording a sentence to reflect a changed default.

Show a plan and wait for approval before you:

- create a page or a directory;
- remove a section or a parameter row;
- rewrite an existing section, or change a page's structure;
- add three or more parameter rows at once.

The plan lists the documentation map, the pages to create (with the proposed paths), the pages to update (with a
one-line summary each), and the cross-references to add.

## Step 5. Write

Read `references/doc-conventions.md` before you write. It holds the default formats for parameter rows, feature pages,
and the other page types, and the rule that the target page's own format wins over those defaults.

- Read the whole target page before you edit it, and keep its heading levels, heading case, table columns, link style,
  and note style.
- When you add a section to a page that has a table of contents, add the matching entry.
- When you create, rename, move, or delete a page, update the `index` page if the repository has one.

## Step 6. Verify

- Read each edited page again and check that tables still have the same number of columns in every row.
- For every link you added or changed, check that the target file exists, resolving the path the way the page's link
  style does (relative to the page, or to the repository root).
- Check that a new feature page is linked from the `parameters` page when it has parameters, and from the `index`
  page when one exists.
- Show the user the result with `git diff` limited to the pages you edited.
