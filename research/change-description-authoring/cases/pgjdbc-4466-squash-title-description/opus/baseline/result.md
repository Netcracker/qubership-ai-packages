## 1. Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. One commit remains:

```text
feat: include the driver version in the default application_name

When a connection leaves ApplicationName unset, the driver now sends
"PostgreSQL JDBC Driver" followed by a space and the driver version,
for example "PostgreSQL JDBC Driver 42.7.14". Before, it sent
"PostgreSQL JDBC Driver". Users want to know which driver version
each of their applications uses, and pg_stat_activity shows the
application_name of every session.

A query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' stops finding pgjdbc
connections after the upgrade. A connection that sets ApplicationName
keeps the value it sets.

Any role that can connect to the database can read the
application_name of every session in pg_stat_activity. With the new
default, other database users can see the driver version.

Closes #2404
```

The repository squash-merges, so the commit on `master` takes the title below with ` (#4466)` added, and the description below as its body.

## 2. Title

```text
feat: include the driver version in the default application_name
```

## 3. Description

```markdown
When a connection leaves `ApplicationName` unset, the driver now sends `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Before, it sent `PostgreSQL JDBC Driver`.

Closes #2404

## Why

Users want to know which driver version each of their applications uses, and they look for it in `pg_stat_activity`. Issue #2404 asks for the same thing: the JDBC driver version of a client, visible from a PostgreSQL view.

`PGProperty.APPLICATION_NAME` now defaults to `DriverInfo.DRIVER_FULL_NAME`, which is `DRIVER_NAME + " " + DRIVER_VERSION`.

I also considered adding the git SHA of the build or the JDK version, but left them out as too much. They can be discussed separately.

## Upgrade impact

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding pgjdbc connections after the upgrade. The `CHANGELOG.md` entry says so and comes first under Changed.
- A connection that sets `ApplicationName` keeps the value it sets.
- Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`. With the new default, other database users can see the driver version. `docs/content/documentation/use.md` says so under `ApplicationName`.

## Tests

`ApplicationNameTest` needs a running server:

- `defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName`, then expects `current_setting('application_name')` to be `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. It fails on `master`, where the value is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and reads back `billing`. It passes on `master` too.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes, for anything that matches the old default `application_name`. See "Upgrade impact" above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
