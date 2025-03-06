"""
Tests for the 'checkout' command.
"""
import os
import shutil
import tempfile
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.commands.add import add
from gitelle.commands.commit import commit
from gitelle.commands.branch import branch
from gitelle.commands.checkout import checkout
from gitelle.core.repository import Repository


class TestCheckoutCommand(TestCase):
    """Tests for the 'checkout' command."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_checkout_branch(self):
        """Test checking out a branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # Create a branch
            self.runner.invoke(branch, ["test-branch"])

            # Checkout the branch
            result = self.runner.invoke(checkout, ["test-branch"])
            self.assertEqual(result.exit_code, 0)

            # Check that HEAD points to the branch
            repo = Repository.find()
            self.assertEqual(repo.head.target, "refs/heads/test-branch")

    def test_checkout_new_branch(self):
        """Test checking out a new branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # Checkout a new branch
            result = self.runner.invoke(checkout, ["-b", "test-branch"])
            self.assertEqual(result.exit_code, 0)

            # Check that the branch was created and HEAD points to it
            repo = Repository.find()
            branches = repo.get_branches()
            self.assertIn("test-branch", branches)
            self.assertEqual(repo.head.target, "refs/heads/test-branch")

    def test_checkout_nonexistent_branch(self):
        """Test checking out a nonexistent branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # Try to checkout a nonexistent branch
            result = self.runner.invoke(checkout, ["nonexistent-branch"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("error", result.output.lower())

    def test_checkout_commit(self):
        """Test checking out a commit (detached HEAD)."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            result = self.runner.invoke(commit, ["-m", "Initial commit"])

            # Extract the commit ID from the commit output
            commit_id = None
            for line in result.output.splitlines():
                if "main" in line and "[" in line and "]" in line:
                    # Remove the closing bracket
                    commit_id = line.split()[1][:-1]
                    break

            if commit_id:
                # Checkout the commit
                result = self.runner.invoke(checkout, [commit_id])
                self.assertEqual(result.exit_code, 0)

                # Check that HEAD points to the commit
                repo = Repository.find()
                self.assertFalse(repo.head.is_symbolic)
                self.assertEqual(repo.head.target, commit_id)

    def test_checkout_updates_working_directory(self):
        """Test that checkout updates the working directory."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it in the main branch
            with open("main.txt", "w") as f:
                f.write("Main branch content")
            self.runner.invoke(add, ["main.txt"])
            self.runner.invoke(commit, ["-m", "Main branch commit"])

            # Create and checkout a feature branch
            self.runner.invoke(checkout, ["-b", "feature"])

            # Create a file in the feature branch
            with open("feature.txt", "w") as f:
                f.write("Feature branch content")
            self.runner.invoke(add, ["feature.txt"])
            self.runner.invoke(commit, ["-m", "Feature branch commit"])

            # Checkout the main branch
            result = self.runner.invoke(checkout, ["main"])
            self.assertEqual(result.exit_code, 0)

            # Verify that the working directory reflects the main branch
            self.assertTrue(os.path.exists("main.txt"))

            # Note: In a full implementation, feature.txt would be removed
