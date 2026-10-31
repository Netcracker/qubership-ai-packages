# Hand-over note: NO_COLOR request for brightwell/quarry

This note is for you, the person filing. It is not part of the issue.

## Filing

The project has no issue templates. `CONTRIBUTING.md` asks for feature requests to start as an issue that describes the
use case, so the draft is written as a feature request with no form fields. Don't open a PR until a maintainer agrees,
because `CONTRIBUTING.md` asks for that.

The first line of `draft.md` is the title. The body starts after the `---` line. To file it:

```bash
tail -n +5 out/draft.md > body.md
gh issue create --repo brightwell/quarry \
  --title "No way to turn off colored output from the environment: NO_COLOR is ignored" \
  --body-file body.md
```

## Fill in before filing

- The two placeholders under "Environment": the CI system and runner version, and the runner OS. If you don't have
  them, replace the line with "not established" instead of guessing.
- `dbt-quarry`: if it's public, link it and give the version you use. A maintainer will want to see how it calls quarry.
- The log shows one data row, `north   1204`, from `sales.parquet`. Replace it with a made-up value if that figure
  shouldn't be public.

## What I did not run or check

I had only your notes, with no network access, and I ran nothing. The log excerpt and the `--color=never` result come
from your CI job, and the issue presents them as your observations.

- **The pseudo-terminal claim.** The draft says your runner allocates a pseudo-terminal. Make sure you can name the
  runner setting that does this. A maintainer may ask why you don't turn the pseudo-terminal off, and the notes don't
  say whether you can.
- **Pull requests and unreleased work.** Your search covered issues only. Run these so you don't file a request the
  main branch has already done:
  - `gh pr list --repo brightwell/quarry --state all --search NO_COLOR`
  - `gh search commits --repo brightwell/quarry NO_COLOR`
  - Read `CHANGELOG.md` on the default branch for anything after v2.4.0 about color.

  If a PR already adds it, deciding whether to comment there instead of opening an issue is up to you.
- **Quotes.** Check the wording of `docs/cli.md`, section "Output", and of the no-color.org sentence against the live
  pages. The issue cites both.
- **Search queries.** Your queries were `NO_COLOR`, `color`, and `ansi` against open and closed issues. The draft
  leaves out `ansi`, because its only hit (#140, Windows console code page) is unrelated.

## Your call

- The project has no AI policy. Decide whether to say that a tool drafted the issue. Either way, you'll be answering
  any follow-up questions yourself, so make sure you can defend every claim in the issue without this note.
- The grounding is an external convention that quarry doesn't claim to follow, plus your own CI case. The draft says
  that plainly. If you know other quarry users who hit the same problem, adding them makes the request stronger.
