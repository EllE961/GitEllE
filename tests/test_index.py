"""
Tests for the Index class.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from gitelle.core.index import Index, IndexEntry
from gitelle.core.repository import Repository


class TestIndex(TestCase):
    """Tests for the Index class."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_index_add_file(self):
        """Test adding a file to the index."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        with open(file_path, "w") as f:
            f.write("Test content")

        # Add the file to the index
        index = Index(self.repo)
        index.add([Path("test.txt")])

        # Check that the file was added
        self.assertIn("test.txt", index.entries)

    def test_index_add_multiple_files(self):
        """Test adding multiple files to the index."""
        # Create files
        file1_path = self.repo_path / "test1.txt"
        file2_path = self.repo_path / "test2.txt"
        with open(file1_path, "w") as f:
            f.write("Test content 1")
        with open(file2_path, "w") as f:
            f.write("Test content 2")

        # Add the files to the index
        index = Index(self.repo)
        index.add([Path("test1.txt"), Path("test2.txt")])

        # Check that the files were added
        self.assertIn("test1.txt", index.entries)
        self.assertIn("test2.txt", index.entries)

    def test_index_remove_file(self):
        """Test removing a file from the index."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        with open(file_path, "w") as f:
            f.write("Test content")

        # Add the file to the index
        index = Index(self.repo)
        index.add([Path("test.txt")])

        # Check that the file was added
        self.assertIn("test.txt", index.entries)

        # Remove the file from the index
        index.remove([Path("test.txt")])

        # Check that the file was removed
        self.assertNotIn("test.txt", index.entries)

    def test_index_write_read(self):
        """Test writing and reading the index."""
        # Create files
        file1_path = self.repo_path / "test1.txt"
        file2_path = self.repo_path / "test2.txt"
        with open(file1_path, "w") as f:
            f.write("Test content 1")
        with open(file2_path, "w") as f:
            f.write("Test content 2")

        # Add the files to the index
        index = Index(self.repo)
        index.add([Path("test1.txt"), Path("test2.txt")])

        # Write the index
        index.write()

        # Read the index
        new_index = Index(self.repo)

        # Check that the files were preserved
        self.assertIn("test1.txt", new_index.entries)
        self.assertIn("test2.txt", new_index.entries)

    def test_index_get_tree_id(self):
        """Test creating a tree from the index."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        with open(file_path, "w") as f:
            f.write("Test content")

        # Add the file to the index
        index = Index(self.repo)
        index.add([Path("test.txt")])

        # Get the tree ID
        tree_id = index.get_tree_id()

        # Check that a tree was created
        self.assertIsNotNone(tree_id)

        # Try to get the tree object
        tree = self.repo.get_object(tree_id)
        self.assertEqual(tree.type, "tree")

        # Check that the tree contains the file
        self.assertEqual(len(tree.entries), 1)
        self.assertEqual(tree.entries[0].name, "test.txt")


class TestIndexEntry(TestCase):
    """Tests for the IndexEntry class."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_index_entry_from_file(self):
        """Test creating an index entry from a file."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        with open(file_path, "w") as f:
            f.write("Test content")

        # Create an index entry from the file
        entry = IndexEntry.from_file(self.repo, Path("test.txt"))

        # Check the entry fields
        self.assertEqual(entry.path, "test.txt")
        self.assertIsNotNone(entry.object_id)

        # Get the blob object
        blob = self.repo.get_object(entry.object_id)
        self.assertEqual(blob.data.decode(), "Test content")

    def test_index_entry_serialize_deserialize(self):
        """Test index entry serialization and deserialization."""
        # Create a file
        file_path = self.repo_path / "test.txt"
        with open(file_path, "w") as f:
            f.write("Test content")

        # Create an index entry from the file
        entry = IndexEntry.from_file(self.repo, Path("test.txt"))

        # Serialize the entry
        serialized = entry.serialize()

        # Deserialize the entry
        deserialized, _ = IndexEntry.deserialize(serialized)

        # Check that the fields were preserved
        self.assertEqual(deserialized.path, "test.txt")
        self.assertEqual(deserialized.object_id, entry.object_id)
