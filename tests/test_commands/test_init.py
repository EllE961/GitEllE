"""
Tests for the 'init' command.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.core.repository import Repository


class TestInitCommand(TestCase):
    """Tests for the 'init' command."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_init_command(self):
        """Test the 'init' command."""
        with self.runner.isolated_filesystem():
            # Run the command
            result = self.runner.invoke(init)
            self.assertEqual(result.exit_code, 0)

            # Check that a repository was created
            cwd = os.getcwd()
            repo_dir = Path(cwd) / Repository.GITELLE_DIR
            self.assertTrue(repo_dir.exists())

    def test_init_command_with_path(self):
        """Test the 'init' command with a path argument."""
        with self.runner.isolated_filesystem():
            # Create a subdirectory
            os.makedirs("subdir")

            # Run the command
            result = self.runner.invoke(init, ["subdir"])
            self.assertEqual(result.exit_code, 0)

            # Check that a repository was created in the subdirectory
            cwd = os.getcwd()
            repo_dir = Path(cwd) / "subdir" / Repository.GITELLE_DIR
            self.assertTrue(repo_dir.exists())

    def test_init_command_existing_repo(self):
        """Test the 'init' command when a repository already exists."""
        with self.runner.isolated_filesystem():
            # Create a repository
            result = self.runner.invoke(init)
            self.assertEqual(result.exit_code, 0)

            # Try to create another repository in the same directory
            result = self.runner.invoke(init)
            self.assertEqual(result.exit_code, 1)
            self.assertIn("already exists", result.output)
