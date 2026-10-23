## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) is folded into commit 1. Its changes to `CHANGELOG.md` and `use.md` belong to the same change, and its subject does not describe them. Commit 2 stays as its own commit, with a Conventional Commits subject and a body that states the test results.

Commit 1:

```text
feat: include driver version in default ApplicationName

Users want to know which driver version their applications use.
pg_stat_activity shows application_name for each connection, so the
default ApplicationName now includes the driver version there.

The default is DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC Driver",
a space, and the driver version, for example "PostgreSQL JDBC Driver
42.7.14". Previously the default was "PostgreSQL JDBC Driver". A
connection that sets ApplicationName is unaffected.

Code that matches the old default, such as
application_name = 'PostgreSQL JDBC Driver', no longer matches the
connections that use the default.

Fixes #2404
```

Commit 2:

```text
test: cover the default and explicit ApplicationName

Add ApplicationNameTest with two tests. Both need a running server.
defaultApplicationNameCarriesTheDriverVersion connects without setting
ApplicationName and checks that current_setting('application_name')
returns "PostgreSQL JDBC Driver " followed by DriverInfo.DRIVER_VERSION.
explicitApplicationNameIsKept connects with ApplicationName=billing and
checks that the value is billing.

On master the default is "PostgreSQL JDBC Driver", so the first test
fails there and the second passes.
```

## 2. Pull request title

```text
feat: include driver version in default ApplicationName
```

## 3. Pull request description

```markdown
The default `ApplicationName` now includes the driver version, so `pg_stat_activity` shows which driver version each connection uses. Fixes #2404.

### Why

Users want to know which driver version their applications use. The git SHA of the build and the JDK version were also considered and left out, as too much for this change. They can be discussed separately.

### What changes for users

A connection that leaves `ApplicationName` unset now sends `PostgreSQL JDBC Driver <version>` instead of `PostgreSQL JDBC Driver`. A connection that sets `ApplicationName` keeps the value it sets.

Queries and dashboards that match `application_name = 'PostgreSQL JDBC Driver'` stop finding those connections after the upgrade.

Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`, so the default version is visible to other database users. `docs/content/documentation/use.md` says so.

### Tests

Both tests are in `ApplicationNameTest`, and both need a running server.

| Test | Connects with | Checks | Fails on master |
| --- | --- | --- | --- |
| `defaultApplicationNameCarriesTheDriverVersion` | no `ApplicationName` | `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION` | yes |
| `explicitApplicationNameIsKept` | `ApplicationName=billing` | `billing` | no |

### Changelog and docs

`CHANGELOG.md` has a `Changed` entry, listed first, that names the query break and links #2404 and #4466. `docs/content/documentation/use.md` shows the new default and says that other database users can see it.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
