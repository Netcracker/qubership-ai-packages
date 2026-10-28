### 1. Commits

Commits 2 and 3 fold into commit 1, so the branch merges as one commit. Commit 3 (`Apply suggestion from @vlsi`) corrects commit 1's changelog line and `use.md`. Commit 2 (`add tests`) belongs to the same change and would otherwise land as a stub with no message of its own.

```text
feat: include the driver version in the default ApplicationName

The default ApplicationName was the constant "PostgreSQL JDBC Driver", so a
connection that left it unset showed the driver name in pg_stat_activity and
no version. Users want to see which driver version their applications use,
and #2404 asks for the same thing.

The default is now the driver's full name, DriverInfo.DRIVER_FULL_NAME: the
driver name, a space, and the version of the driver jar.

User-visible:
Connections that leave ApplicationName unset send "PostgreSQL JDBC Driver X.Y.Z" instead of "PostgreSQL JDBC Driver", for example "PostgreSQL JDBC Driver 42.7.14", and releases up to REL42.7.13 send the old value.
A query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds those connections; match the prefix, or set ApplicationName=PostgreSQL JDBC Driver to keep the old value.
Any role that can connect to the database reads that value in pg_stat_activity for each session that leaves ApplicationName unset.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

### 2. Pull request title

`feat: include the driver version in the default ApplicationName`

### 3. Pull request description

```markdown
The default `ApplicationName` now includes the driver version. Code that matches the old default, `PostgreSQL JDBC Driver`, stops finding pgjdbc connections after the upgrade. `master` is at 42.7.14 in `gradle.properties`, which is not a major release.

### Breaking changes

* Connections that leave `ApplicationName` unset send `PostgreSQL JDBC Driver X.Y.Z` instead of `PostgreSQL JDBC Driver`, for example `PostgreSQL JDBC Driver 42.7.14`. Releases up to REL42.7.13 send the old value.
* A query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the prefix instead, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Why

Users want to see which driver version their applications use, as seen in `pg_stat_activity`. The default was the constant `PostgreSQL JDBC Driver`, which shows no version. Issue #2404 asks for exactly this: the driver version visible from a view in PostgreSQL.

Fixes #2404.

### What

The default is the driver's full name: `PostgreSQL JDBC Driver`, a space, and the version of the driver jar.

### User-visible changes

* Any role that can connect to the database reads that value in `pg_stat_activity` for each session that leaves `ApplicationName` unset, so the driver version is visible to other database users.

Not changed: an explicitly set `ApplicationName` is sent as given.

### Verification

* `explicitApplicationNameIsKept` passes without the change. It pins the path where the caller sets `ApplicationName`, which must not move.
* Both tests in `ApplicationNameTest` need a running server.

### Scope

* The git sha of the build and the JDK version are left out of the default name. They can be discussed separately.

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?
```
