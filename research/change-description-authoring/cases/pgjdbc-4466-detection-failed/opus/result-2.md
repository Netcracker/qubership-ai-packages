## Detecting the merge model

Run these in your clone. `upstream` is pgjdbc/pgjdbc, and `origin` is your fork. The pull request isn't open yet, so `gh pr view` fails and the target falls back to `upstream/HEAD`, which is `master`.

```bash
git fetch upstream
git remote set-head upstream --auto
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

The text below works whatever these report. There is one commit with a full message, and the description can also serve as a commit body.

## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. Commit 3 only reworks the `CHANGELOG.md` and `use.md` lines that commit 1 adds. Commit 2 tests commit 1's change and has nothing to say on its own. This leaves one commit:

```text
feat: include the driver version in the default application_name

Users who want to know which driver version their applications use
look for it in pg_stat_activity. A connection that leaves
ApplicationName unset reports the fixed string "PostgreSQL JDBC Driver"
there, and that string is the same for every driver release.

User-visible changes.
A connection that leaves ApplicationName unset reports application_name as `PostgreSQL JDBC Driver` followed by a space and the driver version, such as `PostgreSQL JDBC Driver 42.7.14`, instead of `PostgreSQL JDBC Driver`. A query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections; match the prefix, or set ApplicationName explicitly.
Any role that can connect to the database reads the application_name of every session in pg_stat_activity, so the default shows the driver version to other database users.

Not changed.
An explicitly set ApplicationName is sent unchanged.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default application_name
```

## 3. Pull request description

The description may become a commit body, so it drops the template's headings. Post the template's checklist as the first comment instead.

```markdown
**Breaking changes.**
A connection that leaves `ApplicationName` unset now reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, such as `PostgreSQL JDBC Driver 42.7.14`. With 42.7.13 it reports `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. To keep finding them, match the prefix (`application_name LIKE 'PostgreSQL JDBC Driver%'`) or set `ApplicationName` explicitly.

Users want to know which driver version their applications use, and they look for it in `pg_stat_activity`. Issue #2404 asks for this. Until now the default `application_name` was the same string for every pgjdbc release.

**User-visible changes.**
Any role that can connect to the database reads the `application_name` of every session in `pg_stat_activity`, so the default shows the driver version to other database users.

**Not changed.**
An explicitly set `ApplicationName` is sent unchanged. `explicitApplicationNameIsKept` guards this and passes on `master` too.

**Scope.**
This change leaves out adding the build's git sha or the JDK version to the default. That can be discussed separately.

Fixes #2404
```
