## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. That leaves one commit with this message:

```text
feat: append the driver version to the default ApplicationName

A connection that left ApplicationName unset reported application_name
as "PostgreSQL JDBC Driver" whatever the driver version, so
pg_stat_activity could not show which pgjdbc version a client used.
Users asked to see the driver version from the server side.

The default is now DriverInfo.DRIVER_FULL_NAME: the driver name, a
space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver <version>", for example "PostgreSQL JDBC Driver 42.7.14", instead of "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so the default value shows the driver version to other database users.
Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Title

```text
feat: append the driver version to the default ApplicationName
```

## 3. Description

```markdown
**Breaking changes.** After the upgrade, a query or dashboard that finds pgjdbc connections by their default `application_name` no longer finds them.

* A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar, for example `PostgreSQL JDBC Driver 42.7.14`. Up to 42.7.13 it reported `PostgreSQL JDBC Driver`. A filter such as `application_name = 'PostgreSQL JDBC Driver'` stops matching. To keep a fixed value, set `ApplicationName` explicitly.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

Users want to see which driver version their applications use, and `pg_stat_activity` is where they look. Before this change, every pgjdbc connection that left `ApplicationName` unset showed the same `PostgreSQL JDBC Driver`.

* Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`. The default value therefore shows the driver version to other database users.
* An explicitly set `ApplicationName` is sent as given. `explicitApplicationNameIsKept` covers this, and it passes on `master` too.

**Scope.** The default leaves out the git sha of the build and the JDK version. Whether to add either one can be discussed separately.

Fixes #2404.

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
