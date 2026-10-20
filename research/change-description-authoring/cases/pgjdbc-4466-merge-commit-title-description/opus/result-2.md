## 1. Commits at merge

The repository merges with merge commits, and every branch commit lands on `master` under its own message. Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1, so the branch merges as one commit with this message:

```text
feat: include the driver version in the default ApplicationName

A connection that leaves ApplicationName unset reports
"PostgreSQL JDBC Driver" in application_name, the same string for every
release. A database administrator looking at pg_stat_activity cannot
tell which driver version each application runs. Users have asked for
this, and issue #2404 asks to see the driver version from a PostgreSQL
view.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC Driver"
followed by a space and the version of the driver jar. Adding the git sha
of the build or the JDK version was considered and left out as more than
a default needs.

User-visible:
A connection that leaves ApplicationName unset reports
"PostgreSQL JDBC Driver 42.7.14" (the driver's version) in
application_name, where 42.7.13 reported "PostgreSQL JDBC Driver"; a
query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' no longer finds these
connections.
Any role that can connect to the database reads application_name of
every session in pg_stat_activity, so the default shows the driver
version to other database users.
Not changed:
A connection that sets ApplicationName reports that value as set.

Closes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
This changes a default in a 42.7.x release. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade:

- A connection that leaves `ApplicationName` unset reports `PostgreSQL JDBC Driver 42.7.14` (the driver's version) in `application_name`, where 42.7.13 reported `PostgreSQL JDBC Driver`. To keep such a query working, match the `PostgreSQL JDBC Driver ` prefix, or set `ApplicationName=PostgreSQL JDBC Driver` on the connection.

Because every connection without an `ApplicationName` reports the same string in every release, a database administrator looking at `pg_stat_activity` cannot tell which driver version each application runs. Users have asked for this, and #2404 asks to see the driver version from a PostgreSQL view.

The default is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. I considered adding the git sha of the build or the JDK version, and left both out as more than a default needs. They can be discussed separately.

User-visible changes:
- Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default shows the driver version to other database users.
- Not changed: a connection that sets `ApplicationName` reports that value as set.

The new `ApplicationNameTest` needs a running server. It checks that the default ends with `DriverInfo.DRIVER_VERSION`, which fails on `master`, and that an explicit `ApplicationName=billing` is kept.

Closes #2404
```
