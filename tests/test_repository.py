"""
Tests for the Repository class.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

import pytest

from gitelle.core.repository import Repository


class TestRepository(TestCase):
    """Tests for the Repository class."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test repository initialization."""
        # Initialize a repository
        repo = Repository.init(self.repo_path)
        
        # Check that the repository was created correctly
        gitelle_dir = self.repo_path / Repository.GITELLE_DIR
        self.assertTrue(gitelle_dir.exists())
        self.assertTrue((gitelle_dir / "HEAD").exists())
        self.assertTrue((gitelle_dir / "objects").exists())
        self.assertTrue((gitelle_dir / "refs" / "heads").exists())
        self.assertTrue((gitelle_dir / "refs" / "tags").exists())
        
        # Check that HEAD points to main
        with open(gitelle_dir / "HEAD", "r") as f:
            head_content = f.read().strip()
        self.assertEqual(head_content, "ref: refs/heads/main")
    
    def test_find(self):
        """Test repository finding."""
        # Initialize a repository
        Repository.init(self.repo_path)
        
        # Create a subdirectory
        subdir = self.repo_path / "subdir" / "subsubdir"
        subdir.mkdir(parents=True)
        
        # Find the repository from the subdirectory
        repo = Repository.find(subdir)
        self.assertIsNotNone(repo)
        self.assertEqual(repo.path, self.repo_path.absolute())
        
        # Try to find a repository in a different directory
        other_dir = Path(self.temp_dir) / "not_a_repo"
        other_dir.mkdir()
        repo = Repository.find(other_dir)
        self.assertIsNone(repo)


@pytest.fixture
def temp_repo():
    """Fixture to create a temporary repository."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test_repo"
    repo_path.mkdir()
    repo = Repository.init(repo_path)
    
    yield repo
    
    shutil.rmtree(temp_dir)


def test_repo_index(temp_repo):
    """Test repository index."""
    # Create a file
    test_file = temp_repo.path / "test.txt"
    with open(test_file, "w") as f:
        f.write("Test content")
    
    # Add the file to the index
    temp_repo.index.add([Path("test.txt")])
    
    # Check that the file was added
    assert "test.txt" in temp_repo.index.entries
    
    # Write the index
    temp_repo.index.write()
    
    # Re-read the index
    new_repo = Repository(temp_repo.path)
    assert "test.txt" in new_repo.index.entries