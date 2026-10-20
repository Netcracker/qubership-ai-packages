## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1. The repository merges pull requests with merge commits, so every branch commit stays in `master`. The tests and the review changes belong with the change they cover, so the branch merges as a single commit:

```text
feat: include driver version in default application_name

Users want to see which driver version each application connects
with, and pg_stat_activity shows application_name for every session.
Issue #2404 asks for this.

The default ApplicationName is now "PostgreSQL JDBC Driver" followed
by a space and the driver version, for example
"PostgreSQL JDBC Driver 42.7.14". It used to be
"PostgreSQL JDBC Driver". A connection that sets ApplicationName
still sends the value it sets.

After the upgrade, a query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc
connections that leave ApplicationName unset. The CHANGELOG entry
says so and is listed first under Changed.

Any role that can connect to the database can read the
application_name of every session in pg_stat_activity. The default
therefore shows the driver version to other database users, and
use.md now says so.

ApplicationNameTest checks the default value and checks that an
explicit ApplicationName is kept. Both tests need a running server.

Closes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default application_name
```

## 3. Pull request description

````markdown
Closes #2404

## Why

Users want to know which driver version their applications use, and `pg_stat_activity` is where they look. Issue #2404
asks to see the JDBC driver version directly from a view in PostgreSQL. The only per-session text pgjdbc sends by
default is `application_name`, and until now it held only `PostgreSQL JDBC Driver`.

## What changes

The default `ApplicationName` is now `PostgreSQL JDBC Driver` followed by a space and the driver version
(`DriverInfo.DRIVER_FULL_NAME`), for example `PostgreSQL JDBC Driver 42.7.14`. A connection that sets `ApplicationName`
still sends the value it sets.

I left out the git sha of the build and the JDK version. They would make the value too long, and we can discuss them
separately.

## Compatibility

A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections
that leave `ApplicationName` unset. The `CHANGELOG.md` entry says so, is listed first under Changed, and links
issue #2404 and PR #4466.

Any role that can connect to the database can read the `application_name` of every session in `pg_stat_activity`. The
default therefore shows the driver version to other database users. The `ApplicationName` entry in `use.md` says so.

## Tests

`ApplicationNameTest` needs a running server:

- `defaultApplicationNameCarriesTheDriverVersion` connects without `ApplicationName` and reads
  `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION` from `current_setting('application_name')`. It
  fails on `master`, where the value is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and reads `billing`. It passes on `master`
  too.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes, for queries that match the old default value exactly. See Compatibility.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
````
