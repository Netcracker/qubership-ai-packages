## Detect the merge model

Run these in your clone. `upstream` is pgjdbc/pgjdbc. No pull request is open yet, so `gh pr view` fails and the target falls back to `upstream/HEAD`.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

The commit and description below hold whatever the result is. The commit stands on its own, and the description can also serve as the commit body.

## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. The branch then merges as one commit:

```text
feat: add the driver version to the default application_name

When ApplicationName was not set, the driver sent "PostgreSQL JDBC
Driver" as application_name. pg_stat_activity showed that a session
came from pgjdbc, but not which driver version it used. Users want to
know which driver version each of their applications runs, and #2404
asks to see it directly from a view in PostgreSQL.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME:
"PostgreSQL JDBC Driver", a space, and the version of the driver jar.
The git hash of the build and the JDK version are left out of the
default.

User-visible:
- A connection that leaves ApplicationName unset reports
  application_name "PostgreSQL JDBC Driver 42.7.14" with driver 42.7.14,
  where 42.7.13 reported "PostgreSQL JDBC Driver". A query that matches
  application_name = 'PostgreSQL JDBC Driver' no longer finds those
  connections.
- Any role that can connect to the database sees the driver version of
  those sessions in pg_stat_activity.
Not changed:
- A connection that sets ApplicationName, for example to billing,
  reports that value as before.

Fixes #2404
```

## 2. Title

```text
feat: add the driver version to the default application_name
```

## 3. Description

```markdown
A connection that leaves `ApplicationName` unset now reports `application_name` as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Version 42.7.13 and earlier report `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. Match `application_name LIKE 'PostgreSQL JDBC Driver %'` instead, or set `ApplicationName` explicitly.

Users want to know which driver version each of their applications uses, and #2404 asks to see it directly from a view in PostgreSQL. Before this change, `pg_stat_activity` showed that a session came from pgjdbc, but not which version it used.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, a space, and the version of the driver jar. The git hash of the build and the JDK version are left out of the default; adding them can be discussed separately.

User-visible:
- Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so it now sees the driver version of connections that leave `ApplicationName` unset.

Not changed:
- A connection that sets `ApplicationName`, for example to `billing`, reports that value as before.

`explicitApplicationNameIsKept` passes without this change as well, because it checks that an explicitly set value stays the same.

Fixes #2404
```
