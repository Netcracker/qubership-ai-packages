**1. Commits**

Commits 2 (`add tests`) and 3 (`Apply suggestion from @vlsi`) are folded into commit 1, leaving one commit. Under squash, a separate commit lands as a bullet, so "add tests" and "Apply suggestion" would otherwise appear in the squash body as noise. The tests and review fixes belong to the same change.

```text
feat: include the driver version in the default ApplicationName

Before this change, the default ApplicationName is "PostgreSQL JDBC
Driver", with no version. A connection that leaves ApplicationName unset
therefore shows only that name in pg_stat_activity, so nothing there
tells which driver version the connection uses. Issue #2404 asks to see
the driver version from a view in PostgreSQL.

The default is now DriverInfo.DRIVER_FULL_NAME, which is the driver name,
a space, and DRIVER_VERSION.

User-visible:
Breaking: from 42.7.14, a connection that leaves ApplicationName unset
sends, for example, "PostgreSQL JDBC Driver 42.7.14" where it sent
"PostgreSQL JDBC Driver" before. A query that matches
application_name = 'PostgreSQL JDBC Driver' stops finding those
connections. Set ApplicationName explicitly to keep the old value.
A connection that leaves ApplicationName unset shows its version to every
role that can connect to the database, because each such role can read
application_name of every session in pg_stat_activity.

Not changed:
An explicitly set ApplicationName is sent unchanged.

Closes #2404
```

**2. Pull request title**

`feat: include the driver version in the default ApplicationName`

**3. Pull request description**

```markdown
### Breaking changes

A query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding the pgjdbc connections that leave `ApplicationName` unset.

* From 42.7.14, the next release from `master`, a connection that leaves `ApplicationName` unset sends `PostgreSQL JDBC Driver 42.7.14` (for example) where it sent `PostgreSQL JDBC Driver` before. Set `ApplicationName` explicitly to keep the old value.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### Changes to Existing Features:

Users want to know which driver version their applications use, and they want to see it in `pg_stat_activity`. The default `ApplicationName` is `PostgreSQL JDBC Driver` with no version, so a connection that leaves `ApplicationName` unset shows no version there. Issue #2404 asks to see the driver version from a view in PostgreSQL. This change does that.

The default becomes `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and `DRIVER_VERSION`. Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the version is visible to those roles too. An explicitly set `ApplicationName` is sent unchanged.

Both tests in `ApplicationNameTest` connect to a running server. `explicitApplicationNameIsKept` passes on `master` too: it pins the explicit name, which must not change.

The build's git SHA and the JDK version are left out. Adding either was considered and left out as too much; they can be discussed separately.

* [x] Does this break existing behaviour? If so please explain. See Breaking changes above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?

Closes #2404
```
