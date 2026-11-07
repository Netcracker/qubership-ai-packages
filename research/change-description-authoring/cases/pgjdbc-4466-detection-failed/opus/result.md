## Detecting the merge model

Run these in your clone. `upstream` is pgjdbc/pgjdbc, the repository the pull request will merge into. The pull request is not open yet, so the second line falls back to `upstream`'s default branch.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

The text below fits any merge model, because it is written for the case where the model is not yet known.

- If the count shows only `squash` and the bodies hold no description, the description stays on GitHub. You can then put the template checklist back under the breaking-changes block.
- If the commit bodies in the history use Markdown, the commit's two lead-ins can take asterisks.

## 1. Commits

Commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) are folded into commit 1. One commit remains:

```text
feat: add the driver version to the default ApplicationName

A connection that left ApplicationName unset sent "PostgreSQL JDBC
Driver" as application_name, whatever the driver version. Users who
want to know which driver version their applications run could not
read it from PostgreSQL, for example in pg_stat_activity, as issue
#2404 asks.

User-visible changes.
A connection that leaves ApplicationName unset sends "PostgreSQL JDBC Driver" followed by a space and the version of the driver jar as application_name, for example "PostgreSQL JDBC Driver 42.7.14"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds such connections, and setting ApplicationName explicitly keeps a fixed value.
Any role that can connect to the database reads the driver version of such connections in pg_stat_activity, which shows application_name for every session.

Not changed.
An explicitly set ApplicationName, such as ApplicationName=billing, is sent as given.

Fixes #2404
```

## 2. Title

```text
feat: add the driver version to the default ApplicationName shown in pg_stat_activity
```

## 3. Description

```markdown
**Breaking changes.**
A connection that leaves `ApplicationName` unset now sends `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar as `application_name`, for example `PostgreSQL JDBC Driver 42.7.14`, instead of `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. To keep a fixed value, set `ApplicationName` explicitly.

Users want to know which driver version their applications run, and to read it from PostgreSQL, for example in `pg_stat_activity` (#2404). Until now the default `application_name` was the same string for every driver version, so the view could not show it.

**User-visible changes.**
Any role that can connect to the database reads the driver version of such connections in `pg_stat_activity`, which shows `application_name` for every session.

**Not changed.**
An explicitly set `ApplicationName`, such as `ApplicationName=billing`, is sent as given.

Both tests in `ApplicationNameTest` need a running server; `explicitApplicationNameIsKept` passes on `master` too, because it checks behavior that must not change.

**Scope.** The default leaves out the git sha of the build and the JDK version; adding either can be discussed separately.

Fixes #2404
```
