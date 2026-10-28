## Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch then merges as one commit:

```text
feat: include the driver version in the default ApplicationName

A connection that left ApplicationName unset reported the same
application_name, "PostgreSQL JDBC Driver", whatever driver version it
ran. pg_stat_activity therefore could not show which pgjdbc version a
client uses (#2404), and users want to see there which driver version
their applications run.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver", a space, and the version of the driver jar.

User-visible:
When ApplicationName is not set, application_name is "PostgreSQL JDBC Driver 42.7.14" (the version of the driver jar) instead of "PostgreSQL JDBC Driver", so a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads in pg_stat_activity the driver version of every session that leaves ApplicationName unset.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## Title

```text
feat: include the driver version in the default ApplicationName
```

## Description

```markdown
In 42.7.13, connections that leave `ApplicationName` unset reported `PostgreSQL JDBC Driver` as their `application_name`. With this change they report a different value:

- `application_name` is now `PostgreSQL JDBC Driver 42.7.14`, which ends in the version of the driver jar, instead of `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. To find them, match `application_name LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

The old default was the same for every driver version, so `pg_stat_activity` could not show which pgjdbc version a client uses, as #2404 asks. Users want to see there which driver version their applications run.

The default is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, a space, and the version of the driver jar.

User-visible:
- Any role that can connect to the database reads in `pg_stat_activity` the driver version of every session that leaves `ApplicationName` unset.

Not changed:
- An explicitly set `ApplicationName` is sent as given. `explicitApplicationNameIsKept` passes on `master` as well and checks that this does not change.

The git sha of the build and the JDK version are not part of this change and can be discussed separately.

Fixes #2404
```
