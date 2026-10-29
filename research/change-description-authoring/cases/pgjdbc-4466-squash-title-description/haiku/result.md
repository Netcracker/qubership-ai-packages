## 1. Commits

Commits 1, 2, and 3 all fold into one squash commit, the only commit that lands on `master`. Its message, with the number GitHub appends:

```text
feat: suffix the default ApplicationName with the driver version (#4466)

Breaking: a connection that leaves ApplicationName unset now sends the driver version after the name, such as `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. Match `PostgreSQL JDBC Driver` as a prefix, or set ApplicationName explicitly to keep the old value.

The default ApplicationName was the constant `PostgreSQL JDBC Driver`, so `pg_stat_activity` could not show which driver version a connection uses. Issue #2404 asks to see that version from a PostgreSQL view, and users want to know which driver version their applications run.

The default is now `DriverInfo.DRIVER_FULL_NAME`, which joins `DriverInfo.DRIVER_NAME` and `DriverInfo.DRIVER_VERSION` with a space. It is sent in the startup message, where the old value went.

User-visible:
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so every such role sees the driver version of each connection that leaves ApplicationName unset.

Not changed:
An ApplicationName the caller sets is sent unchanged, with no version added.

`explicitApplicationNameIsKept` passes on master, because it pins a value that already worked. `defaultApplicationNameCarriesTheDriverVersion` fails there. Both tests need a running server.

The git sha of the build and the JDK version were considered and left out as too much for this change. They can be discussed separately.

Fixes #2404
```

## 2. Pull request title

```text
feat: suffix the default ApplicationName with the driver version
```

## 3. Pull request description

```markdown
Breaking: a connection that leaves ApplicationName unset now sends the driver version after the name, such as `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. Match `PostgreSQL JDBC Driver` as a prefix, or set ApplicationName explicitly to keep the old value.

The default ApplicationName was the constant `PostgreSQL JDBC Driver`, so `pg_stat_activity` could not show which driver version a connection uses. Issue #2404 asks to see that version from a PostgreSQL view, and users want to know which driver version their applications run.

The default is now `DriverInfo.DRIVER_FULL_NAME`, which joins `DriverInfo.DRIVER_NAME` and `DriverInfo.DRIVER_VERSION` with a space. It is sent in the startup message, where the old value went.

User-visible:
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so every such role sees the driver version of each connection that leaves ApplicationName unset.

Not changed:
An ApplicationName the caller sets is sent unchanged, with no version added.

`explicitApplicationNameIsKept` passes on master, because it pins a value that already worked. `defaultApplicationNameCarriesTheDriverVersion` fails there. Both tests need a running server.

The git sha of the build and the JDK version were considered and left out as too much for this change. They can be discussed separately.

Fixes #2404
```
