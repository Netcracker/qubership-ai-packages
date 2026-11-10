## 1. Commits at merge

Fold commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) into commit 1, so the branch has one commit. The repository squashes with GitHub's default message. For a single-commit pull request, that setting keeps the commit's own subject and body and appends `(#4466)`. If the three commits stay separate, the squash body ends with `* add tests` and `* Apply suggestion from @vlsi`.

The one remaining commit:

```text
feat: include the driver version in the default ApplicationName

A connection that leaves ApplicationName unset reported itself to the
server as "PostgreSQL JDBC Driver". A database administrator could see
in pg_stat_activity that a client used pgjdbc, but not which version of
the driver it ran. Users asked for that version directly from a
PostgreSQL view in #2404.

The default is now DriverInfo.DRIVER_FULL_NAME: "PostgreSQL JDBC
Driver", a space, and the version of the driver jar. The git sha of the
build and the JDK version are left out of the default; adding either
can be discussed separately.

User-visible changes.
With ApplicationName unset, application_name is "PostgreSQL JDBC Driver 42.7.14" instead of "PostgreSQL JDBC Driver" (42.7.13 and earlier), so a query or dashboard that matches application_name = 'PostgreSQL JDBC Driver' no longer finds these connections.
With ApplicationName unset, any role that can connect to the database reads the driver version of every such session in pg_stat_activity.

Not changed.
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
**Breaking changes.**
Code that identifies pgjdbc connections by the exact default application name stops matching after the upgrade:

- With `ApplicationName` unset, `application_name` is `PostgreSQL JDBC Driver 42.7.14` instead of `PostgreSQL JDBC Driver` (42.7.13 and earlier). A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds these connections. Match the prefix instead, `application_name LIKE 'PostgreSQL JDBC Driver%'`, or set `ApplicationName` explicitly.

A database administrator could see in `pg_stat_activity` that a client used pgjdbc, but not which version of the driver it ran. Users asked for that version directly from a PostgreSQL view in #2404, and others asked for it in conversations with me.

The default `ApplicationName` is now `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and the version of the driver jar. Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so other database users now see the driver version of each connection that keeps the default. An explicitly set `ApplicationName` is sent as given.

`ApplicationNameTest.explicitApplicationNameIsKept` passes on `master` too. It checks that the explicitly set value stays as given.

**Scope.** The git sha of the build and the JDK version are not part of the default. Adding either can be discussed separately.

Fixes #2404

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain. (See "Breaking changes" above.)
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
