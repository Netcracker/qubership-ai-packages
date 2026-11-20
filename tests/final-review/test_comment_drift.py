"""comment-drift.py against a throwaway git repository: every tag it prints, overloads and same-named members of two
types kept apart, each of the five extensions it accepts, a local that belongs to its function, untracked files, a non-ASCII
path, and a run from a subdirectory. With --history: the three-commit threshold, the test source sets left out, renames
followed through commits, merges, and the uncommitted step, a path a rename freed starting a history of its own, and an
untracked path that looks like pathspec magic."""
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

    def git(self, *args, env=None):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True,
                       env={**os.environ, **env} if env else None)

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


    # ------------------------------------------------------------------ --history

    def history(self, *refs):
        return subprocess.run([sys.executable, os.path.abspath(SCRIPT), "--history", *refs], cwd=self.repo,
                              check=True, capture_output=True, encoding="utf-8").stdout

    def commit_edit(self, name, old, new, subject, date=None):
        """Replace old with new in name, which must contain it, and commit the change as subject, at date if given."""
        with open(os.path.join(self.repo, name), encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text, name)
        self.write(name, text.replace(old, new))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", subject,
                 env={"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else None)
        return self.head_label()

    def head_label(self):
        """The label --history prints for the commit at HEAD."""
        return subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=self.repo, check=True,
                              capture_output=True, encoding="utf-8").stdout.strip()

    def test_a_member_three_commits_changed_is_listed_with_their_subjects(self):
        labels = [self.commit_edit("Reader.java", "return count;", "return count + 1;", "Handle a header"),
                  self.commit_edit("Reader.java", "return count + 1;", "return count + 2;", "Handle a trailer"),
                  self.commit_edit("Reader.java", "    return 0;", "    return -1;", "Skip nothing"),
                  self.commit_edit("Reader.java", "return count + 2;", "return count + 3;", "Handle a footer")]
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    %s\n" % (labels[0], labels[1], labels[3]),
                         self.history("HEAD~4"))

    def test_a_member_two_commits_changed_is_left_out(self):
        labels = [self.commit_edit("Reader.java", "return count;", "return count + 1;", "Handle a header"),
                  self.commit_edit("Reader.java", "    return 0;", "    return 1;", "Skip one"),
                  self.commit_edit("Reader.java", "return count + 1;", "return count + 2;", "Handle a trailer"),
                  self.commit_edit("Reader.java", "    return 1;", "    return 2;", "Skip two"),
                  self.commit_edit("Reader.java", "return count + 2;", "return count + 3;", "Handle a footer")]
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    %s\n" % (labels[0], labels[2], labels[4]),
                         self.history("HEAD~5"))

    def test_a_changed_parameter_list_keeps_the_member_count(self):
        labels = [self.commit_edit("Reader.java", "return count;", "return count + 1;", "Handle a header"),
                  self.commit_edit("Reader.java", "int read(int count) {", "int read(int count, int limit) {",
                                   "Take a limit"),
                  self.commit_edit("Reader.java", "return count + 1;", "return limit;", "Stop at the limit")]
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int); Reader.read(int, int))\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~3"))

    def test_a_directory_whose_name_only_contains_test_is_not_a_test_source_set(self):
        os.makedirs(os.path.join(self.repo, "src", "latest"))
        self.write("src/latest/Probe.java", "class Probe {\n  int g() {\n    return 0;\n  }\n}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add a probe")
        labels = [self.commit_edit("src/latest/Probe.java", "return %d;" % i, "return %d;" % (i + 1),
                                   "Probe %d" % i) for i in range(3)]
        self.assertEqual("== src/latest/Probe.java\n  g: 3 commits (Probe.g())\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~3"))

    def test_a_file_added_at_a_path_a_rename_freed_has_a_history_of_its_own(self):
        self.git("mv", "Reader.java", "FileReader.java")
        self.git("commit", "-q", "-m", "Rename the reader")
        self.write("Reader.java", "interface Reader {\n  int read(int count);\n}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Extract the interface")
        labels = [self.commit_edit("FileReader.java", "return count%s;" % (" + %d" % i if i else ""),
                                   "return count + %d;" % (i + 1), "Handle %d" % i) for i in range(3)]
        self.assertEqual("== FileReader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~5"))

    def test_a_file_renamed_back_keeps_its_count_under_its_first_path(self):
        labels = [self.commit_edit("Reader.java", "return count;", "return count + 1;", "Handle a header")]
        self.git("mv", "Reader.java", "FileReader.java")
        self.git("commit", "-q", "-m", "Rename the reader")
        labels.append(self.commit_edit("FileReader.java", "return count + 1;", "return count + 2;", "Handle a trailer"))
        self.git("mv", "FileReader.java", "Reader.java")
        self.git("commit", "-q", "-m", "Rename the reader back")
        labels.append(self.commit_edit("Reader.java", "return count + 2;", "return count + 3;", "Handle a footer"))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~5"))

    def test_a_deleted_file_is_not_reported_under_a_path_a_new_file_took(self):
        for i in range(3):
            self.commit_edit("Reader.java", "return count%s;" % (" + %d" % i if i else ""),
                             "return count + %d;" % (i + 1), "Handle %d" % i)
        self.git("mv", "Reader.java", "FileReader.java")
        self.git("commit", "-q", "-m", "Rename the reader")
        self.write("Reader.java", "class Reader {\n  int read() {\n    return 0;\n  }\n}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add a new reader")
        added = self.head_label()
        self.git("rm", "-q", "FileReader.java")
        self.git("commit", "-q", "-m", "Drop the file reader")
        labels = [self.commit_edit("Reader.java", "return %d;" % i, "return %d;" % (i + 1), "Read %d" % i)
                  for i in range(3)]
        self.assertEqual("== Reader.java\n  read: 4 commits (Reader.read())\n"
                         "    %s\n    %s\n    %s\n    %s\n" % (added, *labels),
                         self.history("HEAD~9"))

    def test_a_file_renamed_on_a_merged_branch_is_reported_under_its_path_at_the_head(self):
        self.write("Reader.java", "class Reader {\n  int read() {\n    int a = 0;\n\n\n    int b = 0;\n\n\n"
                                  "    int c = 0;\n    return a + b + c;\n  }\n}\n")
        self.git("commit", "-q", "-am", "Spread the reader out")
        self.git("checkout", "-q", "-b", "side")
        self.git("mv", "Reader.java", "Renamed.java")
        side = [self.commit_edit("Renamed.java", "int a = 0;", "int a = 1;", "Rename and set a",
                                 "2026-01-01T00:00:01Z"),
                self.commit_edit("Renamed.java", "int b = 0;", "int b = 1;", "Set b", "2026-01-01T00:00:02Z")]
        self.git("checkout", "-q", "-")
        main = self.commit_edit("Reader.java", "int c = 0;", "int c = 1;", "Set c", "2026-01-01T00:00:03Z")
        self.git("merge", "-q", "--no-edit", "side")
        output = self.history("HEAD~1~1", "HEAD").splitlines()
        self.assertEqual((["== Renamed.java", "  read: 3 commits (Reader.read())"],
                          sorted("    " + label for label in side + [main])),
                         (output[:2], sorted(output[2:])), "(file and member lines, commit lines)")

    def rename_back_uncommitted(self, rename):
        """Commit two edits of read and a rename of Reader.java to Reader.java.disabled, then call rename(old, new)
        to bring it back and edit read once more without committing; return the two commit labels."""
        labels = [self.commit_edit("Reader.java", "return count%s;" % (" + %d" % i if i else ""),
                                   "return count + %d;" % (i + 1), "Handle %d" % i) for i in range(2)]
        self.git("mv", "Reader.java", "Reader.java.disabled")
        self.git("commit", "-q", "-m", "Disable the reader")
        rename("Reader.java.disabled", "Reader.java")
        self.write("Reader.java", BASE.replace("return count;", "return count + 3;"))
        return labels

    def test_an_uncommitted_rename_back_from_another_extension_keeps_the_count(self):
        labels = self.rename_back_uncommitted(
            lambda old, new: os.rename(os.path.join(self.repo, old), os.path.join(self.repo, new)))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    (uncommitted)\n" % tuple(labels),
                         self.history("HEAD~3"))

    def test_a_staged_rename_back_from_another_extension_keeps_the_count(self):
        labels = self.rename_back_uncommitted(lambda old, new: self.git("mv", old, new))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    (uncommitted)\n" % tuple(labels),
                         self.history("HEAD~3"))

    def test_more_untracked_sources_than_one_command_line_holds_are_listed(self):
        # 6000 paths of about 400 characters exceed the 1 MiB argument limit of macOS and the 2 MiB of Linux.
        labels = [self.commit_edit("Reader.java", "return count%s;" % (" + %d" % i if i else ""),
                                   "return count + %d;" % (i + 1), "Handle %d" % i) for i in range(2)]
        deep = os.path.join(self.repo, "g" * 200)
        os.makedirs(deep)
        for i in range(6000):
            open(os.path.join(deep, "%05d%s.java" % (i, "x" * 190)), "w").close()
        self.write("Reader.java", BASE.replace("return count;", "return count + 3;"))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    (uncommitted)\n" % tuple(labels),
                         self.history("HEAD~2"))

    def test_a_rename_back_starts_a_new_history_when_the_deleted_paths_exceed_the_budget(self):
        # 150 paths of about 200 characters take more than the 24000 characters the script allows them.
        names = ["%03d%s.txt" % (i, "y" * 197) for i in range(150)]
        for name in names:
            self.write(name, "")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add notes")
        self.rename_back_uncommitted(
            lambda old, new: os.rename(os.path.join(self.repo, old), os.path.join(self.repo, new)))
        for name in names:
            os.remove(os.path.join(self.repo, name))
        self.assertEqual("", self.history("HEAD~3"),
                         "a rename that git does not pair counts the old file's two commits under no path")

    def test_a_missing_index_is_rebuilt_from_head_for_the_uncommitted_step(self):
        # 150 tracked paths of about 200 characters stay on disk: an empty index would list each as deleted and
        # exceed the budget for deleted paths, so the rename back below would go unpaired.
        for i in range(150):
            self.write("%03d%s.txt" % (i, "y" * 197), "")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add notes")
        labels = self.rename_back_uncommitted(
            lambda old, new: os.rename(os.path.join(self.repo, old), os.path.join(self.repo, new)))
        os.remove(os.path.join(self.repo, ".git", "index"))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    (uncommitted)\n" % tuple(labels),
                         self.history("HEAD~3"))

    def test_the_uncommitted_step_neither_stores_nor_filters_a_file_that_is_not_a_jvm_source(self):
        self.write(".gitattributes", "*.txt filter=broken\n")
        self.write("notes.txt", "draft\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add notes")
        labels = [self.commit_edit("Reader.java", "return count%s;" % (" + %d" % i if i else ""),
                                   "return count + %d;" % (i + 1), "Handle %d" % i) for i in range(2)]
        self.git("config", "filter.broken.clean", "false")
        self.git("config", "filter.broken.required", "true")
        self.write("notes.txt", "edited\n")
        self.write("credentials.local", "secret\n")
        self.write("Reader.java", BASE.replace("return count;", "return count + 3;"))
        output = self.history("HEAD~2")
        blob = subprocess.run(["git", "hash-object", "credentials.local"], cwd=self.repo, check=True,
                              capture_output=True, encoding="utf-8").stdout.strip()
        stored = subprocess.run(["git", "cat-file", "-e", blob], cwd=self.repo, capture_output=True).returncode == 0
        self.assertEqual(("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                          "    %s\n    %s\n    (uncommitted)\n" % tuple(labels), False),
                         (output, stored), "(--history output, untracked credentials.local stored as a blob)")

    def test_the_script_is_executable(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK), "SKILL.md runs %s directly" % SCRIPT)

    def test_a_member_in_a_test_source_set_is_left_out(self):
        os.makedirs(os.path.join(self.repo, "src", "test", "java"))
        self.write("src/test/java/ReaderTest.java", "class ReaderTest {\n  void reads() {\n    int n = 0;\n  }\n}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add a test")
        labels = []
        for i in range(3):
            self.commit_edit("src/test/java/ReaderTest.java", "int n = %d;" % i, "int n = %d;" % (i + 1), "Test %d" % i)
            labels.append(self.commit_edit("Reader.java", "return count%s;" % (" + %d" % i if i else ""),
                                           "return count + %d;" % (i + 1), "Handle %d" % i))
        self.assertEqual("== Reader.java\n  read: 3 commits (Reader.read(int))\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~6"))

    def test_a_file_moved_out_of_a_test_source_set_keeps_its_count(self):
        os.makedirs(os.path.join(self.repo, "src", "integrationTest"))
        self.write("src/integrationTest/Probe.java", "class Probe {\n  int g() {\n    return 0;\n  }\n}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Add a probe")
        labels = [self.commit_edit("src/integrationTest/Probe.java", "return %d;" % i, "return %d;" % (i + 1),
                                   "Probe %d" % i) for i in range(3)]
        os.makedirs(os.path.join(self.repo, "src", "main", "java"))
        self.git("mv", "src/integrationTest/Probe.java", "src/main/java/Probe.java")
        self.git("commit", "-q", "-m", "Move the probe to main")
        self.assertEqual("== src/main/java/Probe.java\n  g: 3 commits (Probe.g())\n"
                         "    %s\n    %s\n    %s\n" % tuple(labels),
                         self.history("HEAD~4", "HEAD"))

    def rename_uncommitted(self, new):
        """Commit two edits of read, then rename Reader.java to new and edit read once more without committing;
        return the two commit labels."""
        labels = [self.commit_edit("Reader.java", "return count;", "return count + 1;", "Handle a header"),
                  self.commit_edit("Reader.java", "return count + 1;", "return count + 2;", "Handle a trailer")]
        os.rename(os.path.join(self.repo, "Reader.java"), os.path.join(self.repo, new))
        self.write(new, BASE.replace("return count;", "return count + 3;"))
        return labels

    def test_an_uncommitted_rename_to_an_untracked_path_counts_as_one_more_step(self):
        labels = self.rename_uncommitted("Renamed.java")
        output = self.history("HEAD~2")
        staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=self.repo, check=True,
                                capture_output=True, encoding="utf-8").stdout
        self.assertEqual(("== Renamed.java\n  read: 3 commits (Reader.read(int))\n"
                          "    %s\n    %s\n    (uncommitted)\n" % tuple(labels), ""),
                         (output, staged), "(--history output, files staged in the real index)")

    @unittest.skipIf(os.name == "nt", "Windows forbids a colon in a file name")
    def test_an_untracked_path_that_looks_like_pathspec_magic_is_read_as_a_path(self):
        labels = self.rename_uncommitted("Renamed.java")
        current = "Renamed.java"
        for name in (":(exclude)*.java", ":(top)Renamed.java"):
            with self.subTest(name):
                os.rename(os.path.join(self.repo, current), os.path.join(self.repo, name))
                current = name
                self.assertEqual("== %s\n  read: 3 commits (Reader.read(int))\n"
                                 "    %s\n    %s\n    (uncommitted)\n" % (name, *labels),
                                 self.history("HEAD~2"))


if __name__ == "__main__":
    unittest.main()
