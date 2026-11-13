"""extract-comments.py on a change committed to a scratch repository: which doc comments it selects through sb, and
what it prints where sb cannot outline a file or is not there."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "adversarial-code-review", ".apm",
                      "skills", "adversarial-code-review", "scripts", "extract-comments.py")

EXAMPLE_JAVA = "/** Says hello. */\nclass Example {}\n"
EXAMPLE_REPORT = "### lines 1-1: Example\n```java\n    1  /** Says hello. */\n    2  class Example {}\n```\n\n"


class ExtractCommentsTest(unittest.TestCase):
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
        """Commit files, a mapping of path to str or bytes content, on top of the base commit."""
        for path, content in files.items():
            full = os.path.join(self.repo, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as fh:
                fh.write(content.encode("utf-8") if isinstance(content, str) else content)
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "head")

    def rebase_on_head(self, files):
        """Commit files as the new base, so the next commit is a change to them."""
        self.commit(files)
        self.base = self.git("rev-parse", "HEAD").strip()

    def run_script(self, env=None):
        """Run the script; its output is decoded without newline translation, so a `\\r` in a path survives."""
        result = subprocess.run([sys.executable, SCRIPT, "--diff-base", self.base, "--repo", self.repo],
                                capture_output=True, env=env)
        return subprocess.CompletedProcess(result.args, result.returncode, result.stdout.decode("utf-8"),
                                           result.stderr.decode("utf-8"))

    def path_with(self, sb_script=None):
        """Return an environment whose PATH holds git and, where sb_script is given, an `sb` that runs it."""
        bin_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bin_dir)
        os.symlink(shutil.which("git"), os.path.join(bin_dir, "git"))
        if sb_script is not None:
            sb = os.path.join(bin_dir, "sb")
            with open(sb, "w") as fh:
                fh.write("#!/bin/sh\n" + sb_script)
            os.chmod(sb, 0o755)
        return dict(os.environ, PATH=bin_dir)


@unittest.skipUnless(shutil.which("sb"), "sb (ast-bro) is not installed")
class SelectionTest(ExtractCommentsTest):
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

    def test_a_doc_comment_is_selected_only_when_the_change_touches_it(self):
        self.rebase_on_head({"b/Retry.java": "class Retry {\n"
                                             "  /** Whether to retry. */\n"
                                             "  boolean retry(int n) {\n"
                                             "    return n < 3;\n"
                                             "  }\n"
                                             "\n"
                                             "  /** Delay in ms. */\n"
                                             "  long delay(int n) {\n"
                                             "    return 100L * n;\n"
                                             "  }\n"
                                             "}\n"})
        self.commit({"b/Retry.java": "class Retry {\n"
                                     "  /** Whether to retry. */\n"
                                     "  boolean retry(int n) {\n"
                                     "    return n < 3 && n >= 0;\n"
                                     "  }\n"
                                     "\n"
                                     "  /** Delay in ms, doubling. */\n"
                                     "  long delay(int n) {\n"
                                     "    return 100L << n;\n"
                                     "  }\n"
                                     "}\n"})
        result = self.run_script()
        report = ("## b/Retry.java\n\n### lines 7-7: Retry.delay\n```java\n    7    /** Delay in ms, doubling. */\n"
                  "    8    long delay(int n) {\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_comment_that_only_lost_a_line_is_read(self):
        self.rebase_on_head({"b/Example.java": "class Example {\n  /**\n   * Locks.\n"
                                               "   * The caller must hold the lock.\n   */\n  void run() {}\n}\n"})
        self.commit({"b/Example.java": "class Example {\n  /**\n   * Locks.\n   */\n  void run() {}\n}\n"})
        result = self.run_script()
        report = ("## b/Example.java\n\n### lines 2-4: Example.run\n```java\n    2    /**\n    3     * Locks.\n"
                  "    4     */\n    5    void run() {}\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_deletion_between_code_lines_selects_no_comment(self):
        self.rebase_on_head({"b/Example.java": "/** Says hello. */\nclass Example {\n  int a;\n  int b;\n}\n"})
        self.commit({"b/Example.java": "/** Says hello. */\nclass Example {\n  int a;\n}\n"})
        result = self.run_script()
        self.assertEqual((0, "", ""), (result.returncode, result.stdout, result.stderr))

    def test_an_annotated_declaration_is_shown_through_the_line_that_names_it(self):
        self.commit({"b/Example.java": "class Example {\n  /** Runs. */\n  @Override\n  public void run() {}\n}\n"})
        result = self.run_script()
        report = ("## b/Example.java\n\n### lines 2-2: Example.run\n```java\n    2    /** Runs. */\n"
                  "    3    @Override\n    4    public void run() {}\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_python_docstring_follows_its_def_past_a_decorator_that_names_it(self):
        self.commit({"m.py": "@register(\"f\")\ndef f(x):\n    \"\"\"Doubles x.\n\n    Pure.\n    \"\"\"\n"
                             "    return 2 * x\n"})
        result = self.run_script()
        report = ("## m.py\n\n### lines 3-6: f\n```python\n    1  @register(\"f\")\n    2  def f(x):\n"
                  "    3      \"\"\"Doubles x.\n    4  \n    5      Pure.\n    6      \"\"\"\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_python_docstring_is_selected_only_when_the_change_touches_it(self):
        self.rebase_on_head({"a.py": "def f(x):\n    \"\"\"Doubles x.\"\"\"\n    return 2 * x\n",
                             "b.py": "def g(x):\n    \"\"\"Halves x.\n\n    Rounds down.\n    \"\"\"\n"
                                     "    return x // 2\n"})
        self.commit({"a.py": "def f(x):\n    \"\"\"Doubles x.\"\"\"\n    return x + x\n",
                     "b.py": "def g(x):\n    \"\"\"Halves x.\n    \"\"\"\n    return x // 2\n"})
        result = self.run_script()
        report = ("## b.py\n\n### lines 2-3: g\n```python\n    1  def g(x):\n    2      \"\"\"Halves x.\n"
                  "    3      \"\"\"\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_submodule_comes_as_its_diff_and_the_files_beside_it_are_read(self):
        self.commit({"b/Example.java": EXAMPLE_JAVA})
        # A submodule's commit lives in its own repository, not in this one.
        self.git("update-index", "--add", "--cacheinfo", "160000,0123456789abcdef0123456789abcdef01234567,sub")
        self.git("commit", "-q", "-m", "submodule")
        result = self.run_script()
        rest = ("## sub: sb found no declaration in it, so here is its diff\n\n```diff\n"
                f"{self.git('diff', self.base + '...HEAD', '--', 'sub')}```\n\n")
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT + rest, ""),
                         (result.returncode, result.stdout, result.stderr))

    def test_a_file_re_encoded_from_latin_1_is_read(self):
        self.rebase_on_head({"b/Example.java": "/** caf\xe9 */\nclass Example {}\n".encode("latin-1")})
        self.commit({"b/Example.java": "/** caf\xe9 */\nclass Example {}\n"})
        result = self.run_script()
        report = ("## b/Example.java\n\n### lines 1-1: Example\n```java\n    1  /** caf\xe9 */\n"
                  "    2  class Example {}\n```\n\n")
        self.assertEqual((0, report, ""), (result.returncode, result.stdout, result.stderr))

    def test_a_file_sb_does_not_outline_comes_as_its_diff_after_the_others(self):
        self.commit({"a.png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", "b/Example.java": EXAMPLE_JAVA,
                     "c.yaml": "# Port.\nport: 1\n"})
        result = self.run_script()
        rest = "".join(f"## {p}: sb found no declaration in it, so here is its diff\n\n```diff\n"
                       f"{self.git('diff', self.base + '...HEAD', '--', p)}```\n\n" for p in ("a.png", "c.yaml"))
        self.assertEqual((0, "## b/Example.java\n\n" + EXAMPLE_REPORT + rest, ""),
                         (result.returncode, result.stdout, result.stderr))


class FallbackTest(ExtractCommentsTest):
    def test_without_sb_the_whole_diff_is_printed(self):
        self.commit({"b/Example.java": EXAMPLE_JAVA})
        result = self.run_script(self.path_with())
        self.assertEqual((0, self.git("diff", self.base + "...HEAD"),
                          "extract-comments: sb is not on PATH; printing the diff instead."
                          " sb is the CLI of ast-bro: https://github.com/aeroxy/ast-bro\n"),
                         (result.returncode, result.stdout, result.stderr))

    def test_when_sb_fails_the_whole_diff_is_printed_with_its_reason(self):
        self.commit({"b/Example.java": EXAMPLE_JAVA})
        result = self.run_script(self.path_with("echo 'error: index is locked' >&2\nexit 3\n"))
        self.assertEqual((0, self.git("diff", self.base + "...HEAD"),
                          "extract-comments: sb map exited with 3: error: index is locked;"
                          " printing the diff instead\n"),
                         (result.returncode, result.stdout, result.stderr))


if __name__ == "__main__":
    unittest.main()
