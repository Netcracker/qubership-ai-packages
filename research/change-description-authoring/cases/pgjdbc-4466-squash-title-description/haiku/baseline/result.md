### 1. Commits

Commits 2 and 3 fold into commit 1, which is the only commit that remains. The tests and the review fixes describe the same change, and the squash merge puts one commit on `master` either way.

```text
feat: include the driver version in the default ApplicationName

The default `ApplicationName` now includes the driver version. Connections that leave `ApplicationName` unset show the version in `pg_stat_activity`. A connection that sets `ApplicationName` keeps its value.

## Why

Users want to know which driver version their applications use. Issue #2404 requests a PostgreSQL view that shows it. This change puts the version in the `application_name` that the driver sends at startup, so `pg_stat_activity` shows it.

I considered adding the git SHA of the build and the JDK version too. I left them out as too much for this change. They can be discussed separately.

## What changes

* The default is `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`.
* `DriverInfo.DRIVER_FULL_NAME` is `DRIVER_NAME + " " + DRIVER_VERSION`, and `PGProperty.APPLICATION_NAME` uses it as its default.
* `use.md` documents the new default and says that other database users can read it.

## Compatibility

This changes behavior for code that matches the old default. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade.

The version is also visible to other database users. Any role that can connect can read `application_name` for every session in `pg_stat_activity`.

## Tests

`ApplicationNameTest` needs a running PostgreSQL server and has two tests.

* `defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName`. It reads `current_setting('application_name')` and expects `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. On master the test fails, because the value there is `PostgreSQL JDBC Driver`.
* `explicitApplicationNameIsKept` connects with `ApplicationName=billing`, reads the value back, and expects `billing`. It passes on master too.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes, see Compatibility above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```

### 2. Pull request title

`feat: include the driver version in the default ApplicationName`

### 3. Pull request description

```markdown
The default `ApplicationName` now includes the driver version. Connections that leave `ApplicationName` unset show the version in `pg_stat_activity`. A connection that sets `ApplicationName` keeps its value.

## Why

Users want to know which driver version their applications use. Issue #2404 requests a PostgreSQL view that shows it. This change puts the version in the `application_name` that the driver sends at startup, so `pg_stat_activity` shows it.

I considered adding the git SHA of the build and the JDK version too. I left them out as too much for this change. They can be discussed separately.

## What changes

* The default is `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`.
* `DriverInfo.DRIVER_FULL_NAME` is `DRIVER_NAME + " " + DRIVER_VERSION`, and `PGProperty.APPLICATION_NAME` uses it as its default.
* `use.md` documents the new default and says that other database users can read it.

## Compatibility

This changes behavior for code that matches the old default. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade.

The version is also visible to other database users. Any role that can connect can read `application_name` for every session in `pg_stat_activity`.

## Tests

`ApplicationNameTest` needs a running PostgreSQL server and has two tests.

* `defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName`. It reads `current_setting('application_name')` and expects `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. On master the test fails, because the value there is `PostgreSQL JDBC Driver`.
* `explicitApplicationNameIsKept` connects with `ApplicationName=billing`, reads the value back, and expects `billing`. It passes on master too.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. Yes, see Compatibility above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
