# Ground rules (all axes)

These rules are the same for every axis. The axis file adds the subject matter; this file fixes the standard.

## Evidence

- **Cite the artifact.** Every finding names `path:line` (or `path` for a whole-file concern) and states a concrete
  trigger: inputs, ordering, scale, configuration, or failure mode. "This could be racy" is not a finding. "Two calls
  to `X` between line 40 and line 58 observe state written by `Y` at line 91, so a caller that reuses the client after
  `close()` gets a nil channel" is.
- **Separate actual from expected.** Say what the code does today, and then what it should do *and where that is
  established*: a specification section, a doc comment, a type signature, a sibling function that gets it right, a
  named ecosystem convention, or the documentation of a technology in the profile's inventory that states what it is
  for and what it does not do. If nothing establishes the expectation, you have a preference rather than a defect —
  drop it. This single question kills more weak findings than any other.
- **Say when a tool's limit produced the defect.** Add a `Tool limit:` line wherever a documented limit of a
  technology from the profile's inventory makes the defect possible, whichever language the finding sits in: a policy
  file, a template, a configuration used as a program, or a primary-language workaround such as a custom built-in or
  an escape hatch. Name the technology and the limit (no recursion, no exceptions, no ordering, a fixed evaluation
  depth, undefined instead of an error). Write `none` where the finding sits in an artifact on an inventory
  technology and no limit is involved, and omit the line where no inventory technology is involved at all. The line
  is cheap for you, and it lets the synthesis axis treat several defects in several reports as one decision. Answer
  it by reading the technology's documentation, not by guessing: a wrong `none` hides the decision again.
- **State the observable consequence** in the terms of whoever gets hurt: the caller, the operator, the workload, the
  next maintainer. A finding whose consequence is "this is not ideal" is not a finding.
- **Falsify before reporting.** For each candidate, actively look for the thing that makes it safe: a guard, a
  validation rule, a framework guarantee, a documented constraint, a test that pins the behavior. Report only what
  survives that search, and say what you checked.
- **Report what you rejected.** The candidates you dropped, each with the mechanism that made it a non-issue, are part
  of the deliverable — not scaffolding to throw away. They show where you looked, they let the verifier resurrect
  something you dismissed too fast, and they distinguish "found little because there is little" from "found little
  because I did not look".
- **Severity is a proposal.** You suggest it; the verifier may lower it and the consolidator settles disagreements
  between axes, because it is the only stage that sees them all.
- **Evidence has to survive the run.** Keep every artifact — command output, reproduction, scanner report, benchmark —
  under the dossier's `work/` directory. A path under `/tmp` is not a retained artifact: it will be gone when someone
  tries to check your claim, which makes the claim unverifiable no matter how carefully you produced it.
- **Do not label your own confidence.** `CONFIRMED` and `PLAUSIBLE` are assigned by the adversarial verifier that
  reviews your findings, never by the agent that raised them — the author of an argument is the worst judge of it.
  What you report is what you did: `method` (`executed`, `traced`, or `inferred`) and `evidence`. For `executed`,
  quote the command and the decisive line of output. For `traced`, name the branches you followed. For `inferred`,
  name the assumption you did not check. These are claims the verifier will test, so overstating them is the fastest
  way to have your finding downgraded.
- **If you are the verifier**, `CONFIRMED` requires that *you* executed something whose output settles the claim.
  Reproducing the author's artifact counts; re-reading the lines the finding already quotes does not. Everything else
  is `PLAUSIBLE`, and an upheld `PLAUSIBLE` finding is a perfectly good outcome.
- **A verifier refutes a `FIT` finding with a force, not with a passing build.** A `FIT` finding (a technology in a
  role it was not designed for, see `axes/architecture.md`) already assumes the code works. "The tests pass" and "it
  has run in production" refute nothing. What refutes it: the upstream documentation does support this use; the
  counted workarounds are not workarounds; the findings it cites do not follow from the limit it names; or a force in
  the domain justifies the role, with the document or the person that states it. Where the force exists and is
  written nowhere, uphold the finding and state in the reason that the force is undocumented and what to write
  down; the consolidator relabels it `ACCEPTED-DEBT`.
- **Prefer execution.** If the repository builds and tests run, a throwaway test that reproduces the defect is worth
  more than three paragraphs of tracing. Use the build and test commands recorded in the profile.
- **Search what you were given before deferring to a human.** "This depends on how the legacy system behaves, so the
  customer must confirm" is a legitimate ending only after you have looked in the material the focus file handed you:
  the design documents, the decision records, the specification archive, the captured fixtures under `testdata/`. Say
  which of them you searched and with what pattern. Measured on a real run, two findings were deferred to the user
  while the answer sat in an archive named in their own axis assignment, and one of them lost half its force as a
  result: the specification defined the exact case the finding turned on. A deferral that names no search is a finding
  that stopped early.
- **A tracked fixture is evidence about the real world when its provenance says so.** Test data generated by an
  anonymizer over a production capture carries the real shape — cardinalities, field presence, tenancy — even though
  every identifier is fake. Read the generator before you decide a fixture is synthetic and therefore uninformative,
  and state the boundary in the finding: which properties came from the capture and which are artifacts of
  generation.

## Scope discipline

- **Stay on your axis.** If you trip over something real that belongs to another axis, record it in one line under
  *Cross-axis notes* at the end of your report and move on. Do not develop it. Another agent owns it, and duplicate
  findings in different vocabularies are expensive to triage.
- **No style noise.** Formatting, naming taste, comment nitpicks, and anything a linter already enforces are out of
  scope on every axis unless the axis file says otherwise.
- **No blanket rewrites.** Propose the minimal change, or a design change stated with its trade-off. "Rewrite this on
  top of <framework>" is not a finding.
- **Assume the tests pass** and that the code works for the happy path, unless the profile says otherwise. You may
  challenge that assumption only with a concrete artifact: a failing test you wrote, an input that reproduces, or a
  line-level contract mismatch.

## Working-tree hygiene

You may need to change the project to measure it: add a coverage plugin, write a throwaway test, mutate a condition to
see whether anything fails, bump a dependency to check a break. All of that is allowed, and none of it happens in the
repository the user is working in.

- **Never leave a modification in the reviewed working tree.** Not a test file, not a plugin declaration, not a
  lockfile update, not a stray build output. The user must be able to run `git status` after the review and see
  nothing.
- **Work in a throwaway copy.** If your agent was started with worktree isolation, you already have one — you are in
  it, and the dossier path is absolute, so reports still land in the right place. Otherwise create one:
  `git worktree add <dossier>/work/<axis>-wt HEAD`, and remove it when you are done. For a non-git tree, copy it.
- **Report what you changed to get the measurement**, as a command or a diff, so a maintainer can reproduce the number
  and decide whether to adopt the setup permanently. A measurement nobody can repeat is not evidence.
- **Missing tooling is a finding, not an excuse.** If the project has no coverage, no benchmark harness, no fuzzer, and
  no race detection in CI, report that once, at the severity it deserves — then go and measure anyway in your copy.

## Adversarial posture

- **Assume careless input.** Callers pass any value the type system permits: empty strings, nulls where optional,
  duplicates, stale copies of someone else's configuration, values from a previous major version. Assume every
  combination the signature allows will eventually arrive.
- **Assume a degraded environment.** The network drops mid-call, the peer returns garbage for ten minutes, the process
  is killed between two writes, clocks skew, disks fill, and threads are starved.
- **Do not inflict that on anything shared.** Stress, fuzzing, malformed-input runs, and large or expensive requests
  belong in your own copy or against a local fixture. Never point them at a live or shared service, a shared database,
  or a colleague's environment, whatever the axis file asks you to test. If a check is only meaningful against a
  shared system, describe it and report the gap instead of running it.
- **Attack the seams, not the middle.** Defects concentrate where two things meet: two components, two threads, two
  versions, two encodings, two lifetimes. Spend your budget there.

## Severity

| Level | Meaning |
| --- | --- |
| `CRITICAL` | Data loss, silent corruption, credential exposure, or an outage of everything that depends on this |
| `HIGH` | A production incident under realistic load or a realistic failure; or a defect that misleads a competent operator into the wrong action |
| `MEDIUM` | Degradation, operational pain, latent correctness, or a design that will force a painful change within a year |
| `LOW` | Hardening, friction that compounds |

Rate by consequence, not by how small the fix is. A one-character fix for a silent data-loss path is `CRITICAL`.

## Budget

Depth beats breadth. Fifteen findings that are each specific, evidenced, and actionable are worth more than sixty
observations. If a part of your axis turns out to be genuinely well handled, say so in one line under *Checked and
sound* — but only after you looked.
