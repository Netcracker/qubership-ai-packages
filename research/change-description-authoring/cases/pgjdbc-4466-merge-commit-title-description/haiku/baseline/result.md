## 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) is folded into commit 1. It only fixes the changelog entry and the `use.md` sentence that belong to the feature. Commit 2 stays as its own commit, with a Conventional Commits subject and a body.

Commit 1:

```text
feat: include the driver version in the default application_name

Users want to know which driver version their applications run. The
driver sends application_name to the server at startup, and
pg_stat_activity shows it for each connection. Before this change the
default was "PostgreSQL JDBC Driver", which carries no version.

The default is now "PostgreSQL JDBC Driver X.Y.Z", where X.Y.Z is the
version of the driver jar, for example "PostgreSQL JDBC Driver 42.7.13".
An ApplicationName set explicitly is not changed.

Any role that can connect to the database can read application_name of
every session in pg_stat_activity, so the default also shows the driver
version to other database users. A query that matches
application_name = 'PostgreSQL JDBC Driver' stops finding connections
that use the default.

Refs: #2404
```

Commit 2:

```text
test: check the default and an explicit ApplicationName

Add ApplicationNameTest, which needs a running server.
defaultApplicationNameCarriesTheDriverVersion connects without setting
ApplicationName and reads current_setting('application_name'), which
must be "PostgreSQL JDBC Driver " followed by DriverInfo.DRIVER_VERSION.
explicitApplicationNameIsKept connects with ApplicationName=billing and
reads billing back.

Without the previous commit, the default is "PostgreSQL JDBC Driver",
so defaultApplicationNameCarriesTheDriverVersion fails. The explicit
name test passes with or without it.
```

## 2. Title

`feat: include the driver version in the default application_name`

## 3. Description

````markdown
## Why

Users want to know which driver version their applications use. `pg_stat_activity` shows `application_name` for each connection, but the default value, `PostgreSQL JDBC Driver`, has no version in it. This change puts the version in the default, so the view shows it. It implements what #2404 asks for.

The git sha of the build and the JDK version were also considered. They are left out as too much for this value, and they can be discussed separately.

## What changes

* The default `ApplicationName` is `PostgreSQL JDBC Driver` followed by the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. An `ApplicationName` set explicitly is unchanged.
* `ApplicationNameTest` checks the default and an explicit value. Both tests need a running PostgreSQL server.
* The `use.md` page describes the new default and who can read it.
* The `CHANGELOG.md` entry goes first under Changed.

## Compatibility

Yes, for connections that leave `ApplicationName` unset: their `application_name` changes after the upgrade. A query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding those connections. The changelog entry says so.

Any role that can connect to the database can read `application_name` for every session in `pg_stat_activity`. The default therefore shows the driver version to other database users, and `use.md` says so.

## Tests

`defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`. `explicitApplicationNameIsKept` passes on `master` too.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [x] Have you successfully run tests with your changes locally?

CHANGELOG entry:

```markdown
* feat: the default `ApplicationName` now includes the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding connections that use the default. An explicitly set `ApplicationName` is unaffected. ([Issue #2404](https://github.com/pgjdbc/pgjdbc/issues/2404)) ([PR #4466](https://github.com/pgjdbc/pgjdbc/pull/4466))
```
````
