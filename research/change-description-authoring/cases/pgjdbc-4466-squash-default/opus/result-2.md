## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. The branch then merges as one commit:

```text
feat: include the driver version in the default application_name

pg_stat_activity did not show which pgjdbc version a connection used.
Unless the application set ApplicationName, the driver sent
"PostgreSQL JDBC Driver" as application_name, with no version. Users
asked to read the driver version of each client from a PostgreSQL view.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME, which is
"PostgreSQL JDBC Driver" followed by a space and the version of the
driver jar. The git sha of the build and the JDK version are left out.

User-visible:
When ApplicationName is not set, application_name is
"PostgreSQL JDBC Driver 42.7.14" (the version of the driver in use)
instead of "PostgreSQL JDBC Driver". A query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc
connections. Set ApplicationName=PostgreSQL JDBC Driver to keep the old
value.
Any role that can connect to the database can see the driver version of
every session that uses the default ApplicationName in pg_stat_activity.
Not changed:
An explicitly set ApplicationName is sent as is.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default application_name
```

## 3. Description

```markdown
**Breaking changes.** Code that finds pgjdbc connections by the old default `application_name` stops finding them:

- When `ApplicationName` is not set, `application_name` in `pg_stat_activity` is `PostgreSQL JDBC Driver 42.7.14` (the version of the driver jar). In 42.7.13 it was `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. To fix it, match `LIKE 'PostgreSQL JDBC Driver%'` or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

`pg_stat_activity` did not show which driver version a client used, because the default `application_name` carried no version. Issue #2404 asks to see it from a PostgreSQL view, and users who want to know which driver version their applications run have asked for the same.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, a space, and the driver version. An explicitly set `ApplicationName` is sent as is. Any role that can connect to the database can see `application_name` for every session in `pg_stat_activity`, so other database users now see the driver version of connections that use the default. The `ApplicationName` entry in `use.md` says so.

`explicitApplicationNameIsKept` also passes on `master`. It covers the explicit value, which this change must leave as it is.

**Scope.** The default leaves out the git sha of the build and the JDK version. Whether to add them can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [x] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See **Breaking changes** above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
