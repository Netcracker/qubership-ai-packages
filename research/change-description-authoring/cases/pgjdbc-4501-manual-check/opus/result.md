`docker/bin/postgres-server` read the host port of the second replica from `PG_REPLICA_ONE_PUBLISH_PORT` instead of `PG_REPLICA_TWO_PUBLISH_PORT`. Setting `PG_REPLICA_ONE_PUBLISH_PORT` therefore published both replica ports on the same host port, and the second replica could not be moved off 5434 on its own.

Checked by starting the script with `PG_PUBLISH_PORT=25432 PG_REPLICA_ONE_PUBLISH_PORT=25433 PG_REPLICA_TWO_PUBLISH_PORT=25434`: `docker ps` shows `25433->5433` and `25434->5434`.
