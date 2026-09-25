# Tests

Tests: JUnit 4 engine; Error Prone's CompilationTestHelper, whose doTest() stops at the first mismatched marker and names it by line number. Write its tests as if doTest() reported every mismatch and told each marker apart: we keep the cases of one rule in one source for the reader, and accept a second run to see the next mismatch until the harness reports them all.
