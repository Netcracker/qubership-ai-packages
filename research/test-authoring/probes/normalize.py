"""Replace what differs between two correct runs of a probe: paths, durations, temp directories, process ids.

Reads stdin, writes stdout. ``run.sh`` passes the probe directory and the repository root as arguments so they can
be replaced by placeholders. Anything an ecosystem alone produces (a header line, a seed) is that probe.sh's job.
"""

import re
import sys


def normalize(text: str, placeholders: dict[str, str]) -> str:
    for path, name in sorted(placeholders.items(), key=lambda item: -len(item[0])):
        text = text.replace(path, name)
    rules = [
        (r"/private/var/folders/\S+", "<tmp>"),
        (r"/var/folders/\S+", "<tmp>"),
        (r"/tmp/\S+", "<tmp>"),
        (r"\b\d+\.\d+ ?(ms|s)\b", r"<duration>"),
        (r"\b\d+:\d\d:\d\d\b", "<time>"),
        (r"\b(pid|PID)[ =:]+\d+\b", r"\1=<pid>"),
        (r"\bat 0x[0-9a-fA-F]+\b", "at 0x<address>"),
    ]
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text)
    # A golden file with trailing spaces is rewritten by most editors on save; pytest pads its "E" lines with them.
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)


def main() -> None:
    placeholders = {}
    for arg in sys.argv[1:]:
        path, _, name = arg.partition("=")
        placeholders[path] = name
    sys.stdout.write(normalize(sys.stdin.read(), placeholders))


if __name__ == "__main__":
    main()
