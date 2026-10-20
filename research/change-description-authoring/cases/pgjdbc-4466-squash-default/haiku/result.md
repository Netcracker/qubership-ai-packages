## 1. Commits

Commits 2 and 3 fold into commit 1, so the branch merges as one commit. A one-commit pull request under GitHub's default squash setting takes that commit's subject and body, so this message is the one that lands in `git log`.

```text
feat: include driver version in default ApplicationName

Before this change, a connection that left ApplicationName unset sent
the application_name "PostgreSQL JDBC Driver" whatever driver version
it ran. pg_stat_activity therefore could not show the version, which
issue #2404 asks for.

The default is now DriverInfo.DRIVER_FULL_NAME, which is
"PostgreSQL JDBC Driver", a space, and the version of the driver jar,
for example "PostgreSQL JDBC Driver 42.7.14". An explicitly set
ApplicationName is sent as it is.

User-visible:
A connection that leaves ApplicationName unset reports application_name
"PostgreSQL JDBC Driver X.Y.Z" instead of "PostgreSQL JDBC Driver". A
query that matches the old value with = no longer finds it. Match with
LIKE 'PostgreSQL JDBC Driver%', or set ApplicationName explicitly to
keep the old value.
Any role that can connect reads application_name for every session in
pg_stat_activity, so the version is visible to other database users.

Not changed:
A connection that sets ApplicationName keeps the value it sets.

Fixes #2404
```

## 2. Pull request title

feat: include driver version in default ApplicationName

## 3. Pull request description

```markdown
This breaks code that matches the default `ApplicationName` by exact value. A query or dashboard that filters `pg_stat_activity` on `application_name = 'PostgreSQL JDBC Driver'` no longer finds connections that leave `ApplicationName` unset, because their value is now `PostgreSQL JDBC Driver X.Y.Z`. Match both values with `LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName` explicitly to keep the old value. The next release from `master` is 42.7.14 (see `gradle.properties`), which is not a major release, so the break comes first.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

Two new tests in `ApplicationNameTest` need a running server. `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the default value is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` passes on `master` too. It guards the explicit value, which this change keeps.

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

Every connection that leaves `ApplicationName` unset reports `PostgreSQL JDBC Driver`, so `pg_stat_activity` cannot show which driver version a connection uses. Issue #2404 asks for exactly that: the driver version visible from a view in PostgreSQL. Fixes #2404.

The default is now `DriverInfo.DRIVER_FULL_NAME`, which is `PostgreSQL JDBC Driver`, a space, and the version of the driver jar. An explicitly set `ApplicationName` is sent as it is.

User-visible:
Any role that can connect to the database reads `application_name` for every session in `pg_stat_activity`, so the driver version is visible to other database users, not only to the application operator.

Not changed:
A connection that sets `ApplicationName` keeps the value it sets.

Scope: The git sha of the build and the JDK version were also considered and left out as too much. They can be discussed separately.

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
