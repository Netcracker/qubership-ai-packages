## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. One commit remains:

```text
feat: include the driver version in the default ApplicationName

A database administrator could not tell from pg_stat_activity which
pgjdbc version a client uses. A connection that left ApplicationName
unset reported application_name as "PostgreSQL JDBC Driver", the same
string for every driver version.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME, which is
"PostgreSQL JDBC Driver" followed by a space and the version of the
driver jar. The git sha of the build and the JDK version were left out
to keep the default short.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver" followed by a space and the driver version, for example "PostgreSQL JDBC Driver 42.7.14", where 42.7.13 reported "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads this driver version for every such session in pg_stat_activity.
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
This changes a default in a patch release. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade.

Breaking: a connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`, where 42.7.13 reported `PostgreSQL JDBC Driver`. Update the match, or set `ApplicationName` explicitly to keep a fixed value.

A database administrator could not tell from `pg_stat_activity` which pgjdbc version a client uses, because every driver version sent the same default `application_name`. Users asked for this in #2404 and in conversations with the author.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is `DriverInfo.DRIVER_NAME` followed by a space and the version of the driver jar. The documentation of `ApplicationName` gives the new default and says that it makes the driver version visible to other database users. The changelog entry is first under Changed and states the break.

User-visible:
Any role that can connect to the database reads this driver version for every such session in `pg_stat_activity`.
Not changed:
An explicitly set `ApplicationName` is sent as given.

The new `ApplicationNameTest` needs a running server. It reads the default back from `current_setting('application_name')`, which fails on master, and it checks that an explicit `ApplicationName` is kept.

Adding the git sha of the build or the JDK version to the default is not part of this change and can be discussed separately.

Fixes #2404
```
