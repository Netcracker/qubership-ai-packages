## Merge model detection

Run these in your clone, after you've opened the pull request or before it exists. The contributor runs them; they have not been run yet.

```bash
remote=upstream
git fetch "$remote"
# If upstream/HEAD is missing: git remote set-head "$remote" --auto
target=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null) && target=$remote/$target || target=$(git rev-parse --abbrev-ref "$remote/HEAD")
git log -n 40 --first-parent --format='%P%x09%s' "$target" -- | awk -F'\t' '$1 ~ / / {m++; next} $2 ~ / \(#[0-9]+\)$/ {s++; next} {p++} END {if (NR == 0) {print "no commits read: the target branch is not on the remote"; exit 1} printf "merge %d squash %d plain %d\n", m, s, p}'
git log -n 10 --first-parent --format='%h %P%n%b%n' "$target" --
```

Read the counts this way: `merge` present means merge commits are enabled. `squash` only means squash. `plain` only means rebase or direct pushes. `squash` with `plain` means both are in use. The text below holds under each of these models.

## 1. Commits

Commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) are folded into commit 1, which leaves one commit. Commit 2 has no body and a subject that cannot stand alone, and its tests belong to this change. Commit 3 is a review fix to lines that commit 1 adds.

```text
feat: add driver version to default ApplicationName

Every connection that leaves ApplicationName unset reports the same
"PostgreSQL JDBC Driver", so a database administrator reading
pg_stat_activity cannot tell which driver version a connection uses.
Users want to know which driver version their applications use, and
issue #2404 asks for this.

The default is now DriverInfo.DRIVER_FULL_NAME: the driver name, a space,
and the version of the driver jar. Reusing that constant keeps the
version in step with the jar.

User-visible:
With ApplicationName unset, the driver sends "PostgreSQL JDBC Driver 42.7.14" instead of "PostgreSQL JDBC Driver". Code that matches the old value exactly stops finding those connections; match the prefix, or set ApplicationName explicitly to keep the old value.
Any role that can connect to the database can read application_name for every session in pg_stat_activity, so other database users see the driver version too.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

`feat: add driver version to default ApplicationName`

## 3. Pull request description

```markdown
### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

#### Breaking changes

This breaks existing behavior for connections that leave `ApplicationName` unset. Code that compares `application_name` with the exact string `PostgreSQL JDBC Driver` stops matching them. `gradle.properties` sets 42.7.14 on `master`, and the latest release is REL42.7.13, so the break reaches the next release if this merges.

* With `ApplicationName` unset, the driver sends `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`. Match the prefix `PostgreSQL JDBC Driver`, or set `ApplicationName` explicitly to keep the old value.

#### Why

Every connection that leaves `ApplicationName` unset reports the same `PostgreSQL JDBC Driver`, so a database administrator reading `pg_stat_activity` cannot tell which driver version a connection uses. The change came out of conversations with users who want that answer. Issue #2404 asks to see the JDBC driver version from a view in PostgreSQL, and this change does that for `pg_stat_activity`. Fixes #2404.

#### What

The default is now `DriverInfo.DRIVER_FULL_NAME`: the driver name, a space, and the version of the driver jar. Reusing that constant keeps the version in step with the jar.

#### User-visible changes

* Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`, so other database users see the driver version too.

Not changed:

* An explicitly set `ApplicationName` is sent as given.

#### Verification

`ApplicationNameTest` has two new tests, and both need a running server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`. It expects `PostgreSQL JDBC Driver` followed by `DriverInfo.DRIVER_VERSION`. `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and passes on `master` too, so it guards the explicit path, which this change leaves alone.

#### Scope

This change leaves out the git SHA of the build and the JDK version. Both were considered and left out as too much for the default. They can be discussed separately.

For a maintainer to decide: should a default that changes for connections that leave `ApplicationName` unset ship in 42.7.14? The code shows the break above. It does not show whether the break is wanted.

* [ ] Does this break existing behaviour? If so please explain.
* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
* [ ] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
