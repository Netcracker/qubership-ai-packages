# Task

Prepare the pull request below for merging. Give, in Markdown:

1. The commits of the branch as they should be when it merges: say which commits, if any, are folded into another,
   and give the full message of every commit that remains.
2. The pull request title.
3. The pull request description, ready to paste into GitHub.

The facts come from the notes below, which were checked against the code and against a running server; treat every
fact in them as verified, and add none that they do not carry.

## Repository facts

- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 40 plain 0`. No `CONTRIBUTING.md` or `AGENTS.md` line names the method. The bodies of the latest
  squash commits are the pull request descriptions as their authors wrote them, for example (abridged):

  ```text
  fix(core): reject a {fn name} escape that has no argument list (#4374)

  ## Why

  A JDBC function escape is written `{fn name(arguments)}`. Without the parentheses the driver rewrote the escape
  into a different statement instead of reporting it: […]

  ### All Submissions:

  * [x] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
  ```

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`, the default branch. Its
  `gradle.properties` says `pgjdbc.version=42.7.14`; the latest release tag is `REL42.7.13`. There is no milestone on
  the pull request.
- The history uses Conventional Commits subjects with a lowercase verb after the prefix (`fix(core): reject …`,
  `feat: add …`). No release tool reads them.
- The repository has this pull request template:

  ```markdown
  ### All Submissions:

  * [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
  * [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

  <!-- You can erase any parts of this template not applicable to your Pull Request. -->

  ### New Feature Submissions:

  1. [ ] Does your submission pass tests?
  2. [ ] Does `./gradlew styleCheck` pass ?
  3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

  ### Changes to Existing Features:

  * [ ] Does this break existing behaviour? If so please explain.
  * [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
  * [ ] Have you written new tests for your core changes, as applicable?
  * [ ] Have you successfully run tests with your changes locally?
  ```

## The branch

The branch has three commits, in this order.

Commit 1, by the pull request author:

```text
feat: Include driver version in default application_name

Adds the driver version to the default application_name sent to the
database as startup. Previously the driver would send the string
"PostgreSQL JDBC Driver". It will now be suffixed with the X.Y.Z
version, e.g, "PostgreSQL JDBC Driver 42.7.13"
```

Its diff:

```diff
--- a/pgjdbc/src/main/java/org/postgresql/PGProperty.java
+++ b/pgjdbc/src/main/java/org/postgresql/PGProperty.java
@@ -71,7 +71,7 @@ public enum PGProperty {
    */
   APPLICATION_NAME(
       "ApplicationName",
-      DriverInfo.DRIVER_NAME,
+      DriverInfo.DRIVER_FULL_NAME,
       "Name of the Application (backend >= 9.0)"),
--- a/docs/content/documentation/use.md
+++ b/docs/content/documentation/use.md
@@ -341,9 +341,10 @@
-* **`ApplicationName (`*String*`)`** *Default `PostgreSQL JDBC Driver`*\
+* **`ApplicationName (`*String*`)`** *Default `PostgreSQL JDBC Driver X.Y.Z`*\
 Specifies the name of the application that is using the connection. 
 This allows a database administrator to see what applications are connected to the server and what resources they are using through views like pg_stat_activity.
+The default value is `PostgreSQL JDBC Driver` suffixed with the version of this driver.
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,7 @@
 ### Changed
+* feat: the default `ApplicationName` now includes the driver version, for example `PostgreSQL JDBC Driver 42.7.14` rather than `PostgreSQL JDBC Driver`, so `pg_stat_activity` shows which driver version each connection is using. An explicitly set `ApplicationName` is unaffected
```

`DriverInfo.DRIVER_FULL_NAME` is `DRIVER_NAME + " " + DRIVER_VERSION`, so the new default is `PostgreSQL JDBC Driver`
followed by a space and the version of the driver jar.

Commit 2, subject `add tests`, no body. It adds `ApplicationNameTest` with two tests, which need a running server:
`defaultApplicationNameCarriesTheDriverVersion` connects without setting `ApplicationName` and reads
`PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION` back from `current_setting('application_name')`;
`explicitApplicationNameIsKept` connects with `ApplicationName=billing` and reads `billing`. The first fails on
`master`, where the value is `PostgreSQL JDBC Driver`; the second passes there too.

Commit 3, subject `Apply suggestion from @vlsi`, no body. It rewrites the `CHANGELOG.md` line and adds one sentence to
`use.md`, both as the review asked (below).

## The discussion

- Issue #2404, "Check JDBC driver version in PG view", open: a user asks to see the version of the JDBC driver a
  client uses directly from a view in PostgreSQL.
- The pull request author: the change came out of conversations with users who want to know which driver version
  their applications use, as seen in `pg_stat_activity`. The author considered adding the git sha of the build or the
  JDK version too, and left that out as too much; it can be discussed separately.
- The review, before commits 2 and 3: the change implements what #2404 asked for, and neither the commit nor the
  changelog references it; the commit message carries no reason for the change, which is only in the pull request
  description; tests are missing. On the changelog line: the version appears only for connections that leave
  `ApplicationName` unset; a query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` stops
  finding pgjdbc connections after the upgrade, so the entry should say so and go first under Changed; the entry
  lacks the `[Issue #2404]` and `[PR #4466]` links its neighbors carry. On `use.md`: any role that can connect to the
  database reads `application_name` of every session in `pg_stat_activity`, so the default now shows the driver
  version to other database users, and the page should say so.
- Commit 3 makes each of those changes to `CHANGELOG.md` and `use.md`. The pull request is #4466.
