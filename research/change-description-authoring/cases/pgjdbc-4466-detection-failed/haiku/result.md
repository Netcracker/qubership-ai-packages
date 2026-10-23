Run these in your clone before you open the pull request. Nobody has run them yet, so the merge model stays unknown until they do.

```bash
# Only if upstream/HEAD is missing:
# git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

## 1. Commits

Commits 2 and 3 fold into commit 1, so the branch lands as one commit.

- Commit 3 (`Apply suggestion from @vlsi`) makes the review's changes to `CHANGELOG.md` and `use.md`. It corrects commit 1, so it folds into it.
- Commit 2 (`add tests`) has no body and fails the subject test. Its tests check the change in commit 1, so they land with it.

One commit with a full message works under every merge model shown above, so the plan does not depend on what the detection commands print.

```text
feat: include driver version in default ApplicationName

Connections that leave ApplicationName unset all send the same name,
PostgreSQL JDBC Driver, whatever driver version they run. The driver
version therefore cannot be read from pg_stat_activity. Issue #2404
asks to see it from a view in PostgreSQL.

This changes a default, not a defect. The default is now the driver's
full name: PostgreSQL JDBC Driver, a space, and the driver version
(DriverInfo.DRIVER_FULL_NAME), for example PostgreSQL JDBC Driver X.Y.Z.

User-visible:
A connection that leaves ApplicationName unset reports PostgreSQL JDBC Driver X.Y.Z in pg_stat_activity.application_name, where it reported PostgreSQL JDBC Driver. A query that matches application_name = 'PostgreSQL JDBC Driver' stops finding those connections; match application_name LIKE 'PostgreSQL JDBC Driver%', or set ApplicationName=PostgreSQL JDBC Driver to keep the old value.
Any role that can connect to the database can read application_name of every session in pg_stat_activity, so the driver version is visible to other database users.

Not changed:
An explicitly set ApplicationName is sent as given.

Closes #2404
```

## 2. Pull request title

```text
feat: include driver version in default ApplicationName
```

## 3. Pull request description

```markdown
Code that matches the default `ApplicationName` string stops matching. A connection that leaves `ApplicationName` unset now reports `PostgreSQL JDBC Driver` followed by the driver version, so a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. The change would ship in 42.7.14, the next release from `master`.

### Breaking changes

- A connection that leaves `ApplicationName` unset reports `PostgreSQL JDBC Driver X.Y.Z` where it reported `PostgreSQL JDBC Driver`. Match `application_name LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Changes to Existing Features:

**Why.** Connections that leave `ApplicationName` unset all send `PostgreSQL JDBC Driver`, whatever driver version they run, so the driver version cannot be read from `pg_stat_activity`. Issue #2404 asks to see it from a view in PostgreSQL.

**What.** The default name is `PostgreSQL JDBC Driver` followed by a space and the driver version. An explicitly set `ApplicationName` is sent unchanged.

**User-visible changes.** Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the driver version is visible to other database users.

**Verification.** Both tests are new and need a running PostgreSQL server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the default is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` passes on `master` too, so it pins the explicit value that this change does not alter.

**Scope.** This change adds only the driver version to the name. Adding the build's git SHA or the JDK version is left out; it can be discussed separately.

Closes #2404
```
