export const meta = {
  name: 'deep-review',
  description: 'Multi-axis repository review: scout, evidence axes, per-axis refutation, distilled synthesis, consolidation',
  phases: [
    { title: 'Scout', detail: 'cheap axes that tell the others where to dig' },
    { title: 'Evidence', detail: 'one agent per review axis' },
    { title: 'Refute', detail: 'adversarial verification of each axis findings' },
    { title: 'Distill', detail: 'generate synthesis-axis prompts from the evidence' },
    { title: 'Synthesis', detail: 'architecture and other axes that need the evidence' },
    { title: 'Consolidate', detail: 'dedup, rank, completeness critic' },
  ],
}

// ---------------------------------------------------------------- inputs

// `args` normally arrives as an object, but a caller that hands the Workflow tool a JSON-encoded
// string gets it through verbatim — accept both rather than failing on line one.
const A = typeof args === 'string' ? JSON.parse(args) : args || {}
const dossier = A.dossier
const repo = A.repo
// Where this skill is installed. Every axis prompt points agents at reference packs underneath it, and the location
// differs per install (~/.claude/skills/ for a personal copy, .claude/skills/ for one apm deployed into a repository),
// so the caller passes the directory it read the skill from rather than the script guessing.
const skill = A.skill
const allAxes = A.axes || []
const models = A.models || {}
const wantCritic = A.completenessCritic !== false

if (!dossier || !repo) throw new Error('args.dossier and args.repo are required')
if (!skill) throw new Error('args.skill is required: the absolute path of the deep-review skill directory')
// An empty `axes` with a non-empty `priorAxes` is a consolidate-only run: re-merge and re-synthesize
// over reports already in the dossier. Needed after a report is added or corrected by hand.
if (allAxes.length === 0 && (A.priorAxes || []).length === 0) {
  throw new Error('args.axes is empty and no priorAxes given — nothing to review and nothing to consolidate')
}

const scoutAxes = allAxes.filter((a) => a.phase === 'scout')
const evidenceAxes = allAxes.filter((a) => a.phase === 'evidence' || !a.phase)
const synthAxes = allAxes.filter((a) => a.phase === 'synthesis')

const modelFor = (axis) => axis.model || models[axis.phase || 'evidence'] || models.default || 'sonnet'

// The verifier must not inherit the finder's model: the same reasoning that produced a finding is
// the reasoning least likely to break it. `models.refute` buys perspective diversity for one line.
const modelForStage = (axis, phase) =>
  phase === 'Refute' ? axis.refuteModel || models.refute || modelFor(axis) : modelFor(axis)

const optsFor = (axis, phase) => {
  const o = { label: `${phase}:${axis.key}`, phase, model: modelForStage(axis, phase) }
  if (axis.agentType) o.agentType = axis.agentType
  if (axis.effort) o.effort = axis.effort
  // Harness-level worktree isolation copies the SESSION's repository, which is only the right
  // thing when the session is running inside the repository under review. Otherwise the agent
  // lands in an unrelated checkout — see makeOwnWorktree below.
  if (axis.needsWriteAccess && A.sessionRepoIsTarget === true) o.isolation = 'worktree'
  return o
}

const makeOwnWorktree = A.sessionRepoIsTarget !== true

const isolationNote = (axis) => {
  if (!axis.needsWriteAccess) {
    return `

Do not modify ${repo}. If you need to change the project to measure it, create a throwaway copy first
(\`git worktree add ${dossier}/work/${axis.key}-wt HEAD\`) and remove it when you are done.`
  }
  if (makeOwnWorktree) {
    return `

**Your axis needs to modify the project, and you must not modify ${repo}.** Before you change anything, make your own
copy and work inside it:

\`\`\`bash
git -C ${repo} worktree add ${dossier}/work/${axis.key}-wt HEAD
cd ${dossier}/work/${axis.key}-wt
\`\`\`

Remove it when you are done (\`git -C ${repo} worktree remove --force ${dossier}/work/${axis.key}-wt\`). Verify with
\`git -C ${repo} status --porcelain\` that the repository is clean before you finish, and clean up any build output
you created there. Report the commands and edits you used to obtain a measurement so a maintainer can repeat them.

Ignore any pre-existing working directory the harness may have placed you in: the repository under review is
${repo} and nothing else. If your environment shows a different repository, that is expected — use the absolute
paths in this prompt.`
  }
  return `

You are running in a private git worktree — a throwaway copy of ${repo}. Modify it freely: add a coverage plugin,
write a probe test, break a condition to see whether the suite notices. The copy is discarded afterwards and the
user's working tree is never touched. The dossier path is absolute and outside the copy, so your report lands in the
right place. Report the commands and edits you used to obtain any measurement, so a maintainer can repeat it.`
}

// ---------------------------------------------------------------- schemas

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['axis', 'findings', 'coverage'],
  properties: {
    axis: { type: 'string' },
    coverage: {
      type: 'string',
      description: 'One or two sentences: what you actually examined, and what you could not reach and why.',
    },
    rejectedCandidates: {
      type: 'array',
      description:
        'What you considered and did NOT report, with the reason. This is the record of your own falsification work: the guard you found, the caller that never passes that value, the test that already covers it, the spec that permits it. Omitting it hides the half of the review that kept the report short — and leaves the verifier no way to resurrect something you dismissed too fast.',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['claim', 'whyRejected'],
        properties: {
          claim: { type: 'string', description: 'The defect you suspected, in one line, with the file.' },
          whyRejected: { type: 'string', description: 'The specific mechanism that made it a non-issue.' },
        },
      },
    },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['id', 'proposedSeverity', 'method', 'evidence', 'title', 'file', 'trigger', 'actual', 'expected', 'consequence'],
        properties: {
          id: { type: 'string', description: 'e.g. CONC-01' },
          proposedSeverity: {
            enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            description:
              'Your proposal, not the verdict. The verifier may lower it and the consolidator settles cross-axis disagreements.',
          },
          method: {
            enum: ['executed', 'traced', 'inferred'],
            description:
              'How you established this, honestly. executed = you ran something that demonstrates it and can quote the output. traced = you read every branch on the path. inferred = you reasoned from part of the code. You do NOT assign a confidence label; the verifier does.',
          },
          evidence: {
            type: 'string',
            description:
              'For executed: the exact command and the decisive line of its output. For traced: the branches you followed. For inferred: the assumption you did not check.',
          },
          title: { type: 'string' },
          file: { type: 'string', description: 'path:line, repo-relative' },
          trigger: { type: 'string' },
          actual: { type: 'string', description: 'What the code does today, under that trigger.' },
          expected: {
            type: 'string',
            description:
              'What it should do instead, and WHERE that is established: a specification section, a doc comment, the type signature, a sibling function that gets it right, or an ecosystem convention you can name. If nothing establishes the expectation, this is a preference, not a defect — drop it.',
          },
          consequence: { type: 'string' },
          fix: { type: 'string' },
          toolLimit: {
            type: 'string',
            description:
              'The documented limit of a technology from the profile\'s inventory that makes this defect possible (no recursion, no exceptions, fixed depth, undefined instead of error), naming the technology, whichever language the finding sits in. "none" for a finding in an artifact on an inventory technology where no limit is involved. Omit where no inventory technology is involved.',
          },
        },
      },
    },
  },
}

const VERDICTS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['axis', 'verdicts'],
  properties: {
    axis: { type: 'string' },
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['id', 'verdict', 'confidence', 'verifiedBy', 'reason'],
        properties: {
          id: { type: 'string' },
          verdict: { enum: ['upheld', 'downgraded', 'refuted'] },
          confidence: {
            enum: ['CONFIRMED', 'PLAUSIBLE'],
            description:
              'You alone assign this. CONFIRMED requires that YOU executed something whose output settles the claim. Anything else is PLAUSIBLE, however convincing the finding reads.',
          },
          verifiedBy: {
            enum: ['executed', 'read', 'none'],
            description: 'What you actually did. Must be "executed" for CONFIRMED.',
          },
          reason: {
            type: 'string',
            description:
              'For executed: the command and the decisive output line. For read: what you checked and what you could not settle. Never a paraphrase of the finding.',
          },
          newSeverity: { enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] },
        },
      },
    },
  },
}

const NOTE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['summary'],
  properties: { summary: { type: 'string' }, path: { type: 'string' } },
}

// ---------------------------------------------------------------- prompts

// Surface packs are lenses, not axes: several axes read the same pack, and the ownership table inside
// it decides which concern belongs to whom. That keeps one defect from being reported four times in
// four vocabularies, and it keeps form-specific rules out of the form-independent axis files.
const surfaces = A.surfaces || []
const surfaceNote = surfaces.length
  ? `

**Surface packs.** This repository exposes its API in the following forms: ${surfaces.join(', ')}. Read the packs for
them — ${surfaces.map((s) => `${skill}/references/surfaces/${s}.md`).join(', ')} — before you start. Each pack opens
with an ownership table saying which axis owns which concern on that surface: work your row and leave the others
alone, however tempting they look. The packs also name the normative source for that form, which is where the
"expected" half of a finding has to come from — an expectation you cannot attribute to a specification, a local
convention, or a documented rule is a preference, and preferences are not findings.`
  : ''

const preamble = `You are one agent in a multi-axis review of the repository at ${repo}.
The review dossier is ${dossier}. Read and write files there; use ${dossier}/work/ for scratch output.

Every path in this prompt is absolute, and that is deliberate: the dossier is how the agents of this review exchange
information, and it lives outside any working copy you may be given. **Always address it by its absolute path**, never
by a path relative to your current directory — a relative path silently writes into the wrong tree, and your report
will not exist as far as the rest of the pipeline is concerned.

Your final text is a return value consumed by a pipeline, not a message to a human — keep it to what the schema asks.`

const axisPrompt = (axis, extraInputs) => `${preamble}

You own the "${axis.key}" axis.

Read these, in order, and follow them:
1. ${skill}/references/common-rules.md — evidence bar, falsification, confidence labels, severity ladder
2. ${skill}/references/report-format.md — the report shape you must produce
3. ${skill}/references/axes/${axis.key}.md — your axis: its filter, its questions, what it must not report
4. ${dossier}/00-profile.md — what this repository is
5. ${dossier}/00-commands.md — the build, test, and tooling commands already known to work, with the flags they need.
   Every command in it has been executed by the profiler; use them instead of deriving your own. **The file is
   read-only for you.** Also read any ${dossier}/work/commands-*.md that exist — those are corrections left by earlier
   axes, and they are often the difference between a tool that runs and an hour lost.

   If a command fails for you, needs another flag, or you found one worth passing on, write your own
   ${dossier}/work/commands-${axis.key}.md — one file per axis, so parallel axes cannot overwrite each other. Create it
   only if you have something to say. State what you ran, what happened, and the fix.
6. ${dossier}/00-focus.md — the agreed focus and what is explicitly out of scope
${extraInputs}${surfaceNote}

Then do the work. Prefer executing things over reasoning about them: run the build, run the tests, write a throwaway
reproduction, run the ecosystem's analyzer.${isolationNote(axis)}

Stay inside your axis — anything real that belongs elsewhere goes in one
line under "Cross-axis notes".

**If 00-focus.md carries a directed question addressed to "${axis.key}", answering it is not optional.** Each such
question is addressed to exactly one axis, and yours is the only agent that will look at it. Answer it under a
"Направленные вопросы" heading in your report, one subsection per question, before the findings. If you could not
settle it, say that in the same place and say what you tried and what would settle it — a question you leave out
entirely reads downstream as a question nobody needed to ask. A directed question that turns out to have an answer
worth reporting becomes a normal finding as well; the heading is the record that the question was addressed, not a
substitute for raising what you found.

**You do not label your own findings CONFIRMED or PLAUSIBLE, and the severity you give is a proposal.** Confidence
belongs to the verifier who comes after you, because the author of an argument is the worst judge of it; severity is
adjusted by the verifier and settled by the consolidator, which is the only stage that sees every axis at once. What
you report instead is what you actually did — \`method\` and \`evidence\` — and those are claims the verifier will check.
Overstating \`executed\` when you only read the code is the one thing that will be caught immediately.

**Report what you rejected, too** (\`rejectedCandidates\`). Every review discards more than it reports, and right now
that work is invisible: the verifier only ever sees what survived your own filter, which is one reason verification
rates look suspiciously clean. List the defects you suspected and dropped, each with the mechanism that made it a
non-issue. A short report with ten rejected candidates says something very different from a short report with none.

Write the full report to ${dossier}/reports/${axis.key}.md in Russian, with identifiers and paths in English. Give
each finding a "Проверка:" line carrying your \`method\` and \`evidence\`; leave the confidence line out — the verifier
stamps it in afterwards.
Then write your findings, exactly as you are about to return them, one JSON object per line to
${dossier}/work/raw-${axis.key}.jsonl. This is the untouched pre-verification record: the verifier writes a separate
file, and having both is what lets a reader check afterwards which claims came from you and which judgements came
from the verification stage. Write it even if it duplicates what you return.

Then return the structured findings. The report and the structured findings must cover the same set, with the same ids.
If you genuinely found nothing after doing the work, return an empty findings array and still write the report — the
"Checked and sound" section is what tells the next reader your axis was covered.

**The structured output is your final act, not a checkpoint.** Emitting it ends your turn immediately: there is no
second chance to do the work afterwards. Call it exactly once, only after ${dossier}/reports/${axis.key}.md exists on
disk with the finished report in it. Never emit a placeholder, a progress note, or a "about to start" value — that
silently destroys the axis, and the pipeline will record it as an axis that ran and found nothing.`

const refutePrompt = (axis, payload) => `${preamble}

You are the adversarial verifier for the "${axis.key}" axis. Another agent produced these findings:

${JSON.stringify(payload.findings, null, 2)}

Its report is at ${dossier}/reports/${axis.key}.md, and the findings exactly as it raised them are in
${dossier}/work/raw-${axis.key}.jsonl. The rules it worked under are at ${skill}/references/common-rules.md; its axis
definition is at ${skill}/references/axes/${axis.key}.md.

That report also carries a "Отклонено автором" section: the defects the author suspected and dropped. **Read it, and
attack it in the opposite direction.** One of those dismissals is the most likely place for a missed defect, because
nobody has checked it at all — the finder rejected it and moved on. If a rejection does not hold, raise it as a new
finding of your own, with an id continuing the axis numbering, and say in your reason that it came from the rejected
list.

Note what the findings do **not** carry: a confidence label. The author cannot award one. Each finding states only
\`method\` (executed / traced / inferred) and \`evidence\` — a claim about the work done, which is itself something for
you to check. **You are the sole authority on \`confidence\`, and that is the substance of this job.**

The rule is mechanical, and you do not have discretion over it:

- \`CONFIRMED\` — **you** ran something whose output settles the claim, and you quote the command and the decisive
  line. Reproducing the author's artifact counts; taking their word for it does not. Set \`verifiedBy: "executed"\`.
- \`PLAUSIBLE\` — everything else, however convincing the finding reads and however thoroughly the author says they
  traced it. Reading the same lines the finding cites is \`verifiedBy: "read"\`, and reading is not confirming.

A previous run of this pipeline upheld 128 findings out of 128 and stamped 88 of them CONFIRMED, having executed
almost nothing. Half the verification notes were a second reading of the lines the finding already quoted. That is
the failure mode to avoid: the finding arrives with a ready-made argument, and agreeing with it feels like checking
it. Do not restate the finding back at me. Go and look for yourself, and where the claim is cheap to run, run it —
a probe, a unit test, a grep whose absence of hits is the answer.

You may need to modify the project to execute something. Never touch ${repo}: make your own copy first
(\`git -C ${repo} worktree add ${dossier}/work/verify-${axis.key}-wt HEAD\`), work there, and remove it when you are
done. Use ${dossier}/00-commands.md for the build and test invocations; they are known to work.

Now the verdict, which is a separate question from confidence. Your default is NOT "refuted" — it is "keep what you
cannot break":

- \`refuted\` — you can name the specific mechanism that makes the finding wrong, or the claim misreads the code.
- \`downgraded\` — the defect is real but smaller than claimed: narrower trigger, milder consequence, fewer callers
  reachable. Give \`newSeverity\` when severity is what changed.
- \`upheld\` — you attacked it and it held.

Also refute anything that belongs to a different axis or that the focus file put out of scope: verdict \`refuted\`,
reason starting with "out-of-scope:".

A \`FIT\` finding (architecture axis: a technology in a role it was not designed for) is refuted only as
common-rules.md says: with the upstream documentation, the workaround count, the findings it cites, or a documented
force in the domain. A passing build or a green test suite refutes nothing there, because the finding already assumes
the code works.

An \`upheld\` finding at \`PLAUSIBLE\` is a perfectly good outcome and the honest one whenever you did not execute
anything. Reserve \`CONFIRMED\` and it will start to mean something to the reader.

Then do two things.

1. Append one JSON object per line to ${dossier}/work/findings-${axis.key}.jsonl — every finding, refuted ones
   included, each with: id, axis, title, file, trigger, actual, expected, consequence, fix, tool_limit,
   proposed_severity, method, evidence (all the author's), plus severity (the author's proposal, or your \`newSeverity\` where you
   changed it), confidence, verified_by, verify_verdict, verify_reason (yours). Do not overwrite the file if it
   already has content; append.
2. Edit ${dossier}/reports/${axis.key}.md: stamp your \`confidence\` onto each finding block, move refuted findings
   into a closing section "## Отклонено при проверке" with the reason for each, and apply downgrades in place.
   Nothing disappears silently.

Return the verdicts.`

const distillPrompt = (axis, evidenceKeys) => `${preamble}

You are writing the review prompt for the "${axis.key}" axis, which runs next. You are not doing the review.

Read:
1. ${skill}/references/axes/${axis.key}.md — the invariant part of this axis, including its filter and report shape
2. ${skill}/references/common-rules.md and ${skill}/references/report-format.md
3. ${dossier}/00-profile.md and ${dossier}/00-focus.md
4. Every evidence report that exists: ${evidenceKeys.map((k) => `${dossier}/reports/${k}.md`).join(', ')}

Write a single self-contained prompt to ${dossier}/prompts/${axis.key}.md. It must:

- restate the axis filter in the concrete terms of THIS repository, with examples of what to reject;
- name the load-bearing mechanisms of this system, with file paths, so the reviewer can find them fast — describe them
  neutrally, so the reviewer judges them rather than inheriting your opinion;
- cluster the evidence findings into candidate root decisions, presented as LEADS TO FALSIFY, never as conclusions.
  State explicitly that restating an evidence finding is rejected, and that citing one as a symptom is correct;
- copy the technology inventory from 00-profile.md verbatim, and under each row list the evidence findings whose
  "Tool limit:" line names that technology, by id. A row with two or more is a lead for the axis's "check the grain"
  step; say so, and say that a row with none still needs a "checked and sound" line;
- list 8–12 pressure-test scenarios specific to this system and its domain — real changes, real failures, real
  migrations — not generic ones;
- name the prior art this genre has: which comparable systems solved these problems, so the reviewer can compare;${
  surfaces.length
    ? `
- carry over the "architectural questions this surface raises" section from each surface pack
  (${surfaces.map((s) => `${skill}/references/surfaces/${s}.md`).join(', ')}), rewritten in the concrete terms of this
  system — those questions are form-specific and the generic axis file cannot ask them;`
    : ''
}
- carry the report format from the axis file verbatim, including the finding block and the severity ladder;
- state the report language: Russian, identifiers and paths in English.

Length: whatever the repository needs, typically 150–300 lines. Do not pad. Return a two-sentence summary of the leads
you framed and the path you wrote.`

const runDistilledPrompt = (axis) => `${preamble}

You own the "${axis.key}" axis. Your instructions are in ${dossier}/prompts/${axis.key}.md — read that file and execute
it exactly. It supersedes the generic axis file where the two differ; where it is silent, fall back to
${skill}/references/axes/${axis.key}.md, ${skill}/references/common-rules.md, and
${skill}/references/report-format.md.

Write the report to ${dossier}/reports/${axis.key}.md, then return the structured findings.`

const consolidatePrompt = (keys) => `${preamble}

You are consolidating the whole review. Read ${dossier}/00-focus.md, every report in ${dossier}/reports/, and every
per-axis findings file in ${dossier}/work/findings-*.jsonl.

Do four things.

0. **Audit the run before you summarize it.** For every axis in the covered list, check that
   ${dossier}/reports/<axis>.md exists and holds a real report. An axis with no report file, or with a stub, did NOT
   run — whatever its findings file says. Report it as **failed**, never as "found nothing": the two look identical
   downstream and only one of them is good news. Do the same for any axis whose findings file is missing while its
   report exists. List every such axis at the top of the Покрытие section.

   **Then audit the directed questions the same way.** Read the \`## Directed questions\` section of
   ${dossier}/00-focus.md and list every question it carries with its owning axis. For each, find the answer in that
   axis's report — normally under its "Направленные вопросы" heading. A question with no answer anywhere is a hole in
   the run, not a question that turned out to be uninteresting, and it must appear in the Вердикт as an explicit
   "не отвечено", not merely in Покрытие. This is the one gap a reader cannot detect from the findings, because an
   unanswered question produces no output at all.

1. Write ${dossier}/findings.jsonl: one JSON object per line, merged from the per-axis files. Deduplicate — the same
   defect found by several axes becomes ONE line whose \`axes\` field lists all of them; keep the clearest
   description. Drop nothing: refuted findings stay, with their verdict. Keep \`tool_limit\` on the merged line. Add
   empty \`verdict\` and \`rejection_reason\` fields for the human triage that follows. A \`FIT\` finding whose
   verifier upheld it with the reason that the justifying force is undocumented gets \`severity\` \`ACCEPTED-DEBT\`.

   **You settle the final severity.** An axis proposes one and its verifier may lower it, but you are the only stage
   that sees every axis, so where two disagree about the same defect, decide — do not silently take the maximum.
   Keep \`proposed_severity\` alongside \`severity\` so the disagreement stays visible, and explain each adjudication
   in the Противоречия section. A synthesizing axis that bundled two defects under one severity is the usual reason
   its number differs from the specialist's; say so when that is what happened.
2. Write ${dossier}/synthesis.md in Russian (identifiers and paths in English):
   - **Вердикт** — at most fifteen lines: is this safe to ship, the three things to fix first, and the single biggest
     risk. No hedging.
   - **Сводная таблица** — every surviving finding: id, axis, severity, confidence, one-line claim, file.
   - **Кластеры** — groups of findings that share a root cause, each with the cause named. This is the most valuable
     section; spend your budget here. A \`FIT\` finding names the evidence findings it explains: cluster those under
     it, and carry the \`tool_limit\` line of each.
   - **Противоречия между осями** — where two axes disagree about the same code, with your reading of who is right.
   - **Направленные вопросы** — one row per question from 00-focus.md: the question, its owning axis, and the
     answer or the word "не отвечено". Put this section directly after Вердикт, not at the end: an unanswered
     directed question is more actionable than most findings, and burying it is how it gets lost twice.
   - **Покрытие** — which axes ran, what each says it could not reach, and which axes did not run at all. Include
     the negative checks the axes actually executed and the count of candidates each one rejected on its own: an axis
     that reported five findings and no rejections either got lucky or did not look hard, and the reader should be
     able to tell those apart.
   - **Отклонено при проверке** — the count per axis, and the three most interesting refutations, because they say
     something about the reviewers as well as the code. Report the verification rate here too: how many findings a
     verifier actually executed something for (\`verified_by: executed\`) versus merely read, and the resulting
     CONFIRMED/PLAUSIBLE split. Confidence is assigned by the verify stage, never by the axis that raised the
     finding — if a per-axis file carries a confidence the verifier did not set, say so, because it means an agent
     went around the rule. A run where almost nothing was executed is a run whose CONFIRMED labels mean little, and
     the reader is entitled to know that before acting on them.
3. Return the counts.

Rank by severity, then confidence, then blast radius. Do not soften anything; do not invent anything that is not in
the inputs. Axes covered: ${keys.join(', ')}.`

const criticPrompt = (keys) => `${preamble}

You are the completeness critic, and you run last: the consolidator has already written
${dossier}/findings.jsonl and ${dossier}/synthesis.md, so critique what is actually there. Read
${dossier}/00-profile.md, ${dossier}/00-focus.md, every report in ${dossier}/reports/, and those two outputs.
Axes that ran: ${keys.join(', ')}.

${dossier}/00-commands.md was written by a human before the run and is not above suspicion — if a claim in it turns
out to be false, that is a finding about the review, and a valuable one: every axis trusted that file.

Answer one question: what is missing? Specifically —
- which part of the codebase no axis actually looked at, by path;
- which claim in the profile or the focus file no report addresses;
- which row of the profile's technology inventory has neither a \`FIT\` finding nor a "checked and sound" line in the
  architecture report;
- which axis reports coverage so thin that its "Checked and sound" section is not credible;
- which finding rests on an assumption nobody verified, and what one command would settle it;
- which axis should have run and did not, given the archetype in the profile.

Be specific and short. Write ${dossier}/work/completeness.md, then return a two-sentence summary. Do not review the
code yourself and do not add findings.`

// ---------------------------------------------------------------- pipeline

const scoutKeys = scoutAxes.map((a) => a.key)
const scoutInputs = scoutKeys.length
  ? `7. The scout reports already written: ${scoutKeys.map((k) => `${dossier}/reports/${k}.md`).join(', ')} — read
   "Where the suite is blind" first if it is there; it says where defects survive.`
  : ''

const runAxis = (axis, extra) => agent(axisPrompt(axis, extra), { ...optsFor(axis, axis.phase === 'scout' ? 'Scout' : 'Evidence'), schema: FINDINGS_SCHEMA })

const refuteStage = (result, axis) => {
  if (!result) return null
  if (!result.findings || result.findings.length === 0) {
    log(`${axis.key}: no findings, skipping refutation`)
    return { axis: axis.key, findings: [], verdicts: [], coverage: result.coverage }
  }
  return agent(refutePrompt(axis, result), { ...optsFor(axis, 'Refute'), schema: VERDICTS_SCHEMA }).then((v) => ({
    axis: axis.key,
    coverage: result.coverage,
    findings: result.findings,
    verdicts: (v && v.verdicts) || [],
  }))
}

const survivors = (r) => {
  if (!r) return 0
  if (!r.verdicts || r.verdicts.length === 0) return r.findings ? r.findings.length : 0
  return r.verdicts.filter((v) => v.verdict !== 'refuted').length
}

phase('Scout')
// The barrier belongs after the scout REPORTS, not after their refutation. Evidence axes read the
// reports; nothing downstream reads a scout verdict before consolidation. Blocking the whole
// evidence phase on the scout verifier is dead time — on a real run, ten idle agents for as long
// as the verifier takes. So: await the reports, then let refutation run alongside the evidence.
let scoutRefutation = null
if (scoutAxes.length) {
  log(`Scout: ${scoutKeys.join(', ')}`)
  const scoutFindings = await parallel(scoutAxes.map((a) => () => runAxis(a, '')))
  log('Scout reports written; refutation continues in the background')
  scoutRefutation = parallel(scoutAxes.map((a, i) => () => refuteStage(scoutFindings[i], a)))
}

phase('Evidence')
log(`Evidence axes: ${evidenceAxes.map((a) => a.key).join(', ') || '(none)'}`)
const evidenceResults = evidenceAxes.length
  ? await pipeline(evidenceAxes, (a) => runAxis(a, scoutInputs), refuteStage)
  : []

const scoutResults = scoutRefutation ? (await scoutRefutation).filter(Boolean) : []

const doneKeys = [...scoutAxes, ...evidenceAxes].map((a) => a.key)
log(`Evidence complete: ${doneKeys.length} axes, ${[...scoutResults, ...evidenceResults].reduce((n, r) => n + survivors(r), 0)} findings survived refutation`)

phase('Distill')
const synthResults = synthAxes.length
  ? await pipeline(
      synthAxes,
      (a) => agent(distillPrompt(a, doneKeys), { label: `distill:${a.key}`, phase: 'Distill', model: modelFor(a), schema: NOTE_SCHEMA }),
      (note, a) => {
        if (!note) {
          log(`${a.key}: distillation failed, skipping the axis`)
          return null
        }
        return agent(runDistilledPrompt(a), { ...optsFor(a, 'Synthesis'), schema: FINDINGS_SCHEMA })
      },
      refuteStage,
    )
  : []

phase('Consolidate')
// `priorAxes` lets a targeted re-run of one axis consolidate over reports an earlier run left in
// the dossier, instead of producing a synthesis that silently covers only the axis just executed.
const priorAxes = A.priorAxes || []
const allKeys = [...priorAxes, ...doneKeys, ...synthAxes.map((a) => a.key)]
// Sequential, not parallel: the critic inspects what the consolidator produced. Run concurrently, it
// reads findings.jsonl before that file exists and reports it as empty — which is how a measured run
// ended up with a critic claiming the consolidator wrote nothing while the consolidator wrote 70 lines.
const consolidated = await agent(consolidatePrompt(allKeys), {
  label: 'consolidate',
  phase: 'Consolidate',
  model: models.consolidate || models.default || 'sonnet',
  schema: NOTE_SCHEMA,
})
const critique = wantCritic
  ? await agent(criticPrompt(allKeys), {
      label: 'completeness-critic',
      phase: 'Consolidate',
      model: models.critic || models.default || 'sonnet',
      schema: NOTE_SCHEMA,
    })
  : null
const tail = [consolidated, critique]

const all = [...scoutResults, ...evidenceResults, ...synthResults]
const ranThisTime = [...scoutAxes, ...evidenceAxes, ...synthAxes].map((a) => a.key)
const failed = ranThisTime.filter((k) => !all.some((r) => r && r.axis === k))

return {
  dossier,
  axes: allKeys,
  axesFailed: failed,
  raised: all.reduce((n, r) => n + (r && r.findings ? r.findings.length : 0), 0),
  survived: all.reduce((n, r) => n + survivors(r), 0),
  perAxis: all.filter(Boolean).map((r) => ({ axis: r.axis, raised: r.findings.length, survived: survivors(r) })),
  consolidate: tail[0] && tail[0].summary,
  completeness: tail[1] && tail[1].summary,
  read: [`${dossier}/synthesis.md`, `${dossier}/findings.jsonl`, `${dossier}/work/completeness.md`],
}
