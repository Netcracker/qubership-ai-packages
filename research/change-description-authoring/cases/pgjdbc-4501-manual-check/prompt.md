# Task

A maintainer called the pull request description below too long for the change. Rewrite it, in Markdown, ready to
paste into GitHub. The facts in it were checked against the code; treat every fact as verified, and add none that
neither it nor the diff carries.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- No pull request template is used. The pull request lives on the target repository and has one commit.
  `git merge-base origin/master HEAD` is `874745258455be18708d91a24cc98a0ae5ae85a3`; the head commit is
  `e399fb2d5e4e321d7bbec3d643b02f6bb35677b9`.
- CI runs the full test suite, against a PostgreSQL server, on every pull request.
- Files changed: `docker/bin/postgres-server` +1 -1.
- #4497 is open.

## The description

````markdown
`docker/bin/postgres-server` read the host port of the second replica from `PG_REPLICA_ONE_PUBLISH_PORT` instead of `PG_REPLICA_TWO_PUBLISH_PORT`. Setting `PG_REPLICA_ONE_PUBLISH_PORT` therefore published both replica ports on the same host port, and the second replica could not be moved off 5434 on its own. The script now reads `PG_REPLICA_TWO_PUBLISH_PORT`, which nothing else in the repository uses.

Checked by starting the script with `PG_PUBLISH_PORT=25432 PG_REPLICA_ONE_PUBLISH_PORT=25433 PG_REPLICA_TWO_PUBLISH_PORT=25434`: `docker ps` shows `25433->5433` and `25434->5434`.

Split out of pgjdbc/pgjdbc#4497, which no longer carries this commit.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
````

## The diff

````diff
diff --git a/docker/bin/postgres-server b/docker/bin/postgres-server
index d9fb4dd137..7946ce544e 100755
--- a/docker/bin/postgres-server
+++ b/docker/bin/postgres-server
@@ -48,7 +48,7 @@ log () {
 main () {
     local publish_port="${PG_PUBLISH_PORT:-5432}"
     local replica_one_port="${PG_REPLICA_ONE_PUBLISH_PORT:-5433}"
-    local replica_two_port="${PG_REPLICA_ONE_PUBLISH_PORT:-5434}"
+    local replica_two_port="${PG_REPLICA_TWO_PUBLISH_PORT:-5434}"
 
     # Determine our current directory and change to be in the same directory as the compose file
     local script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
````
