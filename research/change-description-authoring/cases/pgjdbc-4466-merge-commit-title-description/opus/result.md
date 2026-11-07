## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The repository merges with a merge commit, so every commit on the branch lands on `master` as its own commit. Commit 3 corrects the `CHANGELOG.md` and `use.md` changes from commit 1. Commit 2 adds the tests for that change. One commit remains:

```text
feat: add the driver version to the default ApplicationName

A connection that leaves ApplicationName unset reports application_name
as "PostgreSQL JDBC Driver" with every driver version. A database
administrator who wants to know which pgjdbc version each application
uses cannot tell it from pg_stat_activity, as issue #2404 asks.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
string "PostgreSQL JDBC Driver", a space, and the version of the driver
jar. The git sha of the build and the JDK version are left out of the
default as too much detail.

**User-visible changes.**
**Breaking:** A connection that leaves ApplicationName unset reports application_name as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the prefix instead, or set ApplicationName on the connection.
Any role that can connect to the database reads the driver version of these connections from pg_stat_activity. To hide the version, set ApplicationName on the connection.

**Not changed.**
An explicitly set ApplicationName is sent as given, with no version appended.

Fixes #2404
```

## 2. Pull request title

```text
feat: add the driver version to the default ApplicationName
```

## 3. Pull request description

```markdown
**Breaking changes.**
Code that finds pgjdbc connections by their default `application_name` stops finding them after the upgrade.
A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the prefix instead, or set `ApplicationName` on the connection.

A connection that leaves `ApplicationName` unset reports the same `application_name` with every driver version. Users asked to see which driver version each application uses in `pg_stat_activity`, and issue #2404 asks for that too.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: the string `PostgreSQL JDBC Driver`, a space, and the version of the driver jar. I left the git sha of the build and the JDK version out of the default as too much detail.

**User-visible changes.**
Any role that can connect to the database reads the driver version of these connections from `pg_stat_activity`. To hide the version, set `ApplicationName` on the connection.

**Not changed.**
An explicitly set `ApplicationName` is sent as given, with no version appended. `explicitApplicationNameIsKept` checks this, and it passes on `master` too.

**Scope.** This change does not add the git sha of the build or the JDK version to the default. Adding them can be discussed in a separate issue.

Fixes #2404
```
