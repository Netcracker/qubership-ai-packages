`docker/bin/postgres-server` read the second replica's host port from `PG_REPLICA_ONE_PUBLISH_PORT`. Setting that variable published both replicas on the same host port, and the second replica could not be moved off 5434 on its own.

The script now reads the second replica's host port from `PG_REPLICA_TWO_PUBLISH_PORT`, defaulting to 5434.

Checked by starting the script with `PG_PUBLISH_PORT=25432 PG_REPLICA_ONE_PUBLISH_PORT=25433 PG_REPLICA_TWO_PUBLISH_PORT=25434`: `docker ps` shows `25433->5433` and `25434->5434`.
