# GitLab merge request collection

This reference covers preparing `glab` and collecting the merge request; publishing the findings is `review-delivery`'s.
Do not assume that a self-managed instance behaves like the current GitLab.com release.

## Prepare glab

Use `glab` for every GitLab operation. Run one preflight check before collecting MR data:

1. Confirm that `~/.agents/skills/glab/SKILL.md` exists, then read it completely before the first `glab` command.
2. Run `glab --version`.
3. Read the target MR with `glab mr view <iid> --repo <namespace/project> --output json`.

If all three checks pass, reuse the MR response and proceed directly to collection. Skip separate authentication, host
configuration, transport, and push preflights.

If any check fails, enter the setup flow. Ask before installing or updating a missing CLI or skill. When the CLI is
available but the bundled skill is absent, use `glab skills list` only as a bootstrap discovery command, then use `glab
skills install glab --global` only after approval. Read the installed skill before the next `glab` command. If both are
installed but the MR read fails, follow the skill to configure host, authentication, or repository access. Repeat the
same preflight check after setup.

Use HTTPS for the disposable clone unless the user explicitly asks for SSH. Keep tokens in the operating-system keyring;
never print them or put them in a remote URL, repository, or report.

Record the reported `glab` version. Prefer high-level `glab` commands; use `glab api` only for surfaces that high-level
commands do not cover, including unpublished Draft Notes.

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
```

Do not pick a diff version by array position. Select the version whose base, start, and head SHAs match the MR's current
`diff_refs`. Paginate every list that can exceed one page.

## Collect merge request context

Collect every field required by the main skill's review-input contract. The matching version's base, start, and head
SHAs are the revision tuple; use them for every inline position. Reconcile the diff count with the local Git inventory.
Return every `collapsed`, `too_large`, and overflow indicator, whether the API or Git workspace supplied the content and
position, and which GitLab discussion surfaces were available. If the latest matching diff version is inaccessible,
return the exact error or revision mismatch to the main skill. GitLab can retain a stale discussion while omitting its
former line position from the API. Return it with a location-unavailable marker.
