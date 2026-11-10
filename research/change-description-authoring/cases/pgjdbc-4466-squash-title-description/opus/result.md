## 1. Commits

Commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) fold into commit 1. Merges into `master` are squashed with the pull request title and description, so one commit lands:

```text
feat: add the driver version to the default ApplicationName (#4466)

**Breaking changes.** A query or dashboard that finds pgjdbc connections by the exact default name stops finding them after the upgrade.
A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 and earlier send `PostgreSQL JDBC Driver`; a filter such as `application_name = 'PostgreSQL JDBC Driver'` no longer matches them, so match the `PostgreSQL JDBC Driver ` prefix instead, or set `ApplicationName` explicitly.

PostgreSQL gave no way to see which pgjdbc version a client connection
uses. With `ApplicationName` unset, every driver version sent the same
`application_name`, `PostgreSQL JDBC Driver`, so `pg_stat_activity`
showed one value for all of them. Users asked for the version in a
view, to find out which driver versions their applications run.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`,
the driver name followed by the version of the driver jar. It reaches
`pg_stat_activity` through the startup parameter the driver already
sends.

**User-visible changes.**
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so a connection that leaves `ApplicationName` unset now shows the driver version to other database users; set `ApplicationName` to keep the version out.

**Not changed.**
An explicitly set `ApplicationName` is sent as given, without the version.

**Scope.** The git sha of the build and the JDK version are left out
of the default. Adding either one can be discussed separately.

`explicitApplicationNameIsKept` passes on `master` too, because it checks the explicit value that this change must not alter.

Closes #2404
```

## 2. Title

```text
feat: add the driver version to the default ApplicationName
```

## 3. Description

```markdown
**Breaking changes.** A query or dashboard that finds pgjdbc connections by the exact default name stops finding them after the upgrade.
A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 and earlier send `PostgreSQL JDBC Driver`; a filter such as `application_name = 'PostgreSQL JDBC Driver'` no longer matches them, so match the `PostgreSQL JDBC Driver ` prefix instead, or set `ApplicationName` explicitly.

PostgreSQL gave no way to see which pgjdbc version a client connection
uses. With `ApplicationName` unset, every driver version sent the same
`application_name`, `PostgreSQL JDBC Driver`, so `pg_stat_activity`
showed one value for all of them. Users asked for the version in a
view, to find out which driver versions their applications run.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`,
the driver name followed by the version of the driver jar. It reaches
`pg_stat_activity` through the startup parameter the driver already
sends.

**User-visible changes.**
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so a connection that leaves `ApplicationName` unset now shows the driver version to other database users; set `ApplicationName` to keep the version out.

**Not changed.**
An explicitly set `ApplicationName` is sent as given, without the version.

**Scope.** The git sha of the build and the JDK version are left out
of the default. Adding either one can be discussed separately.

`explicitApplicationNameIsKept` passes on `master` too, because it checks the explicit value that this change must not alter.

Closes #2404
```
