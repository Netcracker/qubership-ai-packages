## 1. Commits

Squash `add tests` and `Apply suggestion from @vlsi` into `feat: Include driver version in default application_name`. The branch then has one commit, with this message:

```text
feat: include the driver version in the default ApplicationName

When ApplicationName was not set, the driver sent "PostgreSQL JDBC
Driver" as application_name at startup. Every pgjdbc connection looked
the same in pg_stat_activity, so a database administrator could not
tell which driver version a client used. Users asked to see the driver
version from a view in PostgreSQL (#2404).

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver" followed by a space and the version of the driver jar.

User-visible:
Breaking: a connection that leaves ApplicationName unset reports application_name `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver`, so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds it; set ApplicationName explicitly to keep a fixed value.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so it now sees the driver version of connections that use the default.
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
### Breaking changes

This changes the default of `ApplicationName`, and 42.7.14 is not a major release. Only connections that leave `ApplicationName` unset are affected.

* A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` rather than `PostgreSQL JDBC Driver`, as in 42.7.13 and earlier. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. To keep a fixed value, set `ApplicationName` explicitly.

### Why

With `ApplicationName` unset, every pgjdbc connection showed the same `application_name` in `pg_stat_activity`, so nobody could tell from the database which driver version a client was running. #2404 asks for exactly that, and users I talked to asked for the same thing.

### What

The default is now `DriverInfo.DRIVER_FULL_NAME`: `PostgreSQL JDBC Driver`, then a space, then the version of the driver jar. `CHANGELOG.md` lists the entry first under Changed and links #2404 and #4466. The `ApplicationName` entry in `use.md` gives the new default.

### User-visible changes

* Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users now see the driver version of connections that use the default.
* Not changed: an explicitly set `ApplicationName` is sent as given.

### Verification

`ApplicationNameTest` is new, and both of its tests need a running server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` passes on `master` too, and it checks that an explicit `ApplicationName` stays as set.

### Scope

Fixes #2404. The git sha of the build and the JDK version are left out of the default; they can be discussed separately.

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
