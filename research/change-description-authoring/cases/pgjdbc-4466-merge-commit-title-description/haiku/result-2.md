### 1. Commits

Commit 3 (`Apply suggestion from @vlsi`) and commit 2 (`add tests`) are folded into commit 1. Commit 3 is a review fix-up to commit 1's changelog and docs. Commit 2 is test-only with no message of its own, so it becomes part of the feature commit. The branch lands as one commit:

```text
feat: include driver version in default ApplicationName

Operators cannot see which driver version a connection uses in
pg_stat_activity: the default ApplicationName names the driver but not
its version. Issue #2404 asks for this.

The default is built from DriverInfo.DRIVER_FULL_NAME, which is the
driver name, a space, and the version. The git sha of the build and the
JDK version were left out as too much; they can be discussed separately.

User-visible:
Breaking: in 42.7.13, the latest release, a query that matches application_name = 'PostgreSQL JDBC Driver' finds connections that leave ApplicationName unset; after the upgrade it finds none of them. Set ApplicationName explicitly to keep the old value, or match the prefix instead.
Connections that leave ApplicationName unset send "PostgreSQL JDBC Driver X.Y.Z", for example "PostgreSQL JDBC Driver 42.7.14", in place of "PostgreSQL JDBC Driver".
Any role that can connect reads the application_name of every session in pg_stat_activity, so the default now shows the driver version to other database users.

Not changed:
An explicitly set ApplicationName is sent as given.

Fixes #2404
```

### 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

### 3. Pull request description

```markdown
A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding the connections from this driver that leave `ApplicationName` unset.

User-visible:
Breaking: in 42.7.13, the latest release, that query finds those connections; after the upgrade it finds none of them. Set `ApplicationName` explicitly to keep the old value, or match the prefix instead.
Connections that leave `ApplicationName` unset send `PostgreSQL JDBC Driver X.Y.Z`, for example `PostgreSQL JDBC Driver 42.7.14`, in place of `PostgreSQL JDBC Driver`.
Any role that can connect reads the `application_name` of every session in `pg_stat_activity`, so the default now shows the driver version to other database users.

Not changed:
An explicitly set `ApplicationName` is sent as given.

Users who want to know which driver version their applications run cannot see it in `pg_stat_activity`: the default `ApplicationName` names the driver but not its version. Issue #2404 asks for this.

The default is built from `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and the version. The git sha of the build and the JDK version were considered and left out as too much; they can be discussed separately.

Needs a running PostgreSQL server. Two new tests in `ApplicationNameTest`: `defaultApplicationNameCarriesTheDriverVersion` fails on `master`, where the value is `PostgreSQL JDBC Driver`; `explicitApplicationNameIsKept` passes there too and guards the explicit value.

Whether the break is acceptable in 42.7.14 is for the maintainers to decide. The code shows the break, not whether it is wanted.

Fixes #2404
```
