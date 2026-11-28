# Case: meeting notes that mix decisions with what follows from them

The input is meeting notes for a record about an upload limit, in a repository with no records. Some notes are
decisions: oversize uploads get 413, the limit setting and its default of 25, an invalid setting stops the start, every
invalid setting is reported at once, and the integration tests move to a real S3 API. Others retell the code or ask for
tests of those decisions: the largest value that the `int32` of the setting holds, the text of a log line, the function
that collects the errors, and tests that show the 413 rule and the stop at start hold. The skill asks for rules for the
first group and no rule for the second. The default of 25 and the move to MinIO are the noise input: a chosen value, and
a choice of how the system is tested, stay decisions. Reporting every invalid setting at once and the move to MinIO
apply beyond the upload limit, so a separate record proposed for each is as good as a rule in this one.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (a retelling of the code gets no rule, and a chosen value is a decision),
  "Confirmation and implementation notes" (a requirement that only asks for a test of another rule is no rule, while how
  the system is tested is a decision; a note names no function or file that one change edits), "Rules" (**Form**, the
  behavior rule)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0001.** A record file `docs/adr/0001-<slug>.md`.
2. **No type maximum.** No rule line contains `2147483647` or `2^31`.
3. **No log text.** No rule line contains `file too large`, unless an open point asks whether anything matches the
   text. The text may stand in an implementation note as an example.
4. **No function of the change.** No rule line and no implementation note names `loadSettings` or `strconv`.
5. **No rule that requires a test of another rule.** No rule line asks for a test, a CI job, or a check that shows the
   413 refusal or the stop at start.
6. **413 rule.** A rule line states the 413 refusal.
7. **Default kept.** A rule line states the default of 25.
8. **MinIO kept.** A rule line states that the integration tests run against MinIO or a real S3 API, or the result
   proposes a separate record for that decision.

Checks 2 to 5 test the rule firing; checks 6 to 8 test it staying quiet.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-derived-values opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-derived-values
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

## Results

Runs of 2026-11-16 on tree `36fdf375`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. Opus r2, Sonnet r1, and Sonnet r2 pass all eight checks. Opus r1 fails check 4: its
implementation notes say that `strconv.ParseInt` rejects the value and that `loadSettings` meets R4 by returning that
error, a retelling of the code in a note. Both Opus results write the log text as a rule and pass check 3 through an
open point that asks whether any alert or log query matches it, which is what "What belongs in an ADR" asks where the
writer cannot tell whether someone chose a value. Each record keeps the 413 refusal, the default of 25, and a rule that
a value the type of the setting cannot hold stops the start, without the number, and every result proposes separate
records for reporting every invalid setting at once and for the move to MinIO.

Two things the checks do not test. Sonnet r2 lists the two CI tests under **Confirmation** though neither exists yet,
against "A rule with no check yet has no entry"; the other results put them in the notes or in the message. Opus r1,
Opus r2, and Sonnet r2 name `loadSettings` in the term "stops the start", as the **Terms** bullet asks a record to say
how a library below the entry point meets an outcome; both controls do the same, and check 4 does not read **Terms**.

Runs on two earlier trees of this change: on `ad071c7e`, which words the retelling item differently, Sonnet r2 named
`loadSettings` in a rule and failed check 4, and the other three passed; on `eac39b10`, all four passed. The results
above replace them.

No result on any tree writes a rule that asks for a test of another rule, and neither do the controls: the old skill
already kept the two CI tests out of the rules. The sentence of "Confirmation and implementation notes" about such a
requirement has no failing case here; it states where the requirement goes, and the motivating record had the rules
because a reviewer asked for them.

`controls/before-opus.md` and `controls/before-sonnet.md` are unedited runs of this prompt on tree `d42618eb`, the skill
before this case was added. Both fail checks 2, 3, and 4: a rule states 2147483647 as the largest value, a rule fixes
the log text, Opus names `strconv.ParseInt` in a note, and Sonnet names `loadSettings` in a rule.
