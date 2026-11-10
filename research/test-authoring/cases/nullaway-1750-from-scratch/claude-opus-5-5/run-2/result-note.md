I added five regression tests for the `SpringHandler` fix in `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. Production code is unchanged and nothing is committed.

- **On the old code:** all five new tests fail with the bug's own symptom, `Saw unexpected error on line 5`, which is the field whose expression only compares against `null`.
- **On the fix:** they pass, along with the rest of `FrameworkTests`, and `./gradlew :nullaway:buildWithNullAway` passes.
- **Regex mutants:** I changed `NULL_COMPARISON_PATTERN` three ways by hand: deleted the left-hand alternative, narrowed `[!=]` to `!`, and replaced `\s*` with `\s`. A test failed each time, and I restored the file after each run.

**Message for the author:**

> Thanks for the fix. I added tests for it in `FrameworkTests`, next to `springValueFieldTest`.
>
> Each test compiles one class with two `@Value` fields:
> - one whose expression uses `null` only in a comparison, which must not be reported;
> - one with the same expression except that a branch returns `null`, which must still be reported.
>
> Keeping the second field in the same source shows that the first stays quiet because of the comparison handling, not because of the setup. There are five tests, one for each form the new pattern handles:
>
> | Test (suffix) | Expression form |
> | --- | --- |
> | `…BesideNotEqualsNull` | `x != null` |
> | `…BesideEqualsNull` | `x == null` |
> | `…BesideNullNotEquals` | `null != x` |
> | `…BesideNullEquals` | `null == x` |
> | `…BesideNotEqualsNullWithoutSpaces` | `x!=null`, no spaces |
>
> Each test covers a different part of `NULL_COMPARISON_PATTERN`. Removing the `null ==`/`null !=` alternative, narrowing `[!=]` to `!`, or changing `\s*` to `\s` each fails at least one of them. All five fail on the code before the fix.
>
> They are separate tests because `CompilationTestHelper` stops at the first mismatch, so one combined source would hide every failure after the first. To share the `@Value` stub, I moved it into a helper, `addSpringValueAnnotationStub`. `springValueFieldTest` now calls it, and its expectations are unchanged.
>
> Not done, for you to decide: SpEL also accepts the word operators `eq` and `ne`. `@Value("#{someBean ne null ? someBean.value : 'default'}")` is still reported, the same false positive the fix removes for `!=`. If that should be silent too, the pattern needs `\b(eq|ne)\s+null\b` and `\bnull\s+(eq|ne)\b`, and two more tests in the same shape.

One suggestion for you rather than the PR: these runs established how Error Prone's `CompilationTestHelper` reports failures, and no reference file covers it. I could add a line to `CLAUDE.md` saying one `doTest()` stops at the first mismatch, names a missing diagnostic by its pattern and an unexpected one by line number, and prints every diagnostic's text below that. I won't edit the file unless you want it.
