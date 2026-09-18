# The skill after each review round

Five snapshots of the same skill, taken before the first review and after each of four cross-review
rounds. Each file concatenates `SKILL.md` and the five reference files as they stood at that moment,
with `<!-- ===== path ===== -->` markers between them. The files are verbatim snapshots and are
excluded from the repository's linter.

They exist so that a later pass can compare the versions and merge the best of each, rather than
assuming the newest is the best. It is not: the loop fixed a real defect in almost every round, and it
also rewrote one rule five times, so some wording got sharper and some got longer for no gain.

| File | Taken | Carries |
| --- | --- | --- |
| `v1-after-synthesis.md` | before review | Written from the two-pass research, plus the two fixes the A/B trial produced |
| `v2-after-round1.md` | after round 1 | 15 review findings and 4 from a final-review pass |
| `v3-after-round2.md` | after round 2 | 5 review findings and 3 from a final-review pass |
| `v4-after-round3.md` | after round 3 | 6 review findings, a hand rework of the analysis test, 3 from a final-review pass |
| `v5-after-round4.md` | after round 4 | 11 review findings; the analysis rule rewritten from the accepted report's own wording |

Findings per round: 15, 5, 6, 11. Blocking: 9, 2, 2, 5. The rise in round 4 is not new ground; it is
nine findings against one rule that three consecutive rounds had each rewritten.

## What changed, by rule

Read this before diffing. Most rules moved once and stayed; one moved five times.

**The causal-analysis rule (five versions, and the reason to read all of them).** v1: analysis goes
after the reproducer, and the test asks that no mechanism sentence precede the symptom. v2: "at the
very end", plus a clause sending it to the form's context field, plus a clause about the form's
opening field — three placements at once. v3: anchored on the first mechanism sentence, which
conflicted with the rule that the target form's field order wins. v4: two questions, one about mixing
and one about gathering, whose "last place you chose" was unanswerable from a report and whose
per-sentence hedge requirement was refuted by the skill's own exemplar. v5: what the accepted report
itself says — mark the guess, and the report stands without it — plus a mixing question that excludes
the expected block, because grounding an expectation in the project's code is what §5 asks for. Each
version failed for a different reason; a merge should start from v5 and check any wording it borrows
against `gradle/gradle#39079`, which refuted three of the earlier versions.

**The boundary with `change-description-authoring`.** v1 claimed a change description "opens with the
mechanism". That is false: its first slot is the problem. v2 states the true difference, which is what
the reader already holds. Do not reintroduce the v1 sentence, however well it reads.

**The grounding order in the expected-behavior test.** v1 stated a measured correlation as an outcome
("the first three get fixed, the last four get closed as invalid") and put personal preference in the
group the source does not put it in. v2 states tendencies. v5 keeps one clause of reason, which is
deliberate: without it the order gets reordered under pressure.

**Scope.** v1 through v3 say "a project you do not maintain" on every surface. v4 widens the body, and
then all six surfaces (description, instruction, package README, package manifest, root manifest,
marketplace entry), because the body is read only after the skill has already loaded.

**Genre exceptions.** v1 said everything in the skill applies to a colleague message and to a request.
v2 cut that back to the research's genre matrix. v3 restored the ownership obligation for a request,
which v2 had wrongly dropped: the skill's own worked case shows an accepted request arguing why its
addressee is the right project.

**Two tests that could not be applied.** v1's ownership test demanded a command sequence using only
the target project, which a defect at a boundary can never satisfy; v2 admits the shortest failing
chain. v1's one-report-per-symptom test asked whether maintainers would fix both in one commit, a
prediction; v2 asks two observable questions and defaults to filing separately.

**The workaround.** v2 added the distinction between a workaround that works, which goes last, and a
setting that does not, which is a negative result and belongs right after the symptom. v3 and v4 moved
its position clauses around as the analysis rule moved; v5 drops the coupling entirely.

**The review checklist.** v1 reached about half the rules that state a test. v4 reaches all fifteen.

**Research material in the skill.** One reviewer filed this four times. Removed over the rounds: the
production narrative in the worked cases, a template-conformance study result, a response-speed claim,
"the reports this skill is drawn from". Kept deliberately, and rejected three times with the same
mechanism: the one-clause reasons behind the grounding order and the expected-behavior test. A merge
should decide this on purpose rather than by taking whichever version is shortest.

## What a merge should check its result against

- `gradle/gradle#39079` and `junit-team/junit-framework#6041`: the two accepted reports. Three
  versions of the analysis rule were refuted by the first one.
- `../trial/`: the A/B trial. Its treatment draft fails v5's mixing question, which is correct and
  recorded there.
- `../phase2_result.md` §3 and §4: the 45 extracted rules with their detections, and the genre matrix.
  Two round-1 fixes went wrong by following a matrix cell without checking its stated ground.
- `decisions/round<N>-fix-report.json`: 36 decision entries over 31 distinct findings, each with the
  evidence behind it. Five findings were decided in more than one round, one of them four times: three
  of those four entries are rejections of the same refiled claim, and reversing one silently would
  undo the rule the rejections were protecting.

## The merge

The five snapshots were merged on 2026-09-07 into the package as it now ships. What the merge took,
and from where:

- v5 for the causal-analysis rule, the position-free form override, and the workaround rule without
  its coupling to the analysis; these are also the formulations that hold inside a Jira description
  box and a plain-text mail, where no field order exists.
- v2 for the ownership test that admits the shortest failing chain, the two observable questions of
  the one-report-per-symptom rule, the tendency wording of the grounding order, and the true
  statement of the boundary with `change-description-authoring`.
- v3 for the ownership obligation kept in a request, and v4 for the scope on every loading surface
  and the checklist reaching every rule that states a test.
- Kept on purpose, against the four-times-filed research-material finding: the one-clause reasons
  behind the grounding order and the expected-behavior test.

What the merge changed beyond choosing between versions. The skill now covers any tracker and a
mailing list, so `project-conventions.md` says what to establish on any platform and where GitHub,
GitLab, Jira and Bugzilla, a list, and a team's own backlog keep it; the backlog section moved there
from `request-genre.md`, because it applies to a defect report as much as to a request. The skill
gained a markup rule, a security-routing line, and a hand-over note for what the agent could not do,
which generalizes the tracker-search hand-over the trial produced. It lost the sentences that were
research reporting rather than instruction: the ecosystem list in the ownership rule, the remark
that duplicate detection is an open research problem, and the summary of enhancement-proposal
processes. The package README had still described the analysis rule as "last and labeled a theory",
two rounds after the rule stopped saying so, and now matches the skill.

Two review passes ran over the merged text, each in a fresh session, with the two accepted reports as
the fixture. Most of what they found was a test the skill stated more strictly than the reports it
cites satisfy: the version had to appear in the pasted output, the search query had to be in the
report body, the negative-result setting had to sit above the ask, the count rule split what the
Gradle report keeps in one issue, the request reference said the reproducer lapses where the JUnit
request carries one, the colleague reference waived symptom-first in one sentence and kept it in the
next. Each test now admits both reports and still fails the trial's treatment draft where the earlier
versions failed it.
