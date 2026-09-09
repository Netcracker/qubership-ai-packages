"""comment-drift.py against a throwaway git repository: every tag it prints, overloads and same-named members of two
types kept apart, each of the five extensions it accepts, a local that belongs to its function, untracked files, a non-ASCII
path, and a run from a subdirectory."""
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "final-review", ".apm", "skills",
                      "final-review", "scripts", "comment-drift.py")

BASE = textwrap.dedent("""\
    class Reader {
      /** Reads count bytes. */
      int read(int count) {
        return count;
      }

      /** Reads the named field. */
      int read(String name) {
        return name.length();
      }

      int skip(long count) {
        return 0;
      }
    }
    """)


class CommentDriftTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        # The defect this suite pins only shows under Git's default quoting, which a global config may turn off.
        self.git("config", "core.quotePath", "true")
        self.write("Reader.java", BASE)
        self.git("add", "Reader.java")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as f:
            f.write(text)

    def drift(self, cwd=None):
        # The script writes UTF-8 whatever the locale is, so read it as UTF-8 rather than through text=True.
        return subprocess.run([sys.executable, os.path.abspath(SCRIPT), "HEAD"], cwd=cwd or self.repo, check=True,
                              capture_output=True, encoding="utf-8").stdout

    def test_overloads_are_reported_apart_with_their_lines(self):
        self.write("Reader.java", BASE.replace("return count;", "return count + 1;")
                   .replace("Reads the named field.", "Reads the named field, case-insensitively."))
        self.assertEqual(
            "== Reader.java\n"
            "  Reader.read(String) @8: comment-changed\n"
            "  Reader.read(int) @3: code-changed, comment-unchanged\n",
            self.drift())

    def test_a_renamed_parameter_keeps_the_member_identity(self):
        self.write("Reader.java", BASE.replace("int read(int count) {\n    return count;", "int read(int n) {\n    return n;"))
        self.assertEqual("== Reader.java\n  Reader.read(int) @3: code-changed, comment-unchanged\n", self.drift())

    def test_a_comment_added_above_an_uncommented_member(self):
        self.write("Reader.java", BASE.replace("  int skip(long count) {", "  /** Skips count bytes. */\n  int skip(long count) {"))
        self.assertEqual("== Reader.java\n  Reader.skip(long) @13: comment-added\n", self.drift())

    def test_a_body_change_under_no_comment(self):
        self.write("Reader.java", BASE.replace("    return 0;", "    return -1;"))
        self.assertEqual("== Reader.java\n  Reader.skip(long) @12: code-changed, no-comment\n", self.drift())

    def test_a_changed_line_above_every_declaration_is_unplaced(self):
        self.write("Reader.java", "import java.io.IOException;\n\n" + BASE)
        out = self.drift()
        self.assertIn("(file level): 2 changed line(s) unplaced", out)

    def test_a_parameter_list_that_continues_on_the_next_line_is_cut_and_marked(self):
        self.write("Reader.java", BASE.replace("  int skip(long count) {", "  int skip(long count,\n      int limit) {"))
        # The declaration line changed too, so the base identity and the cut identity are both reported.
        self.assertEqual(
            "== Reader.java\n"
            "  Reader.skip(long) @base 12: code-changed, no-comment\n"
            "  Reader.skip(long…) @12: code-changed, no-comment\n",
            self.drift())

    def test_a_run_from_a_subdirectory_reads_the_same_tree(self):
        sub = os.path.join(self.repo, "src")
        os.mkdir(sub)
        self.write("Reader.java", BASE.replace("return count;", "return count + 1;"))
        self.assertEqual(self.drift(), self.drift(cwd=sub))
        self.assertEqual("== Reader.java\n  Reader.read(int) @3: code-changed, comment-unchanged\n", self.drift(cwd=sub))

    def test_same_named_members_of_two_types_are_reported_apart(self):
        two = BASE.replace("class Reader {", "class Reader {\n  static class Inner {\n    /** Inner read. */\n    int read(int count) {\n      return count;\n    }\n  }")
        self.write("Reader.java", two)
        self.git("add", "Reader.java")
        self.git("commit", "-q", "-m", "two types")
        self.write("Reader.java", two.replace("      return count;", "      return count + 1;", 1).replace("Reads count bytes.", "Reads count bytes, at most."))
        self.assertEqual(
            "== Reader.java\n"
            "  Reader.Inner.read(int) @4: code-changed, comment-unchanged\n"
            "  Reader.read(int) @9: comment-changed\n",
            self.drift())

    def test_kotlin_overloads_carry_their_parameter_types(self):
        kt = "class Reader {\n    /** Reads count bytes. */\n    fun read(count: Int): Int = count\n\n    /** Reads the named field. */\n    fun read(name: String): Int = name.length\n}\n"
        self.write("Reader.kt", kt)
        self.git("add", "Reader.kt")
        self.git("commit", "-q", "-m", "kotlin")
        self.write("Reader.kt", kt.replace("= count\n", "= count + 1\n").replace("Reads the named field.", "Reads the named field, trimmed."))
        self.assertEqual(
            "== Reader.kt\n"
            "  Reader.read(Int) @3: code-changed, comment-unchanged\n"
            "  Reader.read(String) @6: comment-changed\n",
            self.drift())

    def test_a_kotlin_local_belongs_to_its_function(self):
        kt = "class Reader {\n    /** Reads count bytes. */\n    fun read(count: Int): Int {\n        val result = count\n        return result\n    }\n}\n"
        self.write("Reader.kt", kt)
        self.git("add", "Reader.kt")
        self.git("commit", "-q", "-m", "kotlin")
        self.write("Reader.kt", kt.replace("return result", "return result + 1"))
        self.assertEqual("== Reader.kt\n  Reader.read(Int) @3: code-changed, comment-unchanged\n", self.drift())

    def test_a_scala_parameterless_def_is_a_member(self):
        sc = "class A {\n  /** The size. */\n  def size: Int = 0\n\n  /** The name. */\n  def name = \"a\"\n}\n"
        self.write("A.scala", sc)
        self.git("add", "A.scala")
        self.git("commit", "-q", "-m", "scala")
        self.write("A.scala", sc.replace("= 0", "= 1").replace("The name.", "The display name."))
        self.assertEqual(
            "== A.scala\n"
            "  A.name @6: comment-changed\n"
            "  A.size @3: code-changed, comment-unchanged\n",
            self.drift())

    def test_a_groovy_def_method_carries_its_parameter_types(self):
        gv = "class Reader {\n  /** Reads count bytes. */\n  def read(int count) {\n    return count\n  }\n\n  /** Reads the named field. */\n  def read(String name) {\n    return name.length()\n  }\n}\n"
        self.write("Reader.groovy", gv)
        self.git("add", "Reader.groovy")
        self.git("commit", "-q", "-m", "groovy")
        self.write("Reader.groovy", gv.replace("return count\n", "return count + 1\n"))
        self.assertEqual("== Reader.groovy\n  Reader.read(int) @3: code-changed, comment-unchanged\n", self.drift())

    def test_a_tracked_non_ascii_path_survives_the_extension_filter(self):
        # Git quotes such a path unless core.quotePath is off, and a quoted name does not end in ".java".
        self.write("Пример.java", BASE)
        self.git("add", "Пример.java")
        self.git("commit", "-q", "-m", "non-ascii path")
        self.write("Пример.java", BASE.replace("return count;", "return count + 1;"))
        self.assertEqual("== Пример.java\n  Reader.read(int) @3: code-changed, comment-unchanged\n", self.drift())

    def test_an_untracked_non_ascii_path_survives_the_extension_filter(self):
        # The untracked list is `git ls-files --others`, which quotes such a path the same way the diff does.
        self.write("Черновик.java", "class Draft {\n  /** Writes count bytes. */\n  int write(int count) {\n    return count;\n  }\n}\n")
        self.assertEqual("== Черновик.java\n  Draft @1: code-changed, no-comment\n  Draft.write(int) @3: comment-added\n",
                         self.drift())

    def test_an_untracked_file_is_reported_against_the_working_tree(self):
        self.write("Writer.java", "class Writer {\n  /** Writes count bytes. */\n  int write(int count) {\n    return count;\n  }\n}\n")
        self.assertEqual("== Writer.java\n  Writer @1: code-changed, no-comment\n  Writer.write(int) @3: comment-added\n",
                         self.drift())


if __name__ == "__main__":
    unittest.main()
