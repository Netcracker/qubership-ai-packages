## Commands that detect the merge model

Run these in your clone of `vlsi/pgjdbc`:

```bash
# Merge methods the repository allows. GitHub returns these fields only to accounts
# with write access, so null values mean "not visible"; they do not mean "disabled".
gh api repos/pgjdbc/pgjdbc --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge}'

# Rules on master, including a required linear history or allowed merge methods
gh api repos/pgjdbc/pgjdbc/rules/branches/master

# What recent merges into master look like
git fetch upstream
git log --first-parent --format='%h %p | %s' -20 upstream/master
git log --merges --oneline -10 upstream/master
```

Here is how to read the `git log` output. If first-parent commits have one parent and subjects that end in `(#NNNN)`, the repository uses squash merge. If they are `Merge pull request #NNNN from …` commits with two parents, it uses merge commits. If commits have one parent and no `(#NNNN)` suffix, it uses rebase merge.

## 1. Commits

Fold `add tests` and `Apply suggestion from @vlsi` into the first commit. The branch then has one commit, and it carries the change, its tests, and its documentation. This works with any merge model. If the repository uses squash merge, paste this message into the squash dialog in place of the generated one.

```text
feat: include driver version in default application_name

Users want to know which pgjdbc version each application uses, and
pg_stat_activity shows the application_name of every session. When
ApplicationName is not set, the driver now sends "PostgreSQL JDBC
Driver" followed by a space and the driver version, for example
"PostgreSQL JDBC Driver 42.7.14". Before, it sent only "PostgreSQL JDBC
Driver". An explicitly set ApplicationName is sent unchanged.

A query or dashboard that matches
application_name = 'PostgreSQL JDBC Driver' no longer finds pgjdbc
connections that leave ApplicationName unset. Any role that can connect
to the database reads the application_name of every session in
pg_stat_activity, so the default now shows the driver version to other
database users. The CHANGELOG entry and use.md say both.

ApplicationNameTest checks both defaults against a running server.

Closes #2404
```

## 2. Pull request title

```text
feat: include driver version in default application_name
```

## 3. Pull request description

```markdown
When `ApplicationName` is not set, the driver now sends `PostgreSQL JDBC Driver` followed by a space and the driver version, for example `PostgreSQL JDBC Driver 42.7.14`. Before, it sent only `PostgreSQL JDBC Driver`. An explicitly set `ApplicationName` is sent unchanged.

Closes #2404

### Why

Users want to know which driver version their applications use, and they want to see it in PostgreSQL itself. `pg_stat_activity` shows the `application_name` of every session, so the default value is a good place for the version. #2404 asks for exactly this.

I considered adding the git SHA of the build and the JDK version as well, but left them out because that is too much for this field. We can discuss them separately.

### Behavior change

- A query or dashboard that matches `application_name = 'PostgreSQL JDBC Driver'` no longer finds pgjdbc connections that leave `ApplicationName` unset. The `CHANGELOG.md` entry says so, and it is the first entry under Changed.
- Any role that can connect to the database reads the `application_name` of every session in `pg_stat_activity`. The default therefore shows the driver version to other database users. `docs/content/documentation/use.md` says so in the `ApplicationName` entry.

### Tests

`ApplicationNameTest` needs a running server:

- `defaultApplicationNameCarriesTheDriverVersion` connects without `ApplicationName` and expects `current_setting('application_name')` to be `PostgreSQL JDBC Driver ` followed by `DriverInfo.DRIVER_VERSION`. On `master` it fails, because the value there is `PostgreSQL JDBC Driver`.
- `explicitApplicationNameIsKept` connects with `ApplicationName=billing` and expects `billing`.

### All Submissions:

* [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
* [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?

### New Feature Submissions:

1. [ ] Does your submission pass tests?
2. [ ] Does `./gradlew styleCheck` pass ?
3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?

### Changes to Existing Features:

* [x] Does this break existing behaviour? If so please explain.
  Yes for monitoring that matches the old default. See "Behavior change" above.
* [x] Have you added an explanation of what your changes do and why you'd like us to include them?
* [x] Have you written new tests for your core changes, as applicable?
* [ ] Have you successfully run tests with your changes locally?
```
