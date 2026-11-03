## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit. One commit remains:

```text
feat: include the driver version in the default application_name

Users want to know which pgjdbc version each of their applications
runs, and pg_stat_activity is where they look for it. A connection that
left ApplicationName unset reported "PostgreSQL JDBC Driver" whatever
the driver version was, so the version could not be seen from the
server (issue #2404).

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and DriverInfo.DRIVER_VERSION, the version of the
driver jar. The git sha of the build and the JDK version are left out
of the default; adding them can be discussed separately.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver <version>", for example "PostgreSQL JDBC Driver 42.7.14", where earlier versions reported "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections, so match on the "PostgreSQL JDBC Driver" prefix or set ApplicationName explicitly.
Any role that can connect to the database can read the driver version of such a connection in pg_stat_activity.

Not changed:
An explicitly set ApplicationName is sent as given, without the version.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default application_name
```

## 3. Description

```markdown
**Breaking changes.** Queries and dashboards that use the exact default application name to find pgjdbc connections no longer find them after the upgrade.

* A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver <version>`, for example `PostgreSQL JDBC Driver 42.7.14`. Earlier versions reported `PostgreSQL JDBC Driver`. A filter such as `application_name = 'PostgreSQL JDBC Driver'` no longer matches these connections. To find them, match on the prefix with `application_name LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Users want to know which driver version each of their applications runs, and `pg_stat_activity` is where they look for it. Until now every connection that left `ApplicationName` unset reported the same `PostgreSQL JDBC Driver`, so the server could not show the version (#2404). The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver name followed by a space and the version of the driver jar.

Other outcomes:

* Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`, so the default now shows the driver version to other database users.
* An explicitly set `ApplicationName` is sent as given, without the version.

`explicitApplicationNameIsKept` passes on `master` as well. It makes sure that an explicitly set name does not get the version suffix.

**Scope.** Adding the git sha of the build or the JDK version is outside this change and can be discussed separately.

Fixes #2404.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes: the default `application_name` changes; see **Breaking changes** above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
