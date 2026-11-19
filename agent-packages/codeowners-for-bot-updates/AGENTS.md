# Editing the codeowners-for-bot-updates package

These are instructions for changing or reviewing the skill under `.apm/skills/codeowners-for-bot-updates/` and its
script, not for running it on a repository.

The skill trades exact ownership for fewer review requests. The goal is that an automerged bot PR stops requesting
review from every code owner; a rare file that loses its owners on the way is an accepted cost, not a defect. Review the
change against that goal:

- **A file reached by a broad pattern loses its owners when only the `*` line owned it.** `go.mod` also reaches a
  `vendor/go.mod` under Renovate `ignorePaths`, and an unanchored `values.yaml` also reaches a
  `charts/production/values.yaml` added after the run. Do not add code that reads the effective Renovate configuration,
  inherited presets included, or that tracks each such file. The owners fix one with a line after the block or with
  `--keep`.
- **Project ownership lives after the block.** The first run puts the block right after the last `*` line, and a rerun
  keeps it where it stands, so a block a user moved stays there. Every line after the block wins over it, and a bot PR
  to a file such a line owns still requests review: the report lists those paths, and that is accepted too. Override
  lines inside the block cover only the kept paths that no line after the block owns; their owners are read from the
  lines before the block, with the old block left out.
- **Well-known files go ownerless for people's PRs too.** The always-on patterns, `/.github/workflows/` included,
  and the ecosystem manifests cover files no bot changed yet, so a person's PR that changes only them requests no
  review. The guard is the check of the branch rules: where they require code-owner review, the skill asks the user
  first. Do not add per-file questions on top of it.
- **Rare inputs get no special handling.** File names with glob characters or line breaks, a merge commit by a person
  that adds a file to a bot PR, and similar inputs a repository almost never has are out of scope unless one is seen in
  a real repository.

What stays in scope: a defect that misplaces the block, loses lines outside the markers, writes outside the clone, stops
the script with a traceback, or changes the owners of a file that a common pattern reaches in an ordinary repository.

`make test` runs `tests/codeowners-for-bot-updates/test_bot_paths.py`.
