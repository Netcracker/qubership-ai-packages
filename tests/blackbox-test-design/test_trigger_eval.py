"""The trigger-eval harness of blackbox-test-design: how it reads a session's stream, how it scores a run, and whether
the committed results were measured on the description SKILL.md carries today."""
import collections
import importlib.util
import json
import os
import sys
import time
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TRIGGER = os.path.join(ROOT, "research", "blackbox-test-design", "trigger")

spec = importlib.util.spec_from_file_location("run_trigger_eval", os.path.join(TRIGGER, "run_trigger_eval.py"))
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def skill_call(name):
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}})


def tool_call(name):
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": {}}]}})


RESULT = json.dumps({"type": "result", "is_error": False})
ERROR = json.dumps({"type": "result", "is_error": True})


class SkillsInvokedTest(unittest.TestCase):
    def test_the_candidate_counts_after_another_skill_and_a_tool_call(self):
        stream = [tool_call("Read"), skill_call("test-authoring"), skill_call("blackbox-test-design"), RESULT]
        self.assertEqual((["test-authoring", "blackbox-test-design"], True, None), harness.skills_invoked(stream))

    def test_a_session_that_loads_only_another_skill_does_not_count(self):
        stream = [skill_call("test-authoring"), RESULT]
        self.assertEqual((["test-authoring"], True, None), harness.skills_invoked(stream))

    def test_a_session_that_ends_in_an_error_reaches_no_verdict(self):
        stream = [skill_call("test-authoring"), ERROR]
        self.assertEqual((["test-authoring"], False, None), harness.skills_invoked(stream))

    def test_a_session_cut_off_before_its_result_reaches_no_verdict(self):
        stream = [tool_call("Read")]
        self.assertEqual(([], False, None), harness.skills_invoked(stream))

    def test_a_call_after_the_result_event_is_not_read(self):
        stream = [tool_call("Read"), RESULT, skill_call("blackbox-test-design")]
        self.assertEqual(([], True, None), harness.skills_invoked(stream))

    def test_the_model_comes_from_the_init_event(self):
        init = json.dumps({"type": "system", "subtype": "init", "model": "claude-opus-5-5"})
        self.assertEqual(([], True, "claude-opus-5-5"), harness.skills_invoked([init, RESULT]))

    def test_a_line_that_is_not_json_is_skipped(self):
        stream = ["not json", skill_call("blackbox-test-design")]
        self.assertEqual((["blackbox-test-design"], True, None), harness.skills_invoked(stream))


class RunQueryTest(unittest.TestCase):
    def test_a_session_that_prints_nothing_is_killed_at_the_timeout(self):
        started = time.monotonic()
        result = harness.run_query([sys.executable, "-c", "import time; time.sleep(30)"], ROOT, 0.5)
        self.assertEqual(([], False, None), result)
        self.assertLess(time.monotonic() - started, 10)


class ScoreTest(unittest.TestCase):
    def test_a_query_passes_when_the_majority_of_its_runs_matches_the_label(self):
        evals = [{"query": "port", "should_trigger": True}, {"query": "lecture", "should_trigger": False}]
        result = harness.score(evals, {0: [True, True, False], 1: [True, True, False]})
        self.assertEqual([True, False], [row["pass"] for row in result["rows"]])
        self.assertAlmostEqual(2 / 3, result["recall"])
        self.assertAlmostEqual(2 / 3, result["false_positive_rate"])

    def test_a_query_loaded_in_half_its_runs_counts_as_loaded(self):
        evals = [{"query": "port", "should_trigger": True}, {"query": "lecture", "should_trigger": False}]
        result = harness.score(evals, {0: [True, False], 1: [True, False]})
        self.assertEqual([True, False], [row["pass"] for row in result["rows"]])

    def test_a_query_with_no_verdict_fails_and_stays_out_of_the_rates(self):
        evals = [{"query": "port", "should_trigger": True}, {"query": "stand", "should_trigger": True}]
        result = harness.score(evals, {0: [True], 1: []})
        self.assertEqual([(1.0, True), (None, False)], [(row["rate"], row["pass"]) for row in result["rows"]])
        self.assertEqual(1.0, result["recall"])


class WithDescriptionTest(unittest.TestCase):
    def test_a_folded_description_is_replaced_and_the_other_keys_kept(self):
        skill_md = "---\nname: x\ndescription: >-\n  old line one\n  old line two\nlicense: MIT\n---\nbody\n"
        self.assertEqual('---\nname: x\ndescription: "new"\nlicense: MIT\n---\nbody\n',
                         harness.with_description(skill_md, "new"))


class CommittedResultsTest(unittest.TestCase):
    """A description edit owes a new trigger run (agent-packages/blackbox-test-design/AGENTS.md)."""

    def test_each_results_file_measured_the_current_description(self):
        current = harness.current_description()
        files = sorted(f for f in os.listdir(TRIGGER) if f.startswith("results-") and f.endswith(".json"))
        self.assertTrue(files, "no results-*.json under " + TRIGGER)
        for name in files:
            with self.subTest(name), open(os.path.join(TRIGGER, name)) as f:
                self.assertEqual(current, json.load(f)["description"], name)

    def test_the_eval_set_has_unique_queries_with_both_labels(self):
        with open(os.path.join(TRIGGER, "eval-set.json")) as f:
            evals = json.load(f)
        counts = collections.Counter(e["query"] for e in evals)
        self.assertEqual([], [q for q, n in counts.items() if n > 1])
        self.assertEqual({True, False}, {e["should_trigger"] for e in evals})


if __name__ == "__main__":
    unittest.main()
