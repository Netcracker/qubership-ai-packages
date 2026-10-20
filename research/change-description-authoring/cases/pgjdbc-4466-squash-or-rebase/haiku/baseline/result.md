## 1. Commits

Fold commits 2 and 3 into commit 1. The tests and the review fixes belong to the same change, and commit 3 rewrites lines that commit 1 adds. The branch becomes one commit, and its subject takes the lowercase verb the history uses:

```text
feat: include the driver version in the default ApplicationName

Connections that leave ApplicationName unset now send the driver name
followed by its version, for example "PostgreSQL JDBC Driver 42.7.14",
instead of "PostgreSQL JDBC Driver". The value shows in pg_stat_activity
as application_name, so an administrator can see which driver version
each connection uses. An explicitly set ApplicationName is sent unchanged.

Any role that can connect to the database can read application_name for
every session in pg_stat_activity, so the version is visible to other
database users as well.

A query or dashboard that matches application_name = 'PostgreSQL JDBC
Driver' stops finding connections that leave ApplicationName unset.

The default value is DriverInfo.DRIVER_FULL_NAME, which joins
DRIVER_NAME and DRIVER_VERSION with a space.

Closes #2404

ApplicationNameTest covers the default, which now includes the driver
version, and an explicit ApplicationName. Both tests need a running
server.
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
The default `ApplicationName` now includes the driver version, so `pg_stat_activity` shows which version each connection uses. The default was `PostgreSQL JDBC Driver`. It is now `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.14`. `DriverInfo.DRIVER_FULL_NAME` joins `DRIVER_NAME` and `DRIVER_VERSION` with a space. An explicitly set `ApplicationName` is unaffected.

### Why

Users want to know which driver version their applications use. Issue #2404 asks for the same thing, and this change puts the version in `pg_stat_activity`.

I considered adding the git SHA of the build and the JDK version as well. I left both out as too much for one change. They can be discussed separately.

### Behavior change

This changes existing behavior for connections that leave `ApplicationName` unset:

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections after upgrading the driver.
- Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`, so the default now shows the driver version to other database users.

### Tests

`ApplicationNameTest` adds two tests. Both need a running server.

- `defaultApplicationNameCarriesTheDriverVersion` connects without `ApplicationName` and checks that `current_setting('application_name')` returns `PostgreSQL JDBC Driver` followed by a space and `DriverInfo.DRIVER_VERSION`. It fails on `master`, where the value is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and checks that `current_setting('application_name')` returns `billing`. It passes on `master` too.

Closes #2404
```
