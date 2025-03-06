"""
Implementation of Git references (branches, tags, HEAD).
"""
import os
from pathlib import Path
from typing import Optional


class Reference:
    """
    Represents a Git reference, which can be a branch, tag, or HEAD.

    A reference can be either:
    - A direct reference (points directly to an object ID)
    - A symbolic reference (points to another reference)

    Attributes:
        repo: The repository this reference belongs to
        name: The name of the reference
        is_symbolic: Whether this is a symbolic reference
        target: The target of the reference (object ID or reference name)
    """

    def __init__(self, repo, name: str):
        """
        Initialize a reference.

        Args:
            repo: The repository this reference belongs to
            name: The name of the reference
        """
        self.repo = repo
        self.name = name
        self.is_symbolic = False
        self.target = None

        # Try to load the reference
        self.load()

    @classmethod
    def from_path(cls, repo, name: str) -> 'Reference':
        """
        Create a reference from a path.

        Args:
            repo: The repository
            name: The reference name or path

        Returns:
            A new Reference instance
        """
        return cls(repo, name)

    def load(self) -> None:
        """
        Load the reference from disk.

        If the reference doesn't exist, self.target will be None.
        """
        ref_path = self._get_path()

        if not ref_path.exists():
            return

        with open(ref_path, 'r') as f:
            content = f.read().strip()

        if content.startswith('ref: '):
            self.is_symbolic = True
            self.target = content[5:]  # Remove 'ref: ' prefix
        else:
            self.is_symbolic = False
            self.target = content

    def save(self) -> None:
        """
        Save the reference to disk.

        Raises:
            ValueError: If the reference has no target
        """
        if self.target is None:
            raise ValueError(
                f"Cannot save reference {self.name} with no target")

        ref_path = self._get_path()

        # Create the directory if it doesn't exist
        os.makedirs(ref_path.parent, exist_ok=True)

        with open(ref_path, 'w') as f:
            if self.is_symbolic:
                f.write(f"ref: {self.target}\n")
            else:
                f.write(f"{self.target}\n")

    def delete(self) -> None:
        """Delete the reference from disk."""
        ref_path = self._get_path()

        if ref_path.exists():
            os.remove(ref_path)

    def set_target(self, target: str, symbolic: bool = False) -> None:
        """
        Set the target of the reference.

        Args:
            target: The target object ID or reference name
            symbolic: Whether this should be a symbolic reference
        """
        self.target = target
        self.is_symbolic = symbolic

    def get_resolved_target(self) -> Optional[str]:
        """
        Get the resolved target of the reference.

        For direct references, this is just the target.
        For symbolic references, this follows the chain until it finds a
            direct reference.

        Returns:
            The object ID the reference points to, or None if the reference is empty
        """
        if self.target is None:
            return None

        if not self.is_symbolic:
            return self.target

        # Resolve the symbolic reference
        ref = Reference(self.repo, self.target)
        return ref.get_resolved_target()

    def _get_path(self) -> Path:
        """
        Get the path to the reference file.

        Returns:
            The path to the reference file
        """
        if self.name == "HEAD":
            return self.repo.head_file

        # Handle references in the refs directory
        return self.repo.gitelle_dir / self.name


class BranchReference(Reference):
    """Represents a branch reference (refs/heads/...)."""

    def __init__(self, repo, name: str):
        """
        Initialize a branch reference.

        Args:
            repo: The repository this reference belongs to
            name: The name of the branch (without 'refs/heads/' prefix)
        """
        super().__init__(repo, f"refs/heads/{name}")
        self.short_name = name


class TagReference(Reference):
    """Represents a tag reference (refs/tags/...)."""

    def __init__(self, repo, name: str):
        """
        Initialize a tag reference.

        Args:
            repo: The repository this reference belongs to
            name: The name of the tag (without 'refs/tags/' prefix)
        """
        super().__init__(repo, f"refs/tags/{name}")
        self.short_name = name
