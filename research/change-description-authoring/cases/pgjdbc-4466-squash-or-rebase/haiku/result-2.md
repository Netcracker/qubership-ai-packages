## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) is folded into commit 1, because its edits to `CHANGELOG.md` and `use.md` change lines that commit 1 adds. Commit 2 stays as its own commit, with a new subject and body.

Commit 1:

```text
feat: include the driver version in the default ApplicationName

The default ApplicationName, "PostgreSQL JDBC Driver", names the driver
but not its version, so pg_stat_activity cannot show which driver
version a connection uses. Users want to see which driver version each
application uses (issue #2404).

The default now comes from DriverInfo.DRIVER_FULL_NAME, which is the
driver name and the driver version.

User-visible:
A connection that leaves ApplicationName unset sends
"PostgreSQL JDBC Driver X.Y.Z" instead of "PostgreSQL JDBC Driver".
A query that matches application_name = 'PostgreSQL JDBC Driver' no
longer finds those connections; match the prefix instead, or set
ApplicationName to a fixed value.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

Commit 2:

```text
test: cover the default and explicit ApplicationName

Add ApplicationNameTest for the default value, which carries the driver
version, and for an explicit ApplicationName, which must be kept as
given.
```

## 2. Pull request title

`feat: include the driver version in the default ApplicationName`

## 3. Pull request description

```markdown
### Breaking changes

Code that matches the default `ApplicationName` by its whole value stops finding pgjdbc connections in 42.7.14, the next release. It worked in 42.7.13, the latest release.

- A connection that leaves `ApplicationName` unset now sends `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.13`, instead of `PostgreSQL JDBC Driver`. A query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds those connections. Match the prefix `PostgreSQL JDBC Driver` instead, or set `ApplicationName` to a fixed value.

Not changed: an explicitly set `ApplicationName` is sent as given.

### Why

Users want to see which driver version each application uses. `pg_stat_activity` shows the default `ApplicationName`, which names the driver but not its version. Fixes #2404, which asks for the version to be readable from a view in PostgreSQL.

### What

The default now comes from `DriverInfo.DRIVER_FULL_NAME`, the driver name followed by the driver version. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users also see the driver version. `use.md` now says so.

### Verification

`ApplicationNameTest.explicitApplicationNameIsKept` passes without this change: it pins the explicit value, which must not move. Both tests in `ApplicationNameTest` need a running PostgreSQL server.

### Scope

The git sha of the build and the JDK version are left out as too much. Either can be discussed separately.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [ ] Does this break existing behaviour? If so please explain.
* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
* [ ] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
