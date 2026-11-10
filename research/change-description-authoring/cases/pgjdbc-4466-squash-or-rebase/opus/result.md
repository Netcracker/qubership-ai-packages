## Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. One commit remains:

```text
feat: include the driver version in the default ApplicationName

When a connection left ApplicationName unset, the driver sent
"PostgreSQL JDBC Driver" as application_name. pg_stat_activity then
showed that a connection came from pgjdbc, but not which driver version
it used. Users want to see that version directly from a view in
PostgreSQL, as issue #2404 asks.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC Driver"
followed by a space and the version of the driver jar.

User-visible changes.
Breaking: a connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver 42.7.14" instead of "PostgreSQL JDBC Driver", so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' stops finding pgjdbc connections.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so the default shows the driver version to other database users.

Not changed.
An explicitly set ApplicationName is sent as is.

Fixes #2404
```

## Title

```text
feat: include the driver version in the default ApplicationName
```

## Description

```markdown
**Breaking changes.**
This breaks code that identifies pgjdbc connections by the exact default `application_name`, which is `PostgreSQL JDBC Driver` in 42.7.13 and earlier.
- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections. Match on the `PostgreSQL JDBC Driver ` prefix instead, or set `ApplicationName` explicitly. An explicit value is sent as is.

Users want to know which driver version their applications use, and they look in `pg_stat_activity` to find out. Issue #2404 asks for the same thing: to see the JDBC driver version of a client directly from a view in PostgreSQL. Before this change, the `application_name` column showed `PostgreSQL JDBC Driver` for every pgjdbc version.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`. The default therefore shows the driver version to other database users.

`explicitApplicationNameIsKept` passes on `master` too. It pins the explicit value, which this change must leave alone.

**Scope.** Adding the git SHA of the build or the JDK version to the default would put too much in one value, so this change leaves both out. They can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes, see "Breaking changes" above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
