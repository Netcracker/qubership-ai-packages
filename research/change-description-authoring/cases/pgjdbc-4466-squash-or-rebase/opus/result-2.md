## Commits at merge

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. Commit 2 adds the tests for commit 1's behavior. Commit 3 rewrites commit 1's changelog and documentation lines. The maintainers may rebase instead of squashing, and then each fix-up would land as a commit of its own. One commit remains:

```text
feat: include the driver version in the default application_name

A database administrator who looks at pg_stat_activity cannot tell
which pgjdbc version a client connection uses. A connection that does
not set ApplicationName reports the fixed string
"PostgreSQL JDBC Driver" as its application_name.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name `PostgreSQL JDBC Driver 42.7.14` with driver 42.7.14, instead of `PostgreSQL JDBC Driver`; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads the application_name of every session in pg_stat_activity, so the default shows the driver version to other database users.

Not changed:
A connection that sets ApplicationName reports that value as given.

Fixes #2404
```

## Pull request title

```text
feat: include the driver version in the default ApplicationName (application_name)
```

## Pull request description

```markdown
### Breaking changes

This changes a default in a patch release (`pgjdbc.version=42.7.14`). It affects code that identifies pgjdbc connections by their `application_name`.

* A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`, the value through 42.7.13. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. To keep the old value, set `ApplicationName=PostgreSQL JDBC Driver` explicitly.

### Why

Users want to know which driver version their applications use, and `pg_stat_activity` is where they look. Before this change it showed the same `PostgreSQL JDBC Driver` for every pgjdbc version. #2404 asks for exactly this: to see the JDBC driver version of a client in a PostgreSQL view.

### What

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is `DRIVER_NAME + " " + DRIVER_VERSION`. The version is the version of the driver jar.

### User-visible changes

* Any role that can connect to the database reads the `application_name` of every session in `pg_stat_activity`, so the default shows the driver version to other database users. The `ApplicationName` entry in `use.md` says so.
* Not changed: a connection that sets `ApplicationName` reports that value as given.

### Verification

`explicitApplicationNameIsKept` passes on `master` too. It covers the side that must not change: an explicit `ApplicationName=billing` still reads back as `billing`.

### Scope

The build's git SHA and the JDK version are not in the default. Adding either can be discussed separately.

Fixes #2404

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
