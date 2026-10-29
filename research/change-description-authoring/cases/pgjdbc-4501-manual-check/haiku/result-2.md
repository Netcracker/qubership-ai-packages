With `PG_REPLICA_ONE_PUBLISH_PORT` set, the script asked for the same host port for both replicas. It read the second replica's host port from `PG_REPLICA_ONE_PUBLISH_PORT` instead of `PG_REPLICA_TWO_PUBLISH_PORT`, which it never read, so the second replica could not be moved off 5434 on its own. The script now reads `PG_REPLICA_TWO_PUBLISH_PORT` for the second replica.

A setup that used `PG_REPLICA_ONE_PUBLISH_PORT` to move the second replica now needs `PG_REPLICA_TWO_PUBLISH_PORT` as well. Without it, the second replica stays on 5434.

Checked by starting the script with `PG_PUBLISH_PORT=25432 PG_REPLICA_ONE_PUBLISH_PORT=25433 PG_REPLICA_TWO_PUBLISH_PORT=25434`: `docker ps` shows `25433->5433` and `25434->5434`.
