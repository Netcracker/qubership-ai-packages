## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch lands as one commit:

```text
feat: include the driver version in the default ApplicationName

When a connection left ApplicationName unset, the driver sent the
application_name "PostgreSQL JDBC Driver" whatever its version. A
database administrator looking at pg_stat_activity could not tell which
pgjdbc version a client used. Issue #2404 asks to see the driver
version in a PostgreSQL view, and users who track which driver version
their applications run asked for the same.

The default of ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar. The git sha of
the build and the JDK version were left out to keep the value short;
adding them can be discussed separately.

User-visible:
With ApplicationName unset, application_name is "PostgreSQL JDBC Driver" followed by a space and the driver version, for example "PostgreSQL JDBC Driver 42.7.14", where 42.7.13 sent "PostgreSQL JDBC Driver".
A query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc connections that leave ApplicationName unset; match the prefix "PostgreSQL JDBC Driver " or set ApplicationName explicitly.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so the default now shows the driver version to other database users.
Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
This changes a default in a 42.7.x release. Code that identifies pgjdbc connections by the exact default `application_name` stops matching them:

- With `ApplicationName` unset, `application_name` is `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds those connections. Match the prefix `PostgreSQL JDBC Driver ` or set `ApplicationName` explicitly.

When a connection left `ApplicationName` unset, every pgjdbc version sent the same `application_name`. A database administrator looking at `pg_stat_activity` could not tell which driver version a client used. Issue #2404 asks to see the driver version in a PostgreSQL view, and users who track which driver version their applications run asked for the same.

The default of `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: the driver name, a space, and the version of the driver jar. The git sha of the build and the JDK version were left out to keep the value short. Adding them can be discussed separately.

User-visible:
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. `use.md` says so.
Not changed:
An explicitly set `ApplicationName` is sent as given.

The new `ApplicationNameTest` needs a running server. It checks that the default carries `DriverInfo.DRIVER_VERSION`, which fails on `master`, and that `ApplicationName=billing` is kept.

Fixes #2404
```
