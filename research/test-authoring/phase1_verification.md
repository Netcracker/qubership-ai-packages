# Pass 1 verification: claims in the inventory table and the executive summary against their primary sources

Each section gives the claim as Pass 1 wrote it, the source fetched, a verdict (confirmed, corrected, unreachable, not
found), and the corrected figure or quote where one is needed. Paper PDFs were downloaded and read with `pdftotext`; a
page marked unreachable returned an HTTP error or a login redirect on every attempt.

## 1. Inozemtseva and Holmes, ICSE 2014 (row 14)

Claim: 5 Java projects, 31000 suites, statement, decision, and modified condition coverage, mutation score as the
effectiveness measure, "should not be used as a quality target", low to moderate correlation.

Source: [the ICSE 2014 PDF](https://www.cs.ubc.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf).

Verdict: confirmed, with one correction to the author column. The abstract: "we generated 31,000 test suites for five
systems consisting of up to 724,000 lines of source code. We measured the statement coverage, decision coverage, and
modified condition coverage of these suites and used mutation testing to evaluate their fault detection effectiveness.
We found that there is a low to moderate correlation between coverage and effectiveness when the number of test cases
in the suite is controlled for." The quality-target sentence is verbatim: "coverage, while useful for identifying
under-tested parts of a program, should not be used as a quality target because it is not a good indicator of test
suite effectiveness." The authors were at the University of Waterloo, not UBC; only the PDF's host is UBC.

## 2. Just et al., FSE 2014 (row 15)

Claim: 357 real faults, 5 projects, about 230000 mutants, 73% coupled, 17% not coupled, about 10% need stronger
operators, correlation stronger than statement coverage's.

Source: [the FSE 2014 PDF](https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014.pdf).

Verdict: confirmed. The paper uses "5 large Java programs, 357 real faults, and 230,000 mutants" (JFreeChart, Closure
Compiler, Commons Math, Joda-Time, Commons Lang). Its contribution list gives all three percentages: mutants from
commonly used operators are coupled to 73% of real faults; "10% of real faults require a new or stronger mutation
operator"; "17% of real faults are not coupled to any mutant". The coverage claim is verbatim: a "statistically
significant correlation that is stronger than the correlation between statement coverage and real fault detection."
Affiliations are Washington, Waterloo, and Sheffield, not UBC.

## 3. Zhang and Mesbah, FSE 2015 (row 16)

Claim: 6700 suites, 24000 assertions, 5 projects; assertion count and assertion coverage predict effectiveness better
than size.

Source: [the FSE 2015 PDF](https://people.ece.ubc.ca/amesbah/resources/papers/fse15.pdf).

Verdict: numbers confirmed; the finding needs the paper's wording. "We compose 6,700 test suites in total, using 24,000
assertions of five real-world Java projects." The paper claims three things: the number of assertions "strongly
correlates with its effectiveness, and this factor directly influences the relationship between test suite size and
effectiveness"; assertion coverage "is strongly correlated with effectiveness"; and "the correlation between statement
coverage and effectiveness decreases dramatically when assertion coverage is controlled for." It does not rank
assertions above size as a predictor; it explains the size correlation through assertions.

## 4. Petrović et al., ICSE 2021 and TSE 2021 (row 17)

Claim: about 15 million mutants; 24000 developers, 1000 projects; developers write more and better tests.

Sources: [the ICSE 2021 PDF](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf) and
[arXiv 2102.11378](https://arxiv.org/abs/2102.11378).

Verdict: confirmed, with each number assigned to its paper. The ICSE paper analyzes "a large dataset of almost 15
million mutants" created at Google over six years and concludes that "developers using mutation testing write more
tests, and actively improve their test suites with high quality tests such that fewer mutants remain." The TSE paper
reports the system "used by more than 24,000 developers on more than 1,000 projects" and, in its body, "almost 17
million mutants and 760,000 changes, which surfaced 2 million mutants during code review".

## 5. Luo et al., FSE 2014 (row 18)

Claim: 201 fix commits, 51 projects, the per-cause counts, 78% flaky when first written, 24% of fixes change the code
under test, 94% of those fix a real bug.

Source: [the FSE 2014 PDF](https://petertsehsun.github.io/soen7481/papers/flakyTests.pdf).

Verdict: confirmed; one category is missing. The paper studies "a total of 201 commits that likely fix flaky tests in 51
open-source projects". Table 2 totals: Async Wait 74, Concurrency 32, Test Order Dependency 19, Resource Leak 11,
Network 10, Time 5, IO 4, Randomness 4, Floating Point Operations 3, and Unordered Collections 1, which Pass 1 omitted.
The ten categories sum to 161, the commits the authors could classify. Findings F.2 and F.12 are verbatim: "Most flaky
tests (78%) are flaky the first time they are written" and "Some fixes to flaky tests (24%) modify the CUT, and most of
these cases (94%) fix a bug in the CUT."

## 6. Parry et al., TOSEM 2021 (row 19)

Claim: 76 papers surveyed; order-dependent tests up to 16% of flaky bug reports; a later study's top three are
concurrency 26%, async wait 22%, too restrictive range 17%.

Source: [the accepted manuscript at White Rose](https://eprints.whiterose.ac.uk/id/eprint/230095/1/parry2021.pdf).

Verdict: confirmed, with the attributions made explicit. The survey covers "76 papers". The summary table reads
"Order-dependent tests were found to constitute up to 16% of flaky test bug reports and 9% of previous flaky test
repairs"; the 16% is Vahabzadeh, Fard, and Mesbah, ICSME 2015. The 26%, 22%, and 17% are from Eck, Palomba,
Castelluccio, and Bacchelli, ESEC/FSE 2019, who "asked 21 software developers from Mozilla to classify 200 flaky tests
that they had previously fixed"; order dependency "came in fourth, responsible for 9% of cases". Too Restrictive Range,
Test Case Timeout, Test Suite Timeout, and Platform Dependency are the categories that emerged in that study.

## 7. Bavota et al., EMSE 2015, and Spadini et al., ICSME 2018 (row 20)

Claim: 86% of JUnit classes smelly, comprehension 30% better without smells; 221 releases of 10 systems; Indirect
Testing, Eager Test, and Assertion Roulette most tied to change- and defect-proneness.

Sources: [the Springer abstract](https://link.springer.com/article/10.1007/s10664-014-9313-0), reachable only through
the site's cookie redirect, and [the ICSME 2018 PDF](https://sback.it/publications/icsme2018a.pdf).

Verdict: Bavota confirmed; Spadini corrected in one detail. Bavota's abstract reports "86 % of JUnit tests exhibiting at
least one test smell" and "comprehension is 30 % better in the absence of test smells". Spadini: "we collect data on 221
releases of ten software systems and we analyze more than a million test cases to investigate the association of six
test smells". Result (ii) is "'Indirect Testing', 'Eager Test', and 'Assertion Roulette' are the most significant smells
for change-proneness", and the introduction adds that only "the first two are also related to a higher defect-proneness
of the exercised production code." Assertion Roulette is tied to change-proneness only.

## 8. Panichella et al., EMSE 2022 (row 21)

Claim: the detector misclassifies over 70% of smells; several smells ubiquitous but uncorrelated with real flaws;
vocabulary "highly mismatched".

Source: [the ZHAW repository record](https://digitalcollection.zhaw.ch/handle/11475/25672); the TU Delft page carries no
abstract.

Verdict: confirmed. The tool "misclassified over 70% of test smells, both missing real instances (false negatives) and
marking many smell-free tests as smelly (false positives)"; "multiple smells were ubiquitous on developer-written tests
but virtually never correlated with semantic or maintainability flaws"; "the current vocabulary of test smells is highly
mismatched to real concerns". Which smells are the ubiquitous ones is in the body, which Pass 2 still has to read.

## 9. tsDetect (row 22)

Claim: 19 smells, 96% precision.

Source: [the ESEC/FSE 2020 preprint](https://testsmells.org/assets/publications/FSE2020_TechnicalPaper.pdf).

Verdict: confirmed. "We evaluate the effectiveness of tsDetect on a benchmark of 65 unit test files containing instances
of 19 test smell types. Results show that tsDetect achieves a high detection accuracy with an average precision score of
96% and an average recall score of 97%." Per-smell precision ranges from 85% to 100%.

## 10. Agent-behavior papers (row 37)

Claim: 2602.00409 (1.2 million commits, 48563 by agents, 36% versus 26% add mocks), 2602.07900 (print statements over
assertions), 2606.28430 ("building to the test"), 2406.12952 (SWT-Bench, a fail-to-pass test doubles fix precision),
2511.16858 (test overfitting).

Sources: the arXiv pages [2602.00409](https://arxiv.org/abs/2602.00409), [2602.07900](https://arxiv.org/abs/2602.07900),
[2606.28430](https://arxiv.org/abs/2606.28430), [2406.12952](https://arxiv.org/abs/2406.12952), and
[2511.16858](https://arxiv.org/abs/2511.16858), plus the HTML version of the last.

Verdict: all five IDs resolve to the papers described; one sample in the evidence column needs re-attribution.

- 2602.00409, Hora and Robbes: "over 1.2 million commits made in 2025 in 2,168 TypeScript, JavaScript, and Python
  repositories, including 48,563 commits by coding agents"; "36% of commits made by coding agents add mocks to tests,
  compared with 26% by non-agents." Confirmed.
- 2602.07900, Chen et al.: trajectories of "six strong LLMs on SWE-bench Verified"; "value-revealing print statements
  appearing much more often than assertion-based checks." Confirmed. The "six models on SWE-bench Verified" sample in
  the row belongs to this paper.
- 2606.28430, Ma, Kereopa-Yorke, and Schultz: two Copilot CLI agents (claude-opus-4.7, gpt-5.5) "under a hidden
  222-test Playwright oracle across 18 runs"; with the oracle visible "the score reaches near-perfect" while the
  library is "left dead or absent". Confirmed; not a SWE-bench study.
- 2406.12952, Mündler et al.: "generated tests are an effective filter for proposed code fixes, doubling the precision
  of SWE-Agent." Confirmed; the abstract says generated tests, and fail-to-pass is the benchmark's own criterion.
- 2511.16858, Ahmed et al.: 449 TDD-Bench Verified instances; overfitting 21.8% (Claude 3.7 Sonnet) and 33.0% (GPT-4o),
  rising after test-based refinement and falling to 5.8% and 11.3% with the golden tests. Confirmed.

## 11. LLM test-quality studies (row 36)

Claim: Schäfer et al. TSE 2023; Yuan et al. FSE 2024; Ouedraogo et al. TOSEM 2025 (20505 LLM suites versus 779585 human
tests); Siddiq et al. 2023 (62.4% of HumanEval assertions incorrect across 4 LLMs); Kremer et al. 2025 (assertion errors
64%).

Sources: [2302.06527](https://arxiv.org/abs/2302.06527), [2305.04207](https://arxiv.org/abs/2305.04207) and its PDF,
[2410.10628](https://arxiv.org/abs/2410.10628), [2305.00418](https://arxiv.org/abs/2305.00418) and its PDF,
[2506.14297](https://arxiv.org/abs/2506.14297), and [2501.02901](https://arxiv.org/abs/2501.02901).

Verdict: two corrections.

- Schäfer, Nadi, Eghbali, and Tip: 25 npm packages, 1684 API functions, median statement coverage 70.2%. Confirmed.
- Yuan et al.: 1000 Java focal methods from 185 projects; 24.8% of ChatGPT's tests pass, and 17.3% compile but fail,
  "which mostly result from the incorrect assertions". Confirmed.
- Ouedraogo et al.: "20,505 class-level suites" against "779,585 tests from 34,635 open-source Java projects"; Assertion
  Roulette and Magic Number Test the most common smells. Confirmed.
- Siddiq et al. (2305.00418): three models (Codex, GPT-3.5-Turbo, StarCoder), not four, and no 62.4% figure anywhere in
  the paper; its smells are Duplicated Asserts and Empty Tests. **Corrected:** the 62.4% figure is from DeCon
  (2501.02901, Yu et al.): "assertions generated by four LLMs for the HumanEval benchmark, over 62% of the generated
  assertions are incorrect", 62.4% in the body. Move the figure to the DeCon entry.
- 2506.14297 is "Quality Assessment of Python Tests Generated by Large Language Models" by Alves, Bezerra, Machado,
  Rocha, Virgínio, and Silva; no author is named Kremer. "Assertion errors were the most common, comprising 64% of all
  identified errors" is verbatim. **Corrected:** cite as Alves et al. 2025.

## 12. Reid 1997 (row 12)

Claim: BVA 0.79, EP 0.33, 20 KLOC Ada.

Sources tried: [IEEE Xplore 637166](https://ieeexplore.ieee.org/document/637166/) (HTTP 403, then 418 on the abstract
URL) and the Semantic Scholar record for DOI 10.1109/METRIC.1997.637166, which carries no abstract.

Verdict: unreachable. Secondary sources agree with Pass 1: an "operational avionics system of approximately 20000 lines
of Ada code", "a mean probability of detection of 0.79" for BVA against 0.33 for EP. Venue: Fourth International
Software Metrics Symposium, 1997, pages 64 to 73. Keep the "needs the paper" flag; the paper is paywalled.

## 13. Assertion-message studies (row 39)

Claim: Taha et al. 2023 (2303.00169) and 2408.01751; 20 Java systems; developers rarely supply a message;
identifier-only and literal-only messages differ in readability.

Sources: [arXiv 2303.00169](https://arxiv.org/abs/2303.00169) and [arXiv 2408.01751](https://arxiv.org/abs/2408.01751).

Verdict: corrected on two points. The 2023 paper is by Takebayashi, Peruma, Mkaouer, and Newman, not "Taha"; it examines
"20 open-source Java systems", finds that "developers rarely utilize the option of supplying a message", and that "a
beginner's knowledge of English is required to understand messages containing only identifiers, while a 4th-grade
education level is required to understand messages composed of string literals." The 2024 paper (Peruma et al.) is a
survey of "138 professional software practitioners", not a mining study, so the 20-system sample applies to the first
paper only.

## 14. Wu and Clause (row 40)

Claim: the action-predicate-scenario pattern detects non-descriptive names at 95% precision.

Source: [arXiv 2005.05359](https://arxiv.org/abs/2005.05359), the JSS 2020 paper; the ACM page for the ASE 2016 paper
returned HTTP 403.

Verdict: confirmed with a wording change. "An empirical evaluation on 34352 JUnit tests" shows the approach "accurate,
and useful at discriminating descriptive and non-descriptive names with a 95% true-positive rate." The paper reports a
true-positive rate, not precision; per-project precision on the 265 hand-checked tests ranges from 82% to 100%.

## 15. Goldstein et al., ICSE 2024 (row 38)

Claim: 30 interviews.

Source: [the ICSE 2024 program page](https://conf.researchr.org/details/icse-2024/icse-2024-research-track/90/Property-Based-Testing-in-Practice);
the ACM page returned HTTP 403.

Verdict: confirmed: "30 in-depth interviews with experienced users of PBT at Jane Street". The strengths and weaknesses
in the row match the abstract.

## 16. Contribution guides (rows 31 and 32)

Claim: Kubernetes says "All packages require unit tests" and "Timeout is not a useful error message", has a zero-flake
policy with no automatic retries; Django, rustc, and pytest state the regression-test guarantee; avoid issue numbers in
names.

Sources: the raw `testing.md`, `writing-good-e2e-tests.md`, and `flaky-tests.md` under
[kubernetes/community sig-testing](https://github.com/kubernetes/community/tree/master/contributors/devel/sig-testing);
Django's [submitting-patches](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/submitting-patches/)
and [coding-style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/) pages;
[the rustc-dev-guide page](https://rustc-dev-guide.rust-lang.org/tests/adding.html); and
[pytest's contributing page](https://docs.pytest.org/en/stable/contributing.html).

Verdict: confirmed as paraphrases; the exact wording differs in three places.

- `testing.md`: "All packages and any significant files require unit tests." Pass 1 shortened it.
- `writing-good-e2e-tests.md`: "\"Timeout\" is not a useful error message." The same page lets a test "back off and
  retry a few times" on an API call under load; the no-retry rule is about test jobs, not calls inside a test.
- `flaky-tests.md`: "The project has a 'zero-flake' policy. Test jobs must not automatically retry on test failures."
- Django: "Is there a proper regression test (the test should fail before the fix is applied)?" Pass 1's "fail while
  the bug still exists and pass once fixed" is a paraphrase, not a quote.
- rustc: "This test should fail in `main` but pass after the PR." Pass 1 wrote "master". On issue numbers the guide
  says the opposite of "avoid": "If there is an issue number associated with the test, include the issue number", in
  the file's first comment.
- pytest: "If you can write a demonstration test that currently fails but should pass (xfail), that is a very useful
  commit to make as well." Placement: a regression test for `--lf` goes into `test_cacheprovider.py`.
- The issue-number rule is Django's coding-style page: "Reserve ticket references for obscure issues where the ticket
  has additional details that can't be easily described in docstrings or comments", with the number at the end of the
  docstring sentence. Neither rustc nor pytest states it.

## 17. Google Testing Blog, "Prefer Narrow Assertions in Unit Tests" (row 4)

Claim: found but not readable; the example should be fetched.

Source: [the post](https://testing.googleblog.com/2024/04/prefer-narrow-assertions-in-unit-tests.html), by Kai Kent,
April 4, 2024; the body was extracted from the downloaded HTML.

Verdict: fetched. A loyalty feature adds a `CREATION_DATE` column to the `ACCOUNT` table and an unrelated test fails:

```cpp
TEST_F(AccountTest, UpdatesBalanceAfterWithdrawal) {
  ASSERT_OK_AND_ASSIGN(Account account,
                       database.CreateNewAccount(/*initial_balance=*/5000));
  ASSERT_OK(account.Withdraw(3000));
  const Account kExpected = { .balance = 2000, /* a handful of other fields */ };
  EXPECT_EQ(account, kExpected);
}
```

The diagnosis: "It checks for full equality of a potentially complex object, and thus implicitly tests unrelated
behaviors. Changing anything in Account, such as adding or removing a field, will cause all the tests with a similar
pattern to fail." Broad assertions produce brittle tests that "need frequent fixing even though they aren't finding real
bugs." The fix replaces the last line with `EXPECT_EQ(account.balance, 2000)`. The post limits full-object equality to
tests where every implicitly tested behavior is intended, suggests at most one such test per complex object, and for
protocol buffers points at `comparingExpectedFieldsOnly()` in Java and `protocmp.FilterField` in Go.
