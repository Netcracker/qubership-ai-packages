## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) is folded into commit 1. Commit 2 stays a separate commit with a new subject and body.

Commit 1:

```text
feat: add the driver version to the default ApplicationName

Every driver version sent the same default ApplicationName, PostgreSQL JDBC
Driver, so pg_stat_activity could not show which driver version a connection
uses. Users want that information, and issue #2404 asks to see it from a view
in PostgreSQL.

The default reuses DriverInfo.DRIVER_FULL_NAME, which already joins the driver
name and the version of the driver jar, so the version comes from the jar that
runs rather than from a second string.

User-visible:
When ApplicationName is not set, the driver sends PostgreSQL JDBC Driver X.Y.Z
as application_name in the startup message, for example PostgreSQL JDBC Driver
42.7.14. A filter on application_name = 'PostgreSQL JDBC Driver' stops matching
these connections. The latest release, 42.7.13, sent the old value, so match
the prefix with LIKE or set ApplicationName to keep the old value.
Any role that can connect to the database can read application_name of every
session in pg_stat_activity, so the driver version is visible to other
database users.

Not changed:
An explicitly set ApplicationName is sent as set.

Fixes #2404
```

Commit 2:

```text
test: pin the default and explicit ApplicationName

No test checked the default ApplicationName or an explicitly set one, so a
change to either would pass unnoticed. The new tests read application_name
back with current_setting on the server, which is the value pg_stat_activity
shows, so they check what the server receives rather than what the driver
holds.
```

## 2. Pull request title

```text
feat: add the driver version to the default ApplicationName
```

## 3. Pull request description

````markdown
Code that matches the old default `application_name` breaks.

User-visible:

When `ApplicationName` is not set, the driver sends `PostgreSQL JDBC Driver X.Y.Z` as `application_name` in the startup message, for example `PostgreSQL JDBC Driver 42.7.14`. A filter on `application_name = 'PostgreSQL JDBC Driver'` stops matching these connections. The latest release, 42.7.13, sent the old value. To keep such a filter working, match the prefix with `LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName` to `PostgreSQL JDBC Driver`.

Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the driver version is visible to other database users.

Not changed:

An explicitly set `ApplicationName` is sent as set.

Users want to know which driver version their applications use, and issue #2404 asks to see it from a view in PostgreSQL. The default `ApplicationName` is `PostgreSQL JDBC Driver` for every driver version, so `pg_stat_activity` cannot show the version a connection uses.

The default reuses `DriverInfo.DRIVER_FULL_NAME`, which already joins the driver name and the version of the driver jar, so the version comes from the jar that runs rather than from a second string.

`explicitApplicationNameIsKept` passes without this change, since it pins a value that already worked; both tests need a running server.

The git sha of the build and the JDK version are left out as too much for this change. They can be discussed separately.

Fixes #2404
````
