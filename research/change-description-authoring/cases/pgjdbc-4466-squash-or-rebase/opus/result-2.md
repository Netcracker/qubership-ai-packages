## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit. The branch then merges as one commit, with this message:

```text
feat: include the driver version in the default ApplicationName

A database administrator who looks at pg_stat_activity cannot tell which
pgjdbc version a client runs. A connection that leaves ApplicationName
unset reports the fixed string "PostgreSQL JDBC Driver" in
application_name, whatever the version of the driver.

The default now carries the driver version and nothing else: the git sha
of the build and the JDK version are left out.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver <version>", such as "PostgreSQL JDBC Driver 42.7.14", where it reported "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect reads the application_name of every session in pg_stat_activity, so the default shows the driver version to other database users.
Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Description

```markdown
### Breaking changes

A connection that leaves `ApplicationName` unset now reports `PostgreSQL JDBC Driver` followed by a space and the driver version in `application_name`, such as `PostgreSQL JDBC Driver 42.7.14`. In 42.7.13 it reports `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. Update the query, or set `ApplicationName` explicitly: an explicit value is sent as given.

### Changes to Existing Features

Users want to know which driver version each of their applications runs, and #2404 asks to read it from a view in PostgreSQL. `pg_stat_activity` shows `application_name`, but the default value names only the driver, not its version.

Any role that can connect reads the `application_name` of every session in `pg_stat_activity`. The default therefore shows the driver version to other database users, and the `ApplicationName` entry in the documentation now says so.

`explicitApplicationNameIsKept` passes on `master` as well. It pins the explicit value, which this change must leave alone.

**Scope.** The git sha of the build and the JDK version are left out of the default. Adding them can be discussed separately.

Fixes #2404.

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?
```
