## 1. Commits at merge

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. This leaves one commit on the branch. The repository squash-merges with GitHub's default message, so a single-commit pull request lands with that commit's subject and body, with ` (#4466)` appended to the subject.

The one remaining commit:

```text
feat: include the driver version in the default ApplicationName

The default application_name was "PostgreSQL JDBC Driver" for every
driver release. pg_stat_activity therefore showed that a connection came
from pgjdbc, but not which driver version it used. Issue #2404 asks to
read the driver version a client uses from a PostgreSQL view, and users
who track which driver version their applications run have asked for the
same.

A connection that leaves ApplicationName unset now sends
DriverInfo.DRIVER_FULL_NAME: the old name, a space, and the version of
the driver jar. The git sha of the build and the JDK version were left
out as more than this change needs; they can be discussed separately.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver 42.7.14" (the driver version) instead of "PostgreSQL JDBC Driver", so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database sees the driver version in pg_stat_activity.application_name for these sessions.
Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
### Breaking changes

This changes a default, so code that matches the old default `application_name` stops finding pgjdbc connections.

* In 42.7.13 and earlier, a connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver`. With this change it reports `PostgreSQL JDBC Driver 42.7.14` (the driver version), so a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. To keep finding them, match the prefix (`application_name LIKE 'PostgreSQL JDBC Driver%'`), or set `ApplicationName` explicitly.

### Why

Issue #2404 asks to read the version of the JDBC driver a client uses directly from a PostgreSQL view. Users who want to know which driver version their applications run, as seen in `pg_stat_activity`, have asked for the same. Before this change, every driver release sent the same `PostgreSQL JDBC Driver`, so the view could not tell versions apart.

### What

A connection that leaves `ApplicationName` unset now sends `DriverInfo.DRIVER_FULL_NAME`: the old name, a space, and the version of the driver jar. The default is still a fixed prefix, so a prefix match finds connections from every version.

### User-visible changes

* Any role that can connect to the database sees the driver version in `pg_stat_activity.application_name` for these sessions. The `ApplicationName` entry in `use.md` says so.
* Not changed: an explicitly set `ApplicationName` is sent as given.

### Verification

`ApplicationNameTest` is new, and both of its tests need a running server. `defaultApplicationNameCarriesTheDriverVersion` reads the default back from `current_setting('application_name')`, and it fails on `master`. `explicitApplicationNameIsKept` passes on `master` and on this branch, and it guards the explicit-value case.

### Scope

Fixes #2404. The git sha of the build and the JDK version are left out of the default. They can be discussed separately.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See "Breaking changes" above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
