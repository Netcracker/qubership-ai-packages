## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. Commit 2 adds the tests for commit 1's change, and commit 3 rewrites lines that commit 1 added. That leaves one commit:

```text
feat: include the driver version in the default ApplicationName

Previously, a connection that left ApplicationName unset reported
"PostgreSQL JDBC Driver" as its application_name. A database
administrator looking at pg_stat_activity could not tell which driver
version a client used, which issue #2404 asks for.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME:
"PostgreSQL JDBC Driver", a space, and the version of the driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver" followed by the driver version, for example "PostgreSQL JDBC Driver 42.7.14", instead of "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database sees this driver version for every such session in pg_stat_activity.
Not changed:
A connection that sets ApplicationName explicitly reports that value unchanged.

Fixes #2404
```

## 2. Title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Description

```markdown
### Breaking changes

A connection that leaves `ApplicationName` unset now reports `application_name` as `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. In 42.7.13 it reports `PostgreSQL JDBC Driver`. After the upgrade, a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections. Change it to match the `PostgreSQL JDBC Driver ` prefix, or set `ApplicationName` explicitly on the connection.

### User-visible changes

- Any role that can connect to the database sees the driver version for every session that keeps the default, in `pg_stat_activity`. The `ApplicationName` entry in `use.md` now says so.
- Not changed: a connection that sets `ApplicationName` explicitly reports that value unchanged.

### Why

Users want to know which driver version each of their applications uses, and to see it in `pg_stat_activity` on the server. Issue #2404 asks for the same: the JDBC driver version a client uses, readable from a view in PostgreSQL. `application_name` is the column that view already shows for every session.

### What

The default `ApplicationName` changes from `DriverInfo.DRIVER_NAME` to `DriverInfo.DRIVER_FULL_NAME`, which adds the version of the driver jar. The changelog entry is first under Changed because the old default string no longer matches.

### Verification

There are two new tests in `ApplicationNameTest`, and both need a running server. `defaultApplicationNameCarriesTheDriverVersion` reads `current_setting('application_name')` back from a connection without `ApplicationName`. It fails on `master`, where the value is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and reads `billing` back. It passes on `master` too, and it guards the explicit value against this change.

### Scope

The git sha of the build and the JDK version stay out of the default. Adding them can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See "Breaking changes" above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
