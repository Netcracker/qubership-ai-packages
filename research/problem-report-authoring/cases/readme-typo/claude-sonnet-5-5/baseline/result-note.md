# Hand-over note: tidewatch README install command

Not filed. Draft is in `draft.md`; the first line is the title and the rest is the body.

## Filing

Put the body in a file without the title line, then run:

```bash
gh issue create --repo fernlabs/tidewatch --title "README install command misspells the package name, so \`pip install tidwatch\` fails" --body-file body.md --label documentation
```

The repository has no issue template, so the body uses my own headings. Check that the `documentation` label can be set by you.

## Decisions for you

- **Issue or pull request.** This is a one-character fix on a single line. A pull request that corrects line 23 may serve the maintainers better than an issue. If you open one, keep the observation and the `git blame` result in its description. I did not write one.
- **Where the report claims things.** The transcript, the version numbers, and the `git blame` result come from your notes. The draft uses "I", so it reads as yours. I ran nothing and had no network, so I did not reproduce the failure or check PyPI myself. Re-run both commands before filing, and confirm that you can answer follow-up questions.
- **Name squatting.** `tidwatch` is currently unregistered on PyPI, going by pip's "from versions: none". Anyone could register it, and the README would then send users to that package. I left this out of the report because I observed no instance of it. Raise it privately with the maintainers if you think it matters; I found no security policy.

## Lookups to repeat

- Duplicate search on github.com/fernlabs/tidewatch/issues with closed items included: `tidwatch`, `pip install`, `README install`. Your notes record no hits. I could not run these queries again.
- Open pull requests that touch `README.md`, in case another one changed line 23 after your search. Only #212 was known.
- Confirm that line 23 on `main` still reads `pip install tidwatch` at the time of filing, since `3b9e0d4` may no longer be the head.
- Confirm that the parent of `81ac2f7` has the correct spelling, if you want to name it as the last good commit. The notes only state that the line read `pip install tidewatch` before that commit.

## Not in the report

- No AI policy exists in the repository, so I added no disclosure. Add one if you want to.
- No redaction was needed. The output has no secrets or private names.
