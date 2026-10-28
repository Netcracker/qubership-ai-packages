### 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) folds into commit 1, since it corrects commit 1's `CHANGELOG.md` and `use.md` changes. Commit 2 stays as its own commit because it adds tests, not a correction.

```text
feat: include the driver version in the default ApplicationName

A connection that leaves ApplicationName unset sent the constant
`PostgreSQL JDBC Driver` as its application_name, so pg_stat_activity
could not show which driver version a connection uses. Issue #2404 asks
for that version to be visible from a view in PostgreSQL.

The default is now `PostgreSQL JDBC Driver` followed by a space and the
driver version. Adding the git sha of the build or the JDK version was
considered and left out as too much; it can be discussed separately.

User-visible:
Breaking: a connection that leaves ApplicationName unset sends
`PostgreSQL JDBC Driver 42.7.14` in place of `PostgreSQL JDBC Driver`.
Releases up to 42.7.13 send the old value. A query that matches
application_name = 'PostgreSQL JDBC Driver' no longer finds those
connections; match 'PostgreSQL JDBC Driver%' instead, or set
ApplicationName explicitly.
Any role that can connect to the database reads application_name of
every session in pg_stat_activity, so the default shows the driver
version to other database users.

Not changed:
A connection that sets ApplicationName sends that value unchanged.

Closes #2404
```

```text
test: cover the default and an explicit ApplicationName

The default ApplicationName had no test, so a change to its value
would pass unnoticed. ApplicationNameTest reads the value back with
current_setting('application_name') for a connection that leaves
ApplicationName unset and for one that sets it to billing.

Part of #2404.
```

### 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

### 3. Pull request description

```markdown
This change breaks code that matches the default `application_name`.

User-visible:

- Breaking: a connection that leaves `ApplicationName` unset now sends `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Releases up to 42.7.13 send `PostgreSQL JDBC Driver`. A query that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds those connections. Match `PostgreSQL JDBC Driver%` instead, or set `ApplicationName` explicitly.
- Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. The `use.md` page now says so.

Users who want to know which driver version their applications use cannot see it in `pg_stat_activity`. A connection that leaves `ApplicationName` unset shows `PostgreSQL JDBC Driver` for every driver version. Issue #2404 asks for that version to be visible from a view in PostgreSQL.

The default is now `PostgreSQL JDBC Driver` followed by a space and the driver version. Adding the git sha of the build or the JDK version was considered and left out as too much. It can be discussed separately.

Not changed: an explicitly set `ApplicationName` is sent unchanged.

Verification: `ApplicationNameTest.explicitApplicationNameIsKept` passes without this change, because it pins the explicit value, which the change does not touch.

Closes #2404
```
