// The deep-review workflow script run against fake agents. The Workflow runtime evaluates the script as the body of an
// async function with `args`, `agent`, `parallel`, `pipeline`, `phase`, and `log` in scope, so the harness does the
// same; a script that does not parse fails every test here.
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const SCRIPT = fileURLToPath(
  new URL('../../agent-packages/deep-review/.apm/skills/deep-review/workflow/deep-review.js', import.meta.url),
)
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor
const body = readFileSync(SCRIPT, 'utf8').replace(/^export const meta/m, 'const meta')
const workflow = new AsyncFunction('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', body)

// Runs the workflow. `answer(prompt, opts)` plays every agent; the calls are recorded with their prompts and options.
async function run(args, answer, hold = false) {
  const calls = []
  const agent = async (prompt, opts) => {
    calls.push({ prompt, opts })
    return answer(prompt, opts)
  }
  // As in the runtime, an item whose stage throws comes back as null instead of failing the whole batch.
  const parallel = (thunks) => Promise.all(thunks.map((f) => Promise.resolve().then(f).catch(() => null)))
  const pipeline = (items, ...stages) =>
    Promise.all(
      items.map((item) =>
        stages.reduce((p, stage) => p.then((r) => stage(r, item)), Promise.resolve(item)).catch(() => null),
      ),
    )
  const done = workflow(args, agent, parallel, pipeline, () => {}, () => {})
  if (hold) return { done, calls }
  return { result: await done, calls }
}

// Lets every pending promise callback run, so the calls a held run can make are recorded.
const settle = () => new Promise((resolve) => setTimeout(resolve, 0))

const baseArgs = (overrides) => ({
  dossier: '/d',
  repo: '/r',
  skill: '/s/deep-review',
  completenessCritic: false,
  ...overrides,
})

const finding = (id) => ({ id, title: id, file: 'a.go:1', proposedSeverity: 'LOW', method: 'traced', evidence: 'e' })

// An axis that raises the given findings, and a verifier that answers with the given verdicts.
const axisAnswering = (raised, verdicts) => (prompt, opts) => {
  if (opts.label.startsWith('Evidence:')) return { findings: raised.map(finding), coverage: 'c' }
  if (opts.label.startsWith('Refute:')) return verdicts === null ? null : { verdicts }
  return { summary: 'done' }
}

describe('verification of an axis', () => {
  const axes = [{ key: 'correctness', phase: 'evidence' }]

  it('counts a finding the verifier gave no verdict as an unverified survivor', async () => {
    const { result } = await run(
      baseArgs({ axes }),
      axisAnswering(['COR-01', 'COR-02'], [{ id: 'COR-01', verdict: 'upheld' }]),
    )
    assert.deepEqual(result.findingsUnverified, { correctness: ['COR-02'] })
    assert.equal(result.survived, 2)
  })

  it('reports the axis unverified when the verifier answers none of its findings', async () => {
    const { result } = await run(
      baseArgs({ axes }),
      axisAnswering(['COR-01'], [{ id: 'COR-07', verdict: 'upheld' }]),
    )
    assert.deepEqual(result.axesUnverified, ['correctness'])
  })

  it('tells the consolidator which findings got no verdict', async () => {
    const { calls } = await run(
      baseArgs({ axes }),
      axisAnswering(['COR-01', 'COR-02'], [{ id: 'COR-01', verdict: 'refuted' }]),
    )
    const consolidate = calls.find((c) => c.opts.label === 'consolidate')
    assert.match(consolidate.prompt, /no verdict for some findings — correctness \(COR-02\)/)
  })
})

describe('an axis that returns nothing', () => {
  it('is reported to the consolidator as failed whatever its files say', async () => {
    const { calls } = await run(baseArgs({ axes: [{ key: 'correctness', phase: 'evidence' }] }), (prompt, opts) =>
      opts.label.startsWith('Evidence:') ? null : { summary: 'done' },
    )
    const consolidate = calls.find((c) => c.opts.label === 'consolidate')
    assert.match(consolidate.prompt, /so they failed whatever their files\s+say:\*\* correctness\./)
  })
})

describe('the digest of a sliced axis', () => {
  const label = (calls, prefix) => calls.findIndex((c) => c.opts.label.startsWith(prefix))
  const slices = [
    { key: 'correctness', phase: 'evidence', slice: 'api' },
    { key: 'correctness', phase: 'evidence', slice: 'ui' },
  ]

  it('waits for the verifier of the last slice, then starts before the synthesis axes', async () => {
    let release
    const held = new Promise((resolve) => (release = resolve))
    const answer = axisAnswering(['COR-01'], [{ id: 'COR-01', verdict: 'upheld' }])
    const { done, calls } = await run(
      baseArgs({ axes: [...slices, { key: 'architecture', phase: 'synthesis' }] }),
      (prompt, opts) =>
        opts.label === 'Refute:correctness--ui' ? held.then(() => answer(prompt, opts)) : answer(prompt, opts),
      true,
    )
    await settle()
    assert.equal(label(calls, 'digest:'), -1, `call order: ${calls.map((c) => c.opts.label).join(', ')}`)
    release()
    await done
    assert.ok(
      label(calls, 'digest:correctness') < label(calls, 'distill:architecture'),
      `call order: ${calls.map((c) => c.opts.label).join(', ')}`,
    )
  })

  it('still starts when a slice agent throws', async () => {
    const answer = axisAnswering([], [])
    const { calls } = await run(baseArgs({ axes: slices }), (prompt, opts) => {
      if (opts.label === 'Evidence:correctness--ui') throw new Error('agent died')
      return answer(prompt, opts)
    })
    assert.notEqual(label(calls, 'digest:correctness'), -1)
  })

  it('covers the slices an earlier run left, and starts before any axis of this run', async () => {
    const { calls } = await run(
      baseArgs({ axes: [{ key: 'security', phase: 'evidence' }], priorAxes: ['telemetry--api', 'telemetry--ui'] }),
      axisAnswering([], []),
    )
    assert.equal(label(calls, 'digest:telemetry'), 0)
    assert.match(calls[0].prompt, /ran as 2 slices: telemetry--api, telemetry--ui/)
  })

  it('covers an earlier slice and a new one, after the new one is verified', async () => {
    const { calls } = await run(
      baseArgs({
        axes: [{ key: 'telemetry', phase: 'evidence', slice: 'ui' }],
        priorAxes: ['telemetry--api'],
        rubrics: ['telemetry-authoring'],
      }),
      axisAnswering(['TEL-UI-01'], [{ id: 'TEL-UI-01', verdict: 'upheld' }]),
    )
    assert.ok(label(calls, 'Refute:telemetry--ui') < label(calls, 'digest:telemetry'))
    assert.match(calls[label(calls, 'digest:telemetry')].prompt, /ran as 2 slices: telemetry--api, telemetry--ui/)
  })

  it('sends the consolidator to the slice reports when the digest fails', async () => {
    const answer = axisAnswering([], [])
    const { calls } = await run(baseArgs({ axes: slices }), (prompt, opts) =>
      opts.label === 'digest:correctness' ? null : answer(prompt, opts),
    )
    const consolidate = calls.find((c) => c.opts.label === 'consolidate')
    assert.match(consolidate.prompt, /The digest\s+of correctness failed in this run/)
  })
})

describe('isolation of a system review in the session repository', () => {
  const args = baseArgs({
    sessionRepoIsTarget: true,
    components: [
      { name: 'api', repo: '/r' },
      { name: 'worker', repo: '/w' },
    ],
    axes: [{ key: 'tests', phase: 'evidence', needsWriteAccess: true }],
  })

  it('makes the agent copy the component the harness does not isolate', async () => {
    const { calls } = await run(args, axisAnswering([], []))
    const axis = calls.find((c) => c.opts.label === 'Evidence:tests')
    assert.equal(axis.opts.isolation, 'worktree')
    assert.match(axis.prompt, /git -C '\/w' worktree add '\/d\/work\/tests-wt-worker' HEAD/)
    assert.doesNotMatch(axis.prompt, /git -C '\/r' worktree add/)
  })
})

describe('arguments the workflow refuses', () => {
  const refused = [
    ['an axis key that climbs out of the dossier', { axes: [{ key: '../x' }] }, /axis key "\.\.\/x"/],
    ['a slice name with a slash', { axes: [{ key: 'tests', slice: 'a/b' }] }, /slice "a\/b"/],
    [
      'two entries with one slice name',
      { axes: [{ key: 'tests', slice: 'ui' }, { key: 'tests', slice: 'ui' }] },
      /two entries of args\.axes run as "tests--ui"/,
    ],
    ['an axis whose rubric is not installed', { axes: [{ key: 'docs-pages' }] }, /needs the docs-page-authoring skill/],
    ['a prior axis that climbs out of the dossier', { priorAxes: ['../x'] }, /args\.priorAxes entry "\.\.\/x"/],
    [
      'a prior axis that also runs now',
      { axes: [{ key: 'tests' }], priorAxes: ['tests'] },
      /"tests" is in args\.priorAxes and runs in this invocation as well/,
    ],
  ]
  for (const [condition, overrides, message] of refused) {
    it(`refuses ${condition}`, async () => {
      await assert.rejects(run(baseArgs(overrides), () => ({ summary: 'done' })), message)
    })
  }

  it('starts the telemetry axis with no developer-style skill, and says to report the gap', async () => {
    const { calls } = await run(
      baseArgs({ axes: [{ key: 'telemetry', phase: 'evidence' }], rubrics: ['telemetry-authoring'] }),
      axisAnswering([], []),
    )
    const axis = calls.find((c) => c.opts.label === 'Evidence:telemetry')
    assert.match(axis.prompt, /No developer-style skill is installed/)
  })

  it('gives the telemetry axis every installed developer-style skill', async () => {
    const { calls } = await run(
      baseArgs({
        axes: [{ key: 'telemetry', phase: 'evidence' }],
        rubrics: ['telemetry-authoring', 'english-developer-style', 'russian-developer-style'],
      }),
      axisAnswering([], []),
    )
    const axis = calls.find((c) => c.opts.label === 'Evidence:telemetry')
    assert.match(axis.prompt, /`english-developer-style`: \/s\/english-developer-style\/SKILL\.md/)
    assert.match(axis.prompt, /`russian-developer-style`: \/s\/russian-developer-style\/SKILL\.md/)
  })

  it('gives an axis the path of its installed rubric', async () => {
    const { calls } = await run(
      baseArgs({ axes: [{ key: 'docs-pages', phase: 'evidence' }], rubrics: ['docs-page-authoring'] }),
      axisAnswering([], []),
    )
    const axis = calls.find((c) => c.opts.label === 'Evidence:docs-pages')
    assert.match(axis.prompt, /`docs-page-authoring`: \/s\/docs-page-authoring\/SKILL\.md/)
  })
})
