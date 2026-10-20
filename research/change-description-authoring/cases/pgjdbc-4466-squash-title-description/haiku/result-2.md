**1. Commits**

All three branch commits fold into one. The squash lands a single commit: the title with `(#4466)` appended as the subject, and the description as the body. No branch commit message reaches `git log`.

````text
feat: include driver version in default application_name (#4466)

Breaking: a query that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding connections that leave `ApplicationName` unset. Through 42.7.13, the default was exactly `PostgreSQL JDBC Driver`. From 42.7.14, the next release, these connections send `PostgreSQL JDBC Driver` followed by a space and the driver version, such as `PostgreSQL JDBC Driver 42.7.14`. Match on the prefix, or set `ApplicationName` to keep a fixed value.

Users want to know which driver version their applications use, and `pg_stat_activity` does not show it. Every connection that leaves `ApplicationName` unset reports the same value, `PostgreSQL JDBC Driver`, whatever version it runs. Issue #2404 asks for the driver version in a PostgreSQL view.

`PGProperty.APPLICATION_NAME` now defaults to `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and `DriverInfo.DRIVER_VERSION`. Adding the git sha of the build or the JDK version was considered and left out as too much. It can be discussed separately.

User-visible:
Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the driver version of a connection that leaves `ApplicationName` unset is visible to other database users.

Not changed:
A connection that sets `ApplicationName` sends the value it was given, with no version added.

Verification: the new `ApplicationNameTest` needs a running server. Its default-name test fails on master, where the value is `PostgreSQL JDBC Driver`; its explicit-name test passes there and guards the case under `Not changed:`.

Fixes #2404
````

**2. Pull request title**

````text
feat: include driver version in default application_name
````

**3. Pull request description**

````markdown
Breaking: a query that matches `application_name = 'PostgreSQL JDBC Driver'` stops finding connections that leave `ApplicationName` unset. Through 42.7.13, the default was exactly `PostgreSQL JDBC Driver`. From 42.7.14, the next release, these connections send `PostgreSQL JDBC Driver` followed by a space and the driver version, such as `PostgreSQL JDBC Driver 42.7.14`. Match on the prefix, or set `ApplicationName` to keep a fixed value.

Users want to know which driver version their applications use, and `pg_stat_activity` does not show it. Every connection that leaves `ApplicationName` unset reports the same value, `PostgreSQL JDBC Driver`, whatever version it runs. Issue #2404 asks for the driver version in a PostgreSQL view.

`PGProperty.APPLICATION_NAME` now defaults to `DriverInfo.DRIVER_FULL_NAME`, which is the driver name, a space, and `DriverInfo.DRIVER_VERSION`. Adding the git sha of the build or the JDK version was considered and left out as too much. It can be discussed separately.

User-visible:
Any role that can connect to the database can read `application_name` of every session in `pg_stat_activity`, so the driver version of a connection that leaves `ApplicationName` unset is visible to other database users.

Not changed:
A connection that sets `ApplicationName` sends the value it was given, with no version added.

Verification: the new `ApplicationNameTest` needs a running server. Its default-name test fails on master, where the value is `PostgreSQL JDBC Driver`; its explicit-name test passes there and guards the case under `Not changed:`.

Fixes #2404
````
