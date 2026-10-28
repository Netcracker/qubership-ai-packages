## 1. Commits

Commits 2 and 3 fold into commit 1, so the branch lands as one commit with this message:

```text
feat: include the driver version in the default ApplicationName

The default ApplicationName is "PostgreSQL JDBC Driver" in every driver
version, so pg_stat_activity shows the application of a connection but
not the driver version it runs. A user asked to see that version from a
view (#2404).

The default is now DriverInfo.DRIVER_FULL_NAME, the driver name, a space,
and the version of the driver jar, instead of DriverInfo.DRIVER_NAME. An
explicitly set ApplicationName is sent as given.

User-visible:
Breaking: a connection that leaves ApplicationName unset sends
"PostgreSQL JDBC Driver X.Y.Z" in place of "PostgreSQL JDBC Driver", which
the driver sent through 42.7.13. A query that matches the old value, such
as application_name = 'PostgreSQL JDBC Driver', no longer finds those
connections. Set ApplicationName to keep the old value, or match the
prefix.
Any role that can connect reads application_name of every session in
pg_stat_activity, so the version is visible to other database users.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

`feat: include the driver version in the default ApplicationName`

## 3. Pull request description

```markdown
### Breaking changes

Code that matches the old default breaks. A query, dashboard, or alert that filters on `application_name = 'PostgreSQL JDBC Driver'` no longer finds the connections that leave `ApplicationName` unset.

* When `ApplicationName` is not set, the connection sends `PostgreSQL JDBC Driver X.Y.Z` in place of `PostgreSQL JDBC Driver`, which the driver sent through 42.7.13. Match the prefix `PostgreSQL JDBC Driver` with `LIKE`, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Why

`pg_stat_activity` shows the application name of each session. The default name carries no version, so a user who wants the driver version there has to set `ApplicationName` by hand. A user asked to see the version from a view (#2404).

### What

The default `ApplicationName` is `DriverInfo.DRIVER_FULL_NAME` rather than `DriverInfo.DRIVER_NAME`. That is `PostgreSQL JDBC Driver`, a space, and the version of the driver jar, such as `PostgreSQL JDBC Driver 42.7.14`.

### User-visible changes

* Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the driver version is visible to other database users, not only to operators.

Not changed: an explicitly set `ApplicationName` is sent as given.

### Verification

`explicitApplicationNameIsKept` passes without the change. It pins the explicit `ApplicationName`, which must keep working as before.

### Scope

* The git SHA of the build and the JDK version are left out as too much. They can be discussed separately.

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
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
