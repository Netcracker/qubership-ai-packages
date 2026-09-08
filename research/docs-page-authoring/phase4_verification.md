# Pass 4 verification: pass 2 and pass 3 claims against their primary sources

Three parallel verification passes run on 2026-09-03 before the synthesis. Reports are pasted unedited; the corrections they produced are carried into `phase4_result.md` and listed in its section 13.

## Research papers

# Fact-check: documentation research claims

Checked September 3, 2026 against primary sources: author-hosted PDFs, publisher pages, Crossref metadata, and the live
`diataxis.fr` site. No secondary blog summaries were used as evidence. Full text was obtained for claims 1–6; claim 7
rests on catalog records; claim 8 rests on the live site plus a Wayback snapshot.

## Verdict table

| # | Claim (component) | Verdict | Short reason |
|---|---|---|---|
| 1 | Xia et al., EMSE 2017, DOI, 60 developers, 235 engineers, 21+ countries | VERIFIED | Abstract matches word for word |
| 1 | Frequent tasks: exceptions/error messages, reusable code snippets, common programming bugs | VERIFIED | All three named in the abstract |
| 1 | Debug queries are often the error message pasted directly | VERIFIED (with caveat) | Supported by one interviewee quote, not by a statistic |
| 2 | Robillard & DeLine, EMSE 16(6), 2011, 703–732 | VERIFIED | Crossref confirms volume 16, issue 6, pages 703–732 |
| 2 | "over 440 professional developers" | VERIFIED | Verbatim in the abstract |
| 2 | Follow-up survey n=334, 17.3% response rate | VERIFIED | Verbatim in Section 3.4 |
| 2 | "code examples" and "matching APIs with scenarios" among five factors | VERIFIED | Both in the abstract's list of five |
| 3 | Authors are "Wan et al." | **CORRECTED** | Authors are Tan, Wagner & Treude |
| 3 | EMSE 2023, DOI 10.1007/s10664-023-10397-6, DOCER | VERIFIED (with caveat) | Online 2023; print issue is 29(1), article 5, January 2024 |
| 3 | "28.9% (265/918) of the projects contain at least one outdated document" | VERIFIED | Verbatim in RQ1 |
| 3 | 82.3% of projects outdated at least once | VERIFIED | Verbatim in RQ2, for 800 top1000 projects |
| 3 | References stayed outdated 4.7 years on average | VERIFIED (with caveat) | 4.7 years is the top1000 figure; google projects are 4.2 |
| 3 | Dataset is the top-1000 GitHub projects | **CORRECTED** | Two datasets: top-1000 plus 2,279 Google projects |
| 3 | DOCER is released as a GitHub Action | **CORRECTED** | Released as a script on Zenodo; a GitHub Action is future work |
| 3 | google/glog wiki referenced `DGFLAGS_NAMESPACE`, issue #750 | VERIFIED (with caveat) | Renamed to `DGLOG_GFLAGS_NAMESPACE`; issue #750 also covered `fPIC` |
| 4 | Uddin & Robillard, IEEE Software 32(4):68–75, 2015 | VERIFIED (with caveat) | Volume and issue confirmed; DOI is 10.1109/MS.2014.80, page range not seen |
| 4 | "two surveys of a total of 323 professional software developers" | VERIFIED (with caveat) | 323 is right (69 + 254), but they are IBM software professionals |
| 4 | "analysis of 179 API documentation units" | **CORRECTED** | 179 *examples* covering **131** documentation units |
| 4 | Three severest: ambiguity, incompleteness, incorrectness | VERIFIED | Verbatim in the paper's summary blurb |
| 4 | Six of ten problems were "blockers" | VERIFIED | Six named verbatim |
| 4 | The ten problems, content and presentation split | VERIFIED | Matches Table 2 exactly |
| 5 | Aghajani et al., ICSE 2019, 878 artifacts, four sources | VERIFIED | Verbatim in the abstract |
| 5 | Taxonomy of 162 documentation issue types | VERIFIED | Verbatim in the introduction and conclusion |
| 5 | ICSE 2020: completeness and up-to-dateness rated top issues | **CORRECTED** | Not the paper's finding; clarity ranks highest at 88% |
| 6 | Meng, Steinhardt & Schubert, CDQ 2019 | VERIFIED | CDQ 7(2):40–49, posted January 29, 2019 |
| 6 | Three strategies: systematic, opportunistic, pragmatic | **CORRECTED** | The study observed **two** groups; the three personas are Clarke (2007) |
| 6 | Opportunistic group searched for a specific piece and scanned | VERIFIED | Described as exploratory, risking errors without double-checking |
| 6 | Later paper recommends conceptual information integrated with the task | VERIFIED (with caveat) | Guideline 1.2, SIGDOC 2020; the skipping is *not* strategy-specific |
| 7 | Carroll, *The Nurnberg Funnel*, 1990, MIT Press | VERIFIED | ISBN 0262031639, Cambridge, Mass., 340 pages |
| 8 | diataxis.fr says a page "will always be one, and only one, of the four types" | **CORRECTED** | The phrase appears nowhere on diataxis.fr |
| 8 | Diátaxis calls itself a compass rather than a cage | PARTIAL | "Compass" is its own term; "cage" is not, and it also says it "strongly prescribes a structure" |
| 8 | Diátaxis allows compound or complex document structures | PARTIAL / UNVERIFIABLE on the live site | The nearest statement lives on a page that now 404s |
| 8 | Tom Johnson's post is a critique of Diátaxis | **CORRECTED** | He raises an objection and then resolves it in Diátaxis's favor |

## Notes by claim

### 1. Xia et al., "What do developers search for on the web?"

Source: <https://xin-xia.github.io/publication/emse173.pdf> (author-hosted PDF of the published article). Header
confirms `Empir Software Eng (2017) 22:3149–3185`, `DOI 10.1007/s10664-017-9514-4`. Crossref confirms volume 22, issue
6, pages 3149–3185.

Abstract, verbatim:

> To address this gap, we collected search queries from 60 developers, surveyed 235 software engineers from more than
> 21 countries across five continents.

> We find that searching for explanations for unknown terminologies, explanations for exceptions/error messages (e.g.,
> HTTP 404), reusable code snippets, solutions to common programming bugs, and suitable third-party libraries/services
> are the most frequent search tasks that developers perform […]

Caveat worth carrying into the synthesis: `reusable code snippets` appears in **both** the most-frequent and the
most-difficult list in the same abstract. Citing it only as "most frequent" is accurate but drops half the finding.

On queries being the pasted error message, Section 3.3 attributes this to an interviewee rather than to a measurement:

> Our interviewees pointed out that it is common to search for explanations for exceptions, and "developers would
> directly copy and paste the exception thrown out by an IDE into a search engine's query box' (P7)

The quantitative support nearby is that 1,349 collected queries related to this task, with examples such as
`FileNotFoundException`. Attribute the pasting behavior as an interview report, not a measured rate.

### 2. Robillard & DeLine, "A field study of API learning obstacles"

Source: <https://www.cs.mcgill.ca/~martin/papers/ese2011.pdf>. Header confirms `Empir Software Eng (2011) 16:703–732`,
`DOI 10.1007/s10664-010-9150-8`. Crossref confirms issue 6.

Abstract, verbatim:

> The study involved a combination of surveys and in-person interviews, and collected the opinions and experiences of
> over 440 professional developers.

> Our qualitative analysis elicited five important factors to consider when designing API documentation: documentation
> of intent; code examples; matching APIs with scenarios; penetrability of the API; and format and presentation.

Section 3.4 (Phase III: Follow-up Survey), verbatim:

> A total of 334 developers (17.3%) answered the survey.

The sample frame was 2,000 randomly selected Microsoft developers, 1,936 of them reachable. The claim's framing of 334
as a follow-up survey is correct: the paper's own heading is "Phase III: Follow-up Survey".

### 3. The DOCER paper — three corrections

**Authorship is wrong.** Crossref for `10.1007/s10664-023-10397-6` returns
`[('Wen Siang', 'Tan'), ('Markus', 'Wagner'), ('Christoph', 'Treude')]`. There is no author named Wan. Cite it as
**Tan, Wagner & Treude**. Publisher page: <https://link.springer.com/article/10.1007/s10664-023-10397-6>. Crossref also
gives volume 29, issue 1, article number 5, print issue January 2024, published online November 21, 2023 — so "2023" is
defensible for the online date but the print citation is 29(1) 2024.

Full text checked at <https://arxiv.org/pdf/2212.01479>, whose abstract matches the Crossref abstract verbatim.

RQ1, verbatim:

> In the top1000 dataset, 3.9% (7910/201852) of the code element references detected are currently outdated. We found
> that 19.2% (1880/9784) of the documents contain at least one outdated reference to a code element, and 28.9%
> (265/918) of the projects contain at least one outdated document. In the google dataset, 2.7% (1283/48078) code
> element references, 9.7% (287/2947) documents, and 5.4% (101/1879) projects are currently outdated (Figure 5.2). On
> average, the references are currently outdated for 4.7 years for projects in the top1000 dataset and 4.2 years for
> the google dataset (Figure 5.3).

So 28.9% (265/918) and 4.7 years are both correct, and both are top1000-only figures. Note that 28.9% is the share of
projects containing at least one outdated **document**, which is what the claim says.

RQ2, verbatim:

> To study how documentation evolves, we analysed the entire history of 800 projects from the top1000 dataset. 82.3%
> (658/800) of the projects, 40.7% (2878/7071) of the documents, and 12.3% (23588/191849) of the code element
> references are found to be outdated at some point in history.

82.3% is therefore a share of 800 analyzed projects, not of 1,000.

**Dataset is wrong.** Section 3.1, verbatim:

> We consider two datasets in this paper. The first dataset consists of the 1,000 most popular projects on GitHub,
> ranked by the number of stars. The second dataset consists of all 2,279 GitHub projects from Google.

That is what makes the abstract's "over 3,000 GitHub projects" true. Describing the study as top-1000-only understates
its scope and misattributes the google-dataset figures.

**The GitHub Action is wrong.** Section 6 (Implementation), verbatim:

> The implementation of our approach called DOCER (Detecting Outdated Code Element References) is available in our
> online appendix.

Footnote 24 points to <https://zenodo.org/record/7384588>. The GitHub Action appears only in the future-work discussion:

> A possible direction for future work is to create a workflow that automatically clones the repository, runs the
> analysis, and outputs the potentially outdated references. Using a tool such as GitHub Action to automate the
> workflow simplifies the process considerably […]

**The glog case is nearly right.** Section 2, verbatim:

> We detected an instance of the code element DGFLAGS_NAMESPACE in the source code when the documentation was last
> updated. On 1 June 2018, the code element was renamed to DGLOG_GFLAGS_NAMESPACE in one of the commits. However, the
> documentation was not updated to reflect the changes.

Two details the claim omits: the new name is `DGLOG_GFLAGS_NAMESPACE`, and the same GitHub issue —
<https://github.com/google/glog/issues/750> — also reported a second outdated reference, `fPIC`. The maintainer fixed
it by deleting the document that held both references.

### 4. Uddin & Robillard, "How API Documentation Fails"

Source: <https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf>. The author-hosted cover page gives
`Volume 32, Issue 4`, `July/August 2015`, `DOI: 10.1109/MS.2014.80`. Note the DOI year segment is **2014**, not 2015.
The page range 68–75 is widely cited but does not appear on the author-hosted PDF, and the IEEE page was not reachable;
treat 68–75 as unconfirmed here.

Summary blurb, verbatim:

> Researchers investigated how 10 common documentation problems manifested themselves in practice. The three severest
> problems were ambiguity, incompleteness, and incorrectness of content. The surveyed practitioners considered six of
> the problems "blockers" that forced them to use another API.

Introduction, verbatim:

> we conducted two surveys of API documentation quality with a total of 323 IBM software professionals.

The 323 total decomposes as 69 respondents to the exploratory survey and 254 to the validation survey (23.8% of a
1,064-person target population). Say "IBM software professionals" rather than "professional software developers" — the
population was single-company, which is a real limitation on generalization.

**The 179 figure is misattributed.** Verbatim:

> The respondents provided 179 examples of good or bad documentation for 131 documentation units that documented API
> elements in a total of 72 distinct APIs from six types of programming languages […]

> From the answers to questions 2 and 3 in Table 1, we collected 179 documentation examples: 90 examples of good
> documentation and 89 examples of bad documentation.

So 179 counts **examples**, and the number of documentation units is **131**. The analysis narrowed further: 83 bad
examples survived a validity screen, then 79 comments mapped onto the 10 problem types. Write "179 documentation
examples covering 131 documentation units".

The blocker sentence, verbatim:

> Respondents ranked six problems as "Blocker" at least once: incompleteness, ambiguity, obsoleteness, incorrectness,
> inconsistency, and unexplained examples.

The ten-problem list in the claim matches Table 2 exactly, including the content/presentation split and the wording
"excess structural information" and "tangled information".

### 5. Aghajani et al., ICSE 2019 and ICSE 2020

**ICSE 2019 is fully verified.** Source: <https://emadpres.github.io/pdfs/icse2019.pdf>. Abstract, verbatim:

> We present a large scale empirical study, where we mined, analyzed, and categorized 878 documentation-related
> artifacts stemming from four different sources, namely mailing lists, Stack Overflow discussions, issue repositories,
> and pull requests.

Introduction, verbatim:

> Based on our analysis, we built a comprehensive taxonomy consisting of 162 types of documentation issues linked to
> (i) the information it contains, (ii) how the information is presented, (iii) the documentation process and (iv)
> documentation tool support.

Full citation: Aghajani, Nagy, Vega-Márquez, Linares-Vásquez, Moreno, Bavota & Lanza, ICSE 2019, pp. 1199–1210, DOI
10.1109/ICSE.2019.00122.

**The ICSE 2020 characterization is wrong.** Source: <https://emadpres.github.io/pdfs/icse2020.pdf>. The paper is
"Software Documentation: The Practitioners' Perspective", by Aghajani, Nagy, Linares-Vásquez, Moreno, Bavota, Lanza &
Shepherd, ICSE 2020. It reports two surveys with 146 practitioners (78 to Survey-I, 68 to Survey-II).

The paper does not rank completeness and up-to-dateness as the top issues. Its headline result runs the other way —
conclusion, verbatim:

> our first study showed that only a small subset of the 162 documentation issues reported in our taxonomy are deemed
> important by practitioners

The single highest-rated issue named in the text is clarity:

> Concerning Readability, documentation clarity is the issue perceived as most important by practitioners (88% of
> them) […]

The words "completeness" and "up-to-dateness" do occur together, but as a description of **prior** literature that the
new results agree with, and alongside correctness:

> ® This result is in line with previous studies [8, 69] that underlined the relevance of correctness, completeness,
> and up-to-dateness issues in documentation.

That sentence sits under Information Content (What), where the summary is that 7 of 23 issues (30%) cleared the 60%
importance bar. If the synthesis needs an ICSE 2020 finding, use either the "only a small subset" conclusion or the 88%
clarity figure, and do not present completeness and up-to-dateness as that paper's own top-two ranking.

### 6. Meng, Steinhardt & Schubert

**Venue is right.** *Communication Design Quarterly* 7(2):40–49, posted January 29, 2019, article reference CDQ18002.
Publisher page: <https://sigdoc.acm.org/cdq/how-developers-use-api-documentation-an-observation-study/>. ACM record:
<https://dl.acm.org/doi/10.1145/3358931.3358937>.

**The three strategies are Clarke's, not this study's finding.** The paper's own observations of 11 participants
produced two groups, verbatim:

> We found some developers (P2, P3, P9, P10) to develop the solutions for the test task in an exploratory fashion,
> which Clarke (2007) discusses as a characteristic feature of programmers taking an opportunistic approach.

> In contrast to the opportunistic approach, another group of developers (P4, P5, P7, P8) seemed to follow a strategy
> that fits the systematic approach discussed by Clarke (2007).

The third persona appears only as a citation:

> Clarke (2007) described these strategies in terms of three personas, referred to as systematic, opportunistic and
> pragmatic developers.

No pragmatic group was observed. Write "two groups, matching Clarke's systematic and opportunistic personas".

**The follow-up recommendation is verified, with one important nuance.** The later paper is Meng, Steinhardt &
Schubert, "Optimizing API Documentation: Some Guidelines and Effects", SIGDOC '20, DOI 10.1145/3380851.3416759.
Guideline 1.2, verbatim:

> Guideline 1.2: Present important conceptual information integrated with the description of tasks or usage scenarios
> where knowledge of these concepts is needed.

The motivating observation, verbatim:

> However, it is a challenge that developers tend to ignore documents which focus on conceptual information, hence
> potentially convey the domain-related background knowledge of an API, with the reluctance to refer to concepts
> documents apparently being independent of the learning strategy the developers adopt [14].

The last clause contradicts the claim's framing. The skipping of a separate concepts section is **not** specific to
opportunistic developers — the authors state it holds regardless of learning strategy. That makes the guideline
stronger, not weaker, but the attribution in the claim should be dropped.

### 7. Carroll, *The Nurnberg Funnel*

Confirmed. John M. Carroll, *The Nurnberg Funnel: Designing Minimalist Instruction for Practical Computer Skill*, MIT
Press, Cambridge, Mass., 1990. ISBN 0262031639 / 9780262031639, 340 pages. ACM record:
<https://dl.acm.org/doi/10.5555/80371>. Catalog record via Open Library:
<https://openlibrary.org/search.json?q=title%3A%22Nurnberg+funnel%22>. The MIT Press catalog page
(`mitpress.mit.edu/9780262031639/the-nurnberg-funnel/`) blocks automated fetches, so the publisher's own description
was not retrieved; publisher and year are corroborated by both the ACM record and the catalog record.

The claim asked only to confirm book, year and publisher, so the minimalism principles themselves were not verified
against the text. If the synthesis attributes "brevity, action-first, error recovery, measured against conventional
manuals" to this book, those four should be checked against the book's own chapters before publication.

### 8. Diátaxis

**The "one, and only one" sentence is not on diataxis.fr.** All 15 pages linked from the site navigation were fetched
and searched (`application`, `colophon`, `compass`, `explanation`, `foundations`, `how-to-guides`,
`how-to-use-diataxis`, `map`, `quality`, `reference-explanation`, `reference`, `start-here`, `theory`,
`tutorials-how-to`, `tutorials`, plus the index — 112 KB of extracted text). The string "only one" occurs twice, both
in `tutorials-how-to` and neither about page typing:

> A how-to guide cannot promise safety; often there's only one chance to get it right.

> The conflation of tutorials and how-to guides is by no means the only one made between different kinds of
> documentation […]

The nearest genuine statements are about the taxonomy, not about individual pages. From
<https://diataxis.fr/foundations/>:

> This is why there are four and only four types of documentation. There is simply no other territory to cover.

And from <https://diataxis.fr/compass/>, the decision table is introduced with "…then it must belong to…", followed by:

> The Diátaxis compass is something like a truth-table or decision-tree of documentation.

The wording in the claim most closely resembles the older Divio phrasing, which says something different — from
<https://docs.divio.com/documentation-system/introduction/>:

> It saves the author from wasting a great deal of time trying to wrestle the information they want to impart into a
> shape that makes sense, because each of these kinds of documentation has only one job.

"Each kind has only one job" is a claim about the four genres, not about a page belonging to exactly one of them. If
the synthesis needs to quote a strict-separation claim, quote the Divio sentence and attribute it to Divio, or quote
the Foundations sentence and note that it is about the taxonomy.

**Compass yes, cage no.** "Compass" is Diátaxis's own term — the site has a page titled *The compass*. "Cage" is not
its wording; the word does not appear on the site. The closest self-description is from
<https://diataxis.fr/how-to-use-diataxis/>:

> Use Diátaxis as a guide, not a plan

> Diátaxis describes a complete picture of documentation. However the structure it proposes is not intended to be a
> plan, something you must complete in your documentation. It's a guide, a map to help you check that you're in the
> right place and going in the right directions.

Counter-evidence on the same page, which a fair synthesis should not omit:

> Diátaxis strongly prescribes a structure, but whatever the state of your existing documentation - even if it's a
> complete mess by any standards - it's always possible to improve it, iteratively.

So the framework describes itself as both prescriptive about structure and non-prescriptive about process and sequence.
"Compass rather than cage" is a fair gloss of the second half only.

**Compound and complex structures: the supporting page has been removed.** `https://diataxis.fr/complex-hierarchies/`
returns HTTP 404 on the live site as of September 3, 2026, and "Complex hierarchies" no longer appears in the site
navigation. A Wayback snapshot from August 2, 2026 shows it was live recently:
<http://web.archive.org/web/20260802004758/https://diataxis.fr/complex-hierarchies/>. From that snapshot:

> Secondly, the question highlights a common misunderstanding. Diátaxis is not a scheme into which documentation must
> be placed - four boxes. It posits four different kinds of documentation, around which documentation should be
> structured, but this does not mean that there must be simply four divisions of documentation in the hierarchy, one
> for each of those categories.

> It should be understood as an approach, a way of working with documentation, that identifies four different needs and
> uses them to author and structure documentation effectively. This will tend towards a clear, explicit, structural
> division into the four categories - but that is a typical outcome of the good practice, not its end.

Two cautions. First, this passage permits **complex hierarchies** — several parallel Diátaxis quadrants across user
types or platforms — not compound *documents* that blend two modes on one page. The site says nothing supporting the
latter. Second, citing a 404 URL as current Diátaxis doctrine is not safe; cite the Wayback snapshot with its date, or
find where (if anywhere) the material was relocated.

A live statement in the same spirit does exist, from <https://diataxis.fr/quality/> and the how-to page's insistence
that the reader comes first — for instance, from the archived complex-hierarchies page:

> Remember that you are always authoring for a human user, not fulfilling the demands of a scheme.

**Tom Johnson's post is not a critique.** Source: <https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework>.
He raises the objection and then withdraws it:

> In learning about Diátaxis, I was concerned about the separation of content into distinct groups. Siloing
> documentation into tutorials, how-tos, reference, and explanation seemed overly opinionated and arbitrary as an
> information model. What research was this information model based on? I reached out to Daniele on the #diataxis WTD
> Slack channel, and he clarified that Diátaxis isn't meant to impose four rigid buckets that content must squeeze
> into.

> He acknowledges the critique that people don't strictly separate these modes, but says that documentation itself
> should still be clear about its purpose and stabilize around meeting specific user needs.

The post contains no "one, and only one" quotation and no discussion of compound documents. Do not cite it as a source
for either. It is usable as a source for the objection-and-resolution framing, and for Procida's Slack clarification
that Diátaxis "isn't meant to impose four rigid buckets" — though that clarification is reported speech from a Slack
channel, not a published Diátaxis statement.

## Method and limits

- Crossref (`api.crossref.org/works/<doi>`) supplied volume, issue, page and author metadata for claims 1–4.
- Author-hosted PDFs supplied full text for claims 1, 2, 4, 5 and 6; arXiv 2212.01479 supplied full text for claim 3,
  and its abstract matches the Crossref abstract of the published article verbatim.
- Springer's HTML for claim 2 redirects to an IdP and was not fetched; the McGill author copy was used instead, and its
  header carries the same volume, pages and DOI.
- The ACM Digital Library and IEEE full texts sit behind bot protection (HTTP 403 / JS challenge). Claim 4's page range
  68–75 and claim 6's SIGDOC 2020 page numbers were not confirmed from the publisher.
- `mitpress.mit.edu` returns HTTP 403 to automated fetches, so claim 7 rests on the ACM record and Open Library.

## Project policies and style guides

# Fact-check: documentation-policy claims vs. primary sources

Checked 2026-09-03. Every quote below was read from the URL given in the same row (page fetched and
converted to text locally, or read as raw file from the project's own repository).

## Summary table

| # | Claim | Verdict |
|---|---|---|
| 1 | OpenStack `DocImpact` | VERIFIED (trigger list, auto-bug); **UNVERIFIABLE** for "retired" — evidence points the other way |
| 2 | PostgreSQL `context` values / `search_path` / `hash_mem_multiplier` | VERIFIED for context values, `search_path` default, `hash_mem_multiplier`; **CORRECTED** for "never searched for function or operator names" |
| 3 | PostgreSQL wiki, GUCs kept in 3 places | **CORRECTED** (page is *GUCS Overhaul*; names `postgresql.conf` and `settings.sgml`, not `postgresql.conf.sample` / `config.sgml`) |
| 4 | `man-pages(7)` | VERIFIED for section order and SEE ALSO; **CORRECTED** — the version-information sentence sits under DESCRIPTION, not VERSIONS |
| 5 | Google style guide: tables, lists, procedures, prescriptive | VERIFIED, with two wording corrections ("goal/location before the action"; the "three or more" sentence is a page-summary blurb) |
| 6 | Django `versionadded` / `versionchanged` | **CORRECTED** — "preferred way", not "required"; "two releases" confirmed |
| 7 | Kubernetes task page and dual-sourced content | VERIFIED, but the task-page wording lives on *Writing a new topic*, not *Page content types* |
| 8 | Spring Boot configuration metadata | VERIFIED (both sentences, verbatim) |
| 9 | Rust compiler dev guide, error codes | VERIFIED (all three parts) |
| 10 | Next.js error links | VERIFIED for the sentence; **CORRECTED** — the URL pattern is not stated in that guide (confirmed from source instead) |
| 11 | Angular pull-request template | **CORRECTED** — the parenthetical is not in the template, in any revision back to 2016 |
| 12 | purposeful-readme spec v0.1.0 | VERIFIED (both quotes, verbatim) |
| 13 | OASIS keyword guidelines + RFC 8174 | VERIFIED (minor wording fix: "Normative contents don't always use keywords") |
| 14 | Keep a Changelog 1.1.0 / Common Changelog | VERIFIED (all parts) |
| 15 | Diátaxis on reference | **CORRECTED** — the actual heading is "Respect the structure of the machinery"; "compass, not a cage" is **not** Diátaxis's wording, and there is no compound/complex-documents page |

---

## 1. OpenStack `DocImpact`

**URL read:** <https://wiki.openstack.org/wiki/Documentation/DocImpact>

VERIFIED, verbatim, including the claimed trigger list:

> In any OpenStack project, you can add a DocImpact flag in a commit message to automatically log a bug
> in a specified project in Launchpad. The bug is not set to "Confirmed" until the patch merges. The
> entire commit message is included in the bug.

> If your commit could have an impact on documentation - be it an added/altered/removed command line
> option, a deprecated or new feature, a caveat, if you've written docs in the patch, or if you're just
> not sure, just add "DocImpact" to a line in your commit message.

Note the wiki page is the source of the *verbatim* list. The maintained contributor guide
(<https://docs.openstack.org/doc-contrib-guide/doc-impact.html>) carries a copy-edited variant that
drops "or if you're just not sure" and softens the auto-creation claim:

> In any OpenStack project, you can add a DocImpact flag in a commit message to help identify any bugs
> that require documentation to be written in the OpenStack manuals project.

> If your commit has an impact on documentation, for example an added, altered, or removed command line
> option, a deprecated or new feature, a caveat or if you have written docs in the patch, add
> "DocImpact" to a line in your commit message.

It still says, two paragraphs later: "This creates a Launchpad bug for the project indicated in the
`gerrit/projects.yaml` file in the `openstack/project-config` repository."

**Retirement: UNVERIFIABLE, and the available evidence contradicts it.** No primary OpenStack source
states the flag is retired or deprecated, and three current artifacts say it is still live:

- <https://docs.openstack.org/doc-contrib-guide/doc-impact.html> still documents it, footer "this page
  last updated: 2026-08-12".
- <https://wiki.openstack.org/wiki/GitCommitMessages> still lists it among the supported metadata
  lines: "When this flag is included in a commit message, Gerrit creates a bug for the
  openstack-manuals project to triage and track, or move to the openstack-api-site as needed."
- `openstack/project-config` master still carries 85 `docimpact-group:` entries in
  `gerrit/projects.yaml`, and `opendev/jeepyb` master still ships `jeepyb/cmd/notify_impact.py`
  (<https://opendev.org/opendev/jeepyb/raw/branch/master/jeepyb/cmd/notify_impact.py>, HTTP 200).

Searched: the wiki page, the contributor guide, the GitCommitMessages wiki page, project-config, and
jeepyb. If a retirement was announced it was on a mailing list, not in the documentation. Do not assert
a retirement date.

## 2. PostgreSQL settings

**URL read:** <https://www.postgresql.org/docs/current/view-pg-settings.html>

VERIFIED. The seven values and the ordering phrase are exact:

> There are several possible values of `context`. In order of decreasing difficulty of changing the
> setting, they are:

followed by `internal`, `postmaster`, `sighup`, `superuser-backend`, `backend`, `superuser`, `user`,
in that order. (Note: the list lives in the `pg_settings` view reference, not in the "Setting
Parameters" chapter.)

**URL read:** <https://www.postgresql.org/docs/current/runtime-config-client.html>

`search_path` default — VERIFIED, verbatim:

> The default value for this parameter is `"$user", public`.

"never searched for function or operator names" — **CORRECTED.** The sentence exists but it is about
the *temporary schema*, not about `search_path` as a whole. The full passage:

> Likewise, the current session's temporary-table schema, `pg_temp_nnn`, is always searched if it
> exists. It can be explicitly listed in the path by using the alias `pg_temp`. If it is not listed in
> the path then it is searched first (even before `pg_catalog`). However, the temporary schema is only
> searched for relation (table, view, sequence, etc.) and data type names. It is never searched for
> function or operator names.

The subject of "It is never searched" is "the temporary schema". Saying the *path* is never searched
for function or operator names inverts the meaning.

**URL read:** <https://www.postgresql.org/docs/current/runtime-config-resource.html>

`hash_mem_multiplier` — VERIFIED:

> Used to compute the maximum amount of memory that hash-based operations can use. The final limit is
> determined by multiplying `work_mem` by `hash_mem_multiplier`. The default value is 2.0, which makes
> hash-based operations use twice the usual `work_mem` base amount.

## 3. PostgreSQL wiki on GUCs

**CORRECTED** on page title and on two of the three filenames.

**URL read:** <https://wiki.postgresql.org/wiki/GUCS_Overhaul> (the page is *GUCS Overhaul*; there is no
`Adding_a_new_GUC_variable` page — that URL returns "There is currently no text in this page")

Verbatim, from the "Problems" list:

> GUCS lists are kept in 3 different places (guc.c, postgresql.conf, and settings.sgml), which are only
> synched with each other manually.

So: "3 different places" and "only synched with each other manually" are exact. But the page names
`postgresql.conf` and `settings.sgml`, not `postgresql.conf.sample` and `config.sgml`. Quote the page
as written, or paraphrase the file names.

## 4. `man-pages(7)`

**URL read:** <https://man7.org/linux/man-pages/man7/man-pages.7.html>

Section order — VERIFIED (under "Sections within a manual page"):

> The list below shows conventional or suggested sections.  Most manual pages should include at least
> the highlighted sections.  Arrange a new manual page so that sections are placed in the order shown
> in the list.

SEE ALSO — VERIFIED:

> The list should be ordered by section number and then alphabetically by name.  Do not terminate this
> list with a period.

Version-information sentence — **CORRECTED on its location.** The quote is verbatim:

> Including version information is especially useful to users who are constrained to using older kernel
> or C library versions (which is typical in embedded systems, for example).

but it appears under **DESCRIPTION**, not VERSIONS. Its immediate context is:

> When describing new behavior or new flags for a system call or library function, be careful to note
> the kernel or C library version that introduced the change.  The preferred method of noting this
> information for flags is as part of a `.TP` list, in the following form (here, for a new system call
> flag): `XYZ_FLAG (since Linux 3.7)`

## 5. Google developer documentation style guide

**URL read:** <https://developers.google.com/style/tables>

"three or more" — VERIFIED as a string, but note **where** it appears. The sentence

> Tables are ideal for presenting data with three or more related pieces of information per item, while
> lists are better for simpler data structures.

is in the page's auto-generated "Page Summary" box, not the guidance body. The body states the same
rule as a table row: "Each item is three or more pieces of related data." / "A set of parameters, where
each parameter has a name, a data type, and a description." / "Use a table."

Two-dimensional data and one-column tables — VERIFIED, both verbatim:

> If you have only one column in your table, turn the table into a list.

> Use tables only to present two-dimensional data—that is, material that semantically makes sense to
> display in rows and columns.

(The second sentence closes a bullet about not splitting a long one-dimensional list into columns.)

**URL read:** <https://developers.google.com/style/lists>

VERIFIED, verbatim, formatted as a Note callout:

> Note: Don't use a list to show only one item; a single item isn't really a list. If you want to set a
> single item off from surrounding text, then use some other formatting.

**URL read:** <https://developers.google.com/style/procedures>

**CORRECTED on wording.** Two distinct rules exist, and neither is phrased as "state the location
before the action" in the body prose:

Body prose, "goal" version:

> When a step includes a goal, state the goal before the action. This structure helps readers
> understand and complete the step more easily.

Summary-of-guidelines table, "location" version (this one matches the claim's intent):

> Write in the order that the reader needs to follow. State the location of the action before stating
> the action.

Recommended: "In Google Docs, click File > New > Document." Not recommended: "Click File > New >
Document in Google Docs."

Also on the same page: "Other steps benefit from including a justification for why the step is
important. State the action first and the justification second."

**URL read:** <https://developers.google.com/style/prescriptive-documentation>

VERIFIED, verbatim, from the "Prescriptive writing affects several aspects of documentation" list:

> Example scenarios and procedures. Scenarios and procedures reflect the use cases that are most likely
> relevant to the readers.

> Sample commands. Prescriptive documentation provides commands and arguments that accomplish the task
> for the most common use case.

Also on that page: "The purpose and structure of a document. Prescriptive documentation states a clear,
specific purpose. Headings and content are written with that purpose in mind."

## 6. Django "Writing documentation"

**URL read:** <https://docs.djangoproject.com/en/dev/internals/contributing/writing-documentation/>
(section "Documenting new features")

**CORRECTED: not "required".** The policy is stated as a preference, and the mandatory element is the
blank line, not the directive:

> Our policy for new features is:
>
> All documentation of new features should be written in a way that clearly designates the features
> that are only available in the Django development version. Assume documentation readers are using the
> latest release, not the development version.

> Our preferred way for marking new features is by prefacing the features' documentation with:
> ".. versionadded:: X.Y", followed by a mandatory blank line and an optional description (indented).

> General improvements or other changes to the APIs that should be emphasized should use the
> ".. versionchanged:: X.Y" directive (with the same format as the versionadded mentioned above).

Self-contained and two releases — VERIFIED:

> These versionadded and versionchanged blocks should be "self-contained." In other words, since we only
> keep these annotations around for two releases, it's nice to be able to remove the annotation and its
> contents without having to reflow, reindent, or edit the surrounding text.

Two further rules worth carrying: "Put the changed annotation notes at the bottom of a section, not the
top." and "avoid referring to a specific version of Django outside a versionadded or versionchanged
block."

## 7. Kubernetes

**URL read:** <https://kubernetes.io/docs/contribute/style/write-new-topic/> ("Choosing a page type")

VERIFIED, verbatim — but the source is *Writing a new topic*, **not** the content guide and **not**
*Page content types*:

> A task page shows how to do a single thing. The idea is to give readers a sequence of steps that they
> can actually do as they read the page. A task page can be short or long, provided it stays focused on
> one area. In a task page, it is OK to blend brief explanations with the steps to be performed, but if
> you need to provide a lengthy explanation, you should do that in a concept topic. Related task and
> concept topics should link to each other.

For reference, *Page content types* (<https://kubernetes.io/docs/contribute/style/page-content-types/>)
phrases it differently: "A task page shows how to do a single thing, typically by giving a short
sequence of steps."

**URL read:** <https://kubernetes.io/docs/contribute/style/content-guide/> (section "Dual sourced
content")

VERIFIED, verbatim:

> Wherever possible, Kubernetes docs link to canonical sources instead of hosting dual-sourced content.
> Dual-sourced content requires double the effort (or more!) to maintain and grows stale more quickly.

## 8. Spring Boot configuration metadata

**URL read:** <https://docs.spring.io/spring-boot/specification/configuration-metadata/index.html>

VERIFIED, verbatim:

> The majority of the metadata file is generated automatically at compile time by processing all items
> annotated with `@ConfigurationProperties`.

(Note "The majority of" — the metadata file is not wholly generated.)

**URL read:**
<https://docs.spring.io/spring-boot/specification/configuration-metadata/annotation-processor.html>
(section on adding additional metadata)

VERIFIED, verbatim:

> If you refer to a property that has been detected automatically, the description, default value, and
> deprecation information are overridden, if specified.

Surrounding context: "the annotation processor automatically merges items from
`META-INF/additional-spring-configuration-metadata.json` into the main metadata file" and "If the
manual property declaration is not identified in the current module, it is added as a new property."

## 9. Rust compiler dev guide

**URL read:** <https://rustc-dev-guide.rust-lang.org/diagnostics.html> (section "Error codes and
explanations")

VERIFIED, verbatim:

> As a general rule, give an error a code (with an associated explanation) if the explanation would give
> more information than the error itself. A lot of the time it's better to put all the information in
> the emitted error itself.

Same section: "Most errors have an associated error code. Error codes are linked to long-form
explanations which contains an example of how to trigger the error and in-depth details about the
error. They may be viewed with the `--explain` flag, or via the error index."

**URL read:** <https://rustc-dev-guide.rust-lang.org/diagnostics/error-codes.html>

VERIFIED, verbatim:

> Error codes are stored in `compiler/rustc_error_codes`.

> You will have to write an extended description for your error, which will go in
> `rustc_error_codes/src/error_codes/E0806.md`.

`rustc --explain E0592` — VERIFIED indirectly: E0592 is a live code with a published explanation at
<https://doc.rust-lang.org/error_codes/E0592.html> (HTTP 200), and the guide documents `--explain` as
the way to read those explanations. The compiler prints exactly this form: "For more information about
this error, try `rustc --explain E0999`." (quoted from the dev-guide's own example output).

## 10. Next.js error links

**URL read:**
<https://github.com/vercel/next.js/blob/canary/contributing/core/adding-error-links.md> (raw read from
`raw.githubusercontent.com`, canary branch)

VERIFIED, verbatim — the file is short enough to reproduce the relevant half:

> Next.js has a system to add helpful links to warnings and errors.
>
> This allows the logged message to be short while giving a broader description and instructions on how
> to solve the warning/error on the documentation.
>
> In general, all warnings and errors added should have these links attached.
>
> Below are the steps to add a new link:
>
> 1. Run `pnpm new-error` which will create the error document and update the manifest automatically.
> 2. At the end of the command the URL for the error will be provided, add that to your error.

**CORRECTED on the URL pattern.** The guide does **not** state `nextjs.org/docs/messages/<slug>` — it
says the `pnpm new-error` command prints the URL. The pattern is real but has to be sourced elsewhere:
error documents live in `errors/<slug>.mdx` in the repo, and the compiler/build source emits the URL
directly. For example, `packages/next/src/build/index.ts` on canary contains
`nextjs.org/docs/messages/build-dir-not-writeable`,
`nextjs.org/docs/messages/conflicting-public-file-page`, and others; `errors/no-cache.mdx` resolves to
<https://nextjs.org/docs/messages/no-cache> (HTTP 200). Cite the source file or a live message URL, not
the contributing guide, for the pattern.

## 11. Angular pull-request template

**URL read:** <https://github.com/angular/angular/blob/main/.github/PULL_REQUEST_TEMPLATE.md> (raw read
from `raw.githubusercontent.com`, main branch)

Checklist item — VERIFIED, verbatim:

> - [ ] Docs have been added / updated (for bug fixes / features)

Breaking-change question — **CORRECTED.** The template has the heading and a Yes/No checkbox pair, with
**no** parenthetical:

> ## Does this PR introduce a breaking change?
> - [ ] Yes
> - [ ] No

I checked every revision of that file back to the first (`git log` on the path via the GitHub API:
`6270bba05` 2025-12, `7ecaffc00` 2024-11, `242a3c2a8` 2024-09, `68a6a075f` 2022-05, `a609bf50e` 2018-10,
`719101338` 2017-07, `d8d21c77d` 2017-06, `dae7cfc45` 2016-09, `e0c1c1300` 2016-06, `d33cd43db`
2016-04). None contains "What changes might users need to make in their application due to this PR?".
What the older revisions carry instead is an HTML comment beneath the checkboxes:

> <!-- If this PR contains a breaking change, please describe the impact and migration path for existing
> applications below. -->

The angular/angular.js template (still live, LTS) also has a bare `**Does this PR introduce a breaking
change?**` with no parenthetical. The parenthetical appears to come from a downstream template that
copied Angular's, not from angular/angular. Do not attribute it to Angular.

## 12. purposeful-readme spec v0.1.0

**URL read:**
<https://github.com/purposeful-readme/purposeful-readme/blob/main/spec/spec_v0_1_0.md> (raw read;
version confirmed in-file: "`purposeful-readme` `license: CC BY 4.0` `version: 0.1.0`")

VERIFIED, both quotes verbatim. Section 4.5 "Changelog in README":

> This content has its own standard (`CHANGELOG.md`, governed by [Keep a Changelog](https://keepachangelog.com)
> or another standard). Duplicating it in the README creates two places to maintain the same information
> and all but guarantees the risk of drift.
>
> The README must *not* contain a changelog. It may, however, contain a link to `CHANGELOG.md`.

And the stale-sections test:

> The question to ask before including any section: *"Who is responsible for updating this, and on what
> trigger?"* If the answer is "nobody specific" or "whenever we remember," the section will likely go
> stale. Remove it or link to something that has an owned update schedule.

Preceding sentence, worth keeping with it: "Any section that cannot be realistically kept current with
each release should either be removed or delegated to a specialised file that is maintained by tooling
rather than by hand."

## 13. OASIS keyword guidelines and RFC 8174

**URL read:** <https://www.oasis-open.org/policies-guidelines/keyword-guidelines/>

Non-standards-track — VERIFIED. Two statements, both verbatim:

> OASIS TC Notes (non-normative documents) do not specify conformance clauses. To avoid confusion with
> OASIS TC Specifications and Standards, citation of or use of [RFC 2119] or [ISO/IEC Directives] should
> be avoided in OASIS TC Notes (Non-normative Documents).

and, from the FAQ:

> When a TC is writing a TC Note, also known as a "non-standards track" work product, it should not use
> [RFC 2119], to avoid confusion with OASIS TC Specifications and Standards.

Normative content — VERIFIED with a small wording fix (plural "contents", "don't" not "doesn't"):

> Normative contents don't always use keywords. Often a descriptive or declarative style reads better
> than an imperative style based on keywords. In that case, such content may still be referred to by a
> more general statement — e.g. in a conformance clause — where normative keywords are used to clearly
> indicate what is expected from a conforming implementation.

**URL read:** <https://www.rfc-editor.org/rfc/rfc8174.txt>

VERIFIED. Abstract:

> RFC 2119 specifies common key words that may be used in protocol specifications. This document aims to
> reduce the ambiguity by clarifying that only UPPERCASE usage of the key words have the defined special
> meanings.

The replacement boilerplate RFC 8174 installs into RFC 2119 also carries a point the claim omits, and it
lines up with the OASIS rule above:

> These words can be used as defined here, but using them is not required. Specifically, normative text
> does not require the use of these key words. They are used for clarity and consistency when that is
> what's wanted, but a lot of normative text does not use them and is still normative.

## 14. Keep a Changelog 1.1.0 and Common Changelog

**URL read:** <https://keepachangelog.com/en/1.1.0/>

VERIFIED. Guiding Principles, first bullet:

> Changelogs are for humans, not machines.

The six types, verbatim and complete:

> `Added` for new features. `Changed` for changes in existing functionality. `Deprecated` for
> soon-to-be removed features. `Removed` for now removed features. `Fixed` for any bug fixes. `Security`
> in case of vulnerabilities.

Against commit logs — VERIFIED, under "Can changelogs be bad? / Commit log diffs":

> Using commit log diffs as changelogs is a bad idea: they're full of noise. Things like merge commits,
> commits with obscure titles, documentation changes, etc. The purpose of a commit is to document a step
> in the evolution of the source code. Some projects clean up commits, some don't. The purpose of a
> changelog entry is to document the noteworthy difference, often across multiple commits, to
> communicate them clearly to end users.

Keep a Changelog *recommends* an Unreleased section: "Keep an Unreleased section at the top to track
upcoming changes."

**URL read:** <https://common-changelog.org/>

VERIFIED — Common Changelog forbids it, under the heading "No Unreleased section":

> Common Changelog does not have an Unreleased section at the top of the changelog, which Keep a
> Changelog recommends for listing unreleased changes as they land in the main branch of the project. In
> practice, especially with Common Changelog's addition of references, this is an unproductive workflow:

with three reasons, the sharpest being: "Writing a changelog requires a bird's-eye view of the project,
while individual changes are typically best reviewed and discussed in isolation."

Common Changelog also drops two of Keep a Changelog's categories: "Common Changelog does not have
Deprecated and Security categories. A deprecation can be listed under the Changed category."

## 15. Diátaxis on reference

**URL read:** <https://diataxis.fr/reference/>

**CORRECTED on wording.** The claimed phrase "reflect the structure or architecture of the thing it's
describing" is not on the page. Two passages carry that idea, both verbatim:

In the "Describe and only describe" style-and-form list:

> structured according to the structure of the machinery itself

Under the heading "Respect the structure of the machinery":

> The way a map corresponds to the territory it represents helps us use the former to find our way
> through the latter. It should be the same with documentation: the structure of the documentation
> should mirror the structure of the product, so that the user can work their way through them at the
> same time.
>
> It doesn't mean forcing the documentation into an unnatural structure. What's important is that the
> logical, conceptual arrangement of and relations within the code should help make sense of the
> documentation.

"compass not a cage" — **CORRECTED. This is not Diátaxis's wording.** I enumerated every page on
diataxis.fr (`application/`, `colophon/`, `compass/`, `explanation/`, `foundations/`, `how-to-guides/`,
`how-to-use-diataxis/`, `map/`, `news/`, `quality/`, `reference-explanation/`, `reference/`,
`start-here/`, `theory/`, `translation/`, `tutorials-how-to/`, `tutorials/`) and the word "cage" appears
on none of them. There is also no compound-documents or complex-documents page (`/complex-hierarchies/`
returns 404). "A compass, not a cage" is a third-party gloss circulating in blog posts about Diátaxis.

The site's own equivalent is <https://diataxis.fr/how-to-use-diataxis/>, under "Use Diátaxis as a guide,
not a plan":

> Diátaxis describes a complete picture of documentation. However the structure it proposes is not
> intended to be a plan, something you must complete in your documentation. It's a guide, a map to help
> you check that you're in the right place and going in the right directions.

and, under "Don't worry about structure":

> Getting started with Diátaxis does not require you to think about dividing up your documentation into
> four sections. It certainly does not mean that you should create empty structures for
> tutorials/howto guides/reference/explanation with nothing in them. Don't do that. It's horrible.

The compass itself (<https://diataxis.fr/compass/>) is a two-question decision table, not a caution
against rigidity:

> The Diátaxis compass is something like a truth-table or decision-tree of documentation. It reduces a
> more complex, two-dimensional problem to its simpler parts, and provides the author with a
> course-correction tool.

---

## Notes on method

- Pages were fetched with `curl` and stripped to text locally, so quotes come from the served HTML
  rather than from a summarizer. Repository files (Angular template, purposeful-readme spec, Next.js
  guide) were read raw from `raw.githubusercontent.com`.
- Angular template history was enumerated through the GitHub commits API filtered on the file path, and
  each revision was fetched and grepped individually.
- Two claims cite the wrong page but the right project (claim 3, claim 7); one cites a page that never
  carried the wording (claim 15). In each case the correct URL is given above.
- One claim (the DocImpact retirement) could not be resolved either way from documentation; the
  supporting evidence found all points to the flag still being wired up.

## Pull requests, commits, and issues

# Fact-check report

Checked 2026-09-03. `gh` CLI was authenticated and never rate-limited. Every quote below was pulled from the
source named in the URL column, either through `gh api` or by fetching the page and reading its text.

## Summary table

| # | Claim | Verdict |
| --- | --- | --- |
| 1 | PostgreSQL `9877374` added `idle_session_timeout`, edited `config.sgml` in the same commit, doc entry quote | **CORRECTED** — commit and file list verified; the quote is the *commit message*, not the doc text |
| 2 | Prometheus PR #12019, `scrape_config_files`, merged 2023-03-07 as `c4da9cd`, v2.43.0, doc text, "a little bit vague" | **VERIFIED** (one nuance: the "vague" comment is post-merge, by a user, not a reviewer's review comment) |
| 3 | NumPy issue #27239 proposes removing old `versionadded`/`versionchanged` while preserving current-path info | **VERIFIED** |
| 4 | CPython gh-121277 introduces `.. versionadded:: next` expanded at release time; merged | **VERIFIED** |
| 5 | Sphinx maintainers' concern that accumulated `versionchanged` directives "bloat the docs" | **UNVERIFIABLE** — no such Sphinx issue; "bloat" is not verbatim anywhere I could find |
| 6 | GitHub immutable releases GA October 2025; PyPI files cannot be replaced | **VERIFIED** (2025-10-28) |
| 7 | Red Hat KCS solution structure: Environment / Issue / Resolution / Root Cause | **VERIFIED** |
| 8 | DITA 1.3 troubleshooting topic: condition, cause, remedy | **VERIFIED** |
| 9 | Mintlify: `{#id}` anchors decouple heading text from URL; redirects supported | **VERIFIED** |
| 10 | Hugo `aliases` front matter redirects; Docusaurus `id:`/`slug:` decouple URL from file name | **VERIFIED** |
| 11 | Pew Research "When Online Content Disappears" (2024-05-17): 38% / 54% / 23% / 21% | **VERIFIED** (one wording correction on the 38% figure) |

---

## 1. PostgreSQL `9877374` — CORRECTED

URL: <https://github.com/postgres/postgres/commit/9877374bef76ef03923f6aa8b955f2dbcbe6c2c7>
(fetched via `gh api repos/postgres/postgres/commits/9877374`)

**Verified:**

- Full hash: `9877374bef76ef03923f6aa8b955f2dbcbe6c2c7`
- Author: Tom Lane `<tgl@sss.pgh.pa.us>`, author date `2021-01-06T23:28:42Z`, committer date `2021-01-06T23:28:52Z`
- `doc/src/sgml/config.sgml` **is** in the commit's file list. Full list (11 files):
  `doc/src/sgml/config.sgml`, `src/backend/storage/lmgr/proc.c`, `src/backend/tcop/postgres.c`,
  `src/backend/utils/errcodes.txt`, `src/backend/utils/init/globals.c`, `src/backend/utils/init/postinit.c`,
  `src/backend/utils/misc/guc.c`, `src/backend/utils/misc/postgresql.conf.sample`, `src/include/miscadmin.h`,
  `src/include/storage/proc.h`, `src/include/utils/timeout.h`
- The commit message, verbatim:

  > Add idle_session_timeout.
  >
  > This GUC variable works much like idle_in_transaction_session_timeout,
  > in that it kills sessions that have waited too long for a new client
  > query.  But it applies when we're not in a transaction, rather than
  > when we are.
  >
  > Li Japin, reviewed by David Johnston and Hayato Kuroda, some
  > fixes by me
  >
  > Discussion: https://postgr.es/m/763A0689-F189-459E-946F-F0EC4458980B@hotmail.com

**The correction.** The quoted sentence is the **commit message**, not the documentation. The claim attributes it
to "a reference entry" in `config.sgml`. The doc entry the commit actually added reads:

> Terminate any session that has been idle (that is, waiting for a
> client query), but not within an open transaction, for longer than
> the specified amount of time.
> If this value is specified without units, it is taken as milliseconds.
> A value of zero (the default) disables the timeout.

followed by two more paragraphs:

> Unlike the case with an open transaction, an idle session without a
> transaction imposes no large costs on the server, so there is less
> need to enable this timeout
> than `idle_in_transaction_session_timeout`.

> Be wary of enforcing this timeout on connections made through
> connection-pooling software or other middleware, as such a layer
> may not react well to unexpected connection closure.  It may be
> helpful to enable this timeout only for interactive sessions,
> perhaps by applying it only to particular users.

So the doc text says the same thing in different words, and never uses the phrase "GUC variable". Note also that
the same commit *rewrote* the neighboring `idle_in_transaction_session_timeout` entry, which the claim does not
mention.

## 2. Prometheus PR #12019 — VERIFIED

URL: <https://github.com/prometheus/prometheus/pull/12019>

| Sub-claim | Result |
| --- | --- |
| Added `scrape_config_files` | Verified — title "Add include scrape configs"; added `scrape_config_files` handling in `config/config.go` and 12 new testdata files named `scrape_config_files*` |
| Merged 2023-03-07 | Verified — `mergedAt: 2023-03-07T21:45:38Z` |
| Merge commit `c4da9cd` | Verified — `c4da9cd92fa70c3e5f68b7a77584af3f96132451` |
| Shipped in v2.43.0 | Verified — the commit appears in `gh api repos/prometheus/prometheus/compare/v2.42.0...v2.43.0` (index 87 of that comparison's commit list) |
| Edited `docs/configuration/configuration.md` in the same PR | Verified — listed in the PR's changed files, `+5 −0` |

The doc text added by the PR, verbatim from the diff hunk (it is a YAML comment above the key):

```yaml
# Scrape config files specifies a list of globs. Scrape configs are read from
# all matching files and appended to the list of scrape configs.
scrape_config_files:
  [ - <filepath_glob> ... ]
```

That is exactly the sentence pair in the claim.

**The "a little bit vague" comment.** Author login: **`baryluk`**. URL:
<https://github.com/prometheus/prometheus/pull/12019#issuecomment-1728174143>. Verbatim opening:

> Commenting here, because the https://github.com/prometheus/prometheus/issues/8543 is not accessible.
>
> Documentation is a little bit vague, how to use it:
>
>     # Scrape config files specifies a list of globs. Scrape configs are read from
>     # all matching files and appended to the list of scrape configs.
>
> From reading documentation, I inferred that each file should be of this form:

**Nuance worth carrying into the synthesis:** the claim says "a reviewer commented". This is an ordinary issue
comment on the PR thread, posted **2023-09-20**, roughly six months *after* the 2023-03-07 merge, by someone who
was not among the PR's reviewers (the reviewers were `roidelapluie`, `juliusv`, `ka-keung`). It is a user
reporting confusion after the fact, not review feedback that preceded the merge. That distinction matters if the
synthesis uses it as evidence that review caught the problem — review did not; a reader did.

Incidentally, the exact wording of the doc line came from a `juliusv` review suggestion on the PR:

> ```suggestion
> # Scrape config files specifies a list of globs. Scrape configs are read from
> ```

and `roidelapluie` raised the singular/plural question on the same line ("Not sure about singular or plural
here.").

## 3. NumPy issue #27239 — VERIFIED

URL: <https://github.com/numpy/numpy/issues/27239> (opened by `seberg`, 2024-08-19, now closed)

Title, verbatim:

> DOC: Remove outdated versionadded/changed directives?

Relevant sentences, verbatim:

> We have a huge number of `versionadded` and `versionchanged` directives

> I think we should remove them at some point, since they are not really helpful when relating to NumPy versions
> that are long out of use.

> For example, NumPy 1.18.x only supported Python 3.8 which is EOL.  So I directive up to (and including) 1.19,
> would be OK to be removed.

(The garbled "So I directive up to" is verbatim in the source.)

On preserving current-path information, verbatim:

> When removing, we need to make sure that the information contained for the new paths remains documented.

Both halves of the claim hold, including the "1.19 and earlier" example. A useful supporting comment from `mhvk`:

> One could start by just removing `.. versionadded` for any version that is beyond the support line in NEP
> 29/SPEC 0. Unlike for `.. versionchanged`, there is no text that one has to work elsewhere into the docstring.

## 4. CPython gh-121277 — VERIFIED, merged

URL: <https://github.com/python/cpython/issues/121277> (opened by `encukou`, 2024-07-02)

Title, verbatim:

> Allow `.. versionadded:: next` in docs

Relevant sentences, verbatim:

> In a PR to CPython, the `versionadded`, `versionchanged`, `versionremoved`, `deprecated`,
> `deprecated-removed` directives in documentation should currently be set to the upcoming release.

> - Teach `versionadded` & the others to expand the version argument `next` to `<version> (unreleased)` (e.g.
>   `3.14.0b0 (unreleased)`).
> - Add a tool that replaces the `next` with a given string (e.g. `3.14`).
> - Modify the release manager tooling to run the tool on release.

**Merged: yes.** The main PR <https://github.com/python/cpython/pull/121278> ("gh-121277: Allow
`.. versionadded:: next` in docs") merged **2024-09-25T21:30:40Z**, merge commit
`7d24ea9db3e8fdca52058629c9ba577aba3d8e5c`. The issue was closed as `completed` on 2025-01-27 with all seven
checklist items ticked and seven linked PRs.

Confirmed downstream in the CPython devguide, <https://github.com/python/devguide/blob/main/documentation/markup.rst>:

> Instead of a specific version number, you can---and should---use
> the word ``next``, indicating that the API will first appear in the
> upcoming release.

> When a release is made, the release manager will change the ``next`` to
> the just-released version.

## 5. Sphinx "bloat the docs" — UNVERIFIABLE

**No source found. The word "bloat" is not verbatim, and the attribution to Sphinx maintainers appears wrong.**

What I tried:

- `gh search issues --repo sphinx-doc/sphinx bloat` — 4 hits, none about version directives (they are
  `#13268` llms-full.txt, `#12045` HTML search optimization, `#11807` repeat an admonition, `#2435` slim down
  quickstarted conf.py).
- `gh search issues --repo sphinx-doc/sphinx "versionchanged old versions"` — zero results.
- GitHub-wide `gh api search/issues` for `"bloat" versionchanged in:body` — 25 results, all Dependabot/Renovate
  bump PRs in unrelated forks. GitHub-wide for `"bloat the docs" versionadded` — 1 result,
  <https://github.com/Lightning-AI/pytorch-lightning/issues/5676>, which is about *adopting* the directives, not
  about bloat.
- Read the plausible candidates in full and grepped their comments for "bloat": sphinx-doc/sphinx `#11480`
  (versionremoved), `#11905` (Add versionremoved PR), `#12412` ("[docs] clarify the usage of `versionadded` &
  co" — actually about `::` literal-block parsing, unrelated), `#8309` (old doc versions in Google results).
  Zero occurrences of "bloat" in any of them.
- Read the linked CPython Discourse thread
  <https://discuss.python.org/t/automating-versionadded-changed-markers-in-docs-to-expedite-prs/38423> via its
  JSON API and grepped every post for "bloat" and "clutter". Zero hits.
- Grepped the CPython devguide `documentation/markup.rst` for any removal policy
  (`remove.*version(added|changed)`, "no longer supported", "out of use", "EOL"). Zero hits — the devguide has no
  rule about removing aged directives.
- Checked python/cpython `#131733` ("[Docs] add a new Sphinx `VersionChange` directive
  `.. scheduled-changed::`"). Related to version directives, but about a *new* directive for scheduled changes,
  and does not mention bloat.

**Closest real source.** The concern is real, but it is a **NumPy** concern, not a Sphinx-maintainer one, and it
is the very issue in claim 3: <https://github.com/numpy/numpy/issues/27239>, where `seberg` writes that the
directives "are not really helpful when relating to NumPy versions that are long out of use". If the synthesis
needs a citation for "accumulated version directives are a maintenance burden", that is the one to use — with the
attribution changed from Sphinx maintainers to NumPy maintainers, and with "bloat" dropped or paraphrased rather
than quoted.

## 6. GitHub immutable releases and PyPI file replacement — VERIFIED

**GitHub.** URL:
<https://github.blog/changelog/2025-10-28-immutable-releases-are-now-generally-available/>, dated
**October 28, 2025** — within October 2025 as claimed. Title: "Immutable releases are now generally available".
Verbatim:

> Once you publish a release as immutable, its assets can't be added, modified, or deleted.

> Tags for new immutable releases are protected and can't be deleted or moved.

Corroborated by the community announcement
<https://github.com/orgs/community/discussions/178351> ("🚀 Immutable Releases Are Now Generally Available!").
Note the scope limit the changelog states: enabling the setting makes *new* releases immutable; existing releases
stay mutable unless republished.

**PyPI.** URL: <https://pypi.org/help/>. Verbatim:

> PyPI does not allow for a filename to be reused, even once a project has been deleted and recreated.

> This ensures that a given distribution for a given release for a given project will always resolve to the same
> file, and cannot be surreptitiously changed one day by the projects maintainer or a malicious party (it can
> only be removed).

> Deletion of a project, release or file on PyPI is permanent and irreversible, without exception. Deletion of a
> project makes it uninstallable, and releases the project name for use by any other PyPI user. Deleted files
> cannot be re-uploaded. Deleted projects, releases or files cannot be restored by PyPI administrators.

Precise reading: PyPI's rule is *filename* non-reuse plus irreversible deletion. A file can be deleted; what
cannot happen is a different file appearing under a name already used. "Cannot be replaced once uploaded" is a
fair summary of the effect.

## 7. Red Hat KCS solution structure — VERIFIED

The four named sections are the standing template of a Red Hat Knowledgebase Solution, in the claimed order, and
a fifth (Diagnostic Steps) follows them. Section headings read off two public solution articles:

- <https://access.redhat.com/solutions/1207723> ("Resolution for Bash Code Injection Vulnerability via Specially
  Crafted Environment Variables (CVE-2014-6271, …)"), headings in document order:
  **Environment**, **Issue**, **Resolution**, **Root Cause**, **Diagnostic Steps**
- <https://access.redhat.com/solutions/740043> ("CloudForms Management Engine (CFME): Understanding logrotate —
  identifying and correcting problems"), same five headings in the same order.
- <https://access.redhat.com/solutions/6038> ("How to troubleshoot kernel crashes, hangs, or reboots with kdump
  on Red Hat Enterprise Linux") shows **Environment**, **Issue**, **Resolution**, … **Diagnostic Steps**, with the
  Root Cause section absent — so the sections are a template, not all mandatory.

Caveat: I read the rendered headings, not a Red Hat page that *documents* the template. Red Hat's own
template-authoring guidance sits behind the customer portal login. For an openly documented statement of the same
structure, the KCS v6 Practices Guide from the Consortium for Service Innovation is the vendor-neutral upstream:
<https://library.serviceinnovation.org/KCS/KCS_v6/KCS_v6_Practices_Guide/030/040/010/020> ("Technique 5.1: KCS
Article Structure"), which names Issue / Environment / Cause / Resolution — note **Cause**, not "Root Cause", and a
different ordering. So the exact four-word list in the claim is Red Hat's rendering, not generic KCS.

## 8. DITA 1.3 troubleshooting topic — VERIFIED

URL: <https://docs.oasis-open.org/dita/dita/v1.3/os/part3-all-inclusive/langRef/technicalContent/troubleshooting.html>
(OASIS DITA 1.3 OS, Part 3 all-inclusive, language reference, `<troubleshooting>` element)

Verbatim:

> The `<troubleshooting>` element is the top-level element for a troubleshooting topic. Troubleshooting topics
> document corrective action such as troubleshooting or alarm clearing. Troubleshooting topics begin with a
> description of a condition that the reader might want to correct, followed by one or more cause-remedy pairs.
> Each cause-remedy pair is a potential solution to the trouble described in the condition.

> Troubleshooting topics represent the kind of information that users typically consult to fix a problem.

Element structure: `<troubleshooting>` → `<title>`, `<shortdesc>`, `<troublebody>` → `<condition>`, then one or
more `<troubleSolution>`, each holding `<cause>` and `<remedy>`. Worth noting the spec's own framing: it is one
condition followed by *pairs* of cause and remedy, not a flat three-part sequence.

## 9. Mintlify linking guide — VERIFIED

URL: <https://www.mintlify.com/docs/guides/linking>

Custom anchors, verbatim from the body:

> Override the auto-generated anchor for any heading by appending `{#custom-id}` to the header text:

> This heading is reachable at `#config` instead of `#configuration-options`. Custom IDs keep anchor links stable
> when you update heading text—useful for headings you link to frequently.

And verbatim from the page's FAQ, which is the sentence the claim paraphrases:

> How do I keep anchor links stable when I update headings? Use custom anchor IDs for headings you link to
> frequently. Appending `{#custom-id}` to a heading decouples the anchor from the heading text, so you can update
> the heading text without breaking any links that point to it.

Redirects, verbatim:

> What happens to bookmarked links when I reorganize my documentation? Bookmarked and shared links become 404
> errors without redirects. Set up redirects in your `docs.json` whenever you move or rename a page. Redirects
> are cheap to add […]

Redirect reference page: <https://www.mintlify.com/docs/create/redirects>. Limitation to note: redirect *sources*
cannot include anchors or query strings, though destinations may.

## 10. Hugo aliases and Docusaurus id/slug — VERIFIED

**Hugo.** URL: <https://gohugo.io/content-management/urls/>, section "Aliases". Verbatim:

> Aliases allow you to redirect old URLs to new URLs. This is essential for preventing broken links and ensuring
> that existing bookmarks or external links continue to function when you rename or move content.

> To add redirects to a page, list the previous paths in the `aliases` field in your front matter. Hugo resolves
> these to server-relative paths during the build process, accounting for the baseURL and content dimension
> prefixes such as language, version, or role.

Mechanism: by default Hugo writes an HTML file at each alias path containing a meta-refresh to the new URL;
server-side `_redirects`/`.htaccess` generation via the `Aliases` page method is the alternative. Direction check:
`aliases` lists the **old** paths on the **new** page, so the redirect points *to* the page carrying the front
matter — as the claim says.

**Docusaurus.** URL: <https://docusaurus.io/docs/create-doc>. Verbatim:

> Every document has a unique `id`. By default, a document `id` is the name of the document (without the
> extension) relative to the root docs directory.

> Use the `slug` front matter to provide an explicit document URL and override the default one.

> Changing a document's filename or `id`, will change its default URL. To prevent breaking permalinks when
> renaming files, we recommend setting an explicit `slug` to keep your URLs stable.

That last sentence is the strongest support for the claim: Docusaurus itself recommends `slug` precisely to
decouple the URL from the file path. One precision: in Docusaurus the default URL derives from the file
path/`id`, **not** from the heading — so the "or heading" half of the claim is loose. Heading-derived URLs are the
Mintlify/anchor case in claim 9, not the Docusaurus page-URL case.

## 11. Pew Research Center, "When Online Content Disappears" — VERIFIED

URL: <https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/>, published
**May 17, 2024**. All four figures check out; one wording note.

| Figure | Claimed | Source text (verbatim) |
| --- | --- | --- |
| 38% | "38% of webpages that existed in 2013 are no longer accessible a decade later" | "38% of webpages that existed in 2013 are not available today" |
| 54% | 54% of Wikipedia pages have a broken link in References | "54% of Wikipedia pages contain at least one link in their 'References' section that points to a page that no longer exists" |
| 23% | 23% of news pages carry a broken link | "23% of news webpages contain at least one broken link" |
| 21% | 21% of government pages carry a broken link | "21% of webpages from government sites" have broken links |

Wording note on the 38%: the report says "are not available today", not "no longer accessible a decade later".
The decade framing is accurate arithmetic (2013 to the 2023 sample), but it is a paraphrase — quote it as "not
available today" if the synthesis puts it in quotation marks.
