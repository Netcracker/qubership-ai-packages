## 1. Commits at merge

The pull request is squashed into one commit. GitHub sets that commit's subject to the pull request title and its body to the description. `add tests` and `Apply suggestion from @vlsi` fold into `feat: Include driver version in default application_name`. None of the three branch messages reaches `git log`. GitHub appends the number to the subject, so the commit that remains is:

```text
feat: include the driver version in the default ApplicationName (#4466)

A connection that leaves `ApplicationName` unset now sends
`application_name` as `PostgreSQL JDBC Driver` followed by a space and
the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Until
now the value was `PostgreSQL JDBC Driver`. A query or dashboard that
matches `application_name = 'PostgreSQL JDBC Driver'` stops finding
pgjdbc connections after the upgrade. Match on the
`PostgreSQL JDBC Driver` prefix instead, or set
`ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Before this change, the server could not show which pgjdbc version a
client uses. Every connection that left `ApplicationName` unset appeared
in `pg_stat_activity` as `PostgreSQL JDBC Driver`, whatever version of
the driver it ran. Issue #2404 asks for the driver version to be visible
in a PostgreSQL view. Users who track which driver version their
applications run asked for the same thing.

The default is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver
name, a space, and the version of the driver jar. Adding the git sha of
the build or the JDK version was considered and left out as too much for
this name. Either one can be discussed separately.

User-visible:
Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. Setting `ApplicationName` keeps the version out of it.

Not changed:
An explicitly set `ApplicationName` is sent as given: with `ApplicationName=billing`, `current_setting('application_name')` returns `billing`.

`explicitApplicationNameIsKept` also passes without this change. It pins the `Not changed` line.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
A connection that leaves `ApplicationName` unset now sends
`application_name` as `PostgreSQL JDBC Driver` followed by a space and
the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Until
now the value was `PostgreSQL JDBC Driver`. A query or dashboard that
matches `application_name = 'PostgreSQL JDBC Driver'` stops finding
pgjdbc connections after the upgrade. Match on the
`PostgreSQL JDBC Driver` prefix instead, or set
`ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Before this change, the server could not show which pgjdbc version a
client uses. Every connection that left `ApplicationName` unset appeared
in `pg_stat_activity` as `PostgreSQL JDBC Driver`, whatever version of
the driver it ran. Issue #2404 asks for the driver version to be visible
in a PostgreSQL view. Users who track which driver version their
applications run asked for the same thing.

The default is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver
name, a space, and the version of the driver jar. Adding the git sha of
the build or the JDK version was considered and left out as too much for
this name. Either one can be discussed separately.

User-visible:
Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. Setting `ApplicationName` keeps the version out of it.

Not changed:
An explicitly set `ApplicationName` is sent as given: with `ApplicationName=billing`, `current_setting('application_name')` returns `billing`.

`explicitApplicationNameIsKept` also passes without this change. It pins the `Not changed` line.

Fixes #2404
```
