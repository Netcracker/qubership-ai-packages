## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The branch merges as one commit:

```text
feat: include the driver version in the default application_name

Previously a connection that left ApplicationName unset reported
application_name as "PostgreSQL JDBC Driver". A database administrator
looking at pg_stat_activity could not tell which driver version each
application used. Issue #2404 asks for the version of the JDBC driver
to be visible from a PostgreSQL view.

The default ApplicationName is now DriverInfo.DRIVER_FULL_NAME, which
is the driver name followed by a space and the version of the driver
jar. The git sha of the build and the JDK version are not added.

User-visible:
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver 42.7.14" (the version of the driver jar) instead of "PostgreSQL JDBC Driver", so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so other database users see the driver version of connections that leave ApplicationName unset.
Not changed:
An explicitly set ApplicationName is sent as given.

Closes #2404
```

## 2. Title

```text
feat: include the driver version in the default application_name
```

## 3. Description

```markdown
### Breaking changes

After the upgrade, code that finds pgjdbc connections by the exact default `application_name` no longer matches them.

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` (the version of the driver jar) instead of `PostgreSQL JDBC Driver`, the value through 42.7.13. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the `PostgreSQL JDBC Driver` prefix instead, or set `ApplicationName` explicitly.

### Why

Users want to see in `pg_stat_activity` which driver version their applications use, and #2404 asks for the version of the JDBC driver to be visible from a PostgreSQL view. The default `application_name` named the driver but not its version.

### What

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver name followed by a space and the version of the driver jar.

### User-visible changes

- Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users now see the driver version of connections that leave `ApplicationName` unset. The `ApplicationName` entry in `docs/content/documentation/use.md` now says this.
- An explicitly set `ApplicationName` is sent as given.

### Verification

`ApplicationName` has a new test class, `ApplicationNameTest`, whose two tests need a running server. `defaultApplicationNameCarriesTheDriverVersion` reads the default back from `current_setting('application_name')`. It fails on `master`, where the value is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` checks that `ApplicationName=billing` stays `billing`, and it passes on `master` too.

### Scope

Closes #2404. The git sha of the build and the JDK version are left out of the default because they would add too much. They can be discussed separately.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes, see "Breaking changes" above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
