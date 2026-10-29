## Detect the merge model

Run these in your clone. They read the target repository's settings and its history on `upstream/master`.

```bash
git fetch upstream

# Merge methods the target repository allows. Missing or null values mean the API did not return them for your token.
gh api repos/pgjdbc/pgjdbc --jq '{squash: .allow_squash_merge, merge_commit: .allow_merge_commit, rebase: .allow_rebase_merge}'

# Subjects of the last 200 commits on the default branch.
git log --format=%s -n 200 upstream/master | grep -c '^Merge pull request'
git log --format=%s -n 200 upstream/master | grep -c ' (#[0-9]*)$'
git log --first-parent --format='%h %s' -n 20 upstream/master
```

Read the output this way. `Merge pull request` subjects and an allowed merge commit mean a merge-commit model. Subjects that end in `(#NNNN)` and only squash allowed mean a squash model. Neither, with only rebase allowed, means a rebase model. The commit plan below is one commit, which is correct under all three.

## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) is folded into commit 1. Commit 2 (`add tests`) is also folded into commit 1, since its tests belong to the same change. One commit remains:

```text
feat: include the driver version in the default ApplicationName

When ApplicationName is not set, the driver now sends the driver name
followed by the version as the application_name startup parameter, for
example "PostgreSQL JDBC Driver 42.7.14". It previously sent
"PostgreSQL JDBC Driver". Users want to see which driver version their
applications use in pg_stat_activity. Refs #2404.

An explicitly set ApplicationName is sent unchanged.

This is a behavior change. A query that matches the old default exactly,
such as application_name = 'PostgreSQL JDBC Driver', stops finding
pgjdbc connections that use the default. Any role that can connect to
the database can read application_name of every session in
pg_stat_activity, so the version is visible to other database users too.

The new ApplicationNameTest needs a running server.
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
The default `ApplicationName` now includes the driver version. A connection that leaves `ApplicationName` unset sends `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`, so `pg_stat_activity` shows which driver version each connection uses. Closes #2404.

### Why

Users want to know which driver version their applications use, as seen in `pg_stat_activity`. Issue #2404 asks to see the driver version from a view in PostgreSQL.

I considered adding the git SHA of the build and the JDK version as well. I left them out as too much. They can be discussed separately.

### Behavior change

- Connections that leave `ApplicationName` unset send a different value. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade.
- Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`. The default therefore shows the driver version to other database users too. `use.md` says so.
- Connections that set `ApplicationName` are unaffected.

### Changes

- `PGProperty.APPLICATION_NAME` defaults to `DriverInfo.DRIVER_FULL_NAME` instead of `DriverInfo.DRIVER_NAME`. `DRIVER_FULL_NAME` is `DRIVER_NAME + " " + DRIVER_VERSION`.
- `docs/content/documentation/use.md` describes the new default and who can read it.
- `CHANGELOG.md` has an entry under Changed for the new default and the exact-match change.

### Tests

`ApplicationNameTest` has two tests. They need a running server.

- `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` passes on `master` too, because it sets its own value.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes, see Behavior change above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
