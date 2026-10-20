## 1. Commits

Commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) fold into commit 1, which is the only commit that remains:

```text
feat: append the driver version to the default ApplicationName

Previously the default ApplicationName was "PostgreSQL JDBC Driver" for
every driver version, so pg_stat_activity could not show which driver
version a connection uses. This is a behavior change, not a fix.

The default is now DriverInfo.DRIVER_FULL_NAME, which is DRIVER_NAME, a
space, and DRIVER_VERSION, for example "PostgreSQL JDBC Driver 42.7.14".

User-visible:
Breaking: a connection that leaves ApplicationName unset sends
"PostgreSQL JDBC Driver X.Y.Z" as application_name instead of
"PostgreSQL JDBC Driver". A query that matches the old value stops
finding those connections. Match application_name LIKE
'PostgreSQL JDBC Driver%', or set ApplicationName explicitly.
Any role that can connect reads application_name of every session in
pg_stat_activity, so other database users now see the driver version.

Not changed:
An explicitly set ApplicationName is sent unchanged.

Fixes #2404
```

## 2. Pull request title

```text
feat: append the driver version to the default ApplicationName
```

## 3. Pull request description

```markdown
### Changes to Existing Features:

This changes the default `ApplicationName`, so code that matches the old value stops finding pgjdbc connections. The next release from `master` is 42.7.14, per `gradle.properties`.

#### Breaking changes

Connections that leave `ApplicationName` unset now send `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.14`, as `application_name` instead of `PostgreSQL JDBC Driver`. A query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. To keep finding them, match `application_name LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName` to `PostgreSQL JDBC Driver` to keep the old value.

#### Why

Users want to know which driver version their applications use, as seen in `pg_stat_activity`. The default `ApplicationName` was the same string for every driver version, so the view could not show it. This implements what #2404 asks for.

#### What

The default is now `DriverInfo.DRIVER_FULL_NAME`, which is `DRIVER_NAME`, a space, and `DRIVER_VERSION`.

#### User-visible changes

* Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users now see the driver version of each connection that leaves `ApplicationName` unset.
* Not changed: an explicitly set `ApplicationName` is sent as set.

#### Verification

Two new tests in `ApplicationNameTest` need a running PostgreSQL server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the default is `PostgreSQL JDBC Driver`, so it covers the new default. `explicitApplicationNameIsKept` passes on `master` as well, and guards the explicit value, which must not change.

#### Scope

Adding the git sha of the build or the JDK version to the default was considered and left out as too much. It can be discussed separately.

* [ ] Does this break existing behaviour? If so please explain.
* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
* [ ] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?
```
