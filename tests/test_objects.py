"""
Tests for Git objects (blob, tree, commit).
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from gitelle.core.objects import Blob, Tree, Commit, TreeEntry
from gitelle.core.repository import Repository


class TestBlob(TestCase):
    """Tests for the Blob class."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_blob_serialize_deserialize(self):
        """Test blob serialization and deserialization."""
        # Create a blob
        data = b"Test content"
        blob = Blob(self.repo, data)
        
        # Serialize the blob
        serialized = blob.serialize()
        self.assertEqual(serialized, data)
        
        # Deserialize the blob
        deserialized = Blob.deserialize(self.repo, serialized)
        self.assertEqual(deserialized.data, data)
    
    def test_blob_write_read(self):
        """Test writing and reading a blob."""
        # Create a blob
        data = b"Test content"
        blob = Blob(self.repo, data)
        
        # Write the blob
        blob_id = blob.write()
        
        # Read the blob
        read_blob = Blob.read(self.repo, blob_id)
        self.assertEqual(read_blob.data, data)
    
    def test_blob_from_file(self):
        """Test creating a blob from a file."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        data = b"Test content"
        with open(file_path, "wb") as f:
            f.write(data)
        
        # Create a blob from the file
        blob = Blob.from_file(self.repo, file_path)
        self.assertEqual(blob.data, data)


class TestTree(TestCase):
    """Tests for the Tree class."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_tree_add_entry(self):
        """Test adding an entry to a tree."""
        # Create a tree
        tree = Tree(self.repo)
        
        # Add an entry
        tree.add_entry("100644", "test.txt", "0123456789abcdef0123456789abcdef01234567")
        
        # Check that the entry was added
        self.assertEqual(len(tree.entries), 1)
        self.assertEqual(tree.entries[0].mode, "100644")
        self.assertEqual(tree.entries[0].name, "test.txt")
        self.assertEqual(tree.entries[0].id, "0123456789abcdef0123456789abcdef01234567")
    
    def test_tree_serialize_deserialize(self):
        """Test tree serialization and deserialization."""
        # Create a tree with entries
        tree = Tree(self.repo)
        tree.add_entry("100644", "file1.txt", "0123456789abcdef0123456789abcdef01234567")
        tree.add_entry("100755", "script.sh", "abcdef0123456789abcdef0123456789abcdef01")
        
        # Serialize the tree
        serialized = tree.serialize()
        
        # Deserialize the tree
        deserialized = Tree.deserialize(self.repo, serialized)
        
        # Check that the entries were preserved
        self.assertEqual(len(deserialized.entries), 2)
        self.assertEqual(deserialized.entries[0].mode, "100644")
        self.assertEqual(deserialized.entries[0].name, "file1.txt")
        self.assertEqual(deserialized.entries[0].id, "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(deserialized.entries[1].mode, "100755")
        self.assertEqual(deserialized.entries[1].name, "script.sh")
        self.assertEqual(deserialized.entries[1].id, "abcdef0123456789abcdef0123456789abcdef01")
    
    def test_tree_write_read(self):
        """Test writing and reading a tree."""
        # Create a tree with entries
        tree = Tree(self.repo)
        tree.add_entry("100644", "file1.txt", "0123456789abcdef0123456789abcdef01234567")
        tree.add_entry("100755", "script.sh", "abcdef0123456789abcdef0123456789abcdef01")
        
        # Write the tree
        tree_id = tree.write()
        
        # Read the tree
        read_tree = Tree.read(self.repo, tree_id)
        
        # Check that the entries were preserved
        self.assertEqual(len(read_tree.entries), 2)


class TestCommit(TestCase):
    """Tests for the Commit class."""
    
    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_commit_serialize_deserialize(self):
        """Test commit serialization and deserialization."""
        # Create a commit
        commit = Commit(self.repo)
        commit.tree_id = "0123456789abcdef0123456789abcdef01234567"
        commit.parent_ids = ["abcdef0123456789abcdef0123456789abcdef01"]
        commit.author = "Test User <test@example.com> 1577836800 +0000"
        commit.committer = "Test User <test@example.com> 1577836800 +0000"
        commit.message = "Test commit message"
        
        # Serialize the commit
        serialized = commit.serialize()
        
        # Deserialize the commit
        deserialized = Commit.deserialize(self.repo, serialized)
        
        # Check that the fields were preserved
        self.assertEqual(deserialized.tree_id, "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(deserialized.parent_ids, ["abcdef0123456789abcdef0123456789abcdef01"])
        self.assertEqual(deserialized.author, "Test User <test@example.com> 1577836800 +0000")
        self.assertEqual(deserialized.committer, "Test User <test@example.com> 1577836800 +0000")
        self.assertEqual(deserialized.message, "Test commit message")
    
    def test_commit_write_read(self):
        """Test writing and reading a commit."""
        # Create a commit
        commit = Commit(self.repo)
        commit.tree_id = "0123456789abcdef0123456789abcdef01234567"
        commit.parent_ids = ["abcdef0123456789abcdef0123456789abcdef01"]
        commit.author = "Test User <test@example.com> 1577836800 +0000"
        commit.committer = "Test User <test@example.com> 1577836800 +0000"
        commit.message = "Test commit message"
        
        # Write the commit
        commit_id = commit.write()
        
        # Read the commit
        read_commit = Commit.read(self.repo, commit_id)
        
        # Check that the fields were preserved
        self.assertEqual(read_commit.tree_id, "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(read_commit.parent_ids, ["abcdef0123456789abcdef0123456789abcdef01"])
        self.assertEqual(read_commit.author, "Test User <test@example.com> 1577836800 +0000")
        self.assertEqual(read_commit.committer, "Test User <test@example.com> 1577836800 +0000")
        self.assertEqual(read_commit.message, "Test commit message")