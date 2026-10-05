// Prints one line per mutant of Stryker's JSON report, sorted by position: where, the status, the mutator, the
// replacement, and the first line of the reason Stryker recorded (the failed assertion, the compiler error).
import { readFileSync } from "node:fs";

const report = JSON.parse(readFileSync(process.argv[2], "utf8"));
const lines = [];
for (const [file, { mutants }] of Object.entries(report.files)) {
  for (const m of mutants) {
    const { line, column } = m.location.start;
    const reason = (m.statusReason ?? "").split("\n")[0];
    lines.push({ file, line, column, text: `${file}:${line}:${column} ${m.status} ${m.mutatorName} ${JSON.stringify(m.replacement)} ${reason}`.trimEnd() });
  }
}
lines.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line || a.column - b.column || a.text.localeCompare(b.text));
for (const { text } of lines) console.log(text);
