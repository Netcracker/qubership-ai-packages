## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The history has 3 squash commits and 37 plain ones, and nothing in the repository names the merge method. That means the maintainers squash or rebase each pull request as they see fit. If they rebase, every commit lands as its own commit, so `add tests` and `Apply suggestion from @vlsi` would land without the change they belong to. Folding leaves a single commit. A squash of a single-commit pull request keeps that commit's message.

The one remaining commit:

```text
feat: include the driver version in the default ApplicationName

A connection that leaves ApplicationName unset sent "PostgreSQL JDBC
Driver" as application_name. A database administrator looking at
pg_stat_activity could see that an application uses pgjdbc, but not
which version of the driver it runs. Issue #2404 asks to see that
version directly from a PostgreSQL view.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME:
"PostgreSQL JDBC Driver" followed by a space and the version of the
driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver 42.7.14" (the driver version) instead of "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds it.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so the default ApplicationName shows the driver version to other database users.
Not changed:
An explicitly set ApplicationName is sent as it is.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
### Breaking changes

A query, monitoring rule, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections that leave `ApplicationName` unset:

* A connection with no `ApplicationName` reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` (the driver version), where 42.7.13 and earlier sent `PostgreSQL JDBC Driver`. Match on `application_name LIKE 'PostgreSQL JDBC Driver%'` instead, or set `ApplicationName` explicitly to keep a fixed value.

### What and why

Users want to know which driver version their applications run, as seen in `pg_stat_activity`. Every pgjdbc connection without `ApplicationName` reported `PostgreSQL JDBC Driver`, which says nothing about the version. #2404 asks to see the version of the JDBC driver directly from a PostgreSQL view.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. An explicitly set `ApplicationName` is sent as it is. `ApplicationNameTest.explicitApplicationNameIsKept` covers that case, and it passes on `master` too.

**Scope.** The git sha of the build and the JDK version are left out of the default to keep it short. They can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
