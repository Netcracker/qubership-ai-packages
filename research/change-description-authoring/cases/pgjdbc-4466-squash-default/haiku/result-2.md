**1. Commits**

The pull request merges as a squash, so the history keeps one commit. Commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) fold into commit 1: the tests belong to the change, and commit 3 corrects commit 1's changelog and `use.md` lines. Folded in, the squash message is this single commit's message.

```text
feat: include the driver version in the default application_name

Connections that leave ApplicationName unset all send
"PostgreSQL JDBC Driver", so pg_stat_activity cannot show which driver
version each one uses. Issue #2404 asks for that view.

The default is now the driver name, a space, and the version of the
driver jar, built from DriverInfo.DRIVER_FULL_NAME. An explicitly set
ApplicationName is sent unchanged. The build's git SHA and the JDK
version were left out to keep the value short; they can be discussed
separately.

User-visible:
A query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds connections that leave ApplicationName unset. Match the new value, which starts with that name, or set ApplicationName explicitly to keep the old value.
Connections that leave ApplicationName unset send "PostgreSQL JDBC Driver X.Y.Z" as application_name, for example "PostgreSQL JDBC Driver 42.7.14".
Any role that can connect to the database can read application_name of every session in pg_stat_activity, so those roles see the driver version too.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

**2. Pull request title**

```text
feat: include the driver version in the default application_name
```

**3. Pull request description**

```markdown
### Breaking changes

A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds the connections that leave `ApplicationName` unset. Match the new value, which starts with `PostgreSQL JDBC Driver`, or set `ApplicationName` explicitly to keep the old value.

### Changes to Existing Features:

Connections that leave `ApplicationName` unset all send `PostgreSQL JDBC Driver`, so `pg_stat_activity` cannot show which driver version each one uses. Issue #2404 asks for that view. This change came out of conversations with users who want to know which driver version their applications use.

Fixes #2404

The default is now the driver name, a space, and the version of the driver jar, built from `DriverInfo.DRIVER_FULL_NAME`. An explicitly set `ApplicationName` is sent unchanged.

User-visible changes:

* Connections that leave `ApplicationName` unset send `PostgreSQL JDBC Driver X.Y.Z` as their `application_name`, for example `PostgreSQL JDBC Driver 42.7.14`.
* Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so those roles see the driver version too.

Not changed: an explicitly set `ApplicationName` is sent as given.

Scope: the build's git SHA and the JDK version were considered and left out to keep the value short. They can be discussed separately.

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

### New Feature Submissions:

`ApplicationNameTest` adds two tests, and both need a running PostgreSQL server. `defaultApplicationNameCarriesTheDriverVersion` fails on master, where the default is `PostgreSQL JDBC Driver`, so it is the regression test for this change. `explicitApplicationNameIsKept` passes on master and guards that an explicit value is kept.

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?
```
