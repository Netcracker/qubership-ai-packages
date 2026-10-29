## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit. One commit remains:

```text
feat: include the driver version in the default ApplicationName

When ApplicationName was not set, the driver sent "PostgreSQL JDBC
Driver" as application_name at startup. pg_stat_activity showed which
connections came from pgjdbc, but not which driver version each one
used. Users asked to see that version from the server side.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver" followed by the driver version, for example "PostgreSQL JDBC Driver 42.7.14", where 42.7.13 reports "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads the driver version of these sessions from application_name in pg_stat_activity.
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
This changes a default in a 42.7.x release. Code that matches the old default `application_name` exactly stops finding pgjdbc connections:

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. In 42.7.13 it reports `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. To fix that, match on the `PostgreSQL JDBC Driver` prefix, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Users want to know which driver version each of their applications uses. For every pgjdbc connection that leaves `ApplicationName` unset, `pg_stat_activity` showed only `PostgreSQL JDBC Driver`. Issue #2404 asks for the driver version in a PostgreSQL view.

The default `ApplicationName` is now the driver name, a space, and the version of the driver jar.

- Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`. That means these sessions now show their driver version to other database users.
- An explicitly set `ApplicationName` is sent as given.

This change does not add the git sha of the build or the JDK version to the default.

`explicitApplicationNameIsKept` also passes on `master`. It checks that an explicitly set value stays the same.

Fixes #2404
```
