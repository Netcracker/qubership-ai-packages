# Case: a latency regression with nothing failing

A regression case for `problem-report-authoring`. It is synthetic: the proxy (Ferrygate), its GitLab instance, the
company, and the people are fictional. It was built to test whether the rules added after
[`nested-workflow-tag`](../nested-workflow-tag/README.md) generalize to a performance report, where every run
succeeded and the successful runs are the evidence.

## What it exercises

The rules under suspicion of overfitting, as a first draft of version 1.1.0 stated them; the published 1.1.0
restates each one, and the letters are defined in [the research README](../../README.md#cases). The present tense
below describes that draft:

- **(c)** A log of a run that succeeded earns one line (§7, and the "weakness with no failure" row of §9). Here
  nothing failed, and the successful runs, with their conditions and spread, are what §6 asks a measurement to ship.
  Cut to one line, the report can no longer be repeated or compared.
- **(b)** The decision deletion test keeps a sentence only if it helps reproduce, accept, or choose a fix. A verified
  workaround helps none of the three for the maintainer, and it is what R4, the next user who searches for the
  symptom, needs first. The template has a Workaround heading for it.
- **(a)** Question 7 of §5. The expected behavior is the 4.6.2 latency; the report owes no shape of the coalescer fix,
  and the workaround already shows that a working configuration exists.

The padding: the customer contract and its latency clause, the dashboard, the two unrelated benchmarks, the search
queries and the unrelated hits, and a theory of the cause that was never tested.

## Files

| File | What it is |
| --- | --- |
| `prompt.md` | The investigation notes, frozen as of 2026-09-23, with the drafting task at the end. |
| `<model>/result.md` | The issue body the model wrote. |
| `<model>/result-note.md` | The hand-over note to the person filing, kept apart from the body. |

## How to run

Use the prompt in [`../nested-workflow-tag/README.md`](../nested-workflow-tag/README.md#how-to-run) with `<case>` set
to this directory and "a GitHub issue" read as "a GitLab issue". It needs no network.

## Checks

Each check names the rule or the suspected regression it guards. Read `result.md` against all of them.

1. **Both measurements survive with their spread** (c). The Results section carries, for 4.6.2 and for 4.7.0, the
   p50, the p99, and the requests per second with the number of runs and their spread: the table of ten runs, or
   medians with ranges beside a `wrk` output as printed for each version. One line per version fails.
1. **A reader can repeat the measurement** (§6, measurement). The exact `wrk` command, the warm-up, the machine, the
   kernel, the core pinning, the config, and the statement that nothing else ran on the machine.
1. **The bisected commit is evidence, not a guess** (§3). The commit `3f9c2e7` and !1482 are named with the bisect
   criterion (median p99 over 4 ms in three runs) and the parent's and the commit's p99.
1. **The profile is an extract with its artifact** (§6, evidence too large to paste). The top frames are pasted, and
   the report names `flame-470.svg` with its size (40.2 MB) and offers it, since it exceeds the 10 MB limit.
1. **The verified workaround is kept, after the problem** (b). `worker.io_batch = "off"` sits under the Workaround
   heading with its five-run numbers, and says that it restores most but not all of the 4.6.2 numbers. The report
   does not ask for the default to change because of it, and it does not open with it.
1. **The cause is marked or absent** (§3). The tick-wait theory, where present, is marked as a reading of the commit
   title and the profile that nobody tested, and the report stands without it.
1. **Nothing is there only because it is true.** The body carries none of: the company, the shipper contract or its
   5 ms clause, a description of the dashboard and its panels, the gzip or reload benchmarks, the search queries,
   #2140, #1977. One sentence with the production p99 the dashboard showed is an observed impact and is allowed.
1. **The nearest hit is named** (§4). #2291, the open 4.7.0 issue the search found, is named with how it differs (a
   memory symptom, not latency). A report that says no existing issue was found fails.
1. **The prose is short.** Words outside code blocks and tables: read the result sentence by sentence past 300. The
   numbers belong in code blocks or tables and do not count.

Checks 1 to 5, 7, and 8 can be counted, from this directory, with the model's directory as the argument. Every "present"
marker for evidence should print `True`, at least one of the two spread markers should reach its number, and every
padding marker should print `False`.

```bash
python3 - claude-opus-5-5 <<'EOF'
import re, sys
text = open(f'{sys.argv[1]}/result.md').read()
prose = re.sub(r'```.*?```', '', text, flags=re.S)
prose = '\n'.join(l for l in prose.splitlines() if not l.lstrip().startswith('|'))
print('prose words:', len(prose.split()), '(read sentence by sentence past 300)')
print('wrk outputs pasted (expect >= 2):', text.count('Latency Distribution'))
print('table rows naming a run (expect >= 10 if no wrk outputs):', len(re.findall(r'^\|\s*\d+\s*\|', text, re.M)))
for marker in ['wrk -t4 -c128 -d60s --latency', '6.8.0-45-generic', 'EPYC 7443P', '3f9c2e7', '!1482',
               'io_batch', '#2291']:
    print(f'{marker!r} present (expect True):', marker in text)
print('artifact size given (expect True):', bool(re.search(r'40(\.2)?\s?MB', text)))
for marker in ['Oakridge', 'shipper', 'contract', 'panel', 'gzip', 'reload', '#2140', '#1977']:
    print(f'{marker!r} present (expect False):', marker in text)
EOF
```
