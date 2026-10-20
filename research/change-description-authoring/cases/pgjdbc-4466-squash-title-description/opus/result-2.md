## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. One commit remains:

```text
feat: include the driver version in the default ApplicationName

Previously a connection that left ApplicationName unset sent the
application_name "PostgreSQL JDBC Driver" whatever the driver version,
so pg_stat_activity showed that a session came from pgjdbc but not
which version of the driver it used. Users asked for that version in
#2404, to tell from the server which driver each of their applications
runs.

The default is now DriverInfo.DRIVER_FULL_NAME, the driver name
followed by a space and the version of the driver jar. The git sha of
the build and the JDK version were left out as more than that question
needs.

User-visible:
- For a connection that leaves ApplicationName unset, application_name
  is "PostgreSQL JDBC Driver" followed by a space and the driver
  version, for example "PostgreSQL JDBC Driver 42.7.14"; 42.7.13 and
  earlier send "PostgreSQL JDBC Driver". A filter such as
  application_name = 'PostgreSQL JDBC Driver' no longer matches these
  connections. Match the "PostgreSQL JDBC Driver " prefix instead, or
  set ApplicationName=PostgreSQL JDBC Driver to keep the old value.
- Any role that can connect to the database reads the application_name
  of every session from pg_stat_activity, so the default shows the
  driver version to other database users. Set ApplicationName to keep
  the version out of it.
Not changed:
- An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Description

```markdown
A query, dashboard, or alert that finds pgjdbc connections by the exact default application name stops matching them after this change.

User-visible:
- For a connection that leaves `ApplicationName` unset, `application_name` is `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`; 42.7.13 and earlier send `PostgreSQL JDBC Driver`. A filter such as `application_name = 'PostgreSQL JDBC Driver'` no longer matches these connections. Match the `PostgreSQL JDBC Driver ` prefix instead, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Previously the default `application_name` was `PostgreSQL JDBC Driver` for every driver version, so `pg_stat_activity` showed that a session came from pgjdbc but not which version of the driver it used. Users asked for that version in #2404, to tell from the server which driver each of their applications runs.

The default is now `DriverInfo.DRIVER_FULL_NAME`, the driver name followed by a space and the version of the driver jar. The git sha of the build and the JDK version were left out as more than that question needs, and adding them is outside this change.

User-visible:
- Any role that can connect to the database reads the `application_name` of every session from `pg_stat_activity`, so the default shows the driver version to other database users. Set `ApplicationName` to keep the version out of it.

Not changed:
- An explicitly set `ApplicationName` is sent as given.

`ApplicationNameTest` (new, needs a running server) reads `application_name` back from the server: the default carries the driver version, a check that fails on `master`, and `ApplicationName=billing` stays `billing`.

Fixes #2404
```
