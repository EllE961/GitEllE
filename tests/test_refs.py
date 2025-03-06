"""
Tests for Git references (branches, tags, HEAD).
"""
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from gitelle.core.refs import Reference, BranchReference, TagReference
from gitelle.core.repository import Repository


class TestReference(TestCase):
    """Tests for the Reference class."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_reference_set_target(self):
        """Test setting the target of a reference."""
        # Create a reference
        ref = Reference(self.repo, "refs/test")

        # Set the target
        ref.set_target("0123456789abcdef0123456789abcdef01234567")

        # Check that the target was set
        self.assertEqual(
            ref.target,
            "0123456789abcdef0123456789abcdef01234567")
        self.assertFalse(ref.is_symbolic)

    def test_reference_set_symbolic_target(self):
        """Test setting a symbolic target for a reference."""
        # Create a reference
        ref = Reference(self.repo, "refs/test")

        # Set the symbolic target
        ref.set_target("refs/heads/main", symbolic=True)

        # Check that the target was set
        self.assertEqual(ref.target, "refs/heads/main")
        self.assertTrue(ref.is_symbolic)

    def test_reference_save_load(self):
        """Test saving and loading a reference."""
        # Create a reference
        ref = Reference(self.repo, "refs/test")

        # Set the target
        ref.set_target("0123456789abcdef0123456789abcdef01234567")

        # Save the reference
        ref.save()

        # Load the reference
        new_ref = Reference(self.repo, "refs/test")

        # Check that the target was preserved
        self.assertEqual(
            new_ref.target,
            "0123456789abcdef0123456789abcdef01234567")
        self.assertFalse(new_ref.is_symbolic)

    def test_reference_delete(self):
        """Test deleting a reference."""
        # Create a reference
        ref = Reference(self.repo, "refs/test")

        # Set the target and save
        ref.set_target("0123456789abcdef0123456789abcdef01234567")
        ref.save()

        # Check that the reference exists
        ref_path = self.repo.gitelle_dir / "refs/test"
        self.assertTrue(ref_path.exists())

        # Delete the reference
        ref.delete()

        # Check that the reference was deleted
        self.assertFalse(ref_path.exists())

    def test_reference_get_resolved_target(self):
        """Test resolving a symbolic reference."""
        # Create a direct reference
        direct_ref = Reference(self.repo, "refs/direct")
        direct_ref.set_target("0123456789abcdef0123456789abcdef01234567")
        direct_ref.save()

        # Create a symbolic reference
        sym_ref = Reference(self.repo, "refs/symbolic")
        sym_ref.set_target("refs/direct", symbolic=True)
        sym_ref.save()

        # Resolve the symbolic reference
        resolved = sym_ref.get_resolved_target()

        # Check that the correct target was returned
        self.assertEqual(resolved, "0123456789abcdef0123456789abcdef01234567")


class TestBranchReference(TestCase):
    """Tests for the BranchReference class."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_branch_reference(self):
        """Test creating a branch reference."""
        # Create a branch reference
        branch = BranchReference(self.repo, "test-branch")

        # Check the name
        self.assertEqual(branch.name, "refs/heads/test-branch")
        self.assertEqual(branch.short_name, "test-branch")

        # Set the target and save
        branch.set_target("0123456789abcdef0123456789abcdef01234567")
        branch.save()

        # Check that the reference was saved
        ref_path = self.repo.gitelle_dir / "refs/heads/test-branch"
        self.assertTrue(ref_path.exists())

        # Read the reference content
        with open(ref_path, "r") as f:
            content = f.read().strip()

        # Check the content
        self.assertEqual(content, "0123456789abcdef0123456789abcdef01234567")


class TestTagReference(TestCase):
    """Tests for the TagReference class."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        self.repo = Repository.init(self.repo_path)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_tag_reference(self):
        """Test creating a tag reference."""
        # Create a tag reference
        tag = TagReference(self.repo, "test-tag")

        # Check the name
        self.assertEqual(tag.name, "refs/tags/test-tag")
        self.assertEqual(tag.short_name, "test-tag")

        # Set the target and save
        tag.set_target("0123456789abcdef0123456789abcdef01234567")
        tag.save()

        # Check that the reference was saved
        ref_path = self.repo.gitelle_dir / "refs/tags/test-tag"
        self.assertTrue(ref_path.exists())

        # Read the reference content
        with open(ref_path, "r") as f:
            content = f.read().strip()

        # Check the content
        self.assertEqual(content, "0123456789abcdef0123456789abcdef01234567")
