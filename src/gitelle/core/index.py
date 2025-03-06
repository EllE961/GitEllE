"""
Implementation of the Git index (staging area).
"""
import hashlib
import os
import struct
import time
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from gitelle.core.objects import Blob
from gitelle.utils.filesystem import is_executable


class IndexEntry:
    """
    Represents an entry in the Git index.
    
    Attributes:
        ctime: The last change time (seconds)
        ctime_nsec: The last change time (nanoseconds)
        mtime: The last modification time (seconds)
        mtime_nsec: The last modification time (nanoseconds)
        dev: The device ID
        ino: The inode number
        mode: The file mode
        uid: The user ID
        gid: The group ID
        size: The file size
        object_id: The object ID (SHA-1 hash)
        flags: The entry flags
        path: The file path
    """
    
    def __init__(self):
        """Initialize an empty index entry."""
        self.ctime = 0
        self.ctime_nsec = 0
        self.mtime = 0
        self.mtime_nsec = 0
        self.dev = 0
        self.ino = 0
        self.mode = 0
        self.uid = 0
        self.gid = 0
        self.size = 0
        self.object_id = None
        self.flags = 0
        self.path = None
    
    @classmethod
    def from_file(cls, repo, path: Path, object_id: Optional[str] = None) -> 'IndexEntry':
        """
        Create an index entry from a file.
        
        Args:
            repo: The repository
            path: The path to the file (relative to the repository root)
            object_id: The object ID (if None, a new blob will be created)
        
        Returns:
            A new IndexEntry instance
        """
        entry = cls()
        
        # Get the absolute path to the file
        abs_path = repo.path / path
        
        # Get file stats
        stat = abs_path.stat()
        
        # Set the file metadata
        entry.ctime = int(stat.st_ctime)
        entry.ctime_nsec = int((stat.st_ctime - entry.ctime) * 1_000_000_000)
        entry.mtime = int(stat.st_mtime)
        entry.mtime_nsec = int((stat.st_mtime - entry.mtime) * 1_000_000_000)
        entry.dev = stat.st_dev
        entry.ino = stat.st_ino
        entry.uid = stat.st_uid
        entry.gid = stat.st_gid
        entry.size = stat.st_size
        
        # Set the file mode
        if is_executable(abs_path):
            entry.mode = 0o100755  # Executable file
        else:
            entry.mode = 0o100644  # Regular file
        
        # Set the object ID
        if object_id is None:
            blob = Blob.from_file(repo, abs_path)
            entry.object_id = blob.write()
        else:
            entry.object_id = object_id
        
        # Set the path
        entry.path = str(path)
        
        # Set the flags (assume path length is less than 0xFFF)
        entry.flags = min(0xFFF, len(entry.path))
        
        return entry
    
    def serialize(self) -> bytes:
        """
        Serialize the index entry to bytes.
        
        Returns:
            The serialized index entry
        """
        # The entry format follows Git's index v2 format
        data = struct.pack(
            ">LLLLLLLLLL20sH",
            self.ctime, self.ctime_nsec,
            self.mtime, self.mtime_nsec,
            self.dev, self.ino,
            self.mode, self.uid, self.gid,
            self.size, bytes.fromhex(self.object_id),
            self.flags
        )
        
        # Add the path and padding
        path_bytes = self.path.encode()
        padding_length = 8 - ((len(data) + len(path_bytes)) % 8)
        if padding_length == 8:
            padding_length = 0
        
        return data + path_bytes + b'\x00' * padding_length
    
    @classmethod
    def deserialize(cls, data: bytes) -> Tuple['IndexEntry', bytes]:
        """
        Deserialize an index entry from bytes.
        
        Args:
            data: The serialized index entry data
        
        Returns:
            A tuple of (IndexEntry, remaining_data)
        """
        entry = cls()
        
        # Parse the fixed-length part
        (
            entry.ctime, entry.ctime_nsec,
            entry.mtime, entry.mtime_nsec,
            entry.dev, entry.ino,
            entry.mode, entry.uid, entry.gid,
            entry.size, object_id, entry.flags
        ) = struct.unpack(">LLLLLLLLLL20sH", data[:62])
        
        entry.object_id = object_id.hex()
        
        # Find the end of the path (null byte)
        path_end = data.find(b'\x00', 62)
        entry.path = data[62:path_end].decode()
        
        # Calculate padding
        entry_length = path_end + 1
        padding_length = 8 - (entry_length % 8)
        if padding_length == 8:
            padding_length = 0
        
        # Return the entry and remaining data
        return entry, data[entry_length + padding_length:]


class Index:
    """
    Represents the Git index (staging area).
    
    The index keeps track of the files that will be included
    in the next commit.
    
    Attributes:
        repo: The repository this index belongs to
        entries: A dictionary of index entries, keyed by path
    """
    
    SIGNATURE = b"DIRC"
    VERSION = 2
    
    def __init__(self, repo):
        """
        Initialize an index.
        
        Args:
            repo: The repository this index belongs to
        """
        self.repo = repo
        self.entries = OrderedDict()
        
        # Load the index if it exists
        if self.repo.index_file.exists():
            self.read()
    
    def add(self, paths: List[Union[str, Path]]) -> None:
        """
        Add files to the index.
        
        Args:
            paths: A list of file paths to add (relative to the repository root)
        """
        for path in paths:
            path = Path(path)
            
            # If the path is a directory, add all files in it recursively
            if (self.repo.path / path).is_dir():
                all_files = [p.relative_to(self.repo.path) for p in (self.repo.path / path).glob("**/*") if p.is_file()]
                self.add(all_files)
                continue
            
            # Create an index entry for the file
            entry = IndexEntry.from_file(self.repo, path)
            self.entries[entry.path] = entry
    
    def remove(self, paths: List[Union[str, Path]]) -> None:
        """
        Remove files from the index.
        
        Args:
            paths: A list of file paths to remove (relative to the repository root)
        """
        for path in paths:
            path = str(path)
            if path in self.entries:
                del self.entries[path]
    
    def write(self) -> None:
        """Write the index to disk."""
        # Format: signature (4 bytes) + version (4 bytes) + entry count (4 bytes) + entries + checksum (20 bytes)
        
        # Build the header
        header = struct.pack(">4sLL", self.SIGNATURE, self.VERSION, len(self.entries))
        
        # Build the entries
        entries_data = b''
        for entry in self.entries.values():
            entries_data += entry.serialize()
        
        # Calculate the checksum
        data = header + entries_data
        checksum = hashlib.sha1(data).digest()
        
        # Write to disk
        with open(self.repo.index_file, 'wb') as f:
            f.write(data + checksum)
    
    def read(self) -> None:
        """Read the index from disk."""
        with open(self.repo.index_file, 'rb') as f:
            data = f.read()
        
        # Verify the checksum
        content = data[:-20]
        expected_checksum = data[-20:]
        actual_checksum = hashlib.sha1(content).digest()
        
        if expected_checksum != actual_checksum:
            raise ValueError("Index checksum mismatch")
        
        # Parse the header
        signature, version, entry_count = struct.unpack(">4sLL", content[:12])
        
        if signature != self.SIGNATURE:
            raise ValueError(f"Invalid index signature: {signature}")
        
        if version != self.VERSION:
            raise ValueError(f"Unsupported index version: {version}")
        
        # Parse the entries
        self.entries.clear()
        remaining = content[12:]
        
        for _ in range(entry_count):
            entry, remaining = IndexEntry.deserialize(remaining)
            self.entries[entry.path] = entry
    
    def get_tree_id(self) -> str:
        """
        Create a tree object from the index and return its ID.
        
        Returns:
            The ID of the tree object
        """
        # Implementation of tree creation logic
        pass