## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. Both commits complete the same change, and neither one stands alone on `master`. The branch then has one commit, so a squash merge and a rebase merge record the same change.

```text
feat: include driver version in default application_name

Users want to know which driver version each application connects
with, and pg_stat_activity shows the application_name of every
session. When ApplicationName is not set, the driver now sends
"PostgreSQL JDBC Driver" followed by a space and the driver version,
for example "PostgreSQL JDBC Driver 42.7.14". Before this change it
sent "PostgreSQL JDBC Driver". An explicitly set ApplicationName is
sent unchanged.

A query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' stops finding pgjdbc
connections after the upgrade.

Any role that can connect to the database can read the
application_name of every session in pg_stat_activity. The default
therefore shows the driver version to other database users, and the
ApplicationName entry in use.md says so.

Fixes #2404
```

## 2. Title

```text
feat: include driver version in default application_name
```

## 3. Description

```markdown
Fixes #2404.

When a connection leaves `ApplicationName` unset, the driver now sends `PostgreSQL JDBC Driver` followed by a space and the driver version as `application_name`, for example `PostgreSQL JDBC Driver 42.7.14`. Before this change it sent `PostgreSQL JDBC Driver`. With the version in `pg_stat_activity`, you can see which driver version each connection uses. An explicitly set `ApplicationName` is sent unchanged.

## Why

Issue #2404 asks to see the version of the JDBC driver a client uses directly from a view in PostgreSQL. Users I talked to ask the same question about their applications and look for the answer in `pg_stat_activity`.

The new default is `DriverInfo.DRIVER_FULL_NAME`, which is `DRIVER_NAME + " " + DRIVER_VERSION`.

## Compatibility

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. This affects only connections that leave `ApplicationName` unset.
- Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`. The default therefore shows the driver version to other database users.

The `ApplicationName` entry in `docs/content/documentation/use.md` documents the new default and says that other database users can see it. The `CHANGELOG.md` entry is listed first under Changed. It describes the effect on queries that match the old value and links to issue #2404 and PR #4466.

## Not included

I also considered adding the git SHA of the build or the JDK version. I left both out because they add too much to `application_name`. They can be discussed separately.

## Tests

`ApplicationNameTest` adds two tests, and both need a running server:

- `defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName`. It expects `current_setting('application_name')` to return `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. This test fails on `master`, where the value is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and expects `billing`. This test also passes on `master`.
```
