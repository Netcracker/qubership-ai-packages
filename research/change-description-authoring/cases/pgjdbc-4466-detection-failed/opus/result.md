## Merge model detection

Run these in your clone. Set `remote=upstream`, because `origin` is your fork. If no pull request exists for the branch, the second line falls back to `upstream/HEAD`.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

Nobody has run these yet, so the text below follows the default for an unknown merge model. Every commit is written to stand alone and carries the issue number. The description is written so it can also serve as a commit body.

## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. Commit 3 corrects the `CHANGELOG.md` and `use.md` lines that commit 1 adds. Commit 2 holds the tests for commit 1's behavior. One commit remains:

```text
feat: append the driver version to the default ApplicationName

Previously, a connection that left ApplicationName unset reported
application_name as "PostgreSQL JDBC Driver" whatever the driver
version. A database administrator looking at pg_stat_activity could not
tell which driver version each application used, which issue #2404
asks for.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver", a space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver" followed by a space and the driver version, for example "PostgreSQL JDBC Driver 42.7.14".
A query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds connections that leave ApplicationName unset.
Any role that can connect to the database reads the driver version of such connections in pg_stat_activity.
Not changed:
A connection that sets ApplicationName reports that value.

Fixes #2404
```

## 2. Title

```text
feat: append the driver version to the default ApplicationName
```

## 3. Description

```markdown
This changes a default in 42.7.14, which is not a major release. Monitoring that matches the old default `application_name` stops finding pgjdbc connections after the upgrade:

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds connections that leave `ApplicationName` unset, which it found with 42.7.13. Match `application_name LIKE 'PostgreSQL JDBC Driver %'` instead, or set `ApplicationName=PostgreSQL JDBC Driver` on the connection to keep the old value.

Other user-visible changes:

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`.
- Any role that can connect to the database reads the driver version of such connections in `pg_stat_activity`. The `ApplicationName` entry in `docs/content/documentation/use.md` now says so.
- Not changed: a connection that sets `ApplicationName` reports that value.

Users want to know which driver version their applications use, and `pg_stat_activity` showed `PostgreSQL JDBC Driver` for every version. The default `ApplicationName` now carries the version of the driver jar, so the view shows it directly, as #2404 asks.

The build's git SHA and the JDK version were left out of the default as too much. Adding either one can be discussed separately.

The new `ApplicationNameTest` needs a running server. It reads `current_setting('application_name')` back for a connection with `ApplicationName` unset and for one with it set. The test for the unset case fails on `master`.

Fixes #2404
```
