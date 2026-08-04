# GitLab merge request workflow

Read this reference only when the review target is a GitLab merge request. Use it in two phases:

1. Prepare `glab` and collect GitLab context, then return to the main skill.
2. After the user chooses a publication mode, return here to publish the review or create GitLab Draft Notes.

The main skill remains authoritative for the Git workspace, review checks, finding model, report, authorization,
signature, and cleanup. Do not assume that a self-managed instance behaves like the current GitLab.com release.

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
Draft Notes       glab api projects/<id>/merge_requests/<iid>/draft_notes
```

Use the published-note commands for an immediate review or the Draft Notes flow below for a draft review.

Do not pick a diff version by array position. Select the version whose base, start, and head SHAs match the MR's current
`diff_refs`. Paginate every list that can exceed one page.

## Collect merge request context

Collect every field required by the main skill's review-input contract. Use the API map above for GitLab-specific
surfaces and preserve replies, approval state, and resolved or stale discussions.

Use the merge request's `diff_refs` for initial revision pinning. During collection, retrieve the latest diff version
and confirm its `base_commit_sha`, `start_commit_sha`, and `head_commit_sha` against those refs. The matching version's
base, start, and head SHAs are the platform-authoritative revision tuple. Use them for every inline position. Paginate
through all merge request diffs and reconcile their count with the local Git inventory.
Account for `collapsed`, `too_large`, and overflow indicators; record a coverage gap when neither the API nor Git
workspace can supply material content or a reliable inline position. If discussions are absent from every available
GitLab surface, report that gap and do not claim complete coverage. If the latest diff version is inaccessible, keep a
chat-only review pinned to matching `diff_refs` and local commits, but do not attempt draft publication. GitLab can
retain a stale discussion while omitting its former line position from the API. Preserve the thread body, replies, and
resolution state, but report the location gap instead of reconstructing or inventing a line.

## Create an unpublished draft review

After the main skill applies its authorization, user-verification question, signature, and revision guard, use GitLab
Draft Notes. Do not use regular notes or the Discussions API because they publish immediately.

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

List the draft notes after creation and verify the summary, signature, inline bodies, paths, sides, lines, and SHAs.
Draft Notes do not appear in the regular Discussions list until publication, so verify them through the Draft Notes
endpoint. Leave every note unpublished. Never bulk-publish the draft notes or set a final reviewer state without a
separate, explicit user request. If creation fails partway through, report the exact notes created and remove only those
notes when the user authorized cleanup; never alter a pre-existing draft review.

Return the MR Changes URL and every created draft-note ID. Draft Notes responses can omit a per-note `web_url`; in that
case use `<mr.web_url>/diffs` as the inspection link. Keep the drafts until the user reviews them or asks for cleanup.

If an API call documented in this reference does not work, tell the user.
