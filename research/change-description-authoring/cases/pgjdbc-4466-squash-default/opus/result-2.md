## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. This leaves one commit. The repository uses GitHub's default squash message, so a single-commit pull request lands with that commit's subject and body, and GitHub appends ` (#4466)` to the subject.

```text
feat: append the driver version to the default ApplicationName

A connection that left ApplicationName unset sent the fixed string
"PostgreSQL JDBC Driver" as application_name. pg_stat_activity showed
that a session came from pgjdbc but not which driver version it used.
Users who need to know which driver version each of their applications
runs could not see it from the database.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver", a space, and the version of the driver jar.

User-visible changes.
Breaking: a connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver 42.7.14" (the version of the driver jar), where 42.7.13 reported "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections, so match the prefix instead, or set ApplicationName=PostgreSQL JDBC Driver to keep the old value.
Any role that can connect to the database can read the application_name of every session in pg_stat_activity, so the default now shows the driver version to other database users.

Not changed.
An ApplicationName set explicitly is sent as set.

Fixes #2404
```

## 2. Title

```text
feat: append the driver version to the default ApplicationName
```

## 3. Description

```markdown
**Breaking changes.**
Code that finds pgjdbc sessions by the exact default `application_name` stops finding them after the upgrade:
- A connection that leaves `ApplicationName` unset reports `application_name` `PostgreSQL JDBC Driver 42.7.14` (the version of the driver jar), where 42.7.13 reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the prefix instead, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Issue #2404 asks to see the version of the JDBC driver a client uses directly from a view in PostgreSQL. Users have also asked which driver version their applications use, as seen in `pg_stat_activity`. Before this change, the default `application_name` showed that a session came from pgjdbc but not which version.

The default `ApplicationName` is now `PostgreSQL JDBC Driver`, a space, and the driver version. An `ApplicationName` set explicitly is sent as set. Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. The `ApplicationName` entry in `use.md` says so.

`explicitApplicationNameIsKept` passes on `master` too. It pins the explicit value that this change must leave alone.

**Scope.** The git sha of the build and the JDK version are left out of the default. Adding them can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [x] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
