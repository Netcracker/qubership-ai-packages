# Pass 2 — rules for a problem-report skill

## 1. Executive summary

Seventeen candidates went in. **Eleven survive as rule contributors**: PostgreSQL, the layer-attribution group, the
Gradle reproducer plus bug form, Stack Overflow's MRE page, Homebrew, QUS, the request-genre template group, the
Gradle feature-versus-bug pair, the short-form cluster, the machine-author policy cluster, and Mozilla plus Rahman.
**Four drop to supporting evidence** — Chaparro, Chilana, Bettenburg, CrowdRE'25 — because they measure what reports
contain and how that correlates with outcomes, but state no rule. **One drops to a justification constraint**: the
template-conformance null result, which does not kill the fill-the-fields rule but replaces its rationale. **One is
partly unreachable**: the prior-art-in-agent-skills row; `github/awesome-copilot`'s `github-issues` skill was fetched
and turns out to be an MCP/`gh` mechanics skill with no content rules worth deconflicting, and no
`playwright-bug-reporter` skill could be located at all.

The largest single finding is that the machine-authorship policies, which Pass 1 treated as a compliance cluster,
turn out to be the **only sources that state the maintainer's unsourced rules directly**. The Linux kernel's
security-bugs page instructs an AI-assisted reporter to "ask your tool to propose a fix and **test it** before
reporting the problem" — that is B4, sourced. Its one-issue-per-message clause with an explicit merge exception is
B5, sourced, with a detection attached. Ghostty and Homebrew supply the disclosure and the answer-follow-ups-yourself
obligations.

**Conflicts settled: five of six.** Order is settled per genre with a project-override rule. Reduction is settled as
a stop condition ("no dependency outside the target project") rather than a size target. Duplicates settle in favour
of a cheap search whose *output is written into the report*, not a suppression rule. Regression framing settles
against the maintainer's likely intuition: Chilana et al. group "prior behavior" with the INVALID-prone categories,
so "it used to work in X" is a weak grounding unless the project ships a regression form that makes the last working
version a required field. Sketches settle as permitted-but-subordinated. **One stayed open**: template conformance —
the rule survives, its outcome-based justification does not, and the replacement justification (admission and
routing) is asserted, not measured.

**Bucket split (45 rules):** bucket 1 (text + repository alone) 29; bucket 2 (something must be run) 6, of which
REP6 degrades to bucket 3 where only the run's URL is checked; bucket 3 (tool or lookup) 9; bucket 4 (human
judgment) 1. **Core/reference split:** 31 core, 14 reference across five reference files.

**What resists a writer optimizing for the check.** **Seventeen rules cannot be satisfied in letter alone**, because
their detection either reads an artifact the writer does not control or enumerates something mechanically. The four
strongest are EXP5 (the executed transcript of the proposed form), REP2 (a reviewer re-runs the shipped reproducer),
REP4 (the reproducer's dependency manifest is machine-readable) and REP6 (the linked CI run is fetched); OWN1's
isolation commands and OWN2's version string are likewise re-runnable and checkable. **Twenty-seven are satisfiable
in letter alone** — most of the expected-behavior family, because the only available check is the text's own claim.
For every one of those the table names a *substitute* check: not "did you ground the expectation" but "does the named
grounding resolve to a fetchable artifact that says what is claimed". One rule (MAC5) has no text-derivable detection
at all, which is why it is bucket 4.

## 2. Deep candidate evaluation

Portability columns: F = filed issue, C = colleague message, R = request.

| # | Candidate | Disposition | Strongest contribution | Main weakness | Evidence | Maintained | Before/after examples | FP risk | F / C / R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PostgreSQL Appendix §5 | **Rule contributor (top)** | "State all the facts and only facts"; "This is not what I expected" named as a defect; expectation grounded in another system rejected; client-vs-server layer split | Single-project vocabulary; its reduction dissent is scoped to SQL inputs | asserted | live docs (current) | no | low | F ✓ C ✓ R ✗ |
| 2 | Chaparro et al. FSE'17 | **Supporting evidence** | Measures which slot is missing (EB 35.2%, S2R 51.4%, OB 93.5%, n=2,912) and shows an EB/S2R detector is buildable | States no rule; discourse patterns are English-surface heuristics; **no OB detector exists** | studied | 2017, not maintained | no | med (patterns fire on hedged prose) | F ✓ C ✗ R ✗ |
| 3 | Chilana, Ko & Wobbrock VL/HCC'10 | **Supporting evidence (decisive for EXP3)** | Ranks expectation groundings by outcome; the only source that makes grounding predictive | Mozilla-only; per-category resolution numbers exist only as a bar chart | studied | 2010 | no | — | F ✓ C ✗ R ✓ |
| 4 | Layer attribution (LLVM, curl, PostgreSQL, Arrow) | **Rule contributor** | A named procedure, not an exhortation: run these flags, read this outcome, conclude this component | Each procedure is project-specific; the transferable part is the *shape* | asserted | all live | LLVM yes (flag→conclusion) | low | F ✓ C ✓ R ✗ |
| 5 | `gradle-issue-reproducer` + Gradle bug form | **Rule contributor** | The only oracle in the corpus that produces evidence outside the report's prose: "Verify that the reproducer exhibits the problem on the GitHub Action page. Link your reproducer to the issue" | One project; requires a public fork | asserted | live | no | low | F ✓ C ✗ R ✗ |
| 6 | Stack Overflow MRE | **Rule contributor** | Minimal/Complete/Reproducible; two named reduction procedures; "Double-check that your example reproduces the problem!"; "transport the example to a fresh environment" | Written for questions, not filed issues | asserted | live | no | low | F ✓ C ✓ R ✗ |
| 7 | Bettenburg et al. (TR'07 / FSE'08 / TSE'10 / ICSM'08) | **Supporting evidence** | The only measured importance ranking and delay-cause ranking; duplicates measured as a *minor* delay cause and a *net information gain* | The famous numbers are conditional likelihoods, not shares of developers; "absent beats wrong" is a quoted developer comment, not a measurement | studied | 2007–2010 | no | — | F ✓ C ✗ R ✗ |
| 8 | Homebrew `bug.yml` + Responsible AI Usage | **Rule contributor** | Pre-conditions that gate submission, a required AI-disclosure checkbox with a stated consequence ("we may block you from submitting future issues"), goal-first field order | The pre-conditions Pass 1 listed are partly wrong (see §11) | asserted | live | no | low | F ✓ C ✗ R ✗ |
| 9 | QUS / AQUSA (Lucassen et al.) | **Rule contributor (criteria only)** | *Problem-oriented*, *atomic*, *conceptually sound* survive being lifted off the `As a…` form, because each is defined over the requirement, not the sentence | AQUSA automates 5 of 13 criteria and **none of the four semantic ones**, so the three we want have no shipped detector | studied (tool) / asserted (criteria) | 2016 | yes (violation + repair per criterion) | med | F ✗ C ✗ R ✓ |
| 10 | Request templates (Go, KEP, PEP 1, Rust RFC, Django) | **Rule contributor** | Motivation-first is unanimous across five independent projects; KEP Goals-as-success-test; Non-Goals; Rust "impact of not doing this"; Go's required prior-proposal answer | Heavy for a two-paragraph request | asserted | all live | Go: before/after code required | low | F ✗ C ✗ R ✓ |
| 11 | Gradle feature form vs bug form | **Rule contributor** | Same repo, opposite order, and a required Context field on the feature form only: "What are you trying to accomplish? What other alternatives have you considered?" | n=1 project | asserted | live | no | low | F ✓ C ✗ R ✓ |
| 12 | CrowdRE'25 | **Supporting evidence (weak)** | 34 of 50 requests carry an NL defect; developers sought no clarification in 39 of 50; clarification is strategic, not technical | n=50 from two repos; the mock-up effect is an unquantified observation | studied (small) | 2025 | no | — | F ✗ C ✗ R ✓ |
| 13 | Short-form cluster (ESR, nohello, dontasktoask, xyproblem) | **Rule contributor** | "Describe the goal, not the step"; "Describe the symptoms, not your guesses" with the label-your-guess escape; xyproblem's "share why you've ruled them out" — the sourced core of B6 | Prescriptive, unmeasured, tonally dated | asserted | live (xyproblem now reachable) | yes, paired | med | F ✓ C ✓ R ✓ |
| 14 | Machine-author cluster (kernel, Ghostty, Homebrew, OpenSSF) | **Rule contributor (top)** | The kernel page is the only source that states B4 and B5 as rules for a machine author, with reasons and a merge exception | Security-scoped; OpenSSF text unreachable | asserted | live | no | low | F ✓ C ✓ R ✓ |
| 15 | Template-conformance null result (Sülün et al., TOSEM'24) | **Justification constraint** | Kills the outcome-based case for conformance: d=0.03, p=1.00 | Conformance is measured by field-header matching, so it may measure form-filling, not information | studied | 2024 | no | — | F ✓ C ✗ R ✓ |
| 16 | Prior art in agent skills | **Partly unreachable** | `awesome-copilot/skills/github-issues` fetched: it is `gh api` mechanics, title length, issue types — no content rules to deconflict | `playwright-bug-reporter` **not located** (see §11) | asserted | live / n/a | no | — | — |
| 17 | Mozilla + Rahman et al. | **Rule contributor + evidence** | Mozilla: "It should explain the problem, not your suggested solution"; "If you have multiple issues, please file separate bug reports". Rahman: *Bug Duplication* ("already fixed in the recent releases") and *False Positive Bug* are the top two non-reproducibility factors | Mozilla contradicts itself on actual/expected order; Rahman reports no combined per-factor rate | asserted / studied | live / 2020 | Mozilla yes, paired | low | F ✓ C ✗ R ✗ |

## 3. Extracted rules

Reader codes R1–R5 and buckets 1–4 as in the brief. **C** = core, **Rf** = reference (file named in §12).

| ID | Rule | Rationale | Reader | Source | Evidence | Genre | Detection without the author | Gameable? What is checked instead | Repair | Bkt | C/Rf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OWN1 | Isolate which project owns the defect by running the layer-splitting procedure the ecosystem provides, and put its commands and outputs in the report | A symptom seen through a stack is not evidence about any layer; the wrong tracker costs a full triage cycle | R1, R2 | LLVM `HowToSubmitABug`; curl `BUGS.md` "convert your program over to plain C"; PostgreSQL "isolate the offending queries" / client-vs-server; Arrow "as few non-Arrow dependencies as possible" | asserted | F, C | The report contains a command sequence whose last step uses only the target project; a reviewer re-runs it | No — the commands are in the text and re-runnable | Run the ecosystem's isolation procedure; if none exists, remove one layer at a time and record each result | 2 | C |
| OWN2 | Reproduce on a version the project currently supports, and say which | "chances are we already fixed them"; a report against an unsupported version is closed unread | R1, R2 | curl "Bugs in old versions"; Linux "A significant part of reports are for bugs that have already been fixed"; Node "reproducing the issue in a currently-supported version" | asserted | F | The stated version is inside the project's published support window; the transcript shows that version | No — the version string is checkable against the release schedule and against the pasted output | Re-run on the latest release; if it no longer fails, do not file | 2 | C |
| OWN3 | Search the tracker before filing and write the query and the nearest hit into the report | Duplication of an already-fixed bug is the single largest non-reproducibility factor | R1, R4 | Arrow "Check existing issues"; Django; Mozilla; PEP 1; Homebrew routing; Rahman F1 (Firefox 26.83%, Eclipse 31.33%) | asserted (rule) / studied (cost) | F, R | The report contains a search string and a link, or an explicit "searched X, nothing matched" | Yes, letter-only. Checked instead: the named nearest issue resolves and is genuinely distinct | Run the search; if a match exists, comment on it instead | 3 | C |
| OWN4 | File one report per independently fixable symptom | Two symptoms in one issue cannot both be closed, and neither gets a regression test | R1, R2, R3 | Mozilla "If you have multiple issues, please file separate bug reports"; Arrow "Each issue should deal with a single bug or feature"; Linux security-bugs; QUS *atomic* | asserted | F, R | Count the distinct expected outcomes. Two that could ship in different commits, in different repos, or on different schedules = two reports | No — the count is read off the text | Split; cross-link; state in each that the other exists and that this one does not depend on it | 1 | C |
| OWN5 | Obey the project's routing before filing: its `config.yml` contact links, its "ask here instead" lines, its component/scope questions | A correctly written report in the wrong queue is still closed | R1 | Gradle `config.yml`; Homebrew's single-formula redirect; Django forum-first; Node help repo; Arrow required `Component(s)`; Angular "Which @angular/* package(s)" | asserted | F, R | `.github/ISSUE_TEMPLATE/config.yml` and the form's routing fields are read; the report's subject matches none of the redirect conditions | Yes, letter-only. Checked instead: the redirect conditions are quoted and each answered | Re-target; or use the discussion channel the project names | 3 | C |
| FRM1 | Open with the user-facing symptom — "I do X, Y breaks" — in the project's own vocabulary, before any statement about its internals | The triager decides in about a minute; internals-first forces a decision on a claim the triager cannot check | R1, R4, R5 | Linux "ensure that a clear summary of the problem and all critical details are presented first. Do not require triage engineers to scan multiple pages of text"; Mozilla summary rules; ESR | asserted | F, C, R | Read the first paragraph. If its subject is a class, function, file or commit in the target project rather than an action the reporter took, it fails | Yes, letter-only. Checked instead: the first paragraph names a command or API call the reporter ran and an output they saw | Move the mechanism below the reproducer; write the symptom in user terms | 1 | C |
| FRM2 | The title names the symptom, not the proposed fix | A solution-shaped title is unsearchable by another user with the same symptom, and pre-commits the maintainer | R1, R4 | Mozilla: "It should explain the problem, not your suggested solution", with paired good/bad examples | asserted | F, R | The title contains no imperative verb aimed at the project ("add", "make", "change") for a defect report, and names an observable | No — the title is one string | Rewrite as symptom + condition, under ~60 characters (Mozilla) | 1 | C |
| FRM3 | Put causal analysis and links into the project's source last, and label it a theory | "educated explanations are a great supplement to but no substitute for facts"; a wrong diagnosis stated first costs more than a right one saves | R1, R2 | PostgreSQL §5.2; ESR "Describe the symptoms, not your guesses… If you feel it's important to state your guess, clearly label it as such"; Linux "stick to verifiable facts… without enumerating speculative implications" | asserted | F, C | Any sentence asserting a mechanism inside the target project appears after the reproducer and carries a hedge or a "why I think so" | Yes, letter-only. Checked instead: every mechanism claim cites a file/line or a run, or is marked unverified | Move it down; convert assertions to "I think X because Y; I did not verify Z" | 1 | C |
| FRM4 | State the goal you were pursuing, not only the step you got stuck on | Lets the reader answer a question you did not ask; the step may be the wrong path | R2, R5 | ESR "Describe the goal, not the step" (paired examples); xyproblem.info; Homebrew "What were you trying to do (and why)?"; Gradle Context field | asserted | F, C, R | A sentence exists whose subject is the reporter and whose verb is the task, independent of the target project's API | Yes, letter-only. Checked instead: remove the goal sentence and ask whether the rest still names a use | Add one sentence: what the build/service/user was trying to achieve | 1 | C |
| FRM5 | Where the target form's field order disagrees with this skill, the form wins; write into its fields in its order | The form is what the triager's eye and the project's automation expect | R1 | Gradle bug form (Current first) vs its own feature form (Expected first); Node (expected before actual); Mozilla (actual before expected in the template) | asserted | F, R | Compare the report's headings against the form's `label:` values in order | No — mechanical comparison | Reorder into the form's fields | 3 | C |
| FRM6 | Describe what you did and what the machine did in chronological order | The useful clues lie in the events immediately prior | R1, R3 | ESR "Describe your problem's symptoms in chronological order"; PostgreSQL "the exact sequence of steps from program start-up" | asserted | F, C | Steps are ordered and each has an observable result; no step is stated out of sequence | Yes, letter-only. Checked instead: the pasted transcript's own ordering matches the prose | Re-order; paste the session log | 1 | Rf |
| EXP1 | State the expected result as a concrete observable value, not as an evaluation of the actual one | "we might run it ourselves, scan the output, and think it looks OK"; "it doesn't work" carries no information | R1, R2, R3 | PostgreSQL §5.2 (verbatim); Stack Overflow "'It doesn't work' isn't descriptive enough… tell other readers what the expected behavior should be"; Mozilla bad examples | asserted | F, C, R | The expected block contains at least one literal a machine could compare against: a string, a number, an exit status, an emitted document. If every sentence is an adjective ("correct", "consistent", "work"), it fails | Yes — "should return 0" satisfies the letter. Checked instead: is the literal *sufficient* to write an assertion? Two different actual outputs must not both satisfy it | Paste the expected output next to the actual, in the same format | 1 | C |
| EXP2 | Say what the expectation is grounded in, and why | Node asks it as a required field; the kernel requires "why you consider that the observed behavior as a problem" | R2 | Node bug form: "What is the expected behavior? **Why is that the expected behavior?**"; Linux security-bugs; Chilana et al. | asserted (rule) / studied (payoff) | F, R | The expected block contains a because-clause naming an artifact: a doc page, a spec section, an error the code itself raises, a project promise | Yes, letter-only. Checked instead: the named artifact is fetchable and says what is claimed | Add the grounding, or state that the grounding is preference and mark it so | 1 | C |
| EXP3 | Prefer the strongest grounding available, in this order: the project's own specification or documentation; runtime logic (a crash, an assertion, an error the project raises); community/user expectation. Genre convention, another product's behavior, an industry standard, prior behavior, and personal preference are weak — say so when you use one | Grounding predicts outcome: specification, community expectation and runtime logic correlate with FIXED; standards, genre conventions and prior behavior with INVALID | R2 | Chilana et al. (χ²(7,N=1000)=35.8, p<.001); PostgreSQL "Failing to comply to the SQL standard is not necessarily a bug either, unless compliance for the specific feature is explicitly claimed" and "if a program does something different from what the documentation says, that is a bug" | **derived** — see §5 for the derivation | F, R | Classify the report's grounding into the seven categories; if it lands in the weak set with no hedge, it fails | Yes — a writer can name a doc page falsely. Checked instead: the doc quote is fetched and read | Find a stronger grounding, or add "this is a preference, not a documented promise" | 1 | C |
| EXP4 | State expected values by content, not by position: name the thing, do not index it | An index identifies nothing to a reader and moves when the source data changes, so an archived report names a different case later | R3, R4 | **derived** from EXP1 (a positional token is not an observable value of the thing) + Arrow's "as small an example as possible… it's really hard for us to debug" + PostgreSQL's rejection of "This is not what I expected"; see §5 | derived | F, R | Every identifier in the expected block resolves to a name in the reproducer's source; no bare ordinal, index, or offset is the sole identifier of a case | No — the identifiers are mechanically enumerable against the reproducer | Replace `[1]` with the parameter name and its value; keep the index only as a tiebreak | 1 | C |
| EXP5 | Any form you propose as the expected one must have been executed, and the transcript of that run is in the report | The reporter is proposing work; a form that does not work costs the maintainer the implementation before it costs anyone else | R2, R3 | Linux security-bugs, AI clause: "ask your tool to propose a fix and **test it** before reporting the problem"; and for reproducers "always ensure your tool provides one and **test it thoroughly**"; Stack Overflow "Double-check that your example reproduces the problem!" | asserted | F, C, R | The proposed form appears in a pasted command or output block, not only in prose. Absent that, it fails | **No** — this is the strongest rule in the set: the check is the presence of a transcript a reviewer can re-run | Run it. If it cannot be run (the form does not exist yet), say "not executed" beside it | 2 | C |
| EXP6 | Give each independent symptom its own expected-behavior block; merge only when one commit would fix both | A merged block cannot be partially accepted, and it hides which half the maintainer disagreed with | R2, R3 | Linux: "please send individual messages… The only exception is when an issue concerns closely related parts maintained by the exact same subset of maintainers, and these parts are expected to be fixed all at once by the same commit"; Mozilla; Arrow; QUS *atomic* | asserted | F, R | Apply the kernel's exception test: same maintainer set and one commit? If no, two blocks | No — the test reads the code owners file and the block | Split the block; state that neither half depends on the other | 1 | C |
| EXP7 | Do not ground an expectation solely in another system's behavior, and never without stating the value | "Especially refrain from merely saying that 'This is not what SQL says/Oracle does'"; genre-convention grounding correlates with INVALID | R2 | PostgreSQL §5.2 (verbatim); Chilana et al. genre conventions (n=71, INVALID-prone) | asserted | F, R | The expected block's only grounding is a comparison to a named other product, with no literal expected value | Yes, letter-only. Checked instead: is a concrete value present in addition? | Add the value; move the comparison into a "prior art" line | 1 | Rf |
| EXP8 | Separate the requirement from the rendering: say which part you need and which part is the project's choice | A maintainer who rejects the rendering should not have to reject the requirement with it | R2 | **derived** from KEP *Non-Goals* + Rust RFC "Rationale and alternatives" + QUS *problem-oriented* ("A user story only specifies the problem… If absolutely necessary, implementation hints can be included as comments"); see §5 | derived | F, R | The expected block contains a sentence bounding what is negotiable, or an explicit "any rendering that carries the same values" | Yes, letter-only. Checked instead: strip the concrete example and ask whether the requirement is still stated | Add: "The exact form is yours; what I need is X" | 1 | C |
| REP1 | Everything needed to reproduce is inside the report | "Provide all parts someone else needs to reproduce your problem in the question itself" | R1, R3 | Stack Overflow *Complete*; PostgreSQL "This should be self-contained"; Django | asserted | F, C | Walk the reproducer: every file, dependency version and command it references is either present or a public artifact | No — mechanical | Inline the missing files; replace private data with generated data | 1 | C |
| REP2 | Run the reproducer in exactly the form you shipped, after your last edit to it | The commonest silent failure is fixing the bug while reducing and not re-running | R1, R2 | Stack Overflow (verbatim); Linux AI clause "test it thoroughly"; "transport the example to a fresh environment" | asserted | F, C | The pasted failure output is consistent with the shipped reproducer's own identifiers (file names, symbols, line numbers) | **No** — a reviewer re-runs it | Re-run from a clean checkout and repaste | 2 | C |
| REP3 | Ship the reproducer in the form the target project accepts | Node forbids exactly the form Gradle requires | R1 | Node: "no ZIP archive, no GitHub repository"; Gradle: "Self-contained Reproducer Project" (required); Angular: "a link to a minimal reproduction"; LLVM: reduced test case attached | asserted | F | Compare the shipped form against the form's own `description:` text | No — mechanical | Convert (inline the snippet, or push the repo) | 3 | C |
| REP4 | Reduce until the reproducer has no dependency outside the target project, then stop | Reduction earns its keep by removing suspects, not by shrinking; PostgreSQL explicitly caps the effort | R1, R2 | Arrow "with as few non-Arrow dependencies as possible"; LLVM `creduce`/`llvm-reduce`; Stack Overflow's two procedures; PostgreSQL: "Do not spend all your time to figure out which changes in the input make the problem go away" and "You are encouraged to minimize the size of your example, but this is not absolutely necessary" | asserted (conflict resolved, §8) | F, C | Enumerate the reproducer's declared dependencies. Any that is not the target project or its transitive runtime fails the rule | **No** — the manifest is machine-readable | Remove the outside dependency and re-run; if the failure disappears, the layer attribution was wrong (OWN1) | 2 | C |
| REP5 | Paste the failing output verbatim as text, complete, not as a screenshot or a paraphrase | The error string is what R4 searches for | R1, R4 | Stack Overflow "DO NOT use images of code"; Node "please provide textual output instead of screenshots"; curl `-v`/`--trace`; Arrow; Mozilla | asserted | F, C | The report contains a fenced block whose content is the tool's own output, and the quoted message matches the tool's message format | Yes — a writer can retype. Checked instead: does the pasted text carry incidental detail (timestamps, paths, frame numbers) a paraphrase would drop? | Repaste from the terminal | 1 | C |
| REP6 | Where the project provides an external oracle for reproducers, run it and link the run | Moves the proof out of the report's prose into an artifact the maintainer trusts | R1, R2 | `gradle-issue-reproducer`: "Verify that the reproducer exhibits the problem on the GitHub Action page. Link your reproducer to the issue" | asserted | F | A CI run URL is present and its conclusion is a failure of the expected kind | **No** — the run is fetched | Fork the template, push, link the failing run | 2 or 3 | Rf |
| REP7 | State the version of the target project and of every layer between it and the symptom | The report is unusable to R4 without a version to compare against | R1, R4 | curl (OS, curl version, library versions, URL/protocol); Node (Version, Platform, Subsystem); Homebrew (`brew config`, `brew doctor`); Angular (`ng version`); Gradle (required) | asserted | F, C | Every named tool in the reproduction chain has a version string somewhere in the report | Yes, letter-only. Checked instead: the versions are mutually consistent and consistent with the pasted output | Add the missing versions | 1 | C |
| REP8 | Never write a step you did not execute; where evidence is missing, say what is missing | The failure mode of a machine author is confident completion of an unobserved field | R1, R2 | Linux AI clause: "If the reproducer does not work, or if the tool cannot produce one, the validity of the report should be seriously questioned"; Homebrew Responsible AI Usage: "Read it, run it, test it"; Ghostty "must have been reviewed *and edited* by a human" | asserted | F, C, R | Every step has an observable outcome stated; a step with none is either unexecuted or uninformative | Yes, letter-only — this is the weakest-detection rule in the set. Checked instead: EXP5, REP2 and REP6, which do have artifacts | Delete the step, or run it | 1 | C |
| REQ1 | A request leads with the problem, not with the API you want | "Start by telling us what problem you're trying to solve. Often a solution already exists!" | R2 | JUnit feature template (verbatim); Rust RFC Motivation-first; KEP Motivation; PEP 1; Django "Explain why"; Gradle feature form's required Context; QUS *problem-oriented* | asserted | R | The first section names a task the requester could not complete, not a construct the project does not have | Yes, letter-only. Checked instead: delete every proposed-API sentence; is a problem still stated? | Move the API below; write the blocked task above | 1 | C |
| REQ2 | A known workaround goes last, in an alternatives slot, and the expected behavior must not depend on it | Framing the request around the workaround reads as "configuration is enough for me" while asking the default to change | R2 | **derived** from xyproblem.info ("If there are other solutions you've already ruled out, share why you've ruled them out"), Gradle Context ("What other alternatives have you considered?"), Node ("What alternatives have you considered?"), Rust RFC "Rationale and alternatives"; see §5 | derived | F, R | The workaround appears above the expected-behavior block, or the expected block's text depends on the workaround's vocabulary. Either fails | Yes, letter-only. Checked instead: delete the workaround section; does the expected block still parse and still state the same requirement? | Move it to the end; add "the expected behavior above does not depend on this"; say why the workaround is insufficient | 1 | C |
| REQ3 | Say who else is blocked and what it costs — both the cost of doing it and the cost of not doing it | Requests are prioritized against other work, not judged on their own | R2 | Go language-change form (required: "Who does this proposal help", "Cost Description", "Is this change backward compatible?"); Rust RFC "What is the impact of not doing this?"; PEP 1 "make sure the idea is applicable to the entire community and not just the author" | asserted | R | The request names at least one party other than the author, or explicitly says the author is the only known case | Yes, letter-only. Checked instead: the named party is a citable issue, thread, or user report | Add the affected population, or admit n=1 | 1 | Rf |
| REQ4 | Say how anyone will know it worked | Without a success test, an accepted request cannot be closed | R2, R3 | KEP Goals: "What is it trying to achieve? **How will we know that this has succeeded?**"; KEP Proposal "What is the desired outcome and how do we measure success?" | asserted | R | A sentence exists that could be turned into a test or a measurement | Yes, letter-only. Checked instead: could a reviewer write the assertion from it? | Add the observable that changes | 1 | Rf |
| REQ5 | State what is out of scope | Non-goals are how a maintainer accepts part of a request without accepting the rest | R2 | KEP Non-Goals: "Listing non-goals helps to focus discussion and make progress" | asserted | R | A non-goals sentence exists | Yes, letter-only. Checked instead: does it exclude something a reader would otherwise assume? | Add one line naming the adjacent thing you are not asking for | 1 | Rf |
| REQ6 | Say whether this has been proposed before and how yours differs | Go makes it a required field; PEP 1 makes it the first workflow step | R2, R4 | Go: "Has this idea, or one like it, been proposed before? If so, how does this proposal differ?" (required); PEP 1 "Vetting an idea publicly before going as far as writing a PEP"; Rust RFC Prior art | asserted | R | A link to a prior discussion, or an explicit "searched X, found none" | Yes, letter-only. Checked instead: the linked discussion resolves and is on topic | Search and link | 3 | Rf |
| REQ7 | A sketch — mock-up, snippet, before-and-after code — is welcome, but it sits below the problem statement and is labelled a sketch | Sketches speed a response, but a solution presented as the requirement violates *problem-oriented* | R2 | CrowdRE'25 (qualitative); Go's before/after example code; QUS *problem-oriented* "If absolutely necessary, implementation hints can be included as comments or descriptions" | asserted (conflict resolved, §8) | R | The sketch appears after the problem statement and carries a hedge ("for example", "any equivalent form") | Yes, letter-only. Checked instead: REQ1's deletion test | Move and label | 1 | Rf |
| MAC1 | Disclose that a tool was used and to what extent, in the form the project asks for | Three of the four policies make it a submission condition with a stated consequence | R1, R2 | Ghostty `AI_POLICY.md`: "You must state the tool you used… along with the extent"; Homebrew's required checkbox; Linux security-bugs | asserted | F, C, R | An `AI_POLICY.md`, a `CONTRIBUTING.md` AI section, or a form checkbox exists and the report answers it | Yes, letter-only. Checked instead: the disclosure names a tool and an extent, not a boilerplate line | Add the disclosure; if the project forbids AI-authored reports, do not file | 3 | Rf |
| MAC2 | Put the summary and every critical detail first; do not make the reader scan pages | "AI-generated reports tend to be excessively long… Configure your tools to produce concise, human-style reports" | R1 | Linux security-bugs, AI section (verbatim); ESR "Volume is not precision" | asserted | F, C, R | The affected version, the symptom and the expected value all appear before the first fold; sections that restate each other exist | Yes, letter-only. Checked instead: word count against the project's own accepted reports | Cut restatements; hoist the version and symptom | 1 | C |
| MAC3 | Match the channel's format: plain text where reports travel by email, the form's Markdown where they do not | "These decorations… do not survive the quoting processes involved in forwarding or replying" | R1 | Linux security-bugs: "always convert your report to plain text without any formatting decorations before sending it" | asserted | F, C | The channel is email and the body contains Markdown decoration | No — mechanical | Strip formatting | 3 | Rf |
| MAC4 | Do not enumerate speculative consequences | Invented impact is the machine-author tell that triage engineers name | R1, R2 | Linux: "go to great lengths inventing theoretical consequences… Please stick to verifiable facts" | asserted | F, R | Sentences of the form "this could allow / might lead to" with no observed instance | Yes, letter-only. Checked instead: each impact claim has an observed instance in the report | Delete, or reduce to what was observed | 1 | C |
| MAC5 | The human filing it must be able to explain and defend it without the tool | The obligation the policies actually enforce | R2 | Ghostty: "If you can't explain what your changes do… do not contribute"; Homebrew: "Answer maintainer questions… yourself without using AI/LLM" | asserted | F, C, R | **None available from the text** | — | Ask the human before filing | 4 | C |
| MSG1 | Put the ask in the first message; do not send a greeting alone | "you're actually just making the other person wait for you to phrase your question" | R5 | nohello.net; dontasktoask.com ("The solution is not to ask to ask, but just to ask") | asserted | C | The first message contains no interrogative or imperative directed at the recipient | No — one message, mechanically checked | Merge greeting and question | 1 | Rf |
| MSG2 | Say what you already ruled out and how | Prevents the colleague repeating your last hour | R5, R2 | xyproblem.info; ESR "Describe the diagnostic steps you took to try and pin down the problem yourself" | asserted | C, F | A ruled-out list exists, each entry with its observation | Yes, letter-only. Checked instead: each entry names a command or output | Add the list | 1 | Rf |
| MSG3 | Name the shared artifact by an identifier that resolves in the shared repository | The colleague shares the codebase, not the last hour | R5 | **derived** from EXP4 (identify by content) + Linux "the file names and functions where the bug is suspected"; see §5 | derived | C | Every identifier in the message is greppable in the shared repo at a stated ref | No — mechanical | Replace "that thing in the parser" with the symbol and the ref | 3 | Rf |
| MSG4 | Name what you want back: a decision, a pointer, or a review | Without it the colleague guesses at the interrupt's cost | R5 | ESR "Be explicit about your question"; **derived** with KEP Goals | asserted | C | The message contains a request whose satisfaction is checkable | Yes, letter-only. Checked instead: could the recipient reply in one message? | Add "I need X from you" | 1 | Rf |
| TPL1 | Fill the target project's required fields, by their names, so the text drops into the form unchanged | Filling the fields buys admission and routing. It does **not** buy speed: conformance predicts nothing | R1 | Gradle/Node/Homebrew/Arrow required fields; **Sülün et al. TOSEM'24** for what it does not buy | asserted (rule) / studied (the negative) | F, R | Every `validations: required: true` field in the form has non-placeholder content under its exact `label:` | No — mechanical against the YAML | Fill it, or fail TPL2 | 3 | C |
| TPL2 | A field you have no evidence for says what is missing, not a plausible guess | A guessed field is worse than an empty one because it cannot be distinguished from evidence | R1, R2 | Linux "the reproducer or its status"; **derived** from REP8 + PostgreSQL "state all the facts and only facts" | derived | F, C, R | Each required field either contains an observation or an explicit "not established: <what would establish it>" | Yes, letter-only. Checked instead: cross-check each field's claim against the pasted transcripts | Replace the guess with the gap | 1 | C |

## 4. The genre matrix

Cells: **Req** required, **Opt** optional, **n/a** not applicable.

| Rule family | Filed issue | Colleague message | Request | Source deciding the cells |
| --- | --- | --- | --- | --- |
| OWN1 layer attribution | **Req** | **Req** | n/a | LLVM/curl/Arrow require it before filing; a colleague shares the stack, so the question "whose layer" still decides who acts; a request is about a project you have already chosen |
| OWN2 supported version | **Req** | Opt | Opt | curl, Linux, Node scope it to defects; a request against an old version is still a request |
| OWN3 tracker search | **Req** | n/a | **Req** | Arrow, Django, Mozilla (defects); Go, PEP 1 (requests); a colleague is not a tracker |
| OWN4 one per symptom | **Req** | Opt | **Req** | Mozilla, Arrow, Linux; QUS *atomic* for requests; chat tolerates two questions in one message |
| OWN5 routing | **Req** | n/a | **Req** | Gradle `config.yml`, Homebrew, Django, Node |
| FRM1–2 symptom-first, symptom title | **Req** | **Req** | **Req** (as "problem-first") | Mozilla, Linux, ESR; for requests the same rule is REQ1 |
| FRM3 analysis last | **Req** | Opt | Opt | PostgreSQL, ESR, Linux. In chat a shared-context colleague can take the theory earlier, but it is still labelled |
| FRM4 goal not step | **Req** | **Req** | **Req** | ESR, xyproblem, Homebrew, Gradle Context |
| FRM5 form order wins | **Req** | n/a | **Req** | Gradle's own bug/feature inversion |
| EXP1–3 value, grounding, strength | **Req** | **Req** | **Req** | PostgreSQL, SO, Node's "why", Chilana |
| EXP4 content not position | **Req** | **Req** | **Req** | derived; §5 |
| EXP5 proposed form executed | **Req** | **Req** | **Req** | Linux AI clause; SO |
| EXP6 one block per symptom | **Req** | Opt | **Req** | Linux merge exception; Mozilla |
| EXP7 no cross-product-only grounding | **Req** | Opt | Opt | PostgreSQL verbatim; for a request, prior art is legitimately a motivation |
| EXP8 requirement vs rendering | Opt | Opt | **Req** | KEP Non-Goals; QUS *problem-oriented* |
| REP1–2 complete, re-run | **Req** | **Req** | n/a | SO; Linux |
| REP3 shipped form | **Req** | Opt | n/a | Node vs Gradle vs Angular |
| REP4 reduce to zero outside deps | **Req** | Opt | n/a | Arrow, LLVM; PostgreSQL caps the effort |
| REP5 verbatim output | **Req** | **Req** | Opt | SO, Node, curl, Arrow |
| REP6 external oracle | Opt (**Req** where offered) | n/a | n/a | `gradle-issue-reproducer` |
| REP7 versions | **Req** | Opt | Opt | curl, Node, Homebrew, Angular |
| REP8 no unexecuted step | **Req** | **Req** | **Req** | Linux, Homebrew, Ghostty |
| REQ1, 3, 4, 5, 6, 7 | n/a | Opt | **Req** (REQ5, REQ7 Opt) | JUnit, Rust RFC, KEP, Go, PEP 1, Django, CrowdRE'25 |
| REQ2 workaround last | **Req** | Opt | **Req** | derived; §5. A defect report can carry a workaround too, and the same subordination applies |
| MAC1 disclosure | **Req** where a policy exists | n/a | **Req** where a policy exists | Ghostty, Homebrew, Linux |
| MAC2, 4 concision, no speculation | **Req** | **Req** | **Req** | Linux |
| MAC3 channel format | **Req** for email trackers | n/a | **Req** for email trackers | Linux |
| MAC5 human can defend it | **Req** | Opt | **Req** | Ghostty, Homebrew |
| MSG1–4 | n/a | **Req** | n/a | nohello, dontasktoask, xyproblem, ESR |
| TPL1–2 | **Req** where a form exists | n/a | **Req** where a form exists | Sülün et al. for the justification; the forms for the obligation |

## 5. The expected-behavior test

Send an expected-behavior block through six questions in order. It passes only if every answer is yes; the first no
is the finding.

1. **Is there a literal?** At least one string, number, exit status, or emitted artifact a machine could compare
   against. (EXP1)
2. **Is the literal sufficient?** Could two materially different actual outputs both satisfy it? If yes, it is an
   adjective in disguise. (EXP1)
3. **Does every identifier in it resolve by content?** No bare index, ordinal, or offset is the sole identifier of a
   case. (EXP4)
4. **Is the grounding named, and how strong?** A because-clause naming a fetchable artifact, classified against
   Chilana's seven. Weak groundings must be marked weak. (EXP2, EXP3, EXP7)
5. **Was it executed?** If the block proposes a form, is the transcript of running it present? (EXP5)
6. **Is it one block per symptom, and is the requirement separated from the rendering?** (EXP6, EXP8)

### Deriving EXP3, EXP4, EXP8, REQ2, MSG3

These are the rules Pass 1 could not source. Each is built from sourced criteria, stated here so the derivation can
be audited.

**EXP3 (grounding hierarchy)** is derived from two sourced facts and no third. Chilana et al. measured that the
source of a reporter's expectation predicts resolution (χ²(7, N=1000) = 35.8, p<.001), that specification, community
expectations and runtime logic are the FIXED-associated groups, and that "Bugs about standards, genre conventions,
and prior behavior were more likely to get marked INVALID". PostgreSQL independently states the *mechanism* for two
of the weak cases: a standard is only binding where "compliance for the specific feature is explicitly claimed", and
documentation divergence "is a bug" outright. The ordering is derived; the group membership is studied.

**EXP4 (content not position)** is derived from EXP1 plus the reader table. EXP1 (sourced verbatim from PostgreSQL
and Stack Overflow) requires the expected result to be an *observable value*. A positional token is not a value of
the thing; it is a value of the enumeration the thing currently sits in. R3 and R4 hold the report and the current
code, and nothing of the original run — so a token whose referent depends on the state of the source data at the time
of writing fails to identify anything for them. The derivation is: observable value (sourced) + reader who holds only
the text (fixed in the brief) ⇒ the value must be stable under changes to the enumeration.

**EXP8 (requirement vs rendering)** is derived from KEP *Non-Goals* ("Listing non-goals helps to focus discussion")
and QUS *problem-oriented* ("A user story only specifies the problem… If absolutely necessary, implementation hints
can be included as comments"). Both say the same thing from opposite ends: the maintainer must be able to accept the
requirement while rejecting the shape.

**REQ2 (workaround not the frame)** is derived from xyproblem.info's "If there are other solutions you've already
ruled out, share why you've ruled them out — this gives more information about your requirements", plus the fact that
three independent request forms give the alternatives a *dedicated, subordinate slot* (Gradle Context, Node
"What alternatives have you considered?", Rust RFC "Rationale and alternatives"). The derived part is the position
rule: a slot that exists below the expected behavior in three forms is a slot the workaround belongs in, and the
deletion test (remove the workaround; does the requirement survive?) is the operational form of xyproblem's own
diagnosis — the reporter got stuck on Y and stopped being able to state X.

**MSG3** is EXP4 applied to a reader who shares the repository: the identifier must resolve, which for a colleague
means greppable at a named ref.

### The concrete cases

**Case 1 — `value = "x"` versus `[1]` (the accepted `gradle/gradle#39079`).** The rejected draft proposed
`methodInParameterizedClass(String)[2][1]`. The test: Q1 passes (a literal). Q2 passes (unique). **Q3 fails**: `[2]`
and `[1]` are ordinals into the argument source, and identify nothing to R3 or R4. The rule's repair is "replace the
ordinal with the parameter name and its value; keep the index only as a tiebreak". That is exactly the accepted
text — `firstParameterizedMethod(String) [1] value = ""` — and the accepted issue states the derivation in the
reporter's own words: "An index does not say what ran, and it moves when a row is added to the argument source, so a
report archived last week names a different case today."

**Case 2 — the unexecuted `--tests` form.** The draft argued for an index-based name partly because it would let a
reader re-run one case. **Q5 fails**: no transcript. The rule's repair is "run it, or say 'not executed'". Running it
is what produced the accepted issue's Context section, which pastes two failing invocations
(`> No tests found for given includes: …`) and then names the one form that does work
(`--select-unique-id=…`) and why it is unavailable from the XML. The rule turns a rejected assertion into the
strongest paragraph in the report.

**Case 3 — the workaround as frame.** The draft framed the request around
`junit.jupiter.params.displayname.default`. REQ2's detection: the workaround appeared above the expected block, and
the expected block's vocabulary depended on it. The deletion test fails. The repair — move it last, state that the
expected behavior does not depend on it — is what the accepted issue does verbatim: the Workaround section is last,
and it ends "Note that the Expected Behavior above does not depend on it."

**Case 4 — two symptoms in one block.** `@ParameterizedTest` losing the method name and `@ParameterizedClass` losing
the class arguments were merged. EXP6's detection is the kernel's exception test: same maintainer set, one commit?
No — one is Gradle's XML writer, the other is JUnit's display-name default. Two blocks, and in fact two reports
(OWN4), which is what shipped: `gradle/gradle#39079` and `junit-team/junit-framework#6041`, each stating that it does
not depend on the other.

**Case 5 — the confident cause for a project that had shipped the fix.** OWN2 and OWN3. The accepted JUnit issue
carries the repaired form: "#5441 puts the class-invocation index into the legacy reporting name… #5524 writes the
display names of all ancestors… I verified both on 6.1.3 and on `main` built from source." The already-shipped fixes
are named, their scope is bounded, and the remaining gap is stated — instead of a cause that had already been
removed.

## 6. The shapes that fail vacuously

| Shape | Why every rule's letter is satisfied | Detection |
| --- | --- | --- |
| **The fully-filled template with nothing in it** | Every required field has text; TPL1 passes | Cross-field consistency: the version in the Environment field must appear in the pasted output; the identifiers in the expected block must appear in the reproducer. A filled form whose fields do not reference each other is filled, not written |
| **"It should work"** | An expected block exists; EXP1's letter can be met by "should return successfully" | The test's Q2: could two materially different outputs both satisfy it? Ask a reviewer to write the assertion from the block alone. If they cannot, it fails |
| **The reproducer that was never run** | REP1, REP3, REP5 all pass; a plausible transcript can be composed | The pasted output must carry incidental detail the writer would not invent: absolute paths, timestamps, frame numbers, the tool's exact message punctuation. Then re-run it (REP2) — this is why REP2 is bucket 2 and not bucket 1 |
| **The confident cause for a project that already fixed it** | FRM3 passes if the analysis is at the end and hedged; the analysis may even be correct about an old release | OWN2: the version in the report must be inside the support window *and* appear in the pasted output. Then search the project's closed issues and release notes for the symptom (OWN3). Rahman et al.'s top non-reproducibility factor is exactly this |
| **The request framed around its own workaround** | REQ1 can pass — the first paragraph names a problem — while every subsequent paragraph is about the setting | REQ2's deletion test, applied to the whole document: delete every sentence mentioning the workaround. If the remaining text no longer states a requirement, the workaround is the frame |
| **The report that restates the same fact in four sections** | MAC2's letter ("summary first") passes | Section-to-section novelty: each section must contain at least one literal absent from every earlier section. This is the operational form of the kernel's "Do not require triage engineers to scan multiple pages of text" |
| **The grounding that names a doc page which does not say it** | EXP2 and EXP3 both pass on the text | Fetch the named artifact and read the claimed sentence. This is why EXP3's substitute check is "the doc quote is fetched", not "a grounding is named" |

## 7. Worked examples

One per family, from published sources. Bad/good pairs marked *(published pair)* are the source's own.

**Ownership (OWN1).** Before: "Ghostty crashes when I run my Go program." After, following LLVM's shape: run with
the front-end-only flags, record the outcome, conclude the component; or curl's "convert your program over to plain
C and follow the steps outlined above". The transferable move is that the report contains the elimination, not the
conclusion.

**Framing (FRM2)** *(published pair, Mozilla)*. Before: "Software crashes." After: "Cancelling a File Copy dialog
crashes File Manager." Before: "Browser should work with my web site." After: "Down-arrow scrolling doesn't work in
`<textarea>` styled with `overflow:hidden`."

**Goal not step (FRM4)** *(published pair, ESR)*. Before: "How do I get the color-picker on the FooDraw program to
take a hexadecimal RGB value?" After: "I'm trying to replace the color table on an image with values of my choosing.
Right now the only way I can see to do this is by editing each table slot, but I can't get FooDraw's color picker to
take a hexadecimal RGB value."

**Symptoms not guesses (FRM3)** *(published pair, ESR)*. Before: "I'm getting back-to-back SIG11 errors on kernel
compiles, and suspect a hairline crack on one of the motherboard traces. What's the best way to check for those?"
After: a paragraph of hardware, timing, and what was already swapped out — theory removed, observations kept.

**Expected behavior (EXP1, EXP4)**. Before (`junit-platform-console-standalone`'s own form, quoted in the accepted
issue as the thing not to adopt): `methodInParameterizedClass(String)[2][1]`. After (`gradle/gradle#39079`):
`firstParameterizedMethod(String) [1] value = ""`, with the requirement separated from the rendering — "The exact
rendering is yours to choose. What I need is the method name and the arguments."

**Reproduction (REP1, REP4)** *(published, Arrow)*. Arrow's own good-report example is five lines of `pyarrow` with
the two `print` calls and their exact output pasted, and no dependency outside Arrow. Its stated bad case: "it
crashes trying to read my file, but I can't share it with you."

**Request (REQ1, REQ2)**. Before: "Gradle should support `junit.jupiter.params.displayname.default` per-task."
After (`junit-team/junit-framework#6041`): "Four test cases run… Nothing says whether a row ran with `flag = true` or
`flag = false`" first; the configuration attempt second, under the heading "Even
`junit.jupiter.params.displayname.default` does not fix it"; the ask third.

**Machine authorship (MAC2, MAC4)** *(published rule, Linux)*. Before: a multi-section report enumerating theoretical
consequences. After: "a clear summary of the problem and all critical details are presented first", and impact stated
as a verifiable fact — the kernel's own example, "this bug permits any user to gain CAP_NET_ADMIN".

**Colleague message (MSG1)** *(published pair, nohello.net)*. Before: "hi" … four minutes …
"what time was taht thing again?" After: both in one message.

## 8. Conflicts and how they were decided

**1. Order — settled per genre, with an override.** For a defect, the *user-facing symptom precedes the mechanism*
(FRM1) is universal and survives; *actual precedes expected* does not, and the skill must not state it. Gradle's bug
form requires Current first, its feature form requires Expected first; Node requires expected then actual; Mozilla's
own page puts actual first in its template and expected first in its worked example and its checklist. The skill
therefore states FRM1 as a rule and FRM5 as its resolution: **the target form's field order wins over any ordering
preference**, and the agent reads the form before writing. For requests, motivation-first is unanimous across five
independent projects and is stated as REQ1.

**2. How hard to reduce — settled as a stop condition, not a size target.** The apparent conflict is between
projects that demand reduction (Stack Overflow, LLVM, Arrow, Angular) and PostgreSQL, which says "Do not spend all
your time to figure out which changes in the input make the problem go away" — but PostgreSQL also says "You are
encouraged to minimize the size of your example, but this is not absolutely necessary. If the bug is reproducible, we
will find it either way." Both are consistent with a rule about *purpose*: reduction earns its keep by eliminating
suspect layers, not by being small. REP4 therefore states the stop condition — no dependency outside the target
project — and explicitly does not ask for further shrinking. The *form* is a separate, project-scoped question
settled by REP3: Node forbids the archive and the repository that Gradle requires, and Angular requires a link, so
the agent reads the form. Renovate could not be confirmed as demanding reduction (see §11).

**3. Duplicates — settled in favour of a cheap, recorded search.** Every project requires a search, and the measured
evidence says duplicates cost little (Bettenburg: duplicates rank 16th of 19 delay causes at 10% severeness; "developers
do not suffer too much from bug duplicates") and add information (ICSM'08 Table 1: +0.918 stack traces, +1.412
reporters, +0.631 operating systems per master report, all p<.001). Against that, Rahman et al. find duplication the
largest single non-reproducibility factor (Firefox 26.83%, Eclipse 31.33%). The resolution is that these measure
different things: filing a *second* report of a live bug is cheap; filing a report of a bug *already fixed in a
release you did not test* is expensive and lands in the same bucket. OWN3 therefore requires the search and requires
its result to be written into the report — which serves the compliance obligation and R4 at once — while OWN2
carries the expensive half. The skill does not tell the agent to suppress a report because a similar issue exists.

**4. Regression framing — settled as weak-unless-the-form-asks.** Chilana et al. put prior behavior with the
INVALID-prone groups: "Bugs about standards, genre conventions, and prior behavior were more likely to get marked
INVALID." So "it used to work in X" is a **weak** grounding under EXP3 by default. The condition that makes it strong
is structural, not rhetorical: where the project ships a regression form that makes the last working version a
required field (Gradle `30_contributor_regression.yml`'s "Gradle version that used to work"; Rust's
`regression.md` "It most recently worked on"), the project has declared prior behavior binding, and the grounding
becomes as strong as a specification. The agent's test is whether that form exists, which is a bucket-3 lookup.

**5. Sketch or no sketch — settled as permitted and subordinated.** CrowdRE'25's finding is real but qualitative:
"users who included mock-ups, example code snippets, or links to similar implementations typically received faster
and more positive responses" — no measured effect, n=50, two repositories. QUS's *problem-oriented* is not violated
by a sketch as such; the criterion's own text allows implementation hints "as comments or descriptions". REQ7
therefore permits the sketch, places it below the problem statement, and requires it to be labelled, with REQ1's
deletion test as the detection.

**6. Template conformance — the rule survives, its justification does not. This one stays partly open.** Sülün et
al. (TOSEM 2024, 1,916,057 issues, 100 repositories) find that a project *having* a template predicts faster
resolution (Mann-Whitney U, p=0.00, Cohen's d=0.61; mean TTR 381.02 → 103.18 days) and that an individual issue's
*conformance* predicts nothing (TTR p=1.00, d=0.03; reopens p=0.47, d=0.01; comments p=1.00, d=0.09). TPL1 keeps the
obligation and states what it buys: admission (Homebrew: "We may close your issue without comment if you don't fill
out the checklist below"; Gradle: "we will close issues that don't provide enough information") and routing
(Arrow's `Component(s)`, Angular's package question). **That replacement justification is asserted, not measured**,
and the report flags it as the one conflict returned partly undecided. A plausible confound is worth carrying: the
study measures conformance by field-header matching, so it may be measuring form-filling rather than information —
which is precisely the vacuous shape TPL2 exists to catch.

## 9. The detectability matrix

Bucket 2 rules name the run. Bucket 3 rules name the lookup and its limits.

| Rule | Bkt | Source deciding the bucket | The run / the lookup, and what its verdict establishes |
| --- | --- | --- | --- |
| OWN1 | 2 | LLVM, curl, Arrow | **Run:** the ecosystem's isolation sequence (e.g. `clang -emit-llvm -Xclang -disable-llvm-passes`), each step's outcome recorded. Establishes which component still fails; does not establish the cause inside it |
| OWN2 | 2 | curl, Linux, Node | **Run:** the reproducer on the newest supported release. Establishes that the defect survives; does not establish it is not already fixed on `main` |
| OWN3 | 3 | Arrow, Django, Mozilla | **Lookup:** a tracker search, recorded. Establishes that a query returned nothing; does not establish absence — trackers are searched by title and label, and duplicate detection is a research problem |
| OWN4 | 1 | Mozilla, Arrow, Linux | — |
| OWN5 | 3 | Gradle `config.yml` | **Lookup:** `.github/ISSUE_TEMPLATE/config.yml`, `CONTRIBUTING.md`, the form's routing fields. Establishes where the project wants this; does not establish that the redirect target will take it |
| FRM1–4, FRM6 | 1 | Mozilla, ESR, PostgreSQL, Linux | — |
| FRM5 | 3 | Gradle bug vs feature form | **Lookup:** the form YAML's `label:` sequence. Establishes the required order exactly |
| EXP1, EXP2, EXP3, EXP4, EXP6, EXP7, EXP8 | 1 | PostgreSQL, SO, Node, Chilana, Linux | — (EXP2/EXP3 carry a bucket-3 *substitute* check: fetch the named grounding artifact) |
| EXP5 | 2 | Linux AI clause; SO | **Run:** the proposed form itself, in the tool that would consume it, with the transcript pasted. Establishes that the form works; does not establish that it is the best form |
| REP1, REP5, REP7, REP8 | 1 | SO, Node, curl, Linux | — |
| REP2 | 2 | SO verbatim | **Run:** the shipped reproducer from a clean checkout, after the last edit; ideally "transport the example to a fresh environment". Establishes the failure survives packaging; does not establish it survives another OS |
| REP3 | 3 | Node vs Gradle vs Angular | **Lookup:** the form's `description:` for the reproducer field. Establishes the accepted form |
| REP4 | 2 | Arrow, LLVM, PostgreSQL | **Run:** the reproducer with each non-target dependency removed. Establishes the failure needs only the target project; a failure that disappears refutes OWN1 |
| REP6 | 2 (3 where only the link is checked) | `gradle-issue-reproducer` | **Run:** the project's reproducer CI. **Lookup:** the run URL's conclusion. Establishes the failure on the project's own infrastructure; does not establish it on a released version unless the workflow pins one |
| REQ1, REQ2, REQ3, REQ4, REQ5, REQ7 | 1 | JUnit, Rust RFC, KEP, Go | — |
| REQ6 | 3 | Go (required field), PEP 1 | **Lookup:** tracker and discussion-forum search. Establishes a prior proposal exists; a null result establishes nothing (same limit as OWN3) |
| MAC1 | 3 | Ghostty, Homebrew, Linux | **Lookup:** `AI_POLICY.md`, `CONTRIBUTING.md`, the form's checkboxes. Establishes what disclosure is demanded; does not establish that disclosure is sufficient — Ghostty also bans AI-generated media and Homebrew bans AI-written replies |
| MAC2, MAC4 | 1 | Linux | — |
| MAC3 | 3 | Linux | **Lookup:** the project's `SECURITY.md` / reporting channel. Establishes whether the destination is email |
| MAC5 | **4** | Ghostty, Homebrew | Human judgment. The agent raises it; it may not decide it |
| MSG1, MSG2, MSG4 | 1 | nohello, xyproblem, ESR | — |
| MSG3 | 3 | derived + Linux | **Lookup:** grep the shared repo at the stated ref. Establishes the identifier resolves |
| TPL1 | 3 | the forms; Sülün et al. | **Lookup:** every `validations: required: true` block in the form YAML. Establishes admissibility; **establishes nothing about resolution speed** |
| TPL2 | 1 | derived from REP8 + PostgreSQL | — |

**False-positive costs.** Six detections fire on legitimate reports. **OWN1** fires on a defect genuinely in the
interaction between two projects — the agent files against the project that owns the *contract* and says so, as
`junit-framework#6041` does ("Why this is not a report-format issue"). **EXP4** fires where the artifact's own
vocabulary is positional (a byte offset, a line number, a stack frame) — the agent keeps the ordinal and adds the
content beside it. **OWN4/EXP6** fire on a genuine one-commit fix across two files — the kernel's exception clause is
the escape, and it must be stated. **REP4** fires where the defect only appears through a dependency — the agent says
so and ships the smallest chain, which is what LLVM's front-end path does. **EXP3** fires on a report against a
project with no specification, where personal expectation is the only grounding available — the agent marks it weak
and adds a second reporter if one exists (REQ3). **MAC4** fires on an impact that was actually observed — the agent
keeps it and pastes the observation.

## 10. Baseline audit

| | Verdict | Evidence |
| --- | --- | --- |
| **B1** user-facing problem first | **Survives, rationale strengthened** | Was a taste claim; is now the operational form of the Linux AI clause ("Do not require triage engineers to scan multiple pages of text"), Mozilla's summary rules, and R1's one-minute budget. Becomes FRM1+FRM2 |
| **B2** causal analysis last, if at all | **Survives, rationale changed** | The baseline's reason was "the analysis may be wrong". PostgreSQL's is stronger and different: even a *correct* analysis is no substitute, "If we are going to fix the bug we still have to see it happen for ourselves first". ESR adds the escape the baseline lacked — a guess may be stated if labelled with what ruled it out. Becomes FRM3 |
| **B3** values, not positional artifacts | **Survives as derived, needs restating** | No source states it. It is derivable from PostgreSQL's and Stack Overflow's observable-value rules plus R3/R4, who hold only the text (§5). The restatement adds the missing half: *stability under change of the enumeration* is why, not merely readability. Becomes EXP4 |
| **B4** proposed forms must be checked | **Survives, now sourced** | The Linux security-bugs AI clause states it directly for a machine author: "ask your tool to propose a fix and **test it** before reporting" and, for reproducers, "test it thoroughly. If the reproducer does not work… the validity of the report should be seriously questioned." Stack Overflow's "Double-check that your example reproduces the problem!" covers the reproducer half. Becomes EXP5, the only rule in the set that is both bucket 2 and ungameable |
| **B5** one expectation per symptom | **Survives, now sourced with a detection** | The baseline had only "one bug per report" behind it. The kernel supplies the *test*: separate messages, "The only exception is when an issue concerns closely related parts maintained by the exact same subset of maintainers, and these parts are expected to be fixed all at once by the same commit." That converts an aesthetic into a checkable predicate. Becomes OWN4 + EXP6 |
| **B6** workaround not the frame | **Survives as derived, needs restating** | xyproblem.info supplies the diagnosis and the disposal slot ("share why you've ruled them out"); three request forms supply the slot's position. The restatement adds the detection the baseline lacked: the deletion test. Becomes REQ2 |
| **B7** establish which project owns the defect | **Survives, strongly sourced** | Four projects converge on a *procedure*, not an exhortation, and two (Arrow, Angular) make component attribution a required form field. Becomes OWN1 + OWN5 |
| **B8** fill the target's template fields | **Survives with a changed rationale** | The outcome-based justification is refuted: conformance predicts nothing (d=0.03, p=1.00, n≈717k eligible issues). What survives is admission and routing, both asserted. Becomes TPL1, with TPL2 added to stop the vacuous pass |

**What the baseline misses, in descending order of cost.** The recorded failure's own misses come first.

1. **No supported-version check (OWN2).** The failure proposed filing against a project that had already shipped the
   fix. This is the single largest measured non-reproducibility factor (Rahman: Firefox 26.83%, Eclipse 31.33%) and
   the kernel names it too. The baseline has nothing on it.
2. **No rule that the expectation must be grounded, and no strength ordering (EXP2, EXP3).** The grounding is the one
   variable measured to predict FIXED versus INVALID, and Node makes it a required field. The baseline's B3 governs
   the *form* of the expected value and says nothing about *why* it is expected.
3. **No re-run-what-you-ship rule (REP2).** B4 covers proposed forms; nothing covers the reproducer itself, which is
   the artifact most likely to have been silently fixed during reduction.
4. **Nothing about the machine-authorship obligations (MAC1–MAC5).** Disclosure is a submission condition at three of
   the four projects that have a policy, with stated consequences. Concision and the ban on speculative impact are
   stated *specifically about machine-written reports* and are the tells triagers name.
5. **Nothing about the request genre at all.** B1–B8 are defect rules. Motivation-first, non-goals, the success test,
   the prior-proposal question and the cost statement are all missing, and Gradle's own two forms show that a defect
   rule applied to a request produces the wrong order.
6. **Nothing about a colleague message.** R5 has four rules and the baseline covers none of them.
7. **No stop condition on reduction (REP4).** The baseline neither demands reduction nor bounds it.
8. **No routing step (OWN5).** A correct report in the wrong queue is closed regardless of B1–B8.

## 11. Evidence map and verification

Every figure was read in the source text. Corrections to Pass 1 and to the common secondary retellings are named.

| Figure | Sample | Source (primary text read) | Verdict |
| --- | --- | --- | --- |
| OB present 93.5%, EB 35.2%, S2R 51.4%; all three 22.1% | 2,912 bug reports, 9 projects (Docker, Eclipse, Facebook, Firefox, Hibernate, Httpd, LibreOffice, OpenMRS, Wordpress-Android), 4 trackers | Chaparro et al., FSE'17, author PDF `personal.utdallas.edu/~vince/papers/fse17.pdf`, Table 1 | **Confirmed** |
| Discourse patterns: 154 total (OB 90, EB 31, S2R 33); 87/29/24 unique | same | same, Table 2 | **Confirmed** |
| Detector: EB precision 85.9%, recall 93.2% (F1 89.4); S2R precision 69.2%, recall 83.0% (F1 74.9) | 1,821-report validation set | same, Table 4 | **Confirmed, with a correction.** **There is no OB detector**; DeMIBuD detects missing EB and S2R only. The two figures come from two different best settings of DeMIBuD-ML, not one configuration |
| Ground truth: 9 coders, every report double-coded, 38.9% had a disagreement resolved by a third | 2,912 | same | **Confirmed** |
| Developer importance ranking: steps to reproduce 83%, stack traces 57%, test cases 51%, observed behavior 33%, screenshots 26%, expected behavior 22%, code examples 14%, summary 13% | 130 consistent developer responses (of 156; 466 of 2,226 contacted responded overall) | Bettenburg et al., TSE 2010 Table 2 = FSE 2008 Table 2, `thomas-zimmermann.com/publications/files/zimmermann-tse-2010.pdf` | **Confirmed, with a correction.** The percentage is **not** the share of developers who named the item. It is `Importance(i) = N(named in top three) / N(had used it)` — a conditional likelihood. Any retelling as "83% of developers said steps to reproduce" is wrong |
| Delay causes: errors in steps to reproduce 79%, **incomplete information 74%**, wrong observed behavior 48%, wrong expected behavior 27%, **duplicates 10%** | same | same, Table 2 | **Confirmed**, same conditional-likelihood caveat. Duplicates rank 16th of 19 |
| "The biggest causes of delay are not wrong information, but absent information" | — | same, §3.4 | **Corrected.** This is a **quoted free-text comment from one developer**, not a paper-level finding, and no number attaches to it. Pass 1 should not cite it as a measured result. The nearest measured support is the 74% versus the wrong-field items (7–48%) |
| Duplicate base rates: Mozilla ~30%, Eclipse ~20% | — | Bettenburg et al., ICSM 2008 §1 | **Corrected.** These are **cited from Anvik et al.**, not measured here. The paper's own Eclipse dataset is 211,843 reports with 16,511 masters and 27,838 duplicates, and it never states the ratio |
| Duplicates add information (Eclipse, per master report): stack traces +0.918, reporters +1.412, OS +0.631, screenshots +0.145, all p<.001 | 16,511 masters / 27,838 duplicates | ICSM 2008 Table 1 | **Confirmed.** No figure exists for "what fraction of duplicates added information" — the result is averages per master. Mozilla figures come from TSE 2010 §5, not ICSM |
| Merging duplicates improves triage: SVM Top-1 23.18→25.45, Top-5 50.83→55.95 (McNemar p=.05) | 8,623 masters / 23,990 extended | ICSM 2008 Table 2 | **Confirmed** |
| CUEZILLA accuracy | 289 rated reports | TR'07/FSE'08 vs TSE'10 | **Corrected.** No paper reports a correlation with developer ratings. FSE: 31–48% exact on a 5-point scale (80–91% off-by-one); TSE redid it on 3 classes and reports 43–50%. The two are not comparable, and FSE's own conclusion ("up to 41%") contradicts its own table |
| Expectation groundings: reporter expectations 337, runtime logic 195, specification 177, community expectations 85, genre conventions 71, prior behavior 69, standards 41 (n=975 of 1,000; 25 excluded) | uniform random sample of 1,000 from 420,005 closed Mozilla reports | Chilana, **Amy J.** Ko & Wobbrock, VL/HCC'10, `faculty.washington.edu/wobbrock/pubs/vlhcc-10.02.pdf` | **Confirmed, with corrections.** The author is **Amy J. Ko**, not Andrew J. Ko. Category names corrected as listed. Counts are raw, not percentages |
| Grounding predicts resolution: χ²(7, N=1000) = 35.8, p<.001; specification / community expectations / runtime logic → FIXED; **standards, genre conventions and prior behavior → INVALID**; reporter-expectation-only reports ~20% FIXED | same | same | **Confirmed.** Per-category resolution percentages exist only as a stacked bar chart — any figure of the form "X% of prior-behavior reports were INVALID" is **unreachable** from this paper. The paper also makes **no** distinction between reports that state an expectation and those that do not |
| QUS: 13 criteria (3 syntactic, 4 semantic, 6 pragmatic) | — | Lucassen et al., *Requirements Engineering* 21(3):383–403, `research-portal.uu.nl/ws/files/27327615/Improving.pdf` | **Confirmed** |
| AQUSA: macro recall 92.1% / precision 77.4%; micro recall 93.8% / precision 72.2% | 1,023 user stories, 18 sets, 17 companies | same, Tables 4–5 | **Confirmed** |
| AQUSA implements 5 of 13 criteria | — | same, §5 | **Confirmed, and load-bearing.** The five are well-formed, atomic, minimal, uniform, unique. **All four semantic criteria are excluded** — including *problem-oriented*, the one this skill most wants — because they "require deep understanding of requirements' content." The paper does not claim they are inherently non-automatable |
| Conference version | — | — | **Corrected.** It is **IEEE RE 2015**, not REFSQ 2016. The REFSQ 2016 paper by the same authors is a different study |
| Template study: 1,916,057 issues, 100 repositories, 350 templates | — | Sülün, Saçakçı & Tüzün, *ACM TOSEM* 33(5):117 (2024), Bilkent open copy of the published PDF | **Confirmed.** "1.9 million" is a rounding of 1,916,057 |
| Project has a template → faster resolution: Mann-Whitney U, p=0.00, **Cohen's d = 0.61**; mean TTR 381.02 → 103.18 days | same | same, Tables 3–4 | **Confirmed, with a correction.** d = **0.61**. The widely quoted 0.59 is from the 2023 MSc thesis version, not the published paper |
| Individual conformance predicts nothing: TTR p=1.00 d=0.03; reopens p=0.47 d=0.01; comments p=1.00 d=0.09 | ~716,765 eligible issues | same, Table 3 | **Confirmed.** "However, the effect of the conformance on three metrics is insignificant" |
| 33% of eligible issues have zero conformance; mean conformance 0.74, median 0.78 | same | same | **Confirmed.** The thesis version's 12% / 0.71 / 0.75 must not be mixed with these |
| CrowdRE'25: 34 of 50 requests carry an NL defect (ambiguity 12, incompleteness 12, both 10); developers sought no clarification in 39 of 50 | **50** manually analysed requests, from 476 collected, from **2 repositories** (Signal 414, Mastodon 62) | K C et al., *Towards Better Requirements from the Crowd*, CrowdRE'25, `arxiv.org/pdf/2507.13553` | **Confirmed** |
| Clarifications are about intent and feasibility, not implementation | same | same | **Confirmed as categorical.** **No percentages exist** for clarification categories; do not quote any |
| Mock-ups and code snippets → faster and more positive responses | same | same | **Corrected to unquantified.** The paper's only sentence is a grounded-theory observation. There is no response-time figure, no sentiment score, no test, no effect size. Any numeric claim is unsupported |
| Non-reproducibility factors: Bug Duplication ("already fixed in the recent releases") Firefox 26.83% / Eclipse 31.33%; False Positive Bug 4.57% / 21.67%; Ambiguous Specifications 5.18% / 9.40% | 576 WORKSFORME reports (250 Firefox, 326 Eclipse) + 13 developers | Rahman, Khomh & Castelluccio, ICSME 2020, `arxiv.org/pdf/2108.05316`, Tables II–III | **Confirmed, with a correction.** The paper reports **no combined per-factor rate** — the "All" column belongs to Joorabchi et al. Prose aggregates exist only for duplication (~29%) and a few others |
| "About 17% of reported bugs are non-reproducible" | — | same | **Corrected.** This is Rahman et al. **citing Joorabchi et al.**, not their own finding |
| Mozilla: one bug per report; summary explains the problem, not the solution | — | `bugzilla.mozilla.org/page.cgi?id=bug-writing.html` (the MDN URL 301-redirects here) | **Confirmed** |
| Mozilla's actual/expected order | — | same | **Corrected as internally inconsistent.** Its General Outline template runs Steps → Actual → Expected; its worked example and its checklist put expected first. The page cannot be cited for a single order |
| PostgreSQL: "state all the facts and only facts"; "This is not what I expected" as a defect; "Do not spend all your time to figure out which changes in the input make the problem go away"; "refrain from merely saying that 'This is not what SQL says/Oracle does'"; "Failing to comply to the SQL standard is not necessarily a bug either, unless compliance for the specific feature is explicitly claimed" | — | `postgresql.org/docs/current/bug-reporting.html` §§5.1–5.2 | **All confirmed verbatim** |
| Stack Overflow: Minimal/Complete/Reproducible; "Restart from scratch" and "Divide and conquer"; "'It doesn't work' isn't descriptive enough"; "Double-check that your example reproduces the problem!"; "transport the example to a fresh environment" | — | `stackoverflow.com/help/minimal-reproducible-example` (fetched with a browser user agent; WebFetch is blocked for this host) | **All confirmed verbatim** |
| LLVM flag-by-flag attribution | — | `llvm/docs/HowToSubmitABug.rst` | **Confirmed verbatim** |
| curl "convert your program over to plain C"; "chances are we already fixed them" | — | `curl/docs/BUGS.md` | **Confirmed verbatim** |
| Arrow "as few non-Arrow dependencies as possible"; "Each issue should deal with a single bug or feature" | — | `apache/arrow/docs/source/developers/bug_reports.rst` | **Confirmed verbatim.** **Correction to Pass 1:** this text is in the developer docs, not the issue template; the template requires a `Component(s)` selection |
| Gradle bug form: Current Behavior required, then Expected Behavior, Context optional, reproducer required. Feature form: Expected Behavior required first, Current Behavior optional, Context **required** ("What are you trying to accomplish? What other alternatives have you considered?"). Regression form: "Gradle version that used to work" required | — | `gradle/gradle/.github/ISSUE_TEMPLATE/{10_contributor_bug_report,20_contributor_feature_request,30_contributor_regression}.yml` | **Confirmed verbatim.** Pass 1's filenames were the pre-rename ones |
| `gradle-issue-reproducer`: "Verify that the reproducer exhibits the problem on the GitHub Action page"; "Link your reproducer to the issue" | — | template repo README | **Confirmed verbatim** |
| Node: "no ZIP archive, no GitHub repository"; "a currently-supported version"; "What is the expected behavior? **Why is that the expected behavior?**" | — | `nodejs/node/.github/ISSUE_TEMPLATE/1-bug-report.yml` | **Confirmed verbatim.** The "why" sub-question is new to this pass and is the direct source for EXP2 |
| Homebrew `bug.yml`: `brew doctor` output required; `brew update` twice and still reproduces; `brew doctor` clean; not a single-formula issue; AI disclosure. Consequence: "we may block you from submitting future issues to Homebrew." Field order: what were you trying to do (and why) → what happened → what did you expect → steps | — | `Homebrew/brew/.github/ISSUE_TEMPLATE/bug.yml` (via the API; the raw path 404s) | **Confirmed, with corrections to Pass 1.** The current form has **no "tracker searched" checkbox and no "not a source build" checkbox**. The AI checkbox is broader than Pass 1 described: it also commits the reporter to answering maintainer questions without AI |
| Ghostty: "You must state the tool you used… along with the extent"; "If you can't explain what your changes do… do not contribute"; the public denouncement list | — | `ghostty-org/ghostty/AI_POLICY.md` | **Confirmed verbatim** |
| Linux security-bugs: version range without which the report is not processed; "A significant part of reports are for bugs that have already been fixed"; "Binary-only executables are not accepted"; the whole AI section (length, formatting, impact, reproducer, propose-a-fix-and-test-it); the one-issue-per-message rule with its same-commit exception | — | `Documentation/process/security-bugs.rst` | **All confirmed verbatim.** This is the highest-yield source in the pass and Pass 1 under-read it |
| OpenSSF guide for researchers (May 2026) | — | `openssf.org/resources/securing-open-source-in-the-age-of-ai-a-practical-guide/` | **Unreachable.** The page is a landing page for a gated eBook download; the guidance is not on the page and the PDF is behind a form. Used instead: the Linux security-bugs AI section, Ghostty's `AI_POLICY.md`, and Homebrew's `Responsible-AI-Usage.md`, which cover the same ground with fetchable text |
| `playwright-bug-reporter` skill ("never include a reproduction step you did not personally execute") | — | — | **Unreachable / not located.** Two web searches returned nothing matching the name or the quoted line, and no repository was found. The rule it was cited for (REP8) is sourced instead from the Linux AI clause and Homebrew's Responsible AI Usage. Pass 1's attribution should be treated as unverified |
| `github/awesome-copilot` `skills/github-issues/SKILL.md` | — | raw GitHub | **Confirmed reachable and read.** It is `gh api` / MCP mechanics, title length, and issue-type selection. It states no content rule this skill would duplicate |
| xyproblem.info | — | `xyproblem.info` | **Correction to Pass 1: reachable.** It returned 403 to Pass 1; it returns 200 to a browser user agent. Text confirmed, including "If there are other solutions you've already ruled out, share why you've ruled them out" |
| Renovate demanding reduction | — | `renovatebot/renovate/.github/ISSUE_TEMPLATE` | **Correction to Pass 1.** The repository ships only `administration-only.yml` and `config.yml`; there is no public bug form to cite. Renovate is dropped from the reduction group |
| `gradle/gradle#39079` and `junit-team/junit-framework#6041` | — | fetched via `gh` | **Confirmed.** Both accepted end states were read in full and are used as the worked examples in §5 and §7 |

## 12. What the skill-writing session should be told

**What the skill states, in order.** A short trigger; then a five-step order of operations that is itself the skill's
spine, because the expensive rules are the ones that must run *before* the prose exists.

1. **Read the target project first** (OWN5, FRM5, REP3, TPL1, MAC1), in this order: `.github/ISSUE_TEMPLATE/*.yml`
   and `config.yml`; `CONTRIBUTING.md`; `AI_POLICY.md` or the AI section of `CONTRIBUTING.md`; `SECURITY.md`; the
   support-window statement (release schedule, `SUPPORT.md`, or the newest release). Record the required field names
   and their order before writing a sentence.
2. **Establish ownership and currency** (OWN1, OWN2, OWN3, OWN4). These are bucket-2 runs and a bucket-3 lookup; they
   can invalidate the whole report, so they come before drafting.
3. **Write the report in the form's field order**, with FRM1–FRM4 governing what goes in each field.
4. **Apply the expected-behavior test** (§5, six questions) to every expected block. This is the skill's centre and
   should be the one thing a reader remembers.
5. **Run the writer's own checks** (EXP5, REP2, REP4, REP6) and paste the transcripts. Then TPL2 over every field.

**Length and split.** Target 200–250 lines for `SKILL.md`. It carries the 31 core rules, the five-step order, the
six-question expected-behavior test in full, and the seven vacuous shapes with their detections — the last two are
the parts a Sonnet run must not have to open a file to reach. Five reference files hold the other 14 rules:

- `references/request-genre.md` — REQ3–REQ7, EXP7, and the request field lists from Go, KEP, Rust RFC, PEP 1,
  Django, JUnit, Gradle's feature form. Trigger: the artifact is a request rather than a defect report.
- `references/colleague-message.md` — MSG1–MSG4 and the three short-form sources. Trigger: the artifact is a chat
  message to someone who shares the codebase, not a filed issue.
- `references/machine-authorship.md` — MAC1, MAC3, and the four policies' actual text, including the consequences.
  Trigger: the target project has an `AI_POLICY.md` or an AI clause.
- `references/project-conventions.md` — FRM6, REP6, the file-reading order of step 1 in full, and the per-project
  examples of contradictory requirements (Node versus Gradle on reproducer form; Gradle's own two orders; Mozilla's
  internal inconsistency). Trigger: step 1.
- `references/expected-behavior-cases.md` — the worked cases of §5 and §7. Trigger: an expected block failed the
  test and the writer needs the repair.

**What stays in the research directory and never reaches the skill.** Every figure in §11 with its sample and its
verdict; the three corrections that matter most (Bettenburg's conditional-likelihood framing, Chilana's INVALID
grouping of prior behavior, the conformance null result); the candidate evaluation of §2; the conflict reasoning of
§8. The skill states rules and detections, not evidence. One exception: EXP3's grounding order must carry a
one-clause reason in the skill body, because an agent that does not know *why* specification beats prior behavior
will reorder it under pressure.

**What stays a human judgment.** MAC5 only: whether the person filing can explain and defend the report without the
tool. The agent raises it as a question before filing and does not answer it. Adjacent to it, two decisions the skill
should surface rather than decide: whether to file at all when the only grounding available is personal preference
(EXP3's false-positive case), and whether a project's AI policy forbids an agent-authored report outright.

**What the trigger must say.** It must fire on the *task*, not on the word "issue", because the recorded failure came
from a session that had just finished reproducing something and was asked to "write it up". The trigger should name:
drafting or reviewing a bug report, an issue, a feature or change request, or a short problem message to a colleague,
in a project the author does not maintain; and, explicitly, the moment at the end of a session in which the agent
reproduced something in someone else's project and is now asked to report it. It must also fire on "review this
draft" and "is this ready to file", since the review path is where the detections earn their keep. It should say what
it does not cover — wording (`english-developer-style`), the commit and PR description
(`change-description-authoring`), documentation (`docs-page-authoring`), the regression test
(`test-authoring`) — so it is not loaded for those.
