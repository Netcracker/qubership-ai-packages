## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit. That leaves one commit, and the squash keeps its full message:

```text
feat: include the driver version in the default ApplicationName

A database administrator could not tell from PostgreSQL which pgjdbc
version a client runs. A connection that leaves ApplicationName unset
reported "PostgreSQL JDBC Driver" as application_name whatever the
driver version, so pg_stat_activity showed the same name for every
release. Users who want to know which driver version their applications
use asked for it to be readable directly from a view in PostgreSQL.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME:
"PostgreSQL JDBC Driver" followed by a space and the version of the
driver jar. The git sha of the build and the JDK version are left out;
adding them can be discussed separately.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver 42.7.14", where 42.7.13 reported "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds it.
Any role that can connect to the database reads the driver version of such a connection in pg_stat_activity.
Not changed:
A connection that sets ApplicationName reports that value as application_name.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Description

```markdown
### Breaking changes

This change breaks code that finds pgjdbc connections by the exact default `application_name`:

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14`. In 42.7.13 and earlier it reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. To keep finding them, match on the prefix `PostgreSQL JDBC Driver `, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Why

Users want to know which driver version each of their applications uses, as seen in `pg_stat_activity`. Issue #2404 asks to read the version of the JDBC driver a client uses directly from a view in PostgreSQL. The default name had no version in it, so every pgjdbc release showed the same name.

### What

The default `ApplicationName` is `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, a space, and the version of the driver jar. The changelog entry goes first under Changed because of the break above.

### User-visible changes

- Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users can see the driver version of a connection that leaves `ApplicationName` unset.
- Not changed: a connection that sets `ApplicationName` reports that value.

### How to verify

`explicitApplicationNameIsKept` passes on `master` too. It pins the explicit name, which this change must not alter.

### Scope

The git sha of the build and the JDK version are left out of the default name. Adding them can be discussed separately.

Fixes #2404

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See Breaking changes above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
