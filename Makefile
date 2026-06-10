# Local equivalents of the CI checks in .github/workflows/.
# `apm` and `doccmd` run through uv, so nothing needs a global install.
#
#   make check               # the marketplace gate (.github/workflows/marketplace.yml, validate job)
#   make check-descriptions  # verify all skill description fields are <= 1020 chars
#   make verify-docs         # run the consumer guide's commands (verify-docs job)
#   make pack                # regenerate .claude-plugin/marketplace.json
#
# verify-docs runs the documented consumer flow against a *published* revision,
# so DOC_REF must be reachable on DOC_REPO. Both default to the current commit
# on `origin`, so push first, or override:
#   make verify-docs DOC_REF=v1.1.0
#   make verify-docs DOC_REPO=Netcracker/qubership-ai-packages DOC_REF=main

APM    := uvx --python 3.12 --from apm-cli --with-requirements $(CURDIR)/requirements.txt apm
DOCCMD := uvx --python 3.12 --from doccmd --with-requirements $(CURDIR)/requirements.txt doccmd

DOC_REPO ?= $(shell git remote get-url origin | sed -E -e 's|^.*github\.com[:/]||' -e 's|\.git$$||')
DOC_REF  ?= $(shell git rev-parse HEAD)
MODE     ?= all
TARGETS  ?= claude,codex,cursor

.PHONY: help pack check check-descriptions verify-docs test install-smoke

help:
	@echo "pack                Regenerate .claude-plugin/marketplace.json"
	@echo "check               Validate the index: versions aligned + in sync (no writes)"
	@echo "check-descriptions  Verify all skill descriptions are <= 1020 chars"
	@echo "verify-docs         Run the consumer guide commands (DOC_REPO=$(DOC_REPO) DOC_REF=<ref>, must be pushed)"
	@echo "test                Network-free producer/consumer round-trip (tests/marketplace_roundtrip.sh)"
	@echo "install-smoke       Install each package into a fresh project (MODE=all|diff, needs network)"

pack:
	$(APM) pack

check:
	$(APM) pack --check-versions --check-clean --dry-run

check-descriptions:
	python3 scripts/check-skill-descriptions.py

verify-docs:
	@tmp=$$(mktemp -d) && mkdir -p "$$tmp/.claude" && cd "$$tmp" && \
	DOC_REPO='$(DOC_REPO)' DOC_REF='$(DOC_REF)' APM_REQUIREMENTS='$(CURDIR)/requirements.txt' \
	$(DOCCMD) --language=bash --group-marker=verify \
		--command='$(CURDIR)/scripts/verify-doc-block.sh' \
		'$(CURDIR)/docs/consuming-packages.md'

test:
	bash tests/marketplace_roundtrip.sh

# Install each marketplace package into a fresh project (claude,codex,cursor).
# MODE=all installs everything; MODE=diff BASE_SHA=<sha> installs only changed packages.
install-smoke:
	@APM_REQUIREMENTS='$(CURDIR)/requirements.txt' MODE='$(MODE)' TARGETS='$(TARGETS)' BASE_SHA='$(BASE_SHA)' \
		bash '$(CURDIR)/scripts/install-smoke.sh'
