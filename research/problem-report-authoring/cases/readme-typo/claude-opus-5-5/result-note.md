# Hand-over note: README install command issue for fernlabs/tidewatch

## Filing

The first line of `draft.md` is the title, and everything after the blank line under it is the body. Save the body
as `body.md` and file it with:

```bash
gh issue create --repo fernlabs/tidewatch \
  --title 'README install command names `tidwatch`; the PyPI package is `tidewatch`' \
  --label documentation \
  --body-file body.md
```

The repository has no issue template, no `CONTRIBUTING.md`, and no AI policy, so the issue has no form to fill and
nothing to disclose. Existing issues use Markdown with fenced code blocks, and the draft does too.

## What I did not establish

I had no network and no checkout, so everything in the draft comes from your notes taken on 2026-10-30. I ran none
of it myself. Before filing, check these:

- The pip transcript is from your notes. The draft presents it as the filer's own run. If someone else ran it, either
  re-run it yourself or add their name above the block.

  ```bash
  python3 -m venv /tmp/tw && /tmp/tw/bin/pip install tidwatch; /tmp/tw/bin/pip install tidewatch
  ```

- Line 23 still has the misspelling on today's `main`, and `3b9e0d4` is the commit to cite. If `main` has moved,
  update the hash in the link and in the text:

  ```bash
  gh api repos/fernlabs/tidewatch/contents/README.md -H 'Accept: application/vnd.github.raw' | sed -n '23p'
  gh api repos/fernlabs/tidewatch/commits/main --jq .sha
  ```

- No issue or pull request opened since your search covers it:

  ```bash
  gh issue list --repo fernlabs/tidewatch --state all --search tidwatch
  gh pr list --repo fernlabs/tidewatch --state all --search tidwatch
  ```

  Your earlier queries on issues, open and closed, were `tidwatch`, `pip install`, and `README install`. None of them
  returned anything.

## Left out on purpose

- The history from `git blame`: `81ac2f7` (2026-06-12, "docs: reorganize README") introduced the typo, and before
  that commit the line read `pip install tidewatch`. A maintainer doesn't need this to fix one word. Add it if you
  want to point at the reorganization.
- Your OS, Python, and pip versions: pip rejects a package name that doesn't exist on PyPI under any version.

## For you to decide

- A one-word pull request that changes line 23 to `pip install tidewatch` may serve the maintainers better than an
  issue. It can also go alongside one.
- The project doesn't say whether it accepts reports drafted with a tool. Nothing requires disclosure, so that call
  is yours.
