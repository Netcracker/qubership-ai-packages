# Hand-over note for the person filing

Nothing has been filed. `draft.md` starts with a `Title:` line and a `---` line. Strip both for the body.

## Filing

No issue templates exist, per your notes, so the body is free-form. A form's required fields are not an issue here. A command, after saving the body to `body.md`:

```bash
gh issue create --repo brightwell/quarry --title "<the Title line>" --body-file body.md
```

`CONTRIBUTING.md` asks for the use case first and no PR before a maintainer agrees, so the draft offers no patch. There is no AI policy, so nothing is disclosed.

## Not established (nobody ran these)

- **No local reproduction.** Everything about v2.4.0 comes from your CI job log, and the draft says "not re-run locally". A run on a pseudo-terminal would close it: `script -q /dev/null env NO_COLOR=1 quarry head sales.parquet | cat -v`. On macOS `script` takes the command as written; on Linux use `script -qc "..." /dev/null`. Add the output to the issue if it shows the same escape sequences.
- **The `--color=never` claim** is from your notes, with no transcript. Paste the job log lines if you have them.
- **That the other CLIs stop coloring under `NO_COLOR=1`** is in your notes and is in the draft only as "the other CLIs in those jobs stop coloring". I did not name them.
- **Versions of the other layers:** CI system, runner, and log viewer. The draft names none. A maintainer may ask.
- **Whether `dbt-quarry` calls are colored.** Your notes say they cannot be edited, not that they color. The draft says only that a flag cannot reach them. Confirm this before filing.
- **Newer builds.** The draft cites v2.4.0, the latest release as of your notes. Check that no unreleased change on the main branch touches color handling.

## Searches you could not rerun from here

Issues, open and closed: `NO_COLOR` (no hits), `color`, `ansi`. Also search pull requests and Discussions for `NO_COLOR` and `no-color`, since trackers match titles and labels and a differently worded duplicate can be missed. The draft carries the `NO_COLOR` query only.

## Check before filing

- The sample output `north   1204` and the file name `sales.parquet` are in the public issue. Make sure neither is real company data. If it is, replace it with a synthetic row of the same shape.
- The draft says "the only case I know of." Change it if others on your team or users of `dbt-quarry` have hit this.
- You may prefer a comment on a thread over a new issue only if one turns up in the searches above. The notes found none.

## Open for you

- The grounding is the NO_COLOR convention, which quarry does not claim to implement. It is weaker than a documented promise, and a maintainer may close it as a preference. Decide whether to file as is.
- Maintainer activity was not checked. Your notes show a release on 2026-09-18, and nothing about replies to issues.
