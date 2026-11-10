"""extract-comments.py on a change committed to a scratch repository: the changed-file inventory and the files it cannot
read as text."""
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "adversarial-code-review", ".apm",
                      "skills", "adversarial-code-review", "scripts", "extract-comments.py")

EXAMPLE_JAVA = "/** Says hello. */\nclass Example {}\n"
EXAMPLE_REPORT = "### lines 1-1\n```java\n    1  /** Says hello. */\n    2  class Example {}\n```\n\n"


class ExtractCommentsTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        self.git("commit", "-q", "--allow-empty", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.test", *args],
                              capture_output=True, text=True, check=True).stdout

    def commit(self, files):
        """Commit files, a mapping of path to str or bytes content, on top of the base commit."""
        for path, content in files.items():
            full = os.path.join(self.repo, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as fh:
                fh.write(content.encode("utf-8") if isinstance(content, str) else content)
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "head")

    def run_script(self, *files):
        """Run the script; its output is decoded without newline translation, so a `\\r` in a path survives."""
        result = subprocess.run([sys.executable, SCRIPT, self.repo, self.base, *files], capture_output=True)
        return subprocess.CompletedProcess(result.args, result.returncode, result.stdout.decode("utf-8"),
                                           result.stderr.decode("utf-8"))

    def test_a_changed_path_with_a_space_is_read_whole(self):
        self.commit({"space dir/Example.java": EXAMPLE_JAVA})
        result = self.run_script()
        self.assertEqual((0, "## space dir/Example.java\n\n" + EXAMPLE_REPORT, ""),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_changed_path_with_a_carriage_return_is_read_whole(self):
        self.commit({"cr\rdir/Example.java": EXAMPLE_JAVA})
        result = self.run_script()
        self.assertEqual((0, "## cr\rdir/Example.java\n\n" + EXAMPLE_REPORT, ""),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_file_with_a_byte_order_mark_keeps_its_first_comment(self):
        self.commit({"b/Example.java": b"\xef\xbb\xbf" + EXAMPLE_JAVA.encode("utf-8")})
        result = self.run_script()
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT, ""),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_comment_that_only_lost_a_line_is_read(self):
        self.commit({"b/Example.java": "class Example {\n  /**\n   * Locks.\n   * The caller must hold the lock.\n   */\n"
                                       "  void run() {}\n}\n"})
        self.base = self.git("rev-parse", "HEAD").strip()
        self.commit({"b/Example.java": "class Example {\n  /**\n   * Locks.\n   */\n  void run() {}\n}\n"})
        result = self.run_script()
        report = ("## b/Example.java\n\n### lines 2-4\n```java\n    2    /**\n    3     * Locks.\n    4     */\n"
                  "    5    void run() {}\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_deletion_between_code_lines_selects_no_comment(self):
        self.commit({"b/Example.java": "/** Says hello. */\nclass Example {\n  int a;\n  int b;\n}\n"})
        self.base = self.git("rev-parse", "HEAD").strip()
        self.commit({"b/Example.java": "/** Says hello. */\nclass Example {\n  int a;\n}\n"})
        result = self.run_script()
        self.assertEqual((0, "", ""), (result.returncode, result.stdout, result.stderr))

    def test_a_binary_file_is_skipped_and_the_files_after_it_are_read(self):
        self.commit({"a.png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", "b/Example.java": EXAMPLE_JAVA})
        result = self.run_script()
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT,
                          "extract-comments: skipped a.png: not UTF-8 text\n"),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_utf8_file_with_a_nul_byte_is_skipped(self):
        self.commit({"a.dat": "header\0body\n", "b/Example.java": EXAMPLE_JAVA})
        result = self.run_script()
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT,
                          "extract-comments: skipped a.dat: not UTF-8 text\n"),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_named_file_that_head_does_not_have_is_skipped(self):
        self.commit({"b/Example.java": EXAMPLE_JAVA})
        result = self.run_script("gone.java", "b/Example.java")
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT,
                          "extract-comments: skipped gone.java: not in HEAD\n"),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_file_re_encoded_from_latin_1_is_read(self):
        self.commit({"b/Example.java": "// caf\xe9\nclass Example {}\n".encode("latin-1")})
        self.base = self.git("rev-parse", "HEAD").strip()
        self.commit({"b/Example.java": "// caf\xe9\nclass Example {}\n"})
        result = self.run_script()
        report = "## b/Example.java\n\n### lines 1-1\n```java\n    1  // caf\xe9\n    2  class Example {}\n```\n\n"
        self.assertEqual((0, report, ""),
                         (result.returncode, result.stdout, result.stderr))


if __name__ == "__main__":
    unittest.main()
