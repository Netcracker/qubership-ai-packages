## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. That leaves one commit, and GitHub's default squash keeps its subject and body and appends `(#4466)`. The full message:

```text
feat: include the driver version in the default ApplicationName

Every connection that left ApplicationName unset sent the same
application_name, "PostgreSQL JDBC Driver". So pg_stat_activity could
not show which driver version a client used. Issue #2404 asks to see
that version from a PostgreSQL view, and users who track which driver
version their applications run asked for the same.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME. That is
DriverInfo.DRIVER_NAME followed by a space and the version of the
driver jar.

User-visible:
A connection that leaves ApplicationName unset reports application_name "PostgreSQL JDBC Driver <version>", for example "PostgreSQL JDBC Driver 42.7.14", instead of "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads the application_name of every session in pg_stat_activity, so the default shows the driver version to other database users.
Not changed:
A connection that sets ApplicationName explicitly sends that value as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
## Breaking changes

This breaks code that finds pgjdbc connections by the exact default `application_name`:

- A connection that leaves `ApplicationName` unset reports `PostgreSQL JDBC Driver 42.7.14` in `application_name`. Up to 42.7.13 it reported `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. To keep a fixed value, set `ApplicationName` explicitly.

## Why

Every pgjdbc connection that leaves `ApplicationName` unset looks the same in `pg_stat_activity`. A database administrator can't tell from the server which driver version a client uses. #2404 asks for exactly this, and users who track which driver version their applications run have asked for it too.

## What

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, a space, and the version of the driver jar. The `ApplicationName` entry in `docs/content/documentation/use.md` and the `CHANGELOG.md` entry under Changed describe the new default and the compatibility impact.

## User-visible changes

- Any role that can connect to the database reads the `application_name` of every session in `pg_stat_activity`. So the default shows the driver version to other database users.
- Not changed: a connection that sets `ApplicationName` explicitly, for example `ApplicationName=billing`, sends that value as given.

## How to verify

`ApplicationNameTest.explicitApplicationNameIsKept` passes on `master` too, because it checks the explicit value that this change must not affect. Both tests in `ApplicationNameTest` need a running server.

## Scope

The git sha of the build and the JDK version are not added to the default. That can be discussed separately.

Fixes #2404.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes: see "Breaking changes" above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
