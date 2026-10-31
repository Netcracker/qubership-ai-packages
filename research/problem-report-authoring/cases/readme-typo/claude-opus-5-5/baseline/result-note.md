# Hand-over note: README install typo issue for fernlabs/tidewatch

The draft in `draft.md` is a GitHub issue: the title first, then the body under `# Body`. It is written in your voice, because every observation in it comes from your notes of 2026-10-30. I had no network and no checkout, so I re-ran nothing and fetched nothing.

## Decide before filing

1. **A pull request may serve better than an issue.** The fix is one line in a public README. A PR titled `docs: fix package name in README install command` that changes line 23 to `pip install tidewatch`, with the issue body as its description, is probably faster for the maintainers. It's your call.
2. **The misspelled name is unregistered on PyPI.** Your pip output shows `(from versions: none)` for `tidwatch`. Anyone could register that name, and a user who copies the README command would then install their package. Nothing like that has been observed, so the draft doesn't mention it (the skill bans speculative impact). The repository has no `SECURITY.md`. The typo is already public in the README, so I think a public issue or PR is fine. If you'd rather tell the maintainers privately first, check whether the repository's Security tab offers "Report a vulnerability". If you want the risk on record, add one sentence to the issue saying the name is unregistered. Don't describe how someone could abuse it.
3. **Disclosure.** Per your notes, the repository has no AI policy and no contribution guide, so it asks for no disclosure. Add one if you want to.

## Gaps to close before filing

- **The line may already be fixed.** Your notes are from 2026-10-30. Check `main` again:
  ```bash
  curl -s https://raw.githubusercontent.com/fernlabs/tidewatch/main/README.md | grep -n 'pip install'
  ```
- **The search left out closed PRs.** Your notes cover issues (open and closed) and the open PR #212. Run:
  ```bash
  gh issue list --repo fernlabs/tidewatch --state all --search tidwatch
  gh pr list --repo fernlabs/tidewatch --state all --search tidwatch
  gh pr list --repo fernlabs/tidewatch --state all --search "README install"
  ```
- **The workaround line has no transcript.** Your notes say `pip install tidewatch` installs 0.14.2 but don't show the output. If you want to paste it, run it in a clean venv:
  ```bash
  python3 -m venv /tmp/tw-check && /tmp/tw-check/bin/pip install tidewatch
  ```
- **The links weren't fetched.** I built `https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#L23` from the commit in your notes. Open it once to check that it lands on the `pip install tidwatch` line.

## Filing

From the directory that contains `draft.md`:

```bash
sed '1,/^# Body$/d' draft.md > body.md
gh issue create --repo fernlabs/tidewatch \
  --title 'README install command `pip install tidwatch` fails with "No matching distribution found"' \
  --body-file body.md --label documentation
```

If you don't have triage access, `--label` can fail. In that case, run the command again without it and let a maintainer add the label.
