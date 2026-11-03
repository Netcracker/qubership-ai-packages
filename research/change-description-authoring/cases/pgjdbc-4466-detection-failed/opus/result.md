## Commands that detect the merge model

Run these in the clone. `upstream` is pgjdbc/pgjdbc, and the pull request does not exist yet, so the target falls back to the default branch of `upstream`.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

The branch below has a single commit, and the description can stand as a commit body. Both work whatever these commands report.

## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit (`feat: Include driver version in default application_name`). The branch then has one commit:

```text
feat: include the driver version in the default ApplicationName

A connection that left ApplicationName unset sent the fixed string
"PostgreSQL JDBC Driver" as application_name. pg_stat_activity showed
which connections came from pgjdbc, but not which driver version each
one used. Users asked to see that version from a view in the database
(#2404).

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver", a space, and the version of the driver jar.

User-visible:
When ApplicationName is unset, application_name is "PostgreSQL JDBC Driver" followed by the driver version, for example "PostgreSQL JDBC Driver 42.7.14"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc connections.
When ApplicationName is unset, any role that can connect to the database sees the driver version of the session in pg_stat_activity.
Not changed:
An explicitly set ApplicationName, such as ApplicationName=billing, is sent as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
This changes a default in 42.7.14. Connections that leave `ApplicationName` unset now send `PostgreSQL JDBC Driver 42.7.14` as `application_name` instead of `PostgreSQL JDBC Driver`. Because of that, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. An application that needs the old value can set `ApplicationName` explicitly, because an explicit value is sent as given.

Before this change, `pg_stat_activity` showed which connections came from pgjdbc but not which driver version each one used. Users who want to know which driver version their applications run asked to see it from a view in the database (#2404).

The default is now `DriverInfo.DRIVER_FULL_NAME`, which is `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`. So for connections that leave `ApplicationName` unset, the driver version is now visible to other database users, and the `ApplicationName` entry in `use.md` says so.

`explicitApplicationNameIsKept` also passes on `master`. It pins the behavior that must not change, which is that `ApplicationName=billing` is sent as `billing`.

The default leaves out the git sha of the build and the JDK version, because that much detail is too much for it. Adding them can be discussed separately.

Fixes #2404
```
