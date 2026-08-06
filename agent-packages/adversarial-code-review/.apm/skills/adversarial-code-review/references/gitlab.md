# GitLab merge request workflow

Read this reference only when the review target is a GitLab merge request. Use it in two phases:

1. Prepare `glab` and collect GitLab context, then return to the main skill.
2. For a publication operation routed by the main skill, return here for published-note or Draft Note mechanics.

The main skill remains authoritative for the Git workspace, review checks, finding model, report, language, review
communication, publication authorization, signature, verification, and cleanup. This reference owns only GitLab access
setup, data collection, and write or read mechanics. Do not assume that a self-managed instance behaves like the current
GitLab.com release.

## Prepare glab

Use `glab` for every GitLab operation. Run one preflight check before collecting MR data:

1. Confirm that `~/.agents/skills/glab/SKILL.md` exists, then read it completely before the first `glab` command.
2. Run `glab --version`.
3. Read the target MR with `glab mr view <iid> --repo <namespace/project> --output json`. A successful response confirms
   that `glab` can access the target repository and download its data.

If all three checks pass, reuse the MR response and proceed directly to collection. Skip separate authentication,
host configuration, transport, and push preflights.

If any check fails, enter the setup flow. Ask before installing or updating a missing CLI or skill. When the CLI is
available but the bundled skill is absent, use `glab skills list` only as a bootstrap discovery command, then use
`glab skills install glab --global` only after approval. Read the installed skill before the next `glab` command. If
both are installed but the MR read fails, follow the skill to configure host, authentication, or repository access.
Repeat the same preflight check after setup.

Use HTTPS for the disposable clone unless the user explicitly asks for SSH. Keep tokens in the operating-system
keyring; never print them or put them in a remote URL, repository, or report. A review never requires a push test.

Record the reported `glab` version. Prefer high-level `glab` commands. `glab api` is the CLI's authenticated low-level
subcommand, not a separate client; use it only for surfaces that high-level commands do not cover, including unpublished
Draft Notes.

## API map

Use the authenticated `glab` host and a numeric project ID or URL-encoded project path:

```text
MR metadata       glab mr view <iid> --repo <namespace/project> --output json
Commits           glab api projects/<id>/merge_requests/<iid>/commits
Diff versions     glab api projects/<id>/merge_requests/<iid>/versions
Changed files     glab api 'projects/<id>/merge_requests/<iid>/diffs?per_page=100' --paginate
Discussions       glab mr note list <iid> --repo <namespace/project> -F json
Full discussions  glab api 'projects/<id>/merge_requests/<iid>/discussions?per_page=100' --paginate
Approvals         glab api projects/<id>/merge_requests/<iid>/approvals
Published summary glab mr note create <iid> --repo <namespace/project> < /path/to/summary.md
Published inline  glab mr note create <iid> --repo <namespace/project> --file <path> --line <line> -m '<comment>'
Removed-line note glab mr note create <iid> --repo <namespace/project> --file <path> --old-line <line> -m '<comment>'
Published notes   glab api 'projects/<id>/merge_requests/<iid>/notes?per_page=100' --paginate
Published note    glab api projects/<id>/merge_requests/<iid>/notes/<note-id>
Published thread  glab api projects/<id>/merge_requests/<iid>/discussions/<discussion-id>
Draft Notes       glab api projects/<id>/merge_requests/<iid>/draft_notes
```

For an immediate-publication operation, capture the create response and use its note or discussion ID for read-back. If
a high-level command returns only a URL, resolve the ID from that URL. As a fallback, snapshot IDs before creation and
match new entries by the publishing account, exact body, position, and creation interval. Treat zero or multiple matches
as an ambiguous write result and make no further mutations. Return the created IDs, bodies, positions, paths, sides,
lines, and revision tuple to the main skill.

Use the published-note commands for an immediate-publication operation or the Draft Notes flow below for a draft
operation.

Do not pick a diff version by array position. Select the version whose base, start, and head SHAs match the MR's current
`diff_refs`. Paginate every list that can exceed one page.

## Collect merge request context

Collect every field required by the main skill's review-input contract. Use the API map above for GitLab-specific
surfaces and preserve replies, approval state, and resolved or stale discussions.

Use the merge request's `diff_refs` for initial revision pinning. During collection, retrieve the latest diff version
and confirm its `base_commit_sha`, `start_commit_sha`, and `head_commit_sha` against those refs. The matching version's
base, start, and head SHAs are the platform-authoritative revision tuple. Use them for every inline position. Paginate
through all merge request diffs and reconcile their count with the local Git inventory.
Return every `collapsed`, `too_large`, and overflow indicator, whether the API or Git workspace supplied the content and
position, and which GitLab discussion surfaces were available. If the latest matching diff version is inaccessible,
return the exact error or revision mismatch to the main skill. GitLab can retain a stale discussion while omitting its
former line position from the API. Return its body, replies, resolution state, and a location-unavailable marker.

## Create an unpublished draft review

For a draft operation routed by the main skill, use GitLab Draft Notes. Do not use regular notes or the Discussions API
because they publish immediately.

`glab mr note create` does not support draft mode and publishes the discussion immediately. Do not use it for a draft
review. Create every unpublished summary and inline comment through `glab api` and the GitLab Draft Notes API.

Create the summary as a draft note without a position. For each inline draft note, supply the pinned base, start, and
head SHAs, `old_path`, `new_path`, `position_type: text`, and the correct old or new line. Use `new_line` for added
lines, `old_line` for removed lines, and both only when GitLab identifies an unchanged line in both sides. Use a line
range only when the whole range is the smallest useful location.

Create a summary from a Markdown file:

```shell
glab api --method POST projects/<id>/merge_requests/<iid>/draft_notes \
  --field note=@/path/to/summary.md
```

For an inline draft, write a JSON request body with this shape:

```json
{
  "note": "Comment body",
  "position": {
    "position_type": "text",
    "base_sha": "<base>",
    "start_sha": "<start>",
    "head_sha": "<head>",
    "old_path": "path/to/file",
    "new_path": "path/to/file",
    "new_line": 42
  }
}
```

Then send the structured body:

```shell
glab api --method POST projects/<id>/merge_requests/<iid>/draft_notes \
  --input /path/to/draft.json \
  --header 'Content-Type: application/json'
```

For a multiline draft, keep the top-level `old_line` or `new_line` on the range start and add
`position.line_range.start` and `position.line_range.end`. Each boundary needs `line_code`, `type`, and its old or new
line. A line code has the form `<SHA1(file path)>_<old>_<new>`; use `0` for the side that does not exist. Verify the
returned range exactly instead of trusting the create response alone.

Manage only the drafts created by the current operation:

```text
List    glab api projects/<id>/merge_requests/<iid>/draft_notes
Read    glab api projects/<id>/merge_requests/<iid>/draft_notes/<draft-id>
Update  glab api --method PUT projects/<id>/merge_requests/<iid>/draft_notes/<draft-id> --field note=@<file>
Delete  glab api --method DELETE projects/<id>/merge_requests/<iid>/draft_notes/<draft-id> --silent
```

Send an inline `position` as a structured JSON object through `glab api --input` and set
`Content-Type: application/json`. Do not use bracket-style fields such as `position[new_line]`: `glab` can send them as
unrelated keys, and GitLab can return success while silently creating an unpositioned draft. A successful create is not
enough; require non-null expected SHAs, paths, side and line, and `line_code` in the response and subsequent read-back.

List and read the draft notes after creation. Draft Notes do not appear in the regular Discussions list until
publication, so use the Draft Notes endpoint. Return every created ID, response body, position, path, side, line, SHA,
and API error to the main skill. Do not mutate anything else from this reference after a partial failure.

Draft Notes responses can omit a per-note `web_url`; expose `<mr.web_url>/diffs` as the inspection URL when that occurs.
If a documented API call fails, return the exact command, endpoint, status, and error to the main skill.
