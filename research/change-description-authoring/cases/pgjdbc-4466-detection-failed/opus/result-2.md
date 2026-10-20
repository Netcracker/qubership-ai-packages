## Commands to detect the merge model

Run these in your clone. The pull request targets pgjdbc/pgjdbc, so `remote` is `upstream`. The pull request isn't open yet, so `gh pr view` fails and the second line falls back to `upstream/HEAD`.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

What follows is written for the case where the merge model is unknown. It holds whatever the commands show. A one-commit branch lands the same message under rebase, under merge commits, and under every default squash. The description can also stand as the commit body if the squash setting is "title and description".

## 1. Commits

- Fold commit 2, `add tests`, into commit 1, because the tests belong with the change they check.
- Fold commit 3, `Apply suggestion from @vlsi`, into commit 1, because it corrects that commit's `CHANGELOG.md` line and `use.md` entry.
- The commit that remains keeps commit 1's author.

The one remaining commit:

```text
feat: add the driver version to the default ApplicationName

When a connection leaves ApplicationName unset, the driver sends
"PostgreSQL JDBC Driver" as application_name. pg_stat_activity then
shows which sessions come from pgjdbc, but not which driver version
each one uses. Users who need to know which driver version their
applications run cannot read it from the server, which #2404 asks for.

The default is now "PostgreSQL JDBC Driver" followed by a space and the
version of the driver jar.

User-visible:
When ApplicationName is not set, application_name is "PostgreSQL JDBC Driver 42.7.14" rather than "PostgreSQL JDBC Driver", so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc connections; match the prefix, or set ApplicationName explicitly.
Any role that can connect to the database reads from pg_stat_activity the driver version of every session that leaves ApplicationName unset.
Not changed:
An explicitly set ApplicationName is sent as given, without the version.

Fixes #2404
```

## 2. Pull request title

```text
feat: add the driver version to the default ApplicationName
```

## 3. Pull request description

Post the template's checklist as a separate comment, because a squash may copy this description into `git log`.

```markdown
The default `ApplicationName` changes in 42.7.14, which breaks queries that match the old default:

- When `ApplicationName` is not set, `application_name` is `PostgreSQL JDBC Driver 42.7.14` rather than `PostgreSQL JDBC Driver`, the value through 42.7.13. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections after the upgrade. Match the prefix instead, or set `ApplicationName` explicitly.

When a connection leaves `ApplicationName` unset, the driver sends `PostgreSQL JDBC Driver`. `pg_stat_activity` then shows which sessions come from pgjdbc, but not which driver version each one uses. Users who need to know which driver version their applications run asked in #2404 to read it from a server view.

The default is now `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. The git sha of the build and the JDK version are left out of the default as too much, and adding them can be discussed separately.

Other user-visible changes:

- Any role that can connect to the database reads from `pg_stat_activity` the driver version of every session that leaves `ApplicationName` unset.
- Not changed: an explicitly set `ApplicationName` is sent as given, without the version.

The new `ApplicationNameTest` needs a running server. Its default-name test fails on `master`, and its explicit-name test passes there too, which shows the explicit case is unchanged.

Fixes #2404
```
