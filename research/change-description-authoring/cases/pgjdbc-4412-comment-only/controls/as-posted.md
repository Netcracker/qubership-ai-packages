### Why

Since 42.7.13, `PGXAConnection` no longer saves and restores the caller's `autoCommit` flag ([PR #4114](https://github.com/pgjdbc/pgjdbc/pull/4114)), and a number of comments in `PGXAConnection` and `XADataSourceTest` still describe the behavior that change removed. Three are wrong rather than merely dated, and a reader who trusts them reaches the opposite of what the code does:

* `State.ACTIVE`'s javadoc says "autoCommit is false on a connection returned by getConnection". Nothing sets it to false any more, and the class javadoc three hundred lines above now says the opposite.
* The comment in `getConnection()` described the `autoCommit=false` branch that the same change deleted.
* `XADataSourceTest` quoted `"2nd phase commit must be issued using an idle connection"` as a live precondition. That message went out with the fix, and it also came from `commitPrepared`, not from `recover()` where the comment placed it.

Two more claims contradicted the code beside them: the `recover()` comment said PostgreSQL requires the user to *own* a prepared transaction, where the `WHERE` clause filters on `pg_has_role(current_user, owner, 'member')`; and a batch test called the receive-buffer limit 64 KB, where `MAX_BUFFERED_RECV_BYTES` is 64000.

### What

Two commits, both confined to `PGXAConnection` and `XADataSourceTest`.

The first corrects the comments. Beyond the five factual repairs above, the edits are wording: history narrated in the present tense (`no longer`, `the new contract`), counterfactual branches the code does not have, positional references (`above`, `below`, `the latter`), notation standing in for words (`+`, `/`, `→`), and the enumerated list of XA SQL statements in the class javadoc, which a criterion replaces — every statement the class issues goes through `execSQLUpdate` or `execSQLQuery`, so the list would go stale the next time one is added. It also drops the `QUERY_SUPPRESS_BEGIN` rationale from four call sites, where the class javadoc now carries it once.

`State.ACTIVE` and the `getConnection()` comment were not in the set I set out to sweep. I edited them because the class javadoc I had just rewritten contradicts them in the same file; say the word and I will drop those two hunks.

The second commit renames two tests and the assertion messages under them, which named the same vanished save-and-restore:

| Old | New |
| --- | --- |
| `restoreOfAutoCommit` | `onePhaseBranch_leavesAutoCommitUnchanged` |
| `restoreOfAutoCommitEndThenJoin` | `endThenJoinBranch_leavesAutoCommitUnchanged` |

### Verification

No behavior changes, so the evidence is that none could have. Both files were parsed with comments discarded before and after the first commit and compare identical, so that commit is mechanically comment-only; across both commits `PGXAConnection` is still comment-only, and the only non-comment delta in `XADataSourceTest` is the two method names and three message literals. `compileJava`, `compileTestJava`, `checkstyleMain`, `checkstyleTest`, and `autostyleJavaCheck` are green. Neither old test name is referenced outside its declaration. The XA suite itself was not run; it needs a server with `max_prepared_transactions > 0`.

### Scope

No changelog entry: nothing here is observable to a user.

Two things I found and deliberately left alone. `Arrays.toString(recovered)` in `xaMethods_doNotChangeAutoCommit` is a dead statement whose old comment claimed it silenced an unused-variable warning; Error Prone is disabled for `compileTestJava`, so nothing in this build needs it. I removed the false claim and left the statement, since deleting it is a code change. And `PGXAConnection`'s `conn` field javadoc still lists three of the SQL commands it is used for, which the class javadoc's criterion now supersedes; it is not contradictory, so I left it.
