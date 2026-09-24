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
// `coarse` reviews contracts, boundaries, and deployables and executes only what already exists (the suite, a render,
// a runtime probe). `deep` adds unit-level work: reproduction tests, mutation runs, stress tests. The questions file
// decides; coarse is the default because the skill targets a repository, a microservice, or a system, not a class.
const depth = A.depth || 'coarse'
// A system review names its components. Each one is a checkout the axes read; `repo` stays the checkout that hosts the
// dossier and is the first component unless the list says otherwise.
const components = A.components || []
// The packs that ship under references/surfaces/. Every entry of `surfaces` becomes a path agents are told to read, so
// an unknown name is refused here rather than sending every axis to a missing file.
const KNOWN_PACKS = ['cli', 'gitops-argocd', 'helm', 'helm-qubership', 'kubernetes', 'mcp']
const PHASES = ['scout', 'evidence', 'synthesis']
const DEPTHS = ['coarse', 'deep']

if (!dossier || !repo) throw new Error('args.dossier and args.repo are required')
if (!skill) throw new Error('args.skill is required: the absolute path of the deep-review skill directory')
if (!skill.startsWith('/')) {
  throw new Error(`args.skill must be an absolute path; got "${skill}" (an unexpanded placeholder sends every axis to read from memory)`)
}
if (!DEPTHS.includes(depth)) throw new Error(`args.depth must be one of ${DEPTHS.join(', ')}; got "${depth}"`)
// An empty `axes` with a non-empty `priorAxes` is a consolidate-only run: re-merge and re-synthesize
// over reports already in the dossier. Needed after a report is added or corrected by hand.
if (allAxes.length === 0 && (A.priorAxes || []).length === 0) {
  throw new Error('args.axes is empty and no priorAxes given — nothing to review and nothing to consolidate')
}
for (const axis of allAxes) {
  if (!axis.key) throw new Error(`every entry of args.axes needs a key; got ${JSON.stringify(axis)}`)
  if (axis.phase && !PHASES.includes(axis.phase)) {
    throw new Error(`axis "${axis.key}": phase must be one of ${PHASES.join(', ')}; got "${axis.phase}"`)
  }
}
for (const c of components) {
  if (!c.name || !c.repo) throw new Error(`every entry of args.components needs name and repo; got ${JSON.stringify(c)}`)
}

const surfaces = A.surfaces || []
// Forms the profile named that have no pack in references/surfaces/. They are kept apart from `surfaces` because
// every entry there becomes a pack path the agents are told to read.
const surfacesWithoutPack = A.surfacesWithoutPack || []
for (const s of surfaces) {
  if (!KNOWN_PACKS.includes(s)) {
    throw new Error(`args.surfaces names "${s}", which has no pack under references/surfaces/; move it to args.surfacesWithoutPack`)
  }
}

const scoutAxes = allAxes.filter((a) => a.phase === 'scout')
const evidenceAxes = allAxes.filter((a) => a.phase === 'evidence' || !a.phase)
const synthAxes = allAxes.filter((a) => a.phase === 'synthesis')
const axisKeys = allAxes.map((a) => a.key)

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

// Resume returns the longest unchanged prefix of agent calls from cache. The attempt number is part of the prompt, so
// bumping it on one axis re-runs that axis and every call sequenced after it, while the calls before it come back
// from cache.
const attemptNote = (axis) => (axis.attempt && axis.attempt > 1 ? `\n\nAttempt ${axis.attempt} of this axis.` : '')

const checkouts = components.length ? components : [{ name: 'the repository', repo }]

// Paths come from the user and component names from the profile, so every one is quoted for the shell, and a
// component name becomes a path segment only after everything but letters, digits, dots, and hyphens is replaced.
const q = (s) => `'${String(s).replace(/'/g, `'\\''`)}'`
const slug = (s) => String(s).replace(/[^A-Za-z0-9.-]+/g, '-')
const worktreePath = (axis, prefix, c) =>
  `${dossier}/work/${prefix}${axis.key}-wt${components.length ? `-${slug(c.name)}` : ''}`

const worktreeCommands = (axis, prefix) =>
  checkouts.map((c) => `git -C ${q(c.repo)} worktree add ${q(worktreePath(axis, prefix, c))} HEAD`).join('\n')

const cleanupCommands = (axis, prefix) =>
  checkouts.map((c) => `git -C ${q(c.repo)} worktree remove --force ${q(worktreePath(axis, prefix, c))}`).join('\n')

const statusCommands = () => checkouts.map((c) => `git -C ${q(c.repo)} status --porcelain`).join('\n')

const isolationNote = (axis) => {
  if (!axis.needsWriteAccess) {
    return `

Do not modify ${checkouts.map((c) => c.repo).join(' or ')}. If you need to change the project to measure it, create a
throwaway copy first and remove it when you are done:

\`\`\`bash
${worktreeCommands(axis, '')}
\`\`\``
  }
  if (makeOwnWorktree) {
    return `

**Your axis needs to modify the project, and you must not modify ${checkouts.map((c) => c.repo).join(' or ')}.**
Before you change anything, make your own copy and work inside it:

\`\`\`bash
${worktreeCommands(axis, '')}
\`\`\`

Remove the copies when you are done:

\`\`\`bash
${cleanupCommands(axis, '')}
\`\`\`

Verify that every checkout is clean before you finish, and clean up any build output you created there:

\`\`\`bash
${statusCommands()}
\`\`\`

Report the commands and edits you used to obtain a measurement so a maintainer can repeat them.

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

const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['axis', 'findings', 'coverage', 'rejectedCandidates'],
  properties: {
    axis: { type: 'string' },
    coverage: {
      type: 'string',
      description: 'One or two sentences: what you actually examined, and what you could not reach and why.',
    },
    rejectedCandidates: {
      type: 'array',
      description:
        'What you considered and did NOT report, with the reason. This is the record of your own falsification work: the guard you found, the caller that never passes that value, the test that already covers it, the spec that permits it. Omitting it hides the half of the review that kept the report short — and leaves the verifier no way to resurrect something you dismissed too fast. An empty array is a claim that you rejected nothing.',
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
            enum: SEVERITIES,
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
          file: { type: 'string', description: 'path:line, relative to the checkout named in `component` (or to the repository when there is one)' },
          component: {
            type: 'string',
            description: 'On a system review: the component name from the profile that `file` is relative to. Omit on a single-repository review.',
          },
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
          fit: {
            type: 'object',
            description: 'Only for a FIT finding of the architecture axis: the block fields that have no slot above.',
            additionalProperties: false,
            properties: {
              designedFor: { type: 'string' },
              signalsMeasured: { type: 'string' },
              findingsGenerated: { type: 'array', items: { type: 'string' } },
              forceInDomain: { type: 'string' },
              alternative: { type: 'string' },
              costToChange: { type: 'string' },
            },
          },
          settles: {
            type: 'string',
            description:
              'Only for the runtime-verification axis: the id of the finding from another axis that this execution settles. The consolidator applies `runtimeVerdict` to that finding.',
          },
          runtimeVerdict: {
            enum: ['demonstrated', 'refuted', 'narrowed', 'widened', 'not-reproducible'],
            description: 'Only with `settles`: what the runtime showed about that finding.',
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
          newSeverity: { enum: SEVERITIES },
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
const surfaceNote = (surfaces.length
  ? `

**Surface packs.** This repository exposes its API in the following forms: ${surfaces.join(', ')}. Read the packs for
them — ${surfaces.map((s) => `${skill}/references/surfaces/${s}.md`).join(', ')} — before you start. Each pack
carries an ownership table saying which axis owns which concern on that surface: work your row and leave the others
alone, however tempting they look. The axes in this run are: ${axisKeys.join(', ')}. Where a pack routes a concern to
an axis that is not in this run, the concern has no owner: if it is in reach of your axis, report it and say in the
finding which row you took it from; otherwise record it in one line under "Cross-axis notes" so the consolidator can
list it as uncovered. The packs also name the normative source for that form where one exists, which is where the
"expected" half of a finding has to come from — an expectation you cannot attribute to a specification, a local
convention, or a documented rule is a preference, and preferences are not findings.`
  : '') + (surfacesWithoutPack.length
  ? `

**Forms without a pack.** The repository also exposes its API as ${surfacesWithoutPack.join(', ')}. The skill has no
pack for these forms, so judge them by your axis file's form-independent rules, take the "expected" half of a finding
from the form's own specification or the repository's documented conventions, and list each of these forms in your
coverage section as reviewed without a pack.`
  : '')

const depthNote = depth === 'coarse'
  ? `

**Depth: coarse.** This review is about contracts, boundaries, deployables, and the decisions behind them, not about
individual functions. Execute what already exists: the build, the test suite, a render, a scanner, a probe against a
runtime the focus file allows. Do not write per-function reproduction tests, do not run mutation testing, do not
write stress tests; where your axis file asks for one of those, replace it with the cheapest existing artifact that
answers the same question, and say in your coverage section what you did not do. A finding at this depth names a
contract, a boundary, a configuration surface, or a failure domain, and cites the code that carries it.`
  : `

**Depth: deep.** Unit-level work is in scope: reproduction tests, mutation runs, stress tests, whatever your axis file
asks for, inside your throwaway copy.`

const componentNote = components.length
  ? `

**This is a system review.** The components, each a checkout you can read:

${components.map((c) => `- \`${c.name}\`: ${c.repo}${c.ref ? ` at ${c.ref}` : ''}${c.role ? ` — ${c.role}` : ''}`).join('\n')}

The profile at ${dossier}/00-profile.md says how they interact. Findings about the interaction between two components
are the point of a system review: a contract one component publishes and another consumes, a failure in one that
propagates to another, a schema or a topic two of them share. Set \`component\` on every finding to the name above
that its \`file\` is relative to, and name both components in a finding about an interaction.`
  : ''

const preamble = `You are one agent in a multi-axis review of the repository at ${repo}.
The review dossier is ${dossier}. Read and write files there; use ${dossier}/work/ for scratch output.

Every path in this prompt is absolute, and that is deliberate: the dossier is how the agents of this review exchange
information, and it lives outside any working copy you may be given. **Always address it by its absolute path**, never
by a path relative to your current directory — a relative path silently writes into the wrong tree, and your report
will not exist as far as the rest of the pipeline is concerned.

Your final text is a return value consumed by a pipeline, not a message to a human — keep it to what the schema asks.`

// The part of an axis prompt that every axis needs, whether its instructions come from the axis file or from a
// distilled prompt: the rules about confidence, rejected candidates, the raw findings file, and the final act.
const axisTail = (axis) => `${depthNote}${componentNote}${isolationNote(axis)}

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
${dossier}/work/raw-${axis.key}.jsonl, replacing the file if it exists. This is the untouched pre-verification record:
the verifier writes a separate file, and with both on disk a reader can check afterwards which claims came from you
and which judgements came from the verification stage. Write it even if it duplicates what you return.

Then return the structured findings. The report and the structured findings must cover the same set, with the same ids.
If you genuinely found nothing after doing the work, return an empty findings array and still write the report — the
"Checked and sound" section is what tells the next reader your axis was covered.

**The structured output is your final act, not a checkpoint.** Emitting it ends your turn immediately: there is no
second chance to do the work afterwards. Call it exactly once, only after ${dossier}/reports/${axis.key}.md exists on
disk with the finished report in it. Never emit a placeholder, a progress note, or a "about to start" value — that
silently destroys the axis, and the pipeline will record it as an axis that ran and found nothing.${attemptNote(axis)}`

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

Then do the work. Prefer executing things over reasoning about them: run the build, run the tests, run the
ecosystem's analyzer.${axisTail(axis)}`

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

You may need to modify the project to execute something. Never touch ${checkouts.map((c) => c.repo).join(' or ')}: make
your own copy first, work there, and remove it when you are done:

\`\`\`bash
${worktreeCommands(axis, 'verify-')}
\`\`\`

Use ${dossier}/00-commands.md for the build and test invocations; they are known to work.${depthNote}

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

1. Write ${dossier}/work/findings-${axis.key}.jsonl, one JSON object per line — every finding, refuted ones included,
   and every finding you raised yourself. If the file already exists, first move it to
   ${dossier}/work/history/findings-${axis.key}.<n>.jsonl with the next free <n> (create the directory if it is
   missing), so the current file holds exactly this verification and the history stays readable. Field names are snake_case and fixed, because the consolidator
   and the post-mortem read them by name:
   - the author's, copied from the structured finding: \`id\`, \`axis\`, \`title\`, \`file\`, \`component\`, \`trigger\`,
     \`actual\`, \`expected\`, \`consequence\`, \`fix\`, \`tool_limit\` (from \`toolLimit\`), \`proposed_severity\` (from
     \`proposedSeverity\`), \`method\`, \`evidence\`, and \`fit\`, \`settles\`, \`runtime_verdict\` where present;
   - yours: \`severity\` (the proposal, or your \`newSeverity\` where you changed it), \`confidence\`, \`verified_by\`,
     \`verify_verdict\`, \`verify_reason\`.
2. Edit ${dossier}/reports/${axis.key}.md: stamp your \`confidence\` onto each finding block, move refuted findings
   into a closing section "## Отклонено при проверке" with the reason for each, and apply downgrades in place.
   Nothing disappears silently.

Return the verdicts.${attemptNote(axis)}`

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
- where the axis file has a "check the grain" step: copy the technology inventory from 00-profile.md verbatim, and
  under each row list the evidence findings whose "Tool limit:" line names that technology, by id. A row with two or
  more is a lead for that step; say so, and say that a row with none still needs a "checked and sound" line;
- list 8–12 pressure-test scenarios specific to this system and its domain — real changes, real failures, real
  migrations — not generic ones;
- name the prior art this genre has: which comparable systems solved these problems, so the reviewer can compare;${
  surfaces.length
    ? `
- carry over the "Architectural questions this surface raises" section from each surface pack that has one
  (${surfaces.map((s) => `${skill}/references/surfaces/${s}.md`).join(', ')}), rewritten in the concrete terms of this
  system — those questions are form-specific and the generic axis file cannot ask them;`
    : ''
}
- carry the report format from the axis file verbatim, including the finding block; severity uses the common ladder
  from common-rules.md on every axis;
- state the report language: Russian body text, headings as report-format.md writes them, identifiers and paths in
  English.

Length: whatever the repository needs, typically 150–300 lines. Do not pad. Return a two-sentence summary of the leads
you framed and the path you wrote.${attemptNote(axis)}`

const runDistilledPrompt = (axis) => `${preamble}

You own the "${axis.key}" axis. Your instructions are in ${dossier}/prompts/${axis.key}.md — read that file and execute
it exactly. It supersedes the generic axis file where the two differ; where it is silent, fall back to
${skill}/references/axes/${axis.key}.md, ${skill}/references/common-rules.md, and
${skill}/references/report-format.md. Read ${dossier}/00-commands.md and any ${dossier}/work/commands-*.md before you
run anything.${surfaceNote}${axisTail(axis)}`

const consolidatePrompt = (keys, cleanAxes, unverifiedAxes) => `${preamble}

You are consolidating the whole review. Read ${dossier}/00-focus.md, every report in ${dossier}/reports/, and every
per-axis findings file in ${dossier}/work/findings-*.jsonl.${componentNote}

Do four things.

0. **Audit the run before you summarize it.** For every axis in the covered list, check that
   ${dossier}/reports/<axis>.md exists and holds a real report. An axis with no report file, or with a stub, did NOT
   run — whatever its findings file says. Report it as **failed**, never as "found nothing": the two look identical
   downstream and only one of them is good news. An axis with a report and no findings file is one of two things:
   ${cleanAxes.length ? `these axes completed with zero findings, so no verifier ran and the report's "Checked and sound" section is their evidence: ${cleanAxes.join(', ')}. ` : ''}${unverifiedAxes.length ? `for these axes the verifier failed, so their findings are unverified — carry them at PLAUSIBLE, say so on every one, and list the axis under verification failures: ${unverifiedAxes.join(', ')}. ` : ''}Any other axis with a report and no findings file failed
   between report and verification; report it as failed. List every such axis at the top of the Покрытие section.

   **Then audit the directed questions the same way.** Read the \`## Directed questions\` section of
   ${dossier}/00-focus.md and list every question it carries with its owning axis. For each, find the answer in that
   axis's report — normally under its "Направленные вопросы" heading. A question with no answer anywhere is a hole in
   the run, not a question that turned out to be uninteresting, and it must appear in the Вердикт as an explicit
   "не отвечено", not merely in Покрытие. This is the one gap a reader cannot detect from the findings, because an
   unanswered question produces no output at all.

1. Write ${dossier}/findings.jsonl: one JSON object per line, merged from the per-axis files. Deduplicate — the same
   defect found by several axes becomes ONE line whose \`axes\` field lists all of them; keep the clearest
   description. Drop nothing: refuted findings stay, with their verdict. Keep \`tool_limit\` and \`component\` on the
   merged line. Add empty \`verdict\` and \`rejection_reason\` fields for the human triage that follows. A \`FIT\`
   finding whose verifier upheld it with the reason that the justifying force is undocumented gets \`severity\`
   \`ACCEPTED-DEBT\`.

   **Apply the runtime verdicts.** A finding of the runtime-verification axis with a \`settles\` field is a verdict on
   another finding, not a defect of its own: \`demonstrated\` sets that finding's \`confidence\` to CONFIRMED with the
   runtime evidence as \`verify_reason\`; \`refuted\` sets \`verify_verdict\` to refuted with the runtime's reason;
   \`narrowed\` and \`widened\` set \`severity\` to the runtime's proposal and record the old one in
   \`proposed_severity\`; \`not-reproducible\` leaves the finding as it was and adds the runtime's doubt to
   \`verify_reason\`. Record on the settled line which RUN finding settled it. A RUN finding without \`settles\` is an
   ordinary defect.

   **You settle the final severity.** An axis proposes one and its verifier may lower it, but you are the only stage
   that sees every axis, so where two disagree about the same defect, decide — do not silently take the maximum.
   Keep \`proposed_severity\` alongside \`severity\` so the disagreement stays visible, and explain each adjudication
   in the Противоречия section. A synthesizing axis that bundled two defects under one severity is the usual reason
   its number differs from the specialist's; say so when that is what happened.
2. Write ${dossier}/synthesis.md in Russian (identifiers and paths in English):
   - **Вердикт** — at most fifteen lines: is this safe to ship, the three things to fix first, and the single biggest
     risk. No hedging.
   - **Сводная таблица** — every surviving finding: id, axis, severity, confidence, one-line claim, file${components.length ? ', component' : ''}.
   - **Кластеры** — groups of findings that share a root cause, each with the cause named. This is the most valuable
     section; spend your budget here. A \`FIT\` finding names the evidence findings it explains: cluster those under
     it, and carry the \`tool_limit\` line of each.${components.length ? `
   - **Взаимодействия компонентов** — every finding that names two components, grouped by the pair, and every
     interaction the profile names that no finding and no "Checked and sound" line covers.` : ''}
   - **Противоречия между осями** — where two axes disagree about the same code, with your reading of who is right.
   - **Направленные вопросы** — one row per question from 00-focus.md: the question, its owning axis, and the
     answer or the word "не отвечено". Put this section directly after Вердикт, not at the end: an unanswered
     directed question is more actionable than most findings, and burying it is how it gets lost twice.
   - **Покрытие** — which axes ran, what each says it could not reach, which axes did not run at all, and every
     concern a surface pack routes to an axis that was not in the run (the axes list them under "Cross-axis notes").
     Include the negative checks the axes actually executed and the count of candidates each one rejected on its own:
     an axis that reported five findings and no rejections either got lucky or did not look hard, and the reader
     should be able to tell those apart.
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
Axes that ran: ${keys.join(', ')}.${componentNote}

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

// A synthesis axis whose subject is the verified findings themselves (runtime-verification) reads the per-axis
// findings files directly and needs no distilled prompt. The axis entry says so with `distill: false`.
const verifiedInputs = (keys) => `7. The verified findings of the axes that ran before you, one file per axis:
   ${keys.map((k) => `${dossier}/work/findings-${k}.jsonl`).join(', ')} (an axis with no such file found nothing or
   failed; its report says which), the reports behind them in ${dossier}/reports/, and the findings exactly as raised
   in ${dossier}/work/raw-*.jsonl.`

const runAxis = (axis, extra) => agent(axisPrompt(axis, extra), { ...optsFor(axis, axis.phase === 'scout' ? 'Scout' : 'Evidence'), schema: FINDINGS_SCHEMA })

// Three outcomes, kept apart because the consolidator treats them differently: the axis found nothing (clean, no
// verifier ran), the axis found something and the verifier returned verdicts, or the verifier died (unverified).
const refuteStage = (result, axis) => {
  if (!result) return null
  if (!result.findings || result.findings.length === 0) {
    log(`${axis.key}: no findings, skipping refutation`)
    return { axis: axis.key, findings: [], verdicts: [], clean: true, coverage: result.coverage }
  }
  return agent(refutePrompt(axis, result), { ...optsFor(axis, 'Refute'), schema: VERDICTS_SCHEMA }).then((v) => {
    if (!v || !v.verdicts) log(`${axis.key}: verifier returned nothing; findings are unverified`)
    return {
      axis: axis.key,
      coverage: result.coverage,
      findings: result.findings,
      verdicts: (v && v.verdicts) || [],
      verifyFailed: !v || !v.verdicts,
    }
  })
}

const survivors = (r) => {
  if (!r || r.verifyFailed) return 0
  return r.verdicts.filter((v) => v.verdict !== 'refuted').length
}

const raisedByVerifier = (r) => {
  if (!r || !r.verdicts) return 0
  const ids = new Set(r.findings.map((f) => f.id))
  return r.verdicts.filter((v) => !ids.has(v.id)).length
}

// The barrier belongs after the scout REPORTS, not after their refutation. Evidence axes read the
// reports; nothing downstream reads a scout verdict before consolidation. Blocking the whole
// evidence phase on the scout verifier is dead time — on a real run, ten idle agents for as long
// as the verifier takes. So: await the reports, then let refutation run alongside the evidence.
let scoutRefutation = null
if (scoutAxes.length) {
  phase('Scout')
  log(`Scout: ${scoutKeys.join(', ')}`)
  const scoutFindings = await parallel(scoutAxes.map((a) => () => runAxis(a, '')))
  log('Scout reports written; refutation continues in the background')
  scoutRefutation = parallel(scoutAxes.map((a, i) => () => refuteStage(scoutFindings[i], a)))
}

let evidenceResults = []
if (evidenceAxes.length) {
  phase('Evidence')
  log(`Evidence axes: ${evidenceAxes.map((a) => a.key).join(', ')}`)
  evidenceResults = await pipeline(evidenceAxes, (a) => runAxis(a, scoutInputs), refuteStage)
}

const scoutResults = scoutRefutation ? (await scoutRefutation).filter(Boolean) : []

const doneKeys = [...scoutAxes, ...evidenceAxes].map((a) => a.key)
log(`Evidence complete: ${doneKeys.length} axes, ${[...scoutResults, ...evidenceResults].reduce((n, r) => n + survivors(r), 0)} findings survived refutation`)

let synthResults = []
if (synthAxes.length) {
  phase('Distill')
  synthResults = await pipeline(
    synthAxes,
    (a) => {
      if (a.distill === false) return Promise.resolve({ summary: 'no distillation for this axis' })
      return agent(distillPrompt(a, doneKeys), { label: `distill:${a.key}`, phase: 'Distill', model: modelFor(a), schema: NOTE_SCHEMA })
    },
    (note, a) => {
      if (!note) {
        log(`${a.key}: distillation failed, skipping the axis`)
        return null
      }
      if (a.distill === false) {
        return agent(axisPrompt(a, verifiedInputs(doneKeys)), { ...optsFor(a, 'Synthesis'), schema: FINDINGS_SCHEMA })
      }
      return agent(runDistilledPrompt(a), { ...optsFor(a, 'Synthesis'), schema: FINDINGS_SCHEMA })
    },
    refuteStage,
  )
}

phase('Consolidate')
// `priorAxes` lets a targeted re-run of one axis consolidate over reports an earlier run left in
// the dossier, instead of producing a synthesis that silently covers only the axis just executed.
const priorAxes = A.priorAxes || []
const allKeys = [...priorAxes, ...doneKeys, ...synthAxes.map((a) => a.key)]
const all = [...scoutResults, ...evidenceResults, ...synthResults].filter(Boolean)
const cleanAxes = all.filter((r) => r.clean).map((r) => r.axis)
const unverifiedAxes = all.filter((r) => r.verifyFailed).map((r) => r.axis)
// Sequential, not parallel: the critic inspects what the consolidator produced. Run concurrently, it
// reads findings.jsonl before that file exists and reports it as empty — which is how a measured run
// ended up with a critic claiming the consolidator wrote nothing while the consolidator wrote 70 lines.
const consolidated = await agent(consolidatePrompt(allKeys, cleanAxes, unverifiedAxes), {
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

const ranThisTime = [...scoutAxes, ...evidenceAxes, ...synthAxes].map((a) => a.key)
const failed = ranThisTime.filter((k) => !all.some((r) => r.axis === k))

return {
  dossier,
  depth,
  axes: allKeys,
  axesFailed: failed,
  axesClean: cleanAxes,
  axesUnverified: unverifiedAxes,
  raised: all.reduce((n, r) => n + r.findings.length + raisedByVerifier(r), 0),
  survived: all.reduce((n, r) => n + survivors(r), 0),
  perAxis: all.map((r) => ({
    axis: r.axis,
    raised: r.findings.length,
    raisedByVerifier: raisedByVerifier(r),
    survived: survivors(r),
    clean: r.clean === true,
    verifyFailed: r.verifyFailed === true,
  })),
  consolidate: consolidated && consolidated.summary,
  completeness: critique && critique.summary,
  read: [`${dossier}/synthesis.md`, `${dossier}/findings.jsonl`, `${dossier}/work/completeness.md`],
}
