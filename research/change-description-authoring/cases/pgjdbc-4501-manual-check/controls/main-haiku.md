`docker/bin/postgres-server` reads the host port of the second replica from `PG_REPLICA_ONE_PUBLISH_PORT`, not from `PG_REPLICA_TWO_PUBLISH_PORT`. Setting `PG_REPLICA_ONE_PUBLISH_PORT` therefore publishes both replicas on the same host port, and the second replica cannot be moved off 5434 on its own.

The script now reads the second replica's port from `PG_REPLICA_TWO_PUBLISH_PORT`, and 5434 stays the default. Nothing else in the repository uses that variable, so no other file changes. Anyone who sets `PG_REPLICA_ONE_PUBLISH_PORT` now gets the second replica on 5434, or on `PG_REPLICA_TWO_PUBLISH_PORT` if that is set, instead of a shared port.

This change adds no tests. I checked it by starting the script with `PG_PUBLISH_PORT=25432 PG_REPLICA_ONE_PUBLISH_PORT=25433 PG_REPLICA_TWO_PUBLISH_PORT=25434`. `docker ps` shows `25433->5433` and `25434->5434`, one host port per replica.

This change is split out of #4497, which no longer carries this commit. It touches only `docker/bin/postgres-server`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
