## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch then has a single commit:

```text
feat: include the driver version in the default ApplicationName

Every connection that left ApplicationName unset sent the same
application_name, "PostgreSQL JDBC Driver". As a result,
pg_stat_activity could not show which driver version a client used.
Users asked to read that version directly from a PostgreSQL view, and
administrators asked which driver version their applications run.

The default is now "PostgreSQL JDBC Driver" followed by a space and the
version of the driver jar. The git sha of the build and the JDK version
are left out of the default.

User-visible:
Breaking: with ApplicationName unset, application_name is "PostgreSQL JDBC Driver 42.7.14" instead of "PostgreSQL JDBC Driver". A query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc connections. Set ApplicationName=PostgreSQL JDBC Driver to keep the old value.
Any role that can connect to the database reads the application_name of every session in pg_stat_activity. That role now also sees the driver version of every pgjdbc connection that uses the default.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
Connections that leave `ApplicationName` unset now send `PostgreSQL JDBC Driver 42.7.14` as `application_name` instead of `PostgreSQL JDBC Driver`. After an upgrade from 42.7.13, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. Set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

Every connection that used the default sent the same `application_name`. As a result, `pg_stat_activity` could not show which driver version a client used. #2404 asks to read that version directly from a PostgreSQL view, and users have asked which driver version their applications run.

The default is now `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. The git sha of the build and the JDK version are left out of the default and can be discussed separately.

User-visible:
Any role that can connect to the database reads the `application_name` of every session in `pg_stat_activity`. That role now also sees the driver version of every pgjdbc connection that uses the default.

Not changed:
An explicitly set `ApplicationName` is sent as given. `explicitApplicationNameIsKept` also passes on `master`, so it guards that this value stays the same.

Fixes #2404
```
