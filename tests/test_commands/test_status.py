"""
Tests for the 'status' command.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.commands.add import add
from gitelle.commands.commit import commit
from gitelle.commands.status import status, get_status
from gitelle.core.repository import Repository


class TestStatusCommand(TestCase):
    """Tests for the 'status' command."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_status_clean(self):
        """Test status with a clean repository."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file and commit it
            with open("test.txt", "w") as f:
                f.write("Test content")
            self.runner.invoke(add, ["test.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])
            
            # Check status
            result = self.runner.invoke(status)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("nothing to commit", result.output.lower())
            self.assertIn("working tree clean", result.output.lower())
    
    def test_status_untracked(self):
        """Test status with untracked files."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create an untracked file
            with open("untracked.txt", "w") as f:
                f.write("Untracked content")
            
            # Check status
            result = self.runner.invoke(status)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("untracked files", result.output.lower())
            self.assertIn("untracked.txt", result.output)
    
    def test_status_staged(self):
        """Test status with staged files."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create and stage a file
            with open("staged.txt", "w") as f:
                f.write("Staged content")
            self.runner.invoke(add, ["staged.txt"])
            
            # Check status
            result = self.runner.invoke(status)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("changes to be committed", result.output.lower())
            self.assertIn("staged.txt", result.output)
    
    def test_status_modified(self):
        """Test status with modified files."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file and commit it
            with open("modified.txt", "w") as f:
                f.write("Original content")
            self.runner.invoke(add, ["modified.txt"])
            self.runner.invoke(commit, ["-m", "Initial commit"])
            
            # Modify the file
            with open("modified.txt", "w") as f:
                f.write("Modified content")
            
            # Check status
            result = self.runner.invoke(status)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("changes not staged for commit", result.output.lower())
            self.assertIn("modified.txt", result.output)
    
    def test_status_short(self):
        """Test status with short output format."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create various file states
            # Staged file
            with open("staged.txt", "w") as f:
                f.write("Staged content")
            self.runner.invoke(add, ["staged.txt"])
            
            # Untracked file
            with open("untracked.txt", "w") as f:
                f.write("Untracked content")
            
            # Check short status
            result = self.runner.invoke(status, ["--short"])
            self.assertEqual(result.exit_code, 0)
            
            # In short format, each line should start with a status code
            for line in result.output.splitlines():
                if "staged.txt" in line:
                    self.assertTrue(line.startswith("A "))
                if "untracked.txt" in line:
                    self.assertTrue(line.startswith("? "))
    
    def test_get_status_function(self):
        """Test the get_status function."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create various file states
            # Staged file
            with open("staged.txt", "w") as f:
                f.write("Staged content")
            
            # Untracked file
            with open("untracked.txt", "w") as f:
                f.write("Untracked content")
            
            # Add the staged file
            repo = Repository.find()
            repo.index.add([Path("staged.txt")])
            repo.index.write()
            
            # Get status
            staged, unstaged, untracked = get_status(repo)
            
            # Check the results
            self.assertIn("staged.txt", staged)
            self.assertIn("untracked.txt", untracked)