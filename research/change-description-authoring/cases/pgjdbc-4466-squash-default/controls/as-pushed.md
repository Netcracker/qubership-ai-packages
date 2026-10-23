## 1. Commits

The branch merges as pushed, with its three commits.

```text
feat: Include driver version in default application_name

Adds the driver version to the default application_name sent to the
database as startup. Previously the driver would send the string
"PostgreSQL JDBC Driver". It will now be suffixed with the X.Y.Z
version, e.g, "PostgreSQL JDBC Driver 42.7.13"
```

```text
add tests

(no body)
```

```text
Apply suggestion from @vlsi

(no body)
```

## 2. Title

```text
feat: Include driver version in default application_name
```

## 3. Description

```markdown
Adds the driver version to the default application_name sent to the database as startup. Previously the driver would send the string "PostgreSQL JDBC Driver". It will now be suffixed with the X.Y.Z version, e.g, "PostgreSQL JDBC Driver 42.7.13"

This came about after some in-person conversations with users who wanted to know what version of the driver their apps are using to connect to their DBs in `pg_stat_activity`.

I considered going a step further and including the git sha of the driver build or the JDK version, but that seems like too much. If anything we can discuss that as a separate follow up.
```
