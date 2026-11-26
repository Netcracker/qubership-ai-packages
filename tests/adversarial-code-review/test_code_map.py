"""code-map.py on a change committed to a scratch repository. Without an sb on PATH the map has no declarations, and its
output depends only on git; a fake sb, a Python script, answers `map` and `callers` with fixed JSON."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "adversarial-code-review", ".apm",
                      "skills", "adversarial-code-review", "scripts", "code-map.py")

HEADER = ("# Code map\n\nAdded lines per directory.\n\n"
          "| Directory | Code | Tests | Docs | Data | Config | Generated or lock |\n"
          "| --- | --- | --- | --- | --- | --- | --- |\n")


class CodeMapTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.git("init", "-q")
        self.git("commit", "-q", "--allow-empty", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.test", *args],
                              capture_output=True, text=True, check=True).stdout

    def commit(self, files):
        """Commit files, a mapping of path to content, or to None for a deletion."""
        for path, content in files.items():
            full = os.path.join(self.repo, path)
            if content is None:
                os.remove(full)
                continue
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as fh:
                fh.write(content)
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "change")

    def rebase_on_head(self, files):
        """Commit files as the new base, so the next commit is a change to them."""
        self.commit(files)
        self.base = self.git("rev-parse", "HEAD").strip()

    def run_script(self, *extra, sb=None, stderr=False):
        """Run the script with only git on PATH, and an `sb` that runs the Python source sb where it is given.

        Return its output, or its output and its error stream where stderr is true."""
        bin_dir = self.sb_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bin_dir)
        os.symlink(shutil.which("git"), os.path.join(bin_dir, "git"))
        if sb is not None:
            with open(os.path.join(bin_dir, "sb"), "w") as fh:
                fh.write(f"#!{sys.executable}\n{sb}")
            os.chmod(os.path.join(bin_dir, "sb"), 0o755)
        result = subprocess.run([sys.executable, SCRIPT, "--diff-base", self.base, "--repo", self.repo, *extra],
                                capture_output=True, text=True, env=dict(os.environ, PATH=bin_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        return (result.stdout, result.stderr) if stderr else result.stdout

    def test_a_file_counts_as_code_unless_its_extension_or_name_says_otherwise(self):
        self.commit({"src/a.mts": "x\n", "src/LICENSE": "x\n", "src/BUILD.md": "x\n", "src/go.mod": "x\n",
                     "src/testdata/golden.json": "x\n", "src/a_test.go": "x\n", "src/go.sum": "x\n"})
        self.assertEqual(HEADER + "| `src` | 1 | 1 | 2 | 0 | 1 | 1 |\n| `src/testdata` | 0 | 0 | 0 | 1 | 0 | 0 |\n"
                         "| total | 1 | 1 | 2 | 1 | 1 | 1 |\n\n"
                         "## src/a.mts (+1)\n\nAdded: 1\n\n\n"
                         "## Tests\n\n- src/a_test.go (+1), added 1\n\n",
                         self.run_script())

    def test_a_file_that_only_removes_lines_is_listed(self):
        self.rebase_on_head({"a.py": "a\nb\nc\n", "b_test.py": "a\nb\n"})
        self.commit({"a.py": "a\n", "b_test.py": "a\n"})
        self.assertEqual(HEADER + "| `.` | 0 | 0 | 0 | 0 | 0 | 0 |\n| total | 0 | 0 | 0 | 0 | 0 | 0 |\n\n"
                         "## a.py (+0)\n\nAdded: none (removes 2 lines)\n\n\n"
                         "## Tests\n\n- b_test.py (+0), removes 1 line\n\n",
                         self.run_script())

    def test_an_external_diff_driver_does_not_hide_the_hunks(self):
        self.rebase_on_head({"a.py": "a\n"})
        self.git("config", "diff.external", "true")
        with open(os.path.join(self.repo, ".git", "info", "attributes"), "w") as fh:
            fh.write("*.py diff=upper\n")
        self.git("config", "diff.upper.textconv", "tr a-z A-Z")
        self.commit({"a.py": "a\nb\n"})
        self.assertIn("## a.py (+1)\n\nAdded: 2\n", self.run_script())

    def test_a_deleted_file_is_listed_with_its_kind_and_an_excluded_path_is_left_out(self):
        self.rebase_on_head({"bin/run": "#!/bin/sh\n", "docs/old.md": "x\n", "vendor/lib.py": "x\n"})
        self.commit({"bin/run": None, "docs/old.md": None, "vendor/lib.py": "x\ny\n"})
        self.assertEqual(HEADER + "| total | 0 | 0 | 0 | 0 | 0 | 0 |\n\n"
                         "## Deleted\n\n- bin/run (code)\n- docs/old.md (docs)\n\n",
                         self.run_script("--exclude", "vendor"))

    def test_a_declaration_is_used_where_sb_callers_finds_a_call_with_it_as_the_only_candidate(self):
        self.commit({"lib.go": "x\n", "direct.go": "x\n", "typed.go": "x\n", "ambiguous.go": "x\n",
                     "lib_test.go": "x\n", "suffix.go": "x\n"})
        sb = """import json, sys
if sys.argv[1] == "map":
    decl = {"kind": "function", "name": "label", "start_line": 1, "end_line": 1}
    print(json.dumps({"files": [{"path": p, "declarations": [decl] if p == "lib.go" else []}
                                for p in sys.argv[4:]]}))
elif sys.argv[5] == "label":
    print(json.dumps({"matches": [{"file": "direct.go", "target": "lib.go::label"},
                                  {"file": "lib_test.go", "target": "lib.go::label"},
                                  {"file": "suffix.go", "target": "sub/lib.go::label"}],
                      "unattributed_total": 3, "unattributed": [
        {"file": "typed.go", "candidates": ["lib.go::label"]},
        {"file": "ambiguous.go", "candidates": ["lib.go::label", "other.go::label"]}]}))
"""
        out = self.run_script(sb=sb)
        self.assertIn("- function `label` lines 1-1: used in {direct.go, lib_test.go, typed.go};"
                      " 2 calls sb did not attribute\n", out)
        self.assertIn("- lib_test.go (+1), added 1: uses declarations of lib.go\n", out)

    def test_a_type_is_used_where_its_members_are_called_or_it_is_constructed_and_a_field_is_not_looked_up(self):
        self.commit({"cart.go": "x\n", "use.go": "x\n", "build.go": "x\n", "impl.go": "x\n", "fail.go": "x\n"})
        sb = """import json, os, sys
with open(os.path.join(os.path.dirname(sys.argv[0]), "calls.log"), "a") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
def decl(kind, name, children=()):
    return {"kind": kind, "name": name, "start_line": 1, "end_line": 1, "children": list(children)}
if sys.argv[1] == "map":
    files = {"cart.go": [decl("namespace", "shop", [decl("namespace", "inner", [
                 decl("field", "Max"),
                 decl("struct", "Cart", [decl("method", "Add"), decl("field", "items")])])])],
             "fail.go": [decl("function", "Broken")]}
    print(json.dumps({"files": [{"path": p, "declarations": files.get(p, [])} for p in sys.argv[4:]]}))
    sys.exit()
own = sys.argv[3] + "::"
found = {"matches": [], "types": [], "unattributed": []}
if sys.argv[5] == "Cart":
    found["types"] = [{"qn": own + "shop::Cart", "constructions": [{"file": "build.go"}],
                       "implementations": [{"file": "impl.go"}]}]
elif sys.argv[5] == "Add":
    found["matches"] = [{"file": "use.go", "target": own + "shop::Cart::Add"}]
elif sys.argv[5] == "Broken":
    print(json.dumps({"schema": "ast-bro.error.v1", "kind": "symbol_not_found"}))
    sys.exit(2)
print(json.dumps(found))
"""
        out, err = self.run_script(sb=sb, stderr=True)
        self.assertIn("- field `Max` lines 1-1\n- struct `Cart` lines 1-1: used in {build.go, impl.go, use.go}\n", out)
        self.assertIn("- function `Broken` lines 1-1: sb callers failed\n", out)
        self.assertIn("sb callers failed for 1 declarations", err)
        with open(os.path.join(self.sb_dir, "calls.log")) as fh:
            calls = [line.split() for line in fh]
        looked_up = [c[c.index("--symbol") + 1] for c in calls if c[0] == "callers"]
        self.assertEqual("Cart", looked_up[0], "the first lookup, which builds the index, skips the field")
        self.assertEqual(["Add", "Broken", "Cart"], sorted(looked_up))

    def test_a_failed_sb_map_leaves_the_map_without_declarations_and_says_so(self):
        self.commit({"lib.go": "x\n"})
        out, err = self.run_script(sb="import sys\nprint('boom')\nsys.exit(3)\n", stderr=True)
        self.assertIn("## lib.go (+1)\n\nAdded: 1\n\n\n", out)
        self.assertIn("sb map exited with 3; the map has no declarations", err)


if __name__ == "__main__":
    unittest.main()
