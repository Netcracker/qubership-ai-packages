## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. This leaves one commit. The repository squashes with the "title and description" setting, so the merged commit takes its subject from the pull request title and its body from the description. The commit's message below matches them.

```text
feat: include the driver version in the default ApplicationName

The default application_name that the driver sent at startup was
"PostgreSQL JDBC Driver" for every driver version. Users who want to
know which driver version each of their applications runs could not
see it in pg_stat_activity (#2404).

The default of ApplicationName is now DriverInfo.DRIVER_FULL_NAME,
which is "PostgreSQL JDBC Driver" followed by a space and the version
of the driver jar. The git sha of the build and the JDK version are
left out of the default name.

**User-visible changes.**
**Breaking:** A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 and earlier reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections; match the `PostgreSQL JDBC Driver` prefix instead, or set `ApplicationName` explicitly.
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default name shows the driver version to other database users.

**Not changed.**
An explicitly set `ApplicationName` is sent as given: `ApplicationName=billing` reports `billing`.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
**Breaking changes.**
Queries and dashboards that find pgjdbc connections by the exact default name stop finding them after the upgrade.
A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 and earlier reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections; match the `PostgreSQL JDBC Driver` prefix instead, or set `ApplicationName` explicitly.

The default `application_name` that the driver sent at startup was `PostgreSQL JDBC Driver` for every driver version. Users who want to know which driver version each of their applications runs could not see it in `pg_stat_activity` (#2404).

The default of `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar.

**User-visible changes.**
Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default name shows the driver version to other database users.

**Not changed.**
An explicitly set `ApplicationName` is sent as given: `ApplicationName=billing` reports `billing`. `explicitApplicationNameIsKept` passes on `master` as well, because it covers the case this change must leave alone.

**Scope.** The git sha of the build and the JDK version are left out of the default name. Whether to add them is a separate discussion.

Fixes #2404
```
