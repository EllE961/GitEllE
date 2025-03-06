"""
Tests for the 'commit' command.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.commands.add import add
from gitelle.commands.commit import commit, create_commit
from gitelle.core.repository import Repository


class TestCommitCommand(TestCase):
    """Tests for the 'commit' command."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_commit(self):
        """Test the 'commit' command."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file to the index
            self.runner.invoke(add, ["test.txt"])
            
            # Commit the file
            result = self.runner.invoke(commit, ["-m", "Test commit"])
            self.assertEqual(result.exit_code, 0)
            
            # Check that the commit was created
            repo = Repository.find()
            head_target = repo.head.get_resolved_target()
            self.assertIsNotNone(head_target)
            
            # Get the commit object
            commit_obj = repo.get_object(head_target)
            self.assertEqual(commit_obj.message, "Test commit")
    
    def test_commit_no_message(self):
        """Test the 'commit' command without a message."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file to the index
            self.runner.invoke(add, ["test.txt"])
            
            # Try to commit without a message
            result = self.runner.invoke(commit)
            self.assertEqual(result.exit_code, 1)
            self.assertIn("empty commit message", result.output.lower())
    
    def test_commit_empty_index(self):
        """Test the 'commit' command with an empty index."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Try to commit with an empty index
            result = self.runner.invoke(commit, ["-m", "Test commit"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("nothing to commit", result.output.lower())
    
    def test_commit_author(self):
        """Test the 'commit' command with a custom author."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file to the index
            self.runner.invoke(add, ["test.txt"])
            
            # Commit with a custom author
            author = "Test Author <test@example.com>"
            result = self.runner.invoke(commit, ["-m", "Test commit", "--author", author])
            self.assertEqual(result.exit_code, 0)
            
            # Check that the commit has the correct author
            repo = Repository.find()
            head_target = repo.head.get_resolved_target()
            commit_obj = repo.get_object(head_target)
            self.assertIn("Test Author", commit_obj.author)
            self.assertIn("test@example.com", commit_obj.author)
    
    def test_commit_updates_branch(self):
        """Test that commit updates the current branch."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file to the index
            self.runner.invoke(add, ["test.txt"])
            
            # Get the initial state
            repo_before = Repository.find()
            main_before = repo_before.get_branch("main")
            main_target_before = main_before.target
            
            # Commit the file
            self.runner.invoke(commit, ["-m", "Test commit"])
            
            # Get the final state
            repo_after = Repository.find()
            main_after = repo_after.get_branch("main")
            main_target_after = main_after.target
            
            # Check that the branch was updated
            self.assertNotEqual(main_target_before, main_target_after)
    
    def test_create_commit_function(self):
        """Test the create_commit function."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file to the index
            repo = Repository.find()
            repo.index.add([Path("test.txt")])
            repo.index.write()
            
            # Create a commit
            commit_id = create_commit(repo, "Test commit")
            
            # Check that the commit was created
            commit_obj = repo.get_object(commit_id)
            self.assertEqual(commit_obj.message, "Test commit")
            
            # Check that HEAD points to the commit
            head_target = repo.head.get_resolved_target()
            self.assertEqual(head_target, commit_id)