"""
Implementation of Git object types (blob, tree, commit).
"""
import hashlib
import os
import time
import zlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from gitelle.utils.compression import compress_data, decompress_data
from gitelle.utils.filesystem import ensure_directory_exists


class GitObject(ABC):
    """
    Abstract base class for all Git objects.

    Git objects are content-addressable files in the Git database,
    identified by their SHA-1, and can be of several types.

    Attributes:
        repo: The repository this object belongs to
        id: The object's SHA-1 hash ID
    """

    def __init__(self, repo):
        """
        Initialize a Git object.

        Args:
            repo: The repository this object belongs to
        """
        self.repo = repo
        self._id = None

    @property
    def id(self) -> str:
        """
        Get the object's ID (SHA-1 hash).

        Returns:
            The object's SHA-1 hash ID
        """
        if self._id is None:
            data = self.serialize()
            header = f"{self.type} {len(data)}".encode()
            store = header + b'\x00' + data
            self._id = hashlib.sha1(store).hexdigest()
        return self._id

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Get the object's type.

        Returns:
            The object type as a string
        """
        pass

    @abstractmethod
    def serialize(self) -> bytes:
        """
        Serialize the object to bytes.

        Returns:
            The serialized object data
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, repo, data: bytes) -> 'GitObject':
        """
        Deserialize bytes to create an object.

        Args:
            repo: The repository this object belongs to
            data: The serialized object data

        Returns:
            A new GitObject instance
        """
        pass

    def write(self) -> str:
        """
        Write this object to the repository.

        Returns:
            The object's ID
        """
        object_id = self.id
        object_path = self._get_object_path(object_id)

        # If the object already exists, don't write it again
        if object_path.exists():
            return object_id

        # Create the directory if it doesn't exist
        ensure_directory_exists(object_path.parent)

        # Write the object data
        data = self.serialize()
        header = f"{self.type} {len(data)}".encode()
        store = header + b'\x00' + data
        compressed = compress_data(store)

        with open(object_path, 'wb') as f:
            f.write(compressed)

        return object_id

    @classmethod
    def read(cls, repo, object_id: str) -> 'GitObject':
        """
        Read an object from the repository.

        Args:
            repo: The repository to read from
            object_id: The ID of the object to read

        Returns:
            A GitObject of the appropriate type

        Raises:
            ValueError: If the object does not exist or has an invalid format
        """
        object_path = cls._get_object_path(repo, object_id)

        if not object_path.exists():
            raise ValueError(f"Object {object_id} does not exist")

        # Read and decompress the object data
        with open(object_path, 'rb') as f:
            compressed_data = f.read()

        raw_data = decompress_data(compressed_data)

        # Parse the header
        null_index = raw_data.index(b'\x00')
        header = raw_data[:null_index].decode()
        data = raw_data[null_index + 1:]

        # Extract the type
        type_end = header.index(' ')
        obj_type = header[:type_end]

        # Create the appropriate object type
        if obj_type == 'blob':
            return Blob.deserialize(repo, data)
        elif obj_type == 'tree':
            return Tree.deserialize(repo, data)
        elif obj_type == 'commit':
            return Commit.deserialize(repo, data)
        else:
            raise ValueError(f"Unknown object type: {obj_type}")

    @staticmethod
    def _get_object_path(repo, object_id: str) -> Path:
        """
        Get the path to an object in the repository.

        Args:
            repo: The repository
            object_id: The object ID

        Returns:
            The path to the object file
        """
        return repo.objects_dir / object_id[:2] / object_id[2:]

    def _get_object_path(self, object_id: str) -> Path:
        """
        Get the path to this object in the repository.

        Args:
            object_id: The object ID

        Returns:
            The path to the object file
        """
        return self.repo.objects_dir / object_id[:2] / object_id[2:]


class Blob(GitObject):
    """
    Represents a Git blob object, which stores file content.

    Attributes:
        data: The blob's data as bytes
    """

    def __init__(self, repo, data: bytes):
        """
        Initialize a blob object.

        Args:
            repo: The repository this blob belongs to
            data: The blob's data
        """
        super().__init__(repo)
        self.data = data

    @property
    def type(self) -> str:
        return "blob"

    def serialize(self) -> bytes:
        return self.data

    @classmethod
    def deserialize(cls, repo, data: bytes) -> 'Blob':
        return cls(repo, data)

    @classmethod
    def from_file(cls, repo, path: Union[str, Path]) -> 'Blob':
        """
        Create a blob from a file.

        Args:
            repo: The repository this blob belongs to
            path: The path to the file

        Returns:
            A new Blob instance
        """
        path = Path(path)
        with open(path, 'rb') as f:
            data = f.read()
        return cls(repo, data)


class TreeEntry:
    """
    Represents an entry in a Git tree object.

    Attributes:
        mode: The file mode (e.g., 100644 for a regular file)
        name: The name of the file or directory
        id: The object ID of the entry
    """

    def __init__(self, mode: str, name: str, object_id: str):
        """
        Initialize a tree entry.

        Args:
            mode: The file mode
            name: The name of the file or directory
            object_id: The object ID
        """
        self.mode = mode
        self.name = name
        self.id = object_id

    def serialize(self) -> bytes:
        """
        Serialize the tree entry to bytes.

        Returns:
            The serialized tree entry
        """
        mode = self.mode.encode()
        name = self.name.encode()
        object_id = bytes.fromhex(self.id)
        return mode + b' ' + name + b'\x00' + object_id

    @classmethod
    def deserialize(cls, data: bytes) -> Tuple['TreeEntry', bytes]:
        """
        Deserialize a tree entry from bytes.

        Args:
            data: The serialized tree entry data

        Returns:
            A tuple of (TreeEntry, remaining_data)
        """
        # Find the space separator between mode and name
        space_index = data.index(b' ')
        mode = data[:space_index].decode()

        # Find the null separator between name and object ID
        null_index = data.index(b'\x00', space_index)
        name = data[space_index + 1:null_index].decode()

        # The object ID is 20 bytes (40 hex characters)
        object_id = data[null_index + 1:null_index + 21].hex()

        # Return the entry and the remaining data
        remaining = data[null_index + 21:]
        return cls(mode, name, object_id), remaining


class Tree(GitObject):
    """
    Represents a Git tree object, which stores directory content.

    Attributes:
        entries: A list of TreeEntry objects
    """

    def __init__(self, repo):
        """
        Initialize a tree object.

        Args:
            repo: The repository this tree belongs to
        """
        super().__init__(repo)
        self.entries = []

    @property
    def type(self) -> str:
        return "tree"

    def add_entry(self, mode: str, name: str, object_id: str) -> None:
        """
        Add an entry to the tree.

        Args:
            mode: The file mode
            name: The name of the file or directory
            object_id: The object ID
        """
        self.entries.append(TreeEntry(mode, name, object_id))
        # Invalidate the ID since the tree has changed
        self._id = None

    def serialize(self) -> bytes:
        """
        Serialize the tree to bytes.

        Returns:
            The serialized tree data
        """
        # Sort entries by name
        sorted_entries = sorted(self.entries, key=lambda e: e.name)

        # Serialize each entry and concatenate
        result = b''
        for entry in sorted_entries:
            result += entry.serialize()

        return result

    @classmethod
    def deserialize(cls, repo, data: bytes) -> 'Tree':
        """
        Deserialize bytes to create a tree.

        Args:
            repo: The repository this tree belongs to
            data: The serialized tree data

        Returns:
            A new Tree instance
        """
        tree = cls(repo)
        remaining = data

        # Parse entries until we've consumed all the data
        while remaining:
            entry, remaining = TreeEntry.deserialize(remaining)
            tree.entries.append(entry)

        return tree


class Commit(GitObject):
    """
    Represents a Git commit object.

    Attributes:
        tree_id: The ID of the tree this commit points to
        parent_ids: A list of parent commit IDs
        author: The author information (name, email, timestamp)
        committer: The committer information (name, email, timestamp)
        message: The commit message
    """

    def __init__(self, repo):
        """
        Initialize a commit object.

        Args:
            repo: The repository this commit belongs to
        """
        super().__init__(repo)
        self.tree_id = None
        self.parent_ids = []
        self.author = None
        self.committer = None
        self.message = None

    @property
    def type(self) -> str:
        return "commit"

    def serialize(self) -> bytes:
        """
        Serialize the commit to bytes.

        Returns:
            The serialized commit data
        """
        lines = []

        # Add tree
        lines.append(f"tree {self.tree_id}")

        # Add parents
        for parent_id in self.parent_ids:
            lines.append(f"parent {parent_id}")

        # Add author and committer
        lines.append(f"author {self.author}")
        lines.append(f"committer {self.committer}")

        # Add a blank line followed by the message
        lines.append("")
        lines.append(self.message)

        return "\n".join(lines).encode()

    @classmethod
    def deserialize(cls, repo, data: bytes) -> 'Commit':
        """
        Deserialize bytes to create a commit.

        Args:
            repo: The repository this commit belongs to
            data: The serialized commit data

        Returns:
            A new Commit instance
        """
        commit = cls(repo)

        # Split the data into headers and message
        text = data.decode()
        parts = text.split("\n\n", 1)

        headers = parts[0].split("\n")
        commit.message = parts[1] if len(parts) > 1 else ""

        # Parse headers
        for header in headers:
            if not header:
                continue

            key, value = header.split(" ", 1)

            if key == "tree":
                commit.tree_id = value
            elif key == "parent":
                commit.parent_ids.append(value)
            elif key == "author":
                commit.author = value
            elif key == "committer":
                commit.committer = value

        return commit
