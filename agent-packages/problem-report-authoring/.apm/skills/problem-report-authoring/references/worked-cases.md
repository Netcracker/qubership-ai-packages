# Worked cases

Open this when an expected block failed the test in the skill and you need the repair, or when you
want to see the rules applied end to end. Each case pairs a draft that failed a rule with the report
that was accepted. Both accepted reports are public and worth opening:
[gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
[junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041).

## Case 1: an index where the reader needs a value

The draft asked for a test-report entry named `methodInParameterizedClass(String)[2][1]`. Question 1
of the expected-behavior test passes: there is a literal. Question 2 passes: it is unique. **Question
3 fails.** The two ordinals index the argument source, and a reader who holds only the report cannot
tell what ran.

The repair is to name the thing and keep the index only as a tiebreak. The accepted report asks for
`firstParameterizedMethod(String) [1] value = ""` and states the reason in one line: an index does not
say what ran, and it moves when a row is added to the argument source, so a report archived last week
names a different case today.

It also separates the requirement from the rendering, in the report's own words: the exact rendering
is the project's to choose, and what the reporter needs is the method name and the arguments.

## Case 2: a proposed form nobody ran

The same draft argued for the index form partly on the grounds that a reader could re-run a single
case with it. **Question 5 fails:** no transcript, and the claim was never tested.

Running it produced the strongest section of the accepted report. Two invocations fail with
the tool's own message, a third form works, and the report says which one and why it is unavailable
from the report file. A rejected assertion became evidence.

The rule is about the claims around the proposal, not the proposal. The behavior you are asking for
does not exist, so nothing can run it. What can run is every claim you make about a tool you have, and
the argument for a shape is usually one of those.

## Case 3: a setting in the wrong role

The draft for JUnit opened around a configuration setting, so it read as "configuration is enough for
me" while asking for the default to change.

Apply the skill's workaround deletion test to the whole document: remove every sentence that
mentions the setting. The remaining text no longer stated a requirement, so the setting was the frame.

The accepted report puts the setting in the role the evidence supports. It does not fix the problem,
so it is neither a workaround nor an alternative: it is a negative result, and it appears under a
heading that says so, "Even `junit.jupiter.params.displayname.default` does not fix it", between the
symptom and the ask. Placed there it is the strongest argument that configuration cannot answer the
request, and placed last it would have been an aside.

A setting that does work is the other case, and it goes after everything that states the problem. The
accepted Gradle report carries its `Workaround` section there, with the causal analysis below it.

## Case 4: two symptoms in one block

The draft merged two symptoms: one class of parameterized test losing the method name, and another
losing the arguments of the class invocation.

The owner question settles it. The method name is lost by the build tool that writes the report
file; the class-invocation arguments are absent from the name the test framework supplies, and the
two are different repositories. So two reports, each stating that it does not depend on the other.
The build-tool report keeps two expected blocks of its own, one per symptom in the file it writes,
because a maintainer there could accept one and refuse the other.

## Case 5: a confident cause for a project that had already fixed it

The draft proposed filing against the test framework without checking whether the framework still had
the defect. It did not: two related reporting defects had been fixed and shipped in a maintenance
release.

The version and tracker checks catch this before any prose exists. The accepted report carries the
repaired form: it names the already-shipped fixes, bounds what each one covers, states that both were
verified on a released version and on a build from source, and then states the gap that remains. It
also carries a section arguing why the remaining gap belongs to that project and not to the build
tool, which is the honest answer when a defect lives at a boundary.

## Case 6: the analysis marked once, and the report standing without it

The accepted Gradle report carries its reading of the source under a heading of its own, and opens
that section with one sentence: this part is a guess and may be wrong, and the sections above stand
without it. Nothing above that section names a class in Gradle as the cause; the symptom, the
expected names, and the reproducer are stated from outside. Delete the section and the report still
states the problem, which is the first question of the analysis deletion test in §3 of the skill.

The draft that failed the same test traced the defect into a Gradle class inside the field that
states the current behavior. Deleting its marked reasoning left the report standing, so it passed the
first question; the trace inside the symptom failed the second.

## Published before-and-after pairs worth copying

These come from projects' own guidance rather than from the two reports above.

| Before | After |
| --- | --- |
| "Software crashes." | "Cancelling a File Copy dialog crashes File Manager." |
| "Browser should work with my web site." | "Down-arrow scrolling doesn't work in a `<textarea>` styled with `overflow:hidden`." |
| "How do I get the color picker to take a hexadecimal RGB value?" | "I am trying to replace an image's color table with values of my choosing. The only way I can see is to edit each slot, and the color picker will not take a hexadecimal RGB value." |
| "I get SIG11 errors on kernel compiles and suspect a hairline crack in a motherboard trace. How do I check for those?" | "Kernel compiles die with SIG11 at random points on this board. Here is the hardware, the timings, and what I already swapped out." The theory is gone; the observations stay. |
| "hi" … four minutes … "what time was that thing again?" | "Hi. What time was that thing again?" |
