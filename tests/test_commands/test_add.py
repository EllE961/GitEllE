"""
Tests for the 'add' command.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from click.testing import CliRunner

from gitelle.commands.init import init
from gitelle.commands.add import add
from gitelle.core.repository import Repository


class TestAddCommand(TestCase):
    """Tests for the 'add' command."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_command(self):
        """Test the 'add' command."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a file
            with open("test.txt", "w") as f:
                f.write("Test content")
            
            # Add the file
            result = self.runner.invoke(add, ["test.txt"])
            self.assertEqual(result.exit_code, 0)
            
            # Check that the file was added to the index
            repo = Repository.find()
            self.assertIn("test.txt", repo.index.entries)
    
    def test_add_command_multiple_files(self):
        """Test the 'add' command with multiple files."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create files
            with open("test1.txt", "w") as f:
                f.write("Test content 1")
            with open("test2.txt", "w") as f:
                f.write("Test content 2")
            
            # Add the files
            result = self.runner.invoke(add, ["test1.txt", "test2.txt"])
            self.assertEqual(result.exit_code, 0)
            
            # Check that the files were added to the index
            repo = Repository.find()
            self.assertIn("test1.txt", repo.index.entries)
            self.assertIn("test2.txt", repo.index.entries)
    
    def test_add_command_directory(self):
        """Test the 'add' command with a directory."""
        with self.runner.isolated_filesystem():
            # Initialize a repository
            self.runner.invoke(init)
            
            # Create a directory with files
            os.makedirs("testdir")
            with open("testdir/test1.txt", "w") as f:
                f.write("Test content 1")
            with open("testdir/test2.txt", "w") as f:
                f.write("Test content 2")
            
            # Add the directory
            result = self.runner.invoke(add, ["testdir"])
            self.assertEqual(result.exit_code, 0)
            
            # Check that the files were added to the index
            repo = Repository.find()
            self.assertIn("testdir/test1.txt", repo.index.entries)
            self.assertIn("testdir/test2.txt", repo.index.entries)