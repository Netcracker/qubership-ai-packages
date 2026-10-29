## Detect the merge model

Run these in your clone, in one shell session. `upstream` is the repository the pull request targets, so it is the remote they read. Until the pull request is open, the second line falls back to `upstream`'s default branch. If `upstream/HEAD` is missing, run `git remote set-head upstream --auto` first.

```bash
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

Reading the first output line:

- `merge` above zero: merge commits are allowed.
- `squash` only: squash merge.
- `plain` only: rebase and merge, or direct pushes.
- `squash` and `plain` both: ambiguous. Both methods may be allowed.

The plan below holds under every model in that table.

## 1. Commits

Keep one commit. Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1.

- Commit 3 corrects commit 1's changelog and `use.md` lines. Under rebase and merge it would land as its own commit with a non-descriptive subject.
- Commit 2 holds only tests of commit 1. A test-only commit has no permanent message of its own, and a body for it would be verification, which stays out of `git log`.

```text
feat: include driver version in default ApplicationName

Connections that leave ApplicationName unset all report "PostgreSQL
JDBC Driver", so pg_stat_activity cannot show which driver version
each one runs. Issue #2404 asks for that version to be visible from a
view in PostgreSQL.

The default is now DriverInfo.DRIVER_FULL_NAME: the driver name, a
space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports "PostgreSQL JDBC Driver X.Y.Z", where X.Y.Z is the driver version, for example "PostgreSQL JDBC Driver 42.7.14". Releases before 42.7.14 report "PostgreSQL JDBC Driver", so a filter on that value stops matching connections from 42.7.14 on. Set ApplicationName to "PostgreSQL JDBC Driver" to keep the old value.
Not changed:
A connection that sets ApplicationName reports that value unchanged.

Fixes #2404
```

## 2. Pull request title

```text
feat: include driver version in default ApplicationName
```

## 3. Pull request description

```markdown
### Breaking changes

Code that filters `pg_stat_activity` on the old default breaks: `application_name = 'PostgreSQL JDBC Driver'` no longer matches connections that leave `ApplicationName` unset.

A connection that leaves `ApplicationName` unset reports `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.14`, where X.Y.Z is the driver version. Releases before 42.7.14 report `PostgreSQL JDBC Driver`. To keep the old value, set `ApplicationName` to `PostgreSQL JDBC Driver` explicitly.

### Why

Users want to see which driver version their applications run, as seen in `pg_stat_activity`. Issue #2404 asks for the same thing: the driver version visible from a view in PostgreSQL. Every connection that leaves `ApplicationName` unset shows the same name, so the view cannot tell versions apart.

### What

The default `ApplicationName` is `DriverInfo.DRIVER_FULL_NAME`: the driver name, a space, and the version of the driver jar.

### User-visible changes

Not changed: an explicitly set `ApplicationName` is sent unchanged.

### Verification

`ApplicationNameTest.explicitApplicationNameIsKept` passes without this change: it pins the explicit value, which the change must not move. Both tests in `ApplicationNameTest` need a running PostgreSQL server.

### Scope

Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`. With this default, those roles see the driver version of every connection that leaves `ApplicationName` unset. The decision for the maintainers is whether other database roles should see that version, or the default should stay as it was.

The git SHA of the build and the JDK version are left out as too much for a default. They can be discussed separately.

Fixes #2404.
```
