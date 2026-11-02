## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into commit 1. One commit remains, with this message:

```text
feat: include the driver version in the default application_name

Users want to know which pgjdbc version each of their applications
runs, and the place they look is pg_stat_activity (#2404). Every
connection that left ApplicationName unset sent the same
"PostgreSQL JDBC Driver" as application_name, whatever the driver
version, so the database could not tell driver versions apart.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar. The git sha
of the build and the JDK version are left out as too much for the
default.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver " followed by the driver version, for example "PostgreSQL JDBC Driver 42.7.14", where 42.7.13 reported "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads the driver version of other sessions from application_name in pg_stat_activity.
Not changed:
A connection that sets ApplicationName reports that value unchanged.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
**Breaking changes.** Code that finds pgjdbc connections by the exact default application name stops finding them after the upgrade:

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver ` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Version 42.7.13 reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match `application_name LIKE 'PostgreSQL JDBC Driver%'` instead, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Issue #2404 asks to see the version of the JDBC driver a client uses directly from a view in PostgreSQL. Users have asked the same thing about their applications in `pg_stat_activity`. Until now, every connection that left `ApplicationName` unset showed `PostgreSQL JDBC Driver` there, whatever the driver version.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and the version of the driver jar. A connection that sets `ApplicationName` sends that value unchanged. Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`. Other database users can therefore see the driver version of each connection.

`explicitApplicationNameIsKept` also passes on `master`. It covers the explicitly set value, which this change must leave alone.

**Scope.** The default leaves out the git sha of the build and the JDK version. Adding them can be discussed separately.

Fixes #2404.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes: see **Breaking changes** above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
