#!/usr/bin/env bash
# doccmd --command wrapper used by the "verify-docs" CI job.
#
# doccmd extracts the code blocks in the "verify" group from a guide and hands
# each combined block to this script as a file. The script runs the block
# against the repository revision under review:
#
#   * `apm` is provided through `uvx`, version-pinned via the requirements file
#     in $APM_REQUIREMENTS (required), so no global install.
#   * The canonical marketplace coordinates in the docs are rewritten to the
#     revision under test: `Netcracker/qubership-ai-packages` -> $DOC_REPO and
#     the example tag `v0.1.0` -> $DOC_REF.
#
# Run the consumer guide locally with, for example:
#   DOC_REPO=vlsi/qubership-ai-packages DOC_REF=<sha> APM_REQUIREMENTS="$PWD/requirements.txt" \
#     uvx --python 3.12 --from doccmd --with-requirements requirements.txt doccmd \
#       --language=bash --group-marker=verify \
#       --command="$PWD/scripts/verify-doc-block.sh" docs/consuming-packages.md
set -euo pipefail

block="$1"
repo="${DOC_REPO:-Netcracker/qubership-ai-packages}"
ref="${DOC_REF:-main}"
req="${APM_REQUIREMENTS:?APM_REQUIREMENTS must point to a requirements.txt}"

{
  printf 'apm() { uvx --python 3.12 --from apm-cli --with-requirements %q apm "$@"; }\n' "$req"
  sed -e "s#Netcracker/qubership-ai-packages#${repo}#g" \
      -e "s#v0.1.0#${ref}#g" \
      "$block"
} | bash -euo pipefail
