## Commits

Commit 3, "Apply suggestion from @vlsi", is folded into commit 1, since it only corrects commit 1's `CHANGELOG.md` and `use.md` text. Commit 2 stays as its own commit. Two commits remain, in this order.

### Commit 1

```text
feat: add the driver version to the default ApplicationName

Users want to know which driver version their applications use, and
issue #2404 asks for that to be visible from a view in PostgreSQL.
Without ApplicationName set, the driver sends the fixed string
"PostgreSQL JDBC Driver", so pg_stat_activity does not show the
version. This adds information and fixes no defect.

The default now reuses DriverInfo.DRIVER_FULL_NAME, the driver name
followed by a space and the version, in place of DRIVER_NAME.

User-visible:
Breaking: when ApplicationName is not set, application_name is "PostgreSQL JDBC Driver X.Y.Z" (X.Y.Z is the driver version) instead of "PostgreSQL JDBC Driver". A query that matches application_name = 'PostgreSQL JDBC Driver' stops finding those connections. Set ApplicationName to a value the query matches.
Any role that can connect to the database can read application_name for every session in pg_stat_activity, so the version is visible to other database users.
Not changed: an explicitly set ApplicationName is sent as given.

Fixes #2404
```

### Commit 2

```text
test: cover the default and explicit ApplicationName

The default ApplicationName now carries the driver version, and an
explicit ApplicationName is sent as given. Both tests need a running
server.

Refs #2404
```

## Pull request title

```text
feat: add the driver version to the default ApplicationName
```

## Pull request description

```markdown
User-visible:
Breaking: when `ApplicationName` is not set, the driver now sends `PostgreSQL JDBC Driver X.Y.Z` as `application_name`, where X.Y.Z is the driver version, instead of `PostgreSQL JDBC Driver`. A query that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. The change ships in 42.7.14, the next release. Set `ApplicationName` to a value the query matches.
Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`, so the version is visible to other database users.
Not changed: an explicitly set `ApplicationName` is sent as given.

Users want to know which driver version their applications use, and issue #2404 asks for that to be visible from a view in PostgreSQL. Without `ApplicationName` set, the driver sends the fixed string `PostgreSQL JDBC Driver`, so `pg_stat_activity` does not show the version. This adds information and fixes no defect.

The default now reuses `DriverInfo.DRIVER_FULL_NAME`, the driver name followed by a space and the version, in place of `DRIVER_NAME`. The build's git sha and the JDK version were left out as too much for this change; they can be discussed separately.

`ApplicationNameTest` adds two tests, which need a running server: `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, and `explicitApplicationNameIsKept` passes there too.

Fixes #2404
```
