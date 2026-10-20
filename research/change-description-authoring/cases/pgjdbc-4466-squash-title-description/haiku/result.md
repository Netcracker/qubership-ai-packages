1. Commits 1, 2, and 3 fold into one squash commit when the pull request merges, so no branch commit survives on its own. Its full message:

```text
feat: add the driver version to the default ApplicationName (#4466)

User-visible:

Breaking: a query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding connections that leave `ApplicationName` unset. Those connections now send `PostgreSQL JDBC Driver 42.7.14`, and 42.7.13 and earlier sent `PostgreSQL JDBC Driver`. Match the prefix instead, or set `ApplicationName` yourself.

Any role that can read `pg_stat_activity` sees that version in `application_name` for these connections, so the default now shows the driver version to other database users.

Not changed:

An `ApplicationName` that the application sets is sent as set, with no version added.

Previously the driver sent `PostgreSQL JDBC Driver` as the default `application_name` in every release up to 42.7.13, so `pg_stat_activity` could not show which driver version a connection used. Issue #2404 asks for that view.

Only the default changes. The version comes from the driver jar itself, so the value matches the jar in use.

Two new tests in `ApplicationNameTest` need a running PostgreSQL server. `defaultApplicationNameCarriesTheDriverVersion` fails on master, where the value is `PostgreSQL JDBC Driver`, so it pins the new default. `explicitApplicationNameIsKept` passes on master too, so it pins that an explicit name is kept.

Not included: the git sha of the build and the JDK version. Both were considered for the default and left out as too much; they can be discussed separately.

Fixes #2404
```

2. Pull request title:

```text
feat: add the driver version to the default ApplicationName
```

3. Pull request description:

```markdown
User-visible:

Breaking: a query, view, or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding connections that leave `ApplicationName` unset. Those connections now send `PostgreSQL JDBC Driver 42.7.14`, and 42.7.13 and earlier sent `PostgreSQL JDBC Driver`. Match the prefix instead, or set `ApplicationName` yourself.

Any role that can read `pg_stat_activity` sees that version in `application_name` for these connections, so the default now shows the driver version to other database users.

Not changed:

An `ApplicationName` that the application sets is sent as set, with no version added.

Previously the driver sent `PostgreSQL JDBC Driver` as the default `application_name` in every release up to 42.7.13, so `pg_stat_activity` could not show which driver version a connection used. Issue #2404 asks for that view.

Only the default changes. The version comes from the driver jar itself, so the value matches the jar in use.

Two new tests in `ApplicationNameTest` need a running PostgreSQL server. `defaultApplicationNameCarriesTheDriverVersion` fails on master, where the value is `PostgreSQL JDBC Driver`, so it pins the new default. `explicitApplicationNameIsKept` passes on master too, so it pins that an explicit name is kept.

Not included: the git sha of the build and the JDK version. Both were considered for the default and left out as too much; they can be discussed separately.

Fixes #2404
```
