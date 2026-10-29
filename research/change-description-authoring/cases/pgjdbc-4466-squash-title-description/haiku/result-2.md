## 1. Commits on merge

Commits 1, 2, and 3 fold into one squash commit when the pull request merges. No branch commit keeps its own commit. The landing message is:

```text
feat: include the driver version in the default ApplicationName (#4466)

## Breaking changes

A connection that leaves `ApplicationName` unset sends `PostgreSQL JDBC Driver X.Y.Z` from 42.7.14 on, where 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` finds no pgjdbc connections after the upgrade. Match the prefix instead, or set `ApplicationName` explicitly to keep the old value.

## Why

Users want to see which driver version each application uses, in `pg_stat_activity`. The default `ApplicationName` is only `PostgreSQL JDBC Driver`, so the view cannot show the version. Issue #2404 asks for the same thing: the driver version visible from a view in PostgreSQL.

## What

Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default shows the driver version to those roles too. The `use.md` page says so.

## User-visible changes

Not changed: an explicit `ApplicationName`, such as `billing`, reads back as given.

## Verification

- `explicitApplicationNameIsKept` passes without the change. It pins the explicit name, which must not move.
- Both tests in `ApplicationNameTest` need a running PostgreSQL server.

## Scope

The git SHA of the build and the JDK version are left out as too much for the default. Each can be discussed separately.

Closes #2404
```

## 2. Pull request title

```text
feat: include the driver version in the default ApplicationName
```

## 3. Pull request description

```markdown
## Breaking changes

A connection that leaves `ApplicationName` unset sends `PostgreSQL JDBC Driver X.Y.Z` from 42.7.14 on, where 42.7.13 sent `PostgreSQL JDBC Driver`. A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` finds no pgjdbc connections after the upgrade. Match the prefix instead, or set `ApplicationName` explicitly to keep the old value.

## Why

Users want to see which driver version each application uses, in `pg_stat_activity`. The default `ApplicationName` is only `PostgreSQL JDBC Driver`, so the view cannot show the version. Issue #2404 asks for the same thing: the driver version visible from a view in PostgreSQL.

## What

Any role that can connect to the database reads `application_name` of every session in `pg_stat_activity`, so the default shows the driver version to those roles too. The `use.md` page says so.

## User-visible changes

Not changed: an explicit `ApplicationName`, such as `billing`, reads back as given.

## Verification

- `explicitApplicationNameIsKept` passes without the change. It pins the explicit name, which must not move.
- Both tests in `ApplicationNameTest` need a running PostgreSQL server.

## Scope

The git SHA of the build and the JDK version are left out as too much for the default. Each can be discussed separately.

Closes #2404
```
