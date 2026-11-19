# GitHub pull request review

Read this reference only when the target is a GitHub pull request. The main skill owns authorization, content, and the
write protocol; this file owns only the `gh` mechanics.

## One review per round

Post the inline findings and the general comment as one review attached to `revision.head`, so the author gets one
notification and the comments stay grouped:

```shell
gh api --method POST repos/<owner>/<repo>/pulls/<number>/reviews --input /path/to/review.json
```

```json
{
  "commit_id": "<revision.head>",
  "body": "<general comment>",
  "comments": [
    { "path": "src/A.java", "side": "RIGHT", "line": 42, "body": "<finding>" },
    { "path": "src/A.java", "side": "RIGHT", "start_line": 40, "start_side": "RIGHT", "line": 44, "body": "<finding>" },
    { "path": "src/B.java", "side": "LEFT", "line": 7, "body": "<finding on a removed line>" }
  ]
}
```

`side: new` in the finding is `RIGHT`, `old` is `LEFT`; always send `side`. Publish the finding's range: where
`end_line` is after `start_line`, also send `start_line` with that value, `start_side` equal to `side`, and `line` equal
to `end_line`; otherwise send `line` equal to `start_line`. GitHub rejects a range whose ends are not in one hunk, so
where part of the range lies outside the hunk that holds most of its lines, clip the range to that hunk before sending
it.

A finding's `suggestion` goes at the end of the comment body as a ```` ```suggestion ```` block. GitHub replaces the
comment's whole range with it, so where the range had to be clipped, render the suggestion as a code block tagged with
the file's language instead.

- **Draft:** leave out `event`. The review stays `PENDING`, visible only to the publishing account, until the user
  submits it in the web UI. GitHub allows one pending review per account per pull request: list the reviews first
  (`gh api repos/<owner>/<repo>/pulls/<number>/reviews`), and if a `PENDING` one exists, stop and report it rather than
  adding to it or deleting it.
- **Publish:** set `event` to `REQUEST_CHANGES` for `request_changes`, and to `COMMENT` otherwise. Use `APPROVE` only when
  the user asked to approve: an approval is the user's merge decision, not the review's.

A comment on a line outside every hunk fails the whole request with HTTP 422 (`pull_request_review_thread.line`). Such a
finding belongs in the body (`in_diff: false`); if the request still fails, move the finding the error names into the
body and retry once.

## Replies and thread state

Reply to an earlier review comment, using the ID of the thread's first comment:

```shell
gh api --method POST repos/<owner>/<repo>/pulls/<number>/comments/<comment-id>/replies -F body=@/path/to/reply.md
```

That reply publishes at once, so use it only in publish mode. In draft mode, add the reply to the pending review
instead, with the review's `node_id` from the create response and the thread's node ID from the query below:

```shell
gh api graphql -f query='mutation($r:ID!,$t:ID!,$b:String!){addPullRequestReviewThreadReply(input:{
  pullRequestReviewId:$r,pullRequestReviewThreadId:$t,body:$b}){comment{id url}}}' \
  -f r=<review node_id> -f t=<thread-id> -F b=@/path/to/reply.md
```

Resolving a thread needs GraphQL and the thread's node ID:

```shell
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
  reviewThreads(first:100){nodes{id isResolved comments(first:1){nodes{databaseId author{login}}}}}}}}' \
  -f o=<owner> -f r=<repo> -F n=<number>
gh api graphql -f query='mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{isResolved}}}' -f t=<thread-id>
gh api graphql -f query='mutation($t:ID!){unresolveReviewThread(input:{threadId:$t}){thread{isResolved}}}' -f t=<thread-id>
```

The first comment's `author.login` is the thread owner for the main skill's ownership rule. Paginate `reviewThreads`
when a pull request has more than 100.

## Read-back

Read the created review and its comments back and compare path, side, start line, start side, line, and body with what
was sent:

```shell
gh api repos/<owner>/<repo>/pulls/<number>/reviews/<review-id>
gh api repos/<owner>/<repo>/pulls/<number>/reviews/<review-id>/comments
```

For a pending review the REST comments carry no `line`, `start_line`, or `side`; read the range back through GraphQL
instead, with the review's `node_id` from the create response:

```shell
gh api graphql -f query='query($r:ID!){node(id:$r){... on PullRequestReview{comments(first:100){nodes{
  id path startLine line body}}}}}' -f r=<review node_id>
```

Report the review ID and its `html_url`. For a pending review, the URL is visible only to the publishing account, and
the web UI shows its inline comments but not its body.

## Edit a comment of a pending review

Rewrite the body in place with the comment's node `id` from the query above; the range and the thread stay as they
are:

```shell
gh api graphql -f query='mutation($c:ID!,$b:String!){updatePullRequestReviewComment(input:{
  pullRequestReviewCommentId:$c,body:$b}){pullRequestReviewComment{id}}}' -f c=<comment node id> -F b=@/path/to/body.md
```

## Replace the body of a pending review

```shell
gh api --method PUT repos/<owner>/<repo>/pulls/<number>/reviews/<review-id> -F body=@/path/to/body.md
```

The review stays `PENDING`. Only the publishing account's pending review is rewritten this way.

The user may delete inline comments from the pending review before submitting it. To render the general comment again,
list the comments that are left with the `reviews/<review-id>/comments` command of *Read-back*, which includes the
pending ones, and match each to its finding by the tag at the start of its body.
