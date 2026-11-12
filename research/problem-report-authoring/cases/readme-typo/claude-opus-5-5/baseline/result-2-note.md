# Hand-over note: README install command issue for fernlabs/tidewatch

The issue is in `draft.md`. Line 1 is the title, and the body starts at line 3.

## Filing command

```bash
tail -n +3 out/draft.md | gh issue create --repo fernlabs/tidewatch \
  --title 'README install command fails: `pip install tidwatch` finds no package on PyPI' \
  --body-file -
```

The repository has a `documentation` label. `--label documentation` works only if you have triage access to the repository; otherwise leave it off and a maintainer can add it.

## What I did not run or check

I had no network and ran nothing in this session. Every transcript and fact in the report comes from your notes of October 30, 2026, written in your voice as the person who ran them. Before filing:

- Confirm `main` still has the typo, because `3b9e0d4` may no longer be the head:
  `curl -s https://raw.githubusercontent.com/fernlabs/tidewatch/main/README.md | grep -n 'pip install'`
- Re-run the search, since it may have changed since October 30. An open fix PR would make a comment or a review more useful than a new issue:
  `gh issue list --repo fernlabs/tidewatch --state all --search tidwatch`
  `gh pr list --repo fernlabs/tidewatch --state all --search tidwatch`
  `gh issue list --repo fernlabs/tidewatch --state all --search "pip install"`
- Open PR #212 ("docs: README badges") touches lines 3 to 8 only, so it neither fixes nor conflicts with line 23. I left it out of the report.
- I did not check whether the PyPI page for 0.14.2 shows the same typo in its project description. If 0.14.2 was released after June 12, 2026, it might. Look at the install line on https://pypi.org/project/tidewatch/. If the typo is there, add one line to the report, because fixing the README won't change the published description until the next release.

## Decisions for you

- **Issue or pull request.** This is a one-word fix to a line you have already found. A PR that changes line 23 back to `pip install tidewatch` and uses this text as its description may get merged faster than an issue gets triaged.
- **The unregistered name.** According to your transcript, `tidwatch` had no distribution on PyPI on October 30. If someone registers it, the README command would install their package. I left this out of the report because nothing like that has been observed, and the skill rules out speculative impact. The repository has no `SECURITY.md`. The README already shows the misspelled name publicly, so a public issue adds little exposure, and a fix merged quickly closes the gap. You decide whether to file publicly, also contact the maintainers privately (for example through GitHub private vulnerability reporting, if the Security tab offers it), or open the PR right away.
- **Disclosure.** The repository has no AI policy, so it asks for no disclosure. Whether to mention that a tool drafted the text is up to you.
