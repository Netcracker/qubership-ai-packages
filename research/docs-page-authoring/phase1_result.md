# Pass 1 Discovery Report: Rules for the Structure and Content of Developer Documentation Pages

## TL;DR

- **No single source covers page structure and content for developer documentation above the sentence; synthesis across four disjoint literatures is required** — genre frameworks (Diátaxis), style-guide structure chapters (Google, Kubernetes), standards-body/verifiability conventions (RFC 2119, doctest families, Keep a Changelog), and technical-communication research (Carroll, Aghajani, Uddin & Robillard).
- **The strongest, most agent-convertible material is the studied research plus the verifiability tooling** — these state a rule *and* a rationale and treat a page as a claim about code; the weakest and most polluted category is agent skills for documentation *structure*, which is nearly empty and dominated by prose-style wrappers.
- **Pass 2 should concentrate on (1) mining project contribution guides for content rules with detectable violations and (2) the doctest/version-directive tooling**, because those convert most directly into rules an agent can apply without the author present; frameworks are already well-mapped and research needs distilling, not discovering.

## Key Findings

**The domain is fragmented.** The four relevant literatures barely cite one another. Diátaxis classifies pages by the job they do but says almost nothing about whether a page is *true*. Editorial style guides give procedure and heading rules but treat documentation as writing. Standards bodies (IETF, OASIS) have the only mature discipline for separating a *contract* from an *implementation*, but never wrote it for repository docs. The research literature supplies the only *measured* claims but no authoring rules. A usable skill must be assembled, not adopted.

**The baseline skill's central instinct is corroborated by standards practice, not by documentation guides.** The baseline's "specification not implementation" rule maps directly onto RFC 2119 / BCP 14's normative-versus-informative distinction, reinforced by RFC 8174's case discipline (keywords carry normative force only in uppercase, under a boilerplate). OASIS adds the useful caveat that "normative content doesn't always use keywords." This is the closest existing analogue to the baseline's most important correction, and it is detectable.

**Verifiability is real and shipped, but narrow.** Rust's rustdoc doc-tests, Python's `doctest`, and Sphinx's doctest extension all make examples executable: a stale example fails the build. Python's docs call this "the flavor of 'literate testing' or 'executable documentation.'" This directly answers the baseline's admitted weakness (nothing about testable examples) and converts to a crisp rule: an untested fenced example is an unchecked claim. Beyond executable examples, tooling that diffs prose identifiers against source (DocRef, Fraco, seen in citations) is thin and worth hunting in Pass 2.

**Historicity has named-marker conventions.** Sphinx's `versionadded`, `versionchanged`, and `deprecated` directives give *named* version markers rather than narrated history — exactly the baseline's "`Since 42.8.0`, not `used to`" rule. Keep a Changelog and its stricter fork Common Changelog define where history is legitimate (one entry per version, grouped change types, "changelogs are for humans, not machines," never dump commit logs). A live tension surfaced: Sphinx maintainers worry that accumulated `versionchanged` directives "bloat the docs."

**The defect taxonomies are studied, not asserted, and are the strongest reviewing input.** Two independent, high-quality studies exist. Uddin & Robillard's "How API Documentation Fails" (IEEE Software 32(4):68–75, 2015) reports: "The results are based on two surveys of a total of 323 professional software developers and analysis of 179 API documentation units. The three severest problems were ambiguity, incompleteness, and incorrectness of content," with six of the ten problems named "blockers" that forced developers to use another API. Aghajani et al.'s "Software Documentation Issues Unveiled" (ICSE 2019) "mined, analyzed, and categorized 878 documentation-related artifacts stemming from four different sources, namely mailing lists, Stack Overflow discussions, issue repositories, and pull requests," yielding a taxonomy of 162 documentation issue types. Together these supply the "inaccurate/incomplete/outdated/unusable" spine the brief asks for, grounded in evidence.

**How developers read is measured and supports the baseline's §3.** Meng, Steinhardt & Schubert's "How Developers Use API Documentation: An Observation Study" (Communication Design Quarterly, Jan 2019) identify three developer personas: "systematic" (top-down, understand the API first), "opportunistic" (bottom-up, start coding immediately and search for code examples), and "pragmatic" (combines both). The opportunistic group "did not systematically read larger sections... but typically searched for a specific piece of information and then scanned." This is direct evidence for "claim first, qualification after" and "the first paragraph carries the section."

**Agent-authored structure is a near-empty category.** A handful of Claude Code skills exist (`google-developer-style-guide-structure`, `code-documentation`, `epicenter/documentation`), but they either wrap an existing style guide or focus on prose ("avoid AI feel," TL;DR openings). None treats a page as a verifiable claim about code. The emptiness is a genuine finding: the artifact this brief scopes does not yet exist in public skill marketplaces.

## Details

### Candidate inventory (25 candidates)

| # | Name | URL | Category | Author/Org | Qs | Best use | Evidence | Maint. | Why consider |
|---|------|-----|----------|-----------|-----|----------|----------|--------|--------------|
| 1 | Diátaxis | diataxis.fr | framework | Daniele Procida | 1,5 | authoring | medium; central claim *asserted* ("four and only four") | active | The reference genre model; rationale = user needs |
| 2 | Diátaxis critiques (I'd Rather Be Writing; ekline "content drift") | idratherbewriting.com/blog/what-is-diataxis-documentation-framework | framework | Tom Johnson et al. | 1 | background | medium; opinion | active | Where the four types blur in practice |
| 3 | Google dev-docs style guide — Procedures, Headings, Prescriptive | developers.google.com/style/procedures | style-guide chapter | Google | 3,5,6,8 | authoring/checking | strong; prescriptive, asserted | active | State location before action; heading hierarchy; prescriptive-docs |
| 4 | Kubernetes Content Guide + Style Guide | kubernetes.io/docs/contribute/style/content-guide | project guide | K8s SIG Docs | 1,3,8 | authoring/reviewing | strong; adopted | active | What may NOT go on a page; canonical-source / no-dual-sourcing |
| 5 | RFC 2119 / BCP 14 (+ RFC 8174) | rfc-editor.org/rfc/rfc2119.html | framework/standard | S. Bradner, IETF | 2 | authoring/checking | strong; established | active (BCP) | Normative vs informative; MUST/SHOULD/MAY case discipline |
| 6 | OASIS keyword guidelines | oasis-open.org/policies-guidelines/keyword-guidelines | framework/standard | OASIS | 2 | authoring | medium | active | "Normative content doesn't always use keywords" |
| 7 | Rust rustdoc doc-tests | doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html | tooling | Rust project | 4 | mechanical checking | strong; shipped | active | Examples compiled/run on `cargo test`; failure = stale doc |
| 8 | Python `doctest` module | docs.python.org/3/library/doctest.html | tooling | Python Software Foundation | 4 | mechanical checking | strong; shipped | active | "Executable documentation"; verifies examples produce stated output |
| 9 | Sphinx doctest ext. + version directives | sphinx-doc.org/en/master/usage/extensions/doctest.html | tooling | Sphinx project | 3,4 | mechanical checking | strong; shipped | active | `versionadded/changed/deprecated` = named markers; doctest builder |
| 10 | Keep a Changelog 1.1.0 | keepachangelog.com/en/1.1.0/ | framework/standard | Olivier Lacan et al. | 3 | authoring/reviewing | strong; widely adopted | active | "For humans not machines"; six change types |
| 11 | Common Changelog | common-changelog.org | framework/standard | Vincent Weevers et al. | 3 | authoring/reviewing | medium; opinionated | active | Stricter fork; less room for interpretation |
| 12 | Aghajani et al., "Documentation Issues Unveiled" (ICSE 2019) | dl.acm.org/doi/10.1109/ICSE.2019.00122 | research | Aghajani, Bavota, Lanza et al. | 8 | reviewing | strong; *studied* (878 artifacts, 162 types) | published | The definitive documentation defect taxonomy |
| 13 | Aghajani et al., "Practitioners' Perspective" (ICSE 2020) | semanticscholar.org (CorpusID:219963395) | research | same team | 8 | background | strong; *studied* (survey) | published | Completeness & up-to-dateness rated top issues |
| 14 | Uddin & Robillard, "How API Documentation Fails" (IEEE Sw 2015) | cs.mcgill.ca/~martin/papers/ieeesw2015.pdf | research | Uddin & Robillard, McGill | 8 | reviewing | strong; *studied* (323 IBM pros) | published | Named 10-problem taxonomy with severity |
| 15 | Meng et al., "How Developers Use API Documentation" (CDQ 2019) | sigdoc.acm.org/cdq/how-developers-use-api-documentation-an-observation-study/ | research | Meng, Steinhardt, Schubert | 5 | background | strong; *studied* (observation) | published | Systematic/opportunistic/pragmatic personas; scanning |
| 16 | Carroll, *The Nurnberg Funnel* / minimalism | link.springer.com/chapter/10.1007/978-94-011-2854-4_15 | research | John M. Carroll | 7 | authoring/background | strong; *studied* but dated | canonical | Brevity, action-first, error recovery; measured vs manuals |
| 17 | standard-readme spec | github.com/RichardLitt/standard-readme | framework/standard | Richard Littauer | 1,5 | authoring/checking | medium; adopted | active | Ordered required/optional README sections; machine-checkable |
| 18 | purposeful-readme spec | github.com/purposeful-readme/purposeful-readme | framework/standard | purposeful-readme | 1,5,9 | authoring/checking | medium; new, asserted | active | "Who updates this, on what trigger?"; README must not contain a changelog |
| 19 | ADR (Nygard template) + adr.github.io | adr.github.io | framework | Michael Nygard; Joel Henderson | 1 | authoring | medium; adopted (723+ repos) | active | Status/Context/Decision/Consequences; decision historicity |
| 20 | Mintlify linking/anchors guide | mintlify.com/docs/guides/linking | tooling/style | Mintlify | 6 | authoring/checking | medium; vendor | active | Custom `{#id}` decouples heading text from URL; redirects |
| 21 | GitLab docs review checklist (MR template) | gitlab.com/gitlab-org/gitlab | review rubric | GitLab | 8 | reviewing | strong; used in production | active | Author + primary + tech-writer + maintainer review tiers |
| 22 | Write the Docs — Docs as Code | writethedocs.org/guide/docs-as-code | review rubric | Write the Docs community | 8 | background | medium | active | PR-based review; block merge if no docs; CI link/snippet checks |
| 23 | The Good Docs Project templates | thegooddocsproject.dev/template | framework/templates | Good Docs Project (Cameron Shorter et al.) | 1,5 | authoring | medium; community | active (v1.6 "Iron"; v1.5 "Helix", Dec 11 2025) | Concrete per-genre templates aligned to Diátaxis |
| 24 | google-developer-style-guide-structure (Claude skill) | skills.rest/skill/google-developer-style-guide-structure | agent skill | ghalactic | 5,8,9 | authoring/reviewing | weak; wraps Google guide | active | Rare existing *structure* skill; derivative |
| 25 | linkrot CLI | github.com/iamgeetarted/linkrot | tooling | community | 6 | mechanical checking | weak | active | Checks Markdown/HTML anchors incl. `{#id}`; flags non-descriptive link text |

### Promising shortlist for Pass 2 (9)

1. **Uddin & Robillard, "How API Documentation Fails" (#14).** A named-author, studied taxonomy of ten problems — incompleteness, ambiguity, unexplained examples, obsoleteness, inconsistency, incorrectness (content); bloat, fragmentation, excess structural information, tangled information (presentation) — with severity data from 323 IBM professionals. Converts cleanly into a reviewer rule set; several defects are detectable without reading the whole page (obsoleteness = version references; excess structural information = a signature restated). Best for **reviewing**.

2. **Aghajani et al. issue taxonomy (#12/#13).** The largest evidence-based defect taxonomy (878 artifacts across mailing lists, Stack Overflow, issues, and PRs; 162 issue types), independently praised. Supplies the inaccurate/incomplete/outdated/unusable backbone the brief wants, grounded in real developer discussion. Best for **reviewing**; the classification spine for a defect rubric.

3. **RFC 2119 / BCP 14 (#5) + OASIS (#6).** The only mature discipline for separating a contract (normative) from implementation (informative), with a rationale (interoperability) and a detectable marker (uppercase keywords under a boilerplate). Directly operationalises the baseline's most important rule and makes it mechanically checkable. Best for **authoring and mechanical checking**.

4. **Doctest family: Rust (#7) + Python (#8) + Sphinx (#9).** The core of verifiability: examples that compile/run so a stale claim fails the build. Converts to "an untested fenced example is an unchecked claim." Sphinx's version directives additionally answer historicity with named markers. Best for **mechanical checking**.

5. **Google style guide structure chapters (#3).** The most rule-dense structural guidance with rationale: state location before action, one procedure per task, headings as hierarchy (no numbers, no links, unique H1), prescriptive over optional. Most rules are detectable. **Only** the Procedures, Headings, Lists/Tables, and Prescriptive-Documentation chapters count; its prose chapters duplicate the out-of-scope companion skill. Best for **authoring and checking**.

6. **Kubernetes Content Guide (#4).** Rare in stating what a page *may not* contain — no dual-sourced content, link to the canonical source, third-party content only under strict conditions — with a rationale: "dual-sourced content requires double the effort... and grows stale more quickly." Converts to detectable scope-creep rules. Best for **reviewing**.

7. **Keep a Changelog (#10) + Common Changelog (#11).** Together they define where historicity is legitimate and give detectable rules (entry per version, grouped change types, never dump commit logs, human-not-machine). Common Changelog is the stricter fork. Best for **authoring and reviewing** changelog and migration pages.

8. **API-reading observation study (#15) + Carroll minimalism (#16).** The empirical basis for the baseline's contested §3. Meng et al.'s opportunistic/systematic/pragmatic personas support "claim first, qualification after"; Carroll supplies the studied case for brevity and action-first instruction (tutorials must not offer every option). Best for **authoring** rationale.

9. **standard-readme (#17) + purposeful-readme (#18).** Machine-checkable README section specs. purposeful-readme is notable for two agent-friendly, detectable rules: "who is responsible for updating this, and on what trigger?" and "the README must not contain a changelog." Best for **authoring and mechanical checking** of READMEs.

### Obvious rejects

- **General SEO / link-rot marketing blogs (BacklinkManager, Cuttly, Apidog):** about backlinks and rankings, not headings-as-anchors inside a doc set; reject except the narrow anchor-ID mechanic.
- **"Docs developers actually read" listicles (HackerNoon, Voiden, ReadMe blog):** received wisdom, no rationale, marketing register.
- **Doc tooling comparisons (Hugo/Docusaurus/MkDocs, adoc-studio, markdowntools):** out of scope unless they enforce a content rule.
- **Changelog SaaS pages (AnnounceKit, Quackback, ChangeNote):** marketing wrapped around the Keep a Changelog spec; cite the primary.
- **DEV/Medium "docs as code" intros:** duplicate Write the Docs with less authority.
- **Prose-only Claude skills (`epicenter/documentation` and similar):** contribution is sentence-level, owned by the companion skill; note only that the structure category is thin.
- **Sentence-level chapters of Google/Microsoft guides (voice, tone, person, serial comma):** explicitly out of scope.

## Recommendations

**Stage 1 — Lock the reviewing backbone first (highest leverage, most detectable).** Extract the Uddin & Robillard ten-problem list and the Aghajani 162-issue taxonomy into a single defect rubric, and tag each defect as *mechanically detectable* (obsoleteness = version tokens; excess structural information = signature restated; changelog containing commit hashes; heading containing a number or a link; fenced block with no language tag; README containing a changelog) or *needs whole-page reading* (genre drift, tangled information, "did the promise change"). This is the fastest path to an agent that reviews well.

**Stage 2 — Operationalise the contract/implementation and historicity rules.** Adopt RFC 2119/8174 normativity as the model for the baseline's §1, and adopt Sphinx-style named version markers plus Keep a Changelog change-types for §3. Both give the agent a *marker* to check rather than a judgement to make.

**Stage 3 — Wire in verifiability.** Encode "an untested fenced example is an unchecked claim" from the doctest family, and in Pass 2 hunt specifically for doc-linters that diff prose identifiers against source (DocRef, Fraco) — the thinnest but most on-brief tooling area.

**Stage 4 — Use frameworks and reading research as rationale, not as rules.** Keep Diátaxis for the genre table and Meng/Carroll for the "first paragraph carries the section" and minimalism rules, but do not treat "four and only four types" as a hard constraint given the content-drift evidence.

**Benchmarks that would change these recommendations:** (a) if Pass 2 finds an actively maintained agent skill that already treats a page as a verifiable claim, downgrade Stage 1's build-from-scratch assumption; (b) if a doc-linter that diffs identifiers against source proves reliable, promote it from Stage 3 background to a core mechanical check; (c) if the genre taxonomy fails against a sampled real `docs/` tree (many mixture pages), demote the "one page, one genre" rule from a MUST to a SHOULD with a documented exception for READMEs and migration guides.

## Caveats

- **Studied vs asserted.** Uddin & Robillard, Aghajani, Meng et al., and Carroll are studied and should be weighted highest. Diátaxis's "four and only four types," the style-guide rules, standard-readme, and purposeful-readme are *asserted* from practice — useful but not measured. The report flags each in the inventory's evidence column.
- **Link rot inside doc sets (Q6) is under-served.** The best available figures are general, not doc-set-specific: Pew Research Center's "When Online Content Disappears" (May 17, 2024) found that "38% of webpages that existed in 2013 are no longer accessible a decade later" and that "54% of Wikipedia pages have at least one link in their 'References' section pointing to a non-existent page," with 23% of news pages and 21% of government pages carrying at least one broken link (sample of ~1M Common Crawl pages). Rules specific to *renaming a published heading*, explicit anchor IDs, and cross-doc-set measurement remain thin and are a genuine Pass 2 gap.
- **Live conflicts to resolve in Pass 2.** Diátaxis's "keep the four types separate" versus the observed reality that README and migration pages are mixtures, and versus minimalism's fold-explanation-into-how-to instinct; Keep a Changelog's "entry for every version" versus Sphinx maintainers' concern that accumulated `versionchanged` directives "bloat the docs"; purposeful-readme's "README must not contain a changelog" versus common practice.
- **A minor citation discrepancy** exists for Uddin & Robillard: one arXiv reference list cites pp. 76–83, but the authoritative range is pp. 68–75 per IEEE, ACM, and the authors' own PDF.
- **Residual human-judgement calls.** Whether a rationale is "surprising enough" to include, whether a mixture page should be split or is legitimately a README, and whether an absent fact was wrong or merely moved to the page that owns it — these resist mechanical detection and should be surfaced to a human or model rather than encoded as a lint.