Grade the results of one case of the blackbox-test-design skill against the case's checks.

The case directory is given as `<case>` below.

1. Read `<case>/README.md`: the paragraph says what the case plants, and `## Checks` lists the checks. Read
   `<case>/prompt.md` and the files under `<case>/files/`. Where the case has `src/`, read it: it is the answer
   key, and a finding that contradicts it fails the check it claims to satisfy.
2. For each directory under `<case>/results/`, read every file the session wrote. Grade each check `true` or `false`
   with one sentence of evidence: a short quote and the file it is in, or what is missing. A check passes only where
   the result states the point itself; a passing mention that a reader could not act on fails. Where a check counts
   something the files record (runs in `engine-calls.log`, requests in a round), count it.
3. Grade each arm on its own text. Do not let one arm's answer raise or lower the bar for the other, and do not let
   `run.txt` (which says whether the skill was loaded) influence a grade; read it only after grading.
4. Write `grading.json` into each result directory:

   ```json
   {"checks": [{"check": "the text of the check", "passed": true, "evidence": "..."}], "passed": 9, "total": 11}
   ```

5. Reply with one line per result directory: the directory name, `passed/total`, and the checks it failed.
