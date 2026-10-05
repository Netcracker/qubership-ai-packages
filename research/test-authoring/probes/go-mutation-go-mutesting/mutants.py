"""Print one line per mutant of go-mutesting's report.json: the list it was filed under, the mutator, and the line it
changed. go-mutesting prints the diff only for the mutants it reports as FAIL; this shows which change each PASS was.
"""

import difflib
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
for verdict in ("killed", "escaped", "timeouted", "errored"):
    for mutant in report[verdict] or []:
        m = mutant["mutator"]
        changed = [
            line
            for line in difflib.unified_diff(
                m["originalSourceCode"].splitlines(), m["mutatedSourceCode"].splitlines(), lineterm="", n=0
            )
            if line[:1] in "-+" and line[:3] not in ("---", "+++")
        ]
        print(f"{verdict:9} {m['mutatorName']:28} {' | '.join(line.replace(chr(9), '') for line in changed)}")
