## Detect the merge model

```bash
remote=upstream
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

If `upstream/HEAD` is missing, run `git remote set-head upstream --auto`. If the count reports no commits, run `git fetch upstream` first. Until the count shows one model, the text below uses the default for an unknown model: every surviving commit is a full commit message.

## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) folds into commit 1. It corrects that commit's `CHANGELOG.md` and `use.md` lines, so it must not land as a commit of its own. Commit 2 stays separate because it adds tests.

Commit 1, with commit 3 folded in:

```text
feat: include driver version in default application_name

Before this change, connections that leave ApplicationName unset send
"PostgreSQL JDBC Driver". That does not say which driver version the
connection uses, so pg_stat_activity cannot show it. Issue #2404 asks
for the version to be visible from a PostgreSQL view.

The default is now DriverInfo.DRIVER_FULL_NAME: the driver name, a
space, and the driver version.

User-visible:
Breaking: a query that matches application_name = 'PostgreSQL JDBC Driver'
finds no connection that leaves ApplicationName unset. Set
ApplicationName explicitly to keep the old value, or update the query.
When ApplicationName is not set, the connection sends "PostgreSQL JDBC
Driver X.Y.Z", for example "PostgreSQL JDBC Driver 42.7.14".
Any role that can connect to the database can read application_name of
every session in pg_stat_activity, so other database users see the
driver version too.

Not changed:
An explicitly set ApplicationName is sent unchanged.

Fixes #2404
```

The final lines of commit 1's diff, with commit 3 folded in:

- `CHANGELOG.md`, first entry under `### Changed`:

  ```text
  * **Breaking:** The default `ApplicationName` now includes the driver version, for example `PostgreSQL JDBC Driver 42.7.14` rather than `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections that leave `ApplicationName` unset; set `ApplicationName` explicitly to keep the old value, or update the query. An explicitly set `ApplicationName` is unaffected. [Issue #2404] [PR #4466]
  ```

- `docs/content/documentation/use.md`, the paragraph after the existing sentence "The default value is `PostgreSQL JDBC Driver` suffixed with the version of this driver." ends with this added sentence:

  ```text
  Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so other database users see the driver version too.
  ```

Commit 2:

```text
test: cover the default and explicit application_name

The default application_name now carries the driver version, and an
explicit ApplicationName must still reach the server unchanged. Both
are checked by reading current_setting('application_name') back from a
running server in ApplicationNameTest.

Refs #2404
```

## 2. Pull request title

```text
feat: include driver version in default application_name
```

## 3. Pull request description

```markdown
### Breaking changes

A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections that leave `ApplicationName` unset, because those connections now send the driver version after the name. Set `ApplicationName` explicitly to keep the old value, or update the query. `gradle.properties` on `master` says `42.7.14`, the next release. That is not a major release, so this change ships in it if merged.

### Why

Connections that leave `ApplicationName` unset send only `PostgreSQL JDBC Driver`, so `pg_stat_activity` does not show which driver version a connection uses. Issue #2404 asks for that version to be visible from a PostgreSQL view.

### What

The default reuses `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and the driver version. The version comes from the driver jar.

### User-visible changes

* When `ApplicationName` is not set, the connection sends `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.14`.
* Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so other database users see the driver version too. `use.md` says so.
* Not changed: an explicitly set `ApplicationName` is sent unchanged.

### How to verify

* `explicitApplicationNameIsKept` passes without this change. It pins the value that must not move.
* Both tests in `ApplicationNameTest` need a running PostgreSQL server.

### Scope

The build's git SHA and the JDK version are left out. Both were considered and judged too much for this change. They can be discussed separately.

<details>
<summary>Checklist</summary>

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [ ] Does this break existing behaviour? If so please explain.
* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
* [ ] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

</details>
```
