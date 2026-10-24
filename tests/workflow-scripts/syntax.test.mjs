// Every Workflow script a package ships, compiled the way the Workflow runtime runs it: as the body of an async
// function. Super-Linter excludes these files (.github/super-linter.env), because no ESLint source type accepts an
// exported `meta` together with a top-level `return`, so this test is the only syntax check they get.
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = fileURLToPath(new URL('../../agent-packages/', import.meta.url))
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor

const scripts = []
for (const pkg of readdirSync(ROOT)) {
  const skills = join(ROOT, pkg, '.apm', 'skills')
  if (!existsSync(skills)) continue
  for (const skill of readdirSync(skills)) {
    const dir = join(skills, skill, 'workflow')
    if (!existsSync(dir)) continue
    for (const file of readdirSync(dir).filter((f) => f.endsWith('.js'))) scripts.push(join(dir, file))
  }
}

describe('Workflow scripts in agent-packages', () => {
  it('finds at least one script, so an emptied glob does not pass silently', () => {
    assert.notEqual(scripts.length, 0)
  })
  for (const script of scripts) {
    it(`compiles ${script.slice(ROOT.length)} as an async function body`, () => {
      const source = readFileSync(script, 'utf8')
      assert.match(source, /^export const meta = \{/m, 'a Workflow script starts with `export const meta`')
      assert.doesNotThrow(() => new AsyncFunction('args', source.replace(/^export const meta/m, 'const meta')))
    })
  }
})
