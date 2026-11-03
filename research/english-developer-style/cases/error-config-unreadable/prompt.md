`foo` is a command-line tool. On start it reads its configuration file from the path in the environment variable
`FOO_CONFIG`, or from `/etc/foo.yaml` when the variable is unset. It runs without root privileges, and the package
installs `/etc/foo.yaml` with mode `0640`, owner `root`, group `foo`.

When opening the file fails with `EACCES`, the tool prints one error message to stderr and exits with status 1. No
default configuration is used in that case.

Write that error message, for the case where `FOO_CONFIG` is unset. Give the message text only, as printed.
