`docker/bin/postgres-server` read the second replica's host port from `PG_REPLICA_ONE_PUBLISH_PORT`. Setting that variable put both replicas on the same host port, and the second replica could not be moved off 5434. The script now reads `PG_REPLICA_TWO_PUBLISH_PORT`.

Tested by starting the script with `PG_PUBLISH_PORT`, `PG_REPLICA_ONE_PUBLISH_PORT`, and `PG_REPLICA_TWO_PUBLISH_PORT` set to different ports: `docker ps` shows each replica on its own port.

Split out of #4497.
