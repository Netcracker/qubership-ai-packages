## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch then has one commit. A squash of a single-commit pull request keeps that commit's subject and body and appends `(#4466)`, so `git log` gets this message rather than `add tests` and `Apply suggestion from @vlsi` as bullets.

Message of the remaining commit:

```text
feat: include the driver version in the default ApplicationName

When ApplicationName was not set, the driver sent the fixed string
"PostgreSQL JDBC Driver" as application_name at startup. Every pgjdbc
connection looked the same in pg_stat_activity, so users could not see
from the server which driver version each application used (#2404).

The default is now "PostgreSQL JDBC Driver" followed by a space and the
version of the driver jar. The git sha of the build and the JDK version
were left out as too much for the default.

User-visible:
A connection that leaves ApplicationName unset reports application_name
"PostgreSQL JDBC Driver <version>", for example "PostgreSQL JDBC Driver
42.7.14", instead of "PostgreSQL JDBC Driver". A query or dashboard that
matches application_name = 'PostgreSQL JDBC Driver' no longer finds
these connections.
Any role that can connect to the database reads application_name of
every session in pg_stat_activity, so the default shows the driver
version to other database users.
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
### Breaking changes

A connection that leaves `ApplicationName` unset now reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Up to 42.7.13 it reported `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. Match on the `PostgreSQL JDBC Driver` prefix instead, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Changes to Existing Features

Users want to know which driver version their applications use, as seen in `pg_stat_activity` (#2404). Until now the default `application_name` was the same string for every driver version, so the server could not show it.

Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. An explicitly set `ApplicationName` is sent as given.

`explicitApplicationNameIsKept` also passes on `master`. It checks the explicit value, which the change must not alter.

**Scope.** The git sha of the build and the JDK version are not added to the default. They can be discussed separately.

Fixes #2404

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?
```
