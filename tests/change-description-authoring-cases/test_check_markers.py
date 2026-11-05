"""Phrase tables for the check.py markers that have to tell a phrase from a near miss.

The golden output in check-output.txt covers only the phrasings the committed results happen to use. A marker that
must reject a near miss gets its probes here: the phrasings a case README, a commit message, or a review names, and
the near misses a lookaround in a marker's pattern exists to reject, each with the verdict the check owes it. A pattern
that only splits a result into paragraphs or sentences has no table.
"""
import importlib.util
import os
import sys
import unittest

CHECK = os.path.join(os.path.dirname(__file__), "..", "..", "research", "change-description-authoring", "cases",
                     "check.py")

_spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(_spec)
# A __pycache__ written beside check.py would show up as a directory under cases/.
_dont_write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    _spec.loader.exec_module(check)
finally:
    sys.dont_write_bytecode = _dont_write_bytecode


class ContradictionsLocated4412Test(unittest.TestCase):
    """The recover() comment counts as located only where the phrase names the comment that recover() carries.

    Every probe also names the batch test, so the verdict depends on the recover() marker alone.
    """

    BATCH = " The batch test is wrong as well."

    def verdict(self, phrase):
        return check.contradictions_located_4412(phrase + self.BATCH)[0]

    def test_a_phrase_that_names_the_comment_of_recover_is_located(self):
        for phrase in ["the `recover()` comment got the ownership rule wrong",
                       "the comment in `PGXAConnection.recover()`",
                       "the comment on the `recover()` query",
                       "the comment above `PGXAConnection#recover`"]:
            with self.subTest(phrase=phrase):
                self.assertEqual("PASS", self.verdict(phrase))

    def test_a_phrase_that_names_recover_beside_another_comment_is_not_located(self):
        for phrase in ["not from `recover()`, which has its own comment",
                       "the comment in `getConnection()`, not `recover()`",
                       "the javadoc of `recover_withAutoCommitFalse_doesNotOpenTransaction`"]:
            with self.subTest(phrase=phrase):
                self.assertEqual("FAIL", self.verdict(phrase))


class NoTestNarrationTest(unittest.TestCase):
    """A sentence that narrates a red run or counts passing tests fails; one on a test that passes without the change
    is the slot the skill keeps, and passes."""

    def test_a_narrated_red_run_or_a_count_of_passing_tests_fails(self):
        for sentence in ["`SkipTest` (new) fails without the change.",
                         "Revert the guard and six of the seven fail.",
                         "With the production change reverted, the new test fails.",
                         "All 12 tests pass."]:
            with self.subTest(sentence=sentence):
                self.assertEqual("FAIL", check.no_test_narration(sentence)[0])

    def test_a_test_that_passes_without_the_change_passes(self):
        for sentence in ["`closeReportsAFailedRelease` passes without the change.",
                         "3 tests pass with and without the change."]:
            with self.subTest(sentence=sentence):
                self.assertEqual("PASS", check.no_test_narration(sentence)[0])


class NoRoute4420Test(unittest.TestCase):
    """The mutation run and "I checked" are the route and fail; the `git grep` behind a claim about code outside the
    diff stays, and so does a word that ends in "I", such as "CI"."""

    def test_the_mutation_run_fails(self):
        for sentence in ["I checked each site by breaking it.",
                         "I broke one site at a time.",
                         "The mutation run killed every mutant."]:
            with self.subTest(sentence=sentence):
                self.assertEqual("FAIL", check.no_route_4420(sentence)[0])

    def test_a_check_that_is_not_the_route_passes(self):
        for sentence in ["`git grep` finds no test that turns escape processing off.",
                         "CI checked the build on PostgreSQL 17."]:
            with self.subTest(sentence=sentence):
                self.assertEqual("PASS", check.no_route_4420(sentence)[0])


class FinderNotNamedTest(unittest.TestCase):
    """Naming the audit that found the defect fails; the audit log is a thing the code has, and passes."""

    def test_the_audit_as_the_finder_fails(self):
        for sentence in ["An audit of the bootstrap code caught it.",
                         "The audit found an unguarded read."]:
            with self.subTest(sentence=sentence):
                self.assertEqual("FAIL", check.finder_not_named(sentence)[0])

    def test_the_audit_log_passes(self):
        self.assertEqual("PASS", check.finder_not_named("The audit log records each lookup.")[0])


if __name__ == "__main__":
    unittest.main()
