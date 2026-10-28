## 1. Commits

Fold commit 2 (`add tests`) and commit 3 (`Apply suggestion from @vlsi`) into commit 1, so the branch has one commit. The tests and the review fixes to `CHANGELOG.md` and `use.md` belong to the change they test and correct. The maintainers can squash or rebase this pull request. If they rebase, any commit left on the branch lands on `master` as its own commit.

```text
feat: append the driver version to the default application_name

A connection that left ApplicationName unset reported application_name
as "PostgreSQL JDBC Driver" whatever driver version it ran. A database
administrator reading pg_stat_activity could not tell which pgjdbc
version each application used.

ApplicationName now defaults to DriverInfo.DRIVER_FULL_NAME: the driver
name, a space, and the version of the driver jar.

User-visible:
With ApplicationName unset, application_name is "PostgreSQL JDBC Driver 42.7.14" for driver 42.7.14, where 42.7.13 sent "PostgreSQL JDBC Driver"; a query that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
Any role that can connect to the database sees the driver version of every such session in pg_stat_activity.
Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Title

```text
feat: append the driver version to the default application_name
```

## 3. Description

```markdown
### Breaking changes

This changes a default in 42.7.14. It affects code that identifies pgjdbc connections by their `application_name`.

- With `ApplicationName` unset, the driver now sends `PostgreSQL JDBC Driver 42.7.14` as `application_name`. That is the driver name, a space, and the version of the driver jar. 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections. To fix it, match on the prefix, or set `ApplicationName=PostgreSQL JDBC Driver` to keep the old value.

### Why

Users want to know which driver version their applications use, as seen in `pg_stat_activity`. Issue #2404 asks to see the version of the JDBC driver a client uses directly from a view in PostgreSQL. Until now, every connection that left `ApplicationName` unset showed the same `PostgreSQL JDBC Driver`.

### What

`ApplicationName` now defaults to `DriverInfo.DRIVER_FULL_NAME` instead of `DriverInfo.DRIVER_NAME`. The changelog entry is first under Changed and states the break.

### User-visible changes

- Any role that can connect to the database sees the driver version of every session that leaves `ApplicationName` unset in `pg_stat_activity`. `use.md` documents this.
- An explicitly set `ApplicationName` is sent as given.

### How to verify

`ApplicationNameTest.explicitApplicationNameIsKept` also passes on `master`. It covers the behavior this change must keep: an explicit `ApplicationName` is sent unchanged.

### Scope

This change leaves out the git sha of the build and the JDK version, which would make the value too long. They can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See "Breaking changes" above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
