"""
Tests for the 'branch' command.
"""
import shutil
import tempfile
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.commands.add import add
from gitelle.commands.commit import commit
from gitelle.commands.branch import branch
from gitelle.core.repository import Repository


class TestBranchCommand(TestCase):
    """Tests for the 'branch' command."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_branch_list(self):
        """Test listing branches."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # List branches
            result = self.runner.invoke(branch)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("main", result.output)
            self.assertIn("*", result.output)  # Current branch indicator

    def test_branch_create(self):
        """Test creating a branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # Create a branch
            result = self.runner.invoke(branch, ["test-branch"])
            self.assertEqual(result.exit_code, 0)

            # Check that the branch was created
            repo = Repository.find()
            branches = repo.get_branches()
            self.assertIn("test-branch", branches)

    def test_branch_create_no_commits(self):
        """Test creating a branch when there are no commits."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Try to create a branch
            result = self.runner.invoke(branch, ["test-branch"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("error", result.output.lower())

    def test_branch_delete(self):
        """Test deleting a branch."""
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

            # Delete the branch
            result = self.runner.invoke(branch, ["-d", "test-branch"])
            self.assertEqual(result.exit_code, 0)

            # Check that the branch was deleted
            repo = Repository.find()
            branches = repo.get_branches()
            self.assertNotIn("test-branch", branches)

    def test_branch_delete_current(self):
        """Test deleting the current branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # Try to delete the current branch
            result = self.runner.invoke(branch, ["-d", "main"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("error", result.output.lower())

    def test_branch_verbose(self):
        """Test branch listing with verbose output."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)

            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])

            # List branches with verbose output
            result = self.runner.invoke(branch, ["-v"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("main", result.output)
            self.assertIn("Initial commit", result.output)
