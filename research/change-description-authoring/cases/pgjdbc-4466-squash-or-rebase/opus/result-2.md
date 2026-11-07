## Commits

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1. The maintainers may squash or rebase this pull request, so whichever commit lands on `master` has to stand alone. The tests and the reviewed changelog and docs text belong to the same change. One commit remains:

```text
feat: add the driver version to the default ApplicationName

Users want to know which pgjdbc version each of their applications
runs, and the server gave them no way to see it. A connection that
leaves ApplicationName unset sent "PostgreSQL JDBC Driver" as
application_name for every driver version, so pg_stat_activity showed
the same value whichever version connected.

The default ApplicationName is now "PostgreSQL JDBC Driver" followed by
a space and the version of the driver jar. Adding the git sha of the
build or the JDK version was left out because it puts too much in the
value. Either can be discussed separately.

User-visible changes.
A connection that leaves ApplicationName unset reports application_name as "PostgreSQL JDBC Driver 42.7.14" for driver 42.7.14, where 42.7.13 and earlier reported "PostgreSQL JDBC Driver"; a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database reads application_name of every session in pg_stat_activity, so the default now shows the driver version to other database users.

Not changed.
An explicitly set ApplicationName is sent as given, without the version.

Fixes #2404
```

## Title

```text
feat: add the driver version to the default ApplicationName
```

## Description

```markdown
**Breaking changes.**
Queries and dashboards that find pgjdbc connections by the exact default application name break:

- A connection that leaves `ApplicationName` unset reports `application_name` as `PostgreSQL JDBC Driver 42.7.14` for driver 42.7.14, where 42.7.13 and earlier reported `PostgreSQL JDBC Driver`. A match on `application_name = 'PostgreSQL JDBC Driver'` stops finding these connections. Update the match to the new value, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old one.

Users want to know which driver version each of their applications runs, as seen in `pg_stat_activity`. #2404 asks to read the version of the JDBC driver a client uses directly from a view in PostgreSQL. Until now every driver version sent the same default, so the view could not show it.

The default `ApplicationName` is now `PostgreSQL JDBC Driver` followed by a space and the version of the driver jar. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users. `use.md` says so. An explicitly set `ApplicationName` is sent as given, without the version.

`explicitApplicationNameIsKept` passes on `master` too. It checks that an explicit `ApplicationName` is not changed.

Fixes #2404.

**Scope.** Adding the git sha of the build or the JDK version is left out because it puts too much in the value. Either can be discussed separately. `gradle.properties` names 42.7.14 as the next version. A maintainer needs to decide whether a changed default can ship in that patch release or should wait for a minor version.

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
