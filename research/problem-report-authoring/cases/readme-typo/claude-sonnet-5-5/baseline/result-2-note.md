# Hand-over note: tidewatch README install issue

The first line of `draft.md` is the title. The rest is the body. Split them before filing.

Suggested filing command, run after saving the body (everything below the title line) as `body.md`:

```bash
gh issue create --repo fernlabs/tidewatch \
  --title "README install command misspells the package name: \`pip install tidwatch\` finds no distribution" \
  --body-file body.md --label documentation
```

Drop `--label` if you lack triage rights; the label exists but I could not check who can apply it.

## Not established by me

- Nothing was run in this session. The pip transcript, the PyPI check, the `git blame` result, and the search all come from your notes. The report writes them in the first person as yours. Re-run `pip install tidwatch` once more if the transcript is more than a day old.
- The report links no URL for the README at the commit, because I could not confirm one. If you want it, use `https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#installation`.
- I did not check whether `tidwatch` appears anywhere else in the repository. Run `git grep -n tidwatch 3b9e0d4`. If it does, add the locations to the issue or fix them in the same pull request.
- The channel lookups (no issue template, `CONTRIBUTING.md`, security or AI policy) are from your notes. The report says nothing about disclosure of tool use for that reason. If a policy turns up, `gh repo view fernlabs/tidewatch --web` is the quick check.

## Queries to keep out of the report

You searched issues, open and closed, for `tidwatch`, `pip install`, and `README install`. A typo report is often worded differently, so also try `typo`, `readme`, and `installation`.

## For you to decide

- Whether to open a pull request that changes `tidwatch` to `tidewatch` on line 23 instead of, or together with, the issue. The fix is one character, and the project has no contribution guide that asks for an issue first. If you open one, reference the issue from it.
- Whether PR #212 (README badges) will conflict. It touches lines 3 to 8 only, so a merge conflict is unlikely, but check before it lands.
