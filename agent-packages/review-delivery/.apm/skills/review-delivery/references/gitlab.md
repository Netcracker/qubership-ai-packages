# GitLab merge request publication

Read this reference only when the target is a GitLab merge request. The main skill owns authorization, content, the
thread-ownership rule, and the write protocol; this file owns only the `glab` mechanics of writing and reading back.
`adversarial-code-review` has already prepared `glab` and read the merge request; if this skill runs on its own, follow
that skill's GitLab reference, section *Prepare glab*, first.

Use the revision from `review.json` (`base`, `start`, `head`) for every inline position, after the main skill's step 1
confirmed it is still the merge request's current `diff_refs`.

## Write commands

```text
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

## Reply to and resolve discussions

Use the main skill's ownership and authorization rules. Collect all discussion pages with the commands
above and retain full IDs, replies, authors, and each note's `resolvable` and `resolved` fields. Read the target
discussion again before writing. A general note or system note may not be resolvable; skip unsupported state changes
without changing the finding assessment.
Resolution capability does not establish that the publishing account has permission to change it.

Prefer the installed CLI's supported subcommands. Use the full discussion ID and the explicit target repository URL,
including the self-managed host, rather than relying on the current directory or a shortened ID:

```text
Reply    glab mr note create <iid> --repo <repository-url> --reply <discussion-id> < /path/to/reply.md
Resolve  glab mr note resolve <iid> <discussion-id> --repo <repository-url>
Reopen   glab mr note reopen <iid> <discussion-id> --repo <repository-url>
```

Check subcommand help when the installed CLI differs. If it lacks these operations, use the
[Discussions API](https://docs.gitlab.com/api/discussions/#resolve-a-merge-request-thread) through `glab api`:

```shell
glab api --hostname <host> --method POST \
  projects/<id>/merge_requests/<iid>/discussions/<discussion-id>/notes --field body=@/path/to/reply.md
glab api --hostname <host> --method PUT \
  projects/<id>/merge_requests/<iid>/discussions/<discussion-id> --field resolved=true
```

Use `--field resolved=false` to reopen. These operations publish immediately, so do not execute them for a draft.
After a reply or state change, verify the returned note and all resolvable notes' state by reading the discussion:

```shell
glab api --hostname <host> projects/<id>/merge_requests/<iid>/discussions/<discussion-id>
```

Return the discussion ID, note URL, observed state, and any permission or capability error to the main skill. On an
uncertain reply outcome, read back before retrying so a successful but timed-out reply is not duplicated.

## Create an unpublished draft review

For a draft operation routed by the main skill, use GitLab Draft Notes. Do not use regular notes or the Discussions API
because they publish immediately.

`glab mr note create` does not support draft mode and publishes the discussion immediately. Do not use it for a draft
review. Create every unpublished summary and inline comment through `glab api` and the GitLab Draft Notes API.

A reply to an existing discussion, for a finding with `prior_thread`, is a draft note with
`in_reply_to_discussion_id` set to the full discussion ID and no position; it is published with the rest of the draft.

Create the summary as a draft note without a position. For each inline draft note, supply the pinned base, start, and
head SHAs, `old_path`, `new_path`, `position_type: text`, and the correct old or new line. Use `new_line` for added
lines, `old_line` for removed lines, and both only when GitLab identifies an unchanged line in both sides. Where the
finding's `end_line` is after `start_line`, publish the range as a multiline draft (described below), clipped to the
hunk that holds most of its lines.

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

A finding's `suggestion` goes at the end of the note as a ```` ```suggestion:-0+<n> ```` block, where `<n>` is
`end_line` minus `start_line`: GitLab counts the lines it replaces from the line the note is anchored at, which is
`start_line` in both a draft and a published note (`--line`). Where the range had to be clipped, render the suggestion as a code block tagged with the file's
language instead. Read the note back and check that GitLab shows the suggestion on the intended lines.

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

The user may delete draft notes before publishing the review. To render the summary again, list the draft notes, match
each one that carries a finding, inline or a reply, to that finding by the tag at the start of its `note`, and replace
the summary draft with the *Update* command above.

Draft Notes responses can omit a per-note `web_url`; expose `<mr.web_url>/diffs` as the inspection URL when that occurs.
If a documented API call fails, return the exact command, endpoint, status, and error to the main skill.
