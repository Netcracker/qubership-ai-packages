## 1. Commits

The last 40 merges on `master` are merge commits, so every commit on the branch lands on `master` as it is. Fold `add tests` and `Apply suggestion from @vlsi` into commit 1. That leaves one commit, with the code, its tests, the docs and the changelog together:

```text
feat: append the driver version to the default ApplicationName

A connection that left ApplicationName unset reported application_name
as "PostgreSQL JDBC Driver". In pg_stat_activity, a database
administrator could see that a session came from pgjdbc but not which
driver version the client ran. Issue #2404 asks to see that version
directly from a view in PostgreSQL.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar.

**User-visible changes.**
Breaking: a connection that leaves ApplicationName unset reports application_name as `PostgreSQL JDBC Driver 42.7.14` (the version of the driver jar), where 42.7.13 reported `PostgreSQL JDBC Driver`; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections, so match the `PostgreSQL JDBC Driver` prefix or set ApplicationName explicitly.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so with the default ApplicationName other database users see the driver version.

**Not changed.**
A connection that sets ApplicationName, for example ApplicationName=billing, reports that value unchanged.

Fixes #2404
```

## 2. Pull request title

```text
feat: append the driver version to the default ApplicationName
```

## 3. Pull request description

```markdown
**Breaking changes.** A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade.
A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` (the version of the driver jar), where 42.7.13 reported `PostgreSQL JDBC Driver`. To keep such a query working, match the `PostgreSQL JDBC Driver` prefix, or set `ApplicationName` explicitly.

Every pgjdbc connection that left `ApplicationName` unset showed up in `pg_stat_activity` as `PostgreSQL JDBC Driver`. A database administrator could see that a session came from pgjdbc but not which driver version the client ran. Users have asked to see that version directly from a view in PostgreSQL (#2404).

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: the driver name, a space, and the version of the driver jar. The `ApplicationName` entry in `use.md` documents the new default.

**User-visible changes.**
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so with the default `ApplicationName` other database users see the driver version.

**Not changed.**
A connection that sets `ApplicationName`, for example `ApplicationName=billing`, reports that value unchanged.

**Scope.** The default does not include the git SHA of the build or the JDK version. Both were considered and left out as too much, and can be discussed separately.

`ApplicationNameTest.explicitApplicationNameIsKept` also passes on `master`: it checks that an explicitly set name is not changed.

Fixes #2404
```
