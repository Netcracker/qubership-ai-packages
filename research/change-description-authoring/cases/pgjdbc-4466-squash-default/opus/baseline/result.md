## Commits

Fold `add tests` and `Apply suggestion from @vlsi` into `feat: Include driver version in default application_name`. The branch then has one commit:

```text
feat: include the driver version in the default application_name

Users want to know which driver version each of their applications
uses, and pg_stat_activity is where they look (issue #2404). Before
this change, every driver version sent the same default
application_name, "PostgreSQL JDBC Driver", so the view could not
show the version.

The default is now "PostgreSQL JDBC Driver" followed by a space and
the version of the driver jar, for example
"PostgreSQL JDBC Driver 42.7.14". A connection that sets
ApplicationName still sends the value it sets.

A query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' stops finding pgjdbc
connections that leave ApplicationName unset. Any role that can
connect to the database can read the application_name of every
session in pg_stat_activity. Other database users can therefore see
the driver version. The changelog entry and the ApplicationName entry
in use.md describe both effects.

ApplicationNameTest checks the default value and an explicitly set
value against a running server.

Closes #2404
```

## Title

```text
feat: include the driver version in the default application_name
```

## Description

```markdown
The default `ApplicationName` now includes the driver version: `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`. You can now see which pgjdbc version each connection uses in `pg_stat_activity`.

Closes #2404

### Why

Users have asked which driver version their applications use, and `pg_stat_activity` is where they look. Issue #2404 asks for the same thing. Before this change, every release sent the same default, so the view could not show the version.

### What changes

- `PGProperty.APPLICATION_NAME` defaults to `DriverInfo.DRIVER_FULL_NAME`. Its value is `PostgreSQL JDBC Driver`, a space, and the version of the driver jar.
- A connection that sets `ApplicationName` still sends the value it sets.
- The `ApplicationName` entry in `docs/content/documentation/use.md` documents the new default. It also says that the default shows the driver version to other database users.
- `CHANGELOG.md` has the entry first under "Changed", with links to issue #2404 and PR #4466.

### Behavior change

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections that leave `ApplicationName` unset. Connections that set `ApplicationName` are not affected.
- Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`. With this change, those roles can also see the driver version of every connection that uses the default.

### Tests

`ApplicationNameTest` adds two tests. Both need a running server:

- `defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName`. It expects `current_setting('application_name')` to return `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. This test fails on `master`, which returns `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and expects `billing`. This test also passes on `master`.

### Not included

The default could also carry the git SHA of the build or the JDK version. I left both out because they add too much to the name. We can discuss them in a separate issue.

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes for queries that match the old default string; see "Behavior change".
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
```
