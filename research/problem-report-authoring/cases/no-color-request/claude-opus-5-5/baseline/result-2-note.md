# Hand-over note: quarry `NO_COLOR` request

Nothing was filed. Everything in the draft comes from your notes of 2026-10-30. I had no access to the repository, the tracker, or the network, and I ran nothing.

## Filing

The draft is a feature request, not a bug report: quarry never promised `NO_COLOR` support, and `CONTRIBUTING.md` asks for feature requests to open as an issue that describes the use case. There are no issue templates, so the headings are mine.

The title is the bold line at the top of `draft.md`. The body is everything below the `---` rule. Save the body to its own file and file it with:

```bash
gh issue create --repo brightwell/quarry \
  --title 'Colored output can'"'"'t be turned off from the environment: `NO_COLOR` is ignored' \
  --body-file body.md
```

`CONTRIBUTING.md` asks contributors not to open a PR until a maintainer agrees, so the draft doesn't offer a patch. If you have one, mention it after a maintainer replies.

No AI policy exists according to your notes, so the draft carries no disclosure.

## Gaps to close before filing

- **Runner OS and image.** The draft says these are not established. If you know them, replace that sentence with the OS, the image or runner version, and the CI system.
- **A run outside CI.** This would show that the behavior doesn't depend on the CI system. On Linux: `NO_COLOR=1 script -qc 'quarry head sales.parquet' /dev/null | cat -v`. On macOS: `NO_COLOR=1 script -q /dev/null quarry head sales.parquet | cat -v`. If `^[` shows up, change "we have only run it in CI" to say where you reproduced it, and paste the output.
- **A public input file.** `sales.parquet` is yours, so a maintainer can't run the same step. If any Parquet file shows the same thing, use a public one or add a few lines that generate one. Also confirm that `north 1204` is fine to publish. If it isn't, re-run the step on synthetic data and paste that output, since edited output would no longer be what quarry printed.
- **Trimmed output.** Check whether the logged `head` output had more rows than the two in your notes. If it did, add "(trimmed)" under the block.
- **`dbt-quarry` and the environment.** The draft says you haven't checked whether the wrapper passes `NO_COLOR` on to quarry. Check that, and the wrapper's version, before a maintainer asks. If the wrapper clears the environment, the request doesn't help those calls.
- **Unreleased support.** Check that `main` doesn't already handle `NO_COLOR`. Search the code for `NO_COLOR`, read the changelog after v2.4.0, and search PRs: `is:pr NO_COLOR` and `is:pr color`, open and closed. Also search Discussions, if the repository has them.
- **The docs claim.** Re-read `docs/cli.md`, section "Output", on v2.4.0 and confirm that the quoted `auto` behavior matches what it says.

## Left out of the draft

- "The other CLIs in those jobs stop coloring": your notes have no log excerpt for this. If you want it in the issue, add one log line from one of those tools and name the tool and its version.
- The `ansi` search hit #140, which is about the Windows console code page and unrelated, so the draft doesn't mention it.
