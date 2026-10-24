"""new-dossier.sh against a throwaway repository: the reviewed repository controls everything under .review, so the
script writes only into directories it created and refuses a path the repository could point elsewhere."""
import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "agent-packages", "deep-review", ".apm", "skills",
                      "deep-review", "scripts", "new-dossier.sh")


class NewDossierTest(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = os.path.join(self.tmp, "repo")
        self.outside = os.path.join(self.tmp, "outside")
        os.mkdir(self.repo)
        os.mkdir(self.outside)

    def new_dossier(self, *args):
        return subprocess.run(["bash", os.path.abspath(SCRIPT), self.repo, *args], capture_output=True, text=True)

    def test_creates_the_dossier_under_review_and_prints_its_path(self):
        done = self.new_dossier("audit")
        self.assertEqual(0, done.returncode, done.stderr)
        dossier = done.stdout.strip()
        self.assertEqual(os.path.join(self.repo, ".review"), os.path.dirname(dossier))
        self.assertEqual(["audit", "findings.jsonl", "issues", "prompts", "reports", "work"], sorted(os.listdir(dossier)))
        with open(os.path.join(self.repo, ".review", ".gitignore")) as f:
            self.assertEqual("*\n", f.read())

    def test_refuses_a_review_directory_that_is_a_symbolic_link(self):
        os.symlink(self.outside, os.path.join(self.repo, ".review"))
        done = self.new_dossier()
        self.assertEqual(1, done.returncode)
        self.assertIn("is a symbolic link", done.stderr)
        self.assertEqual([], os.listdir(self.outside))

    def test_refuses_a_label_that_leaves_review(self):
        done = self.new_dossier("../../outside/x")
        self.assertEqual(1, done.returncode)
        self.assertEqual([], os.listdir(self.outside))

    def test_refuses_a_label_with_a_slash_after_a_letter(self):
        done = self.new_dossier("a/../../../outside/x")
        self.assertEqual(1, done.returncode)
        self.assertIn("letters, digits", done.stderr)
        self.assertEqual([], os.listdir(self.outside))

    def test_skips_a_dossier_name_the_repository_planted_as_a_link(self):
        os.mkdir(os.path.join(self.repo, ".review"))
        planted = os.path.join(self.repo, ".review", subprocess.check_output(["date", "+%Y-%m-%d"], text=True).strip())
        os.symlink(os.path.join(self.outside, "d"), planted)
        done = self.new_dossier()
        self.assertEqual(planted + "-2", done.stdout.strip(), done.stderr)
        self.assertEqual([], os.listdir(self.outside))

    def test_leaves_a_gitignore_link_alone(self):
        os.mkdir(os.path.join(self.repo, ".review"))
        os.symlink(os.path.join(self.outside, "ignored"), os.path.join(self.repo, ".review", ".gitignore"))
        done = self.new_dossier()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertEqual([], os.listdir(self.outside))


if __name__ == "__main__":
    unittest.main()
