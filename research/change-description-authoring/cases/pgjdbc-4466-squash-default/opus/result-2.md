## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch merges as one commit:

```text
feat: append the driver version to the default ApplicationName

A connection that leaves ApplicationName unset reported
application_name as "PostgreSQL JDBC Driver" for every driver version.
A database administrator who reads pg_stat_activity could not tell
which pgjdbc version a client runs. Issue #2404 asks for the driver
version to be visible from a view in PostgreSQL.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME. That
value is the driver name, a space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver <version>", such as "PostgreSQL JDBC Driver 42.7.14", instead of "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads the driver version of these sessions from application_name in pg_stat_activity.

Not changed:
An explicitly set ApplicationName is sent as given, without the version.

Fixes #2404
```

## 2. Title

```text
feat: append the driver version to the default ApplicationName sent as application_name
```

## 3. Description

```markdown
### Breaking changes

The default `application_name` changes. Code that matches the old string stops finding pgjdbc connections after the upgrade:

* A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver ` followed by the driver version, such as `PostgreSQL JDBC Driver 42.7.14`. In 42.7.13 and earlier it reports `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match on the prefix instead (`application_name LIKE 'PostgreSQL JDBC Driver%'`), or set `ApplicationName` explicitly.

Users want to know which driver version their applications run, as seen in `pg_stat_activity`. Every pgjdbc version reported the same default `application_name`, so the view could not tell versions apart.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and the driver version. An explicitly set `ApplicationName` is sent as given. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users.

Fixes #2404.

**Scope.** The default does not include the git sha of the build or the JDK version. Adding them can be discussed separately.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes: see Breaking changes.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

`ApplicationNameTest.explicitApplicationNameIsKept` passes on `master` too. It checks that an explicitly set name stays unchanged.
```
