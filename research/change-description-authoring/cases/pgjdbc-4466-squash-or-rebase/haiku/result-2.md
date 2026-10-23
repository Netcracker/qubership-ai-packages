## 1. Commits

Commits 2 and 3 fold into commit 1, which leaves one commit. Commit 3 corrects the changelog and `use.md` lines that commit 1 added, and commit 2 tests the behavior that commit 1 adds. Neither has a full commit message of its own, so under a rebase neither would stand alone.

```text
feat: add driver version to default ApplicationName

Connections that leave ApplicationName unset send "PostgreSQL JDBC
Driver" as application_name at startup, so every such connection looks
the same in pg_stat_activity and an operator cannot tell which driver
version an application uses. Issue #2404 asks for the driver version to
be visible from a PostgreSQL view.

The default is now DriverInfo.DRIVER_FULL_NAME, the driver name followed
by a space and DRIVER_VERSION. Any role that can connect to the database
can read application_name in pg_stat_activity, so the version is visible
to other database users as well.

User-visible:
Breaking: a connection that leaves ApplicationName unset sends
"PostgreSQL JDBC Driver X.Y.Z", where X.Y.Z is the driver version,
instead of "PostgreSQL JDBC Driver". A query that matches the old value
stops finding it; match the prefix "PostgreSQL JDBC Driver" instead.
Not changed: a connection that sets ApplicationName sends the value it sets.

Fixes #2404
```

## 2. Pull request title

`feat: add driver version to default ApplicationName`

## 3. Pull request description

```markdown
### Breaking changes

Code that matches the old default `application_name` stops finding connections that leave `ApplicationName` unset.

* Connections that leave `ApplicationName` unset send `PostgreSQL JDBC Driver X.Y.Z`, where `X.Y.Z` is the driver version, instead of `PostgreSQL JDBC Driver`. Match the prefix `PostgreSQL JDBC Driver` instead of the whole value, since the version now follows it.

The next release from `master` is 42.7.14 (`gradle.properties`), which is not a major release, so this break comes first.

### Why

Issue #2404 asks for the JDBC driver version to be visible from a PostgreSQL view. Users who want to know which driver version their applications use cannot get it from `pg_stat_activity` today: a connection that leaves `ApplicationName` unset shows `PostgreSQL JDBC Driver` whatever the version.

### What

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, the driver name followed by a space and the driver version. Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the version is visible to other database users as well. `docs/content/documentation/use.md` says so.

### User-visible changes

* Not changed: a connection that sets `ApplicationName` sends the value it sets.

### Verification

`ApplicationNameTest` has two new tests, and both need a running server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`, so it guards the new default. `explicitApplicationNameIsKept` passes on `master` as well and guards the explicit value. The claim that other roles can read `application_name` in `pg_stat_activity` was checked against a running server, not by a test.

### Scope

Adding the git sha of the build and the JDK version to the default name was considered and left out as too much. It can be discussed separately.

<details>
<summary>Pull request checklist</summary>

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

</details>
```
