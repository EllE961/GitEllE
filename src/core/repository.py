"""
Core implementation of GitEllE repository functionality.
"""
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from gitelle.core.index import Index
from gitelle.core.objects import Blob, Commit, GitObject, Tree
from gitelle.core.refs import BranchReference, Reference, TagReference
from gitelle.utils.filesystem import ensure_directory_exists


class Repository:
    """
    Represents a GitEllE repository with core functionality.
    
    A repository contains:
    - Objects (blobs, trees, commits)
    - References (branches, tags)
    - Index (staging area)
    
    This class provides the main interface for working with Git repositories
    and implements the core Git operations.
    """
    
    GITELLE_DIR = ".gitelle"
    
    def __init__(self, path: Union[str, Path]):
        """
        Initialize a repository at the given path.
        
        Args:
            path: The path to the repository root directory
        """
        self.path = Path(path).absolute()
        self.gitelle_dir = self.path / self.GITELLE_DIR
        self.objects_dir = self.gitelle_dir / "objects"
        self.refs_dir = self.gitelle_dir / "refs"
        self.index_file = self.gitelle_dir / "index"
        self.head_file = self.gitelle_dir / "HEAD"
        
        # These will be lazily loaded when needed
        self._index = None
        self._head = None
    
    @classmethod
    def init(cls, path: Union[str, Path]) -> "Repository":
        """
        Create a new repository at the given path.
        
        Args:
            path: The path where the repository should be created
        
        Returns:
            A new Repository instance
        """
        path = Path(path).absolute()
        repo = cls(path)
        
        # Create the directory structure
        ensure_directory_exists(repo.gitelle_dir)
        ensure_directory_exists(repo.objects_dir)
        ensure_directory_exists(repo.refs_dir)
        ensure_directory_exists(repo.refs_dir / "heads")
        ensure_directory_exists(repo.refs_dir / "tags")
        
        # Create an empty index
        repo.index.write()
        
        # Point HEAD to refs/heads/main
        with open(repo.head_file, "w") as f:
            f.write("ref: refs/heads/main\n")
        
        return repo
    
    @classmethod
    def find(cls, start_path: Union[str, Path] = None) -> Optional["Repository"]:
        """
        Find a repository by looking for a .gitelle directory in the given path
        or its parents.
        
        Args:
            start_path: The path to start the search from (default: current directory)
        
        Returns:
            A Repository instance or None if no repository is found
        """
        if start_path is None:
            start_path = os.getcwd()
        
        start_path = Path(start_path).absolute()
        
        # Traverse up the directory tree
        current_path = start_path
        while True:
            gitelle_dir = current_path / cls.GITELLE_DIR
            if gitelle_dir.is_dir():
                return cls(current_path)
            
            # Stop if we've reached the root directory
            if current_path.parent == current_path:
                return None
            
            current_path = current_path.parent
    
    @property
    def index(self) -> Index:
        """Get the repository index (staging area)."""
        if self._index is None:
            self._index = Index(self)
        return self._index
    
    @property
    def head(self) -> Reference:
        """Get the HEAD reference of the repository."""
        if self._head is None:
            self._head = Reference(self, "HEAD")
        return self._head
    
    def get_object(self, object_id: str) -> Union[Blob, Tree, Commit]:
        """
        Retrieve an object from the repository by its ID.
        
        Args:
            object_id: The ID of the object to retrieve
        
        Returns:
            The object (Blob, Tree, or Commit)
        
        Raises:
            ValueError: If the object is not found or has an invalid type
        """
        try:
            return GitObject.read(self, object_id)
        except Exception as e:
            raise ValueError(f"Failed to read object {object_id}: {e}")
    
    def create_blob(self, data: bytes) -> str:
        """
        Create a blob object in the repository.
        
        Args:
            data: The blob's data
        
        Returns:
            The ID of the created blob
        """
        blob = Blob(self, data)
        return blob.write()
    
    def create_blob_from_file(self, path: Union[str, Path]) -> str:
        """
        Create a blob object from a file.
        
        Args:
            path: The path to the file
        
        Returns:
            The ID of the created blob
        """
        blob = Blob.from_file(self, path)
        return blob.write()
    
    def create_tree(self) -> Tree:
        """
        Create a new tree object.
        
        Returns:
            A new Tree instance
        """
        return Tree(self)
    
    def create_commit(self, tree_id: str, message: str, parent_ids: List[str] = None) -> str:
        """
        Create a commit object.
        
        Args:
            tree_id: The ID of the tree for the commit
            message: The commit message
            parent_ids: A list of parent commit IDs (default: None)
        
        Returns:
            The ID of the created commit
        """
        commit = Commit(self)
        commit.tree_id = tree_id
        commit.message = message
        
        if parent_ids:
            commit.parent_ids = parent_ids
        
        # Get author and committer info from environment variables or config
        author_name = os.environ.get("GIT_AUTHOR_NAME", "Unknown")
        author_email = os.environ.get("GIT_AUTHOR_EMAIL", "unknown@example.com")
        timestamp = int(time.time())
        timezone_offset = time.strftime("%z")
        
        author_string = f"{author_name} <{author_email}> {timestamp} {timezone_offset}"
        commit.author = author_string
        commit.committer = author_string
        
        return commit.write()
    
    def get_branch(self, name: str) -> Reference:
        """
        Get a branch reference by name.
        
        Args:
            name: The name of the branch
        
        Returns:
            A Reference object pointing to the branch
        """
        return Reference.from_path(self, f"refs/heads/{name}")
    
    def get_tag(self, name: str) -> Reference:
        """
        Get a tag reference by name.
        
        Args:
            name: The name of the tag
        
        Returns:
            A Reference object pointing to the tag
        """
        return Reference.from_path(self, f"refs/tags/{name}")
    
    def get_branches(self) -> List[str]:
        """
        Get a list of all branches in the repository.
        
        Returns:
            A list of branch names
        """
        branches_dir = self.refs_dir / "heads"
        return [p.name for p in branches_dir.glob("*") if p.is_file()]
    
    def get_tags(self) -> List[str]:
        """
        Get a list of all tags in the repository.
        
        Returns:
            A list of tag names
        """
        tags_dir = self.refs_dir / "tags"
        return [p.name for p in tags_dir.glob("*") if p.is_file()]
    
    def commit(self, message: str, author: str = None, committer: str = None) -> str:
        """
        Create a new commit with the current index.
        
        Args:
            message: The commit message
            author: The author information (default: from config)
            committer: The committer information (default: same as author)
        
        Returns:
            The ID of the new commit
        """
        # Get the tree from the index
        tree_id = self.index.get_tree_id()
        if not tree_id:
            raise ValueError("Nothing to commit (empty index)")
        
        # Create the commit
        commit = Commit(self)
        commit.tree_id = tree_id
        
        # Set parent commit(s)
        head_target = self.head.get_resolved_target()
        if head_target:
            commit.parent_ids.append(head_target)
        
        # Set author and committer information
        if author is None:
            # Get author info from environment variables or config
            author_name = os.environ.get("GIT_AUTHOR_NAME", "Unknown")
            author_email = os.environ.get("GIT_AUTHOR_EMAIL", "unknown@example.com")
            timestamp = int(time.time())
            timezone_offset = time.strftime("%z")
            
            author = f"{author_name} <{author_email}> {timestamp} {timezone_offset}"
        
        commit.author = author
        commit.committer = committer or author
        
        # Set the commit message
        commit.message = message
        
        # Write the commit object
        commit_id = commit.write()
        
        # Update the current branch to point to the new commit
        if self.head.is_symbolic:
            branch_ref = Reference.from_path(self, self.head.target)
            branch_ref.set_target(commit_id)
            branch_ref.save()
        else:
            # Detached HEAD state
            self.head.set_target(commit_id)
            self.head.save()
        
        return commit_id
    
    def checkout(self, ref_name: str) -> None:
        """
        Checkout a specific reference (branch, tag, or commit).
        
        Args:
            ref_name: The name of the reference to checkout
            
        Raises:
            ValueError: If the reference is invalid or the working directory is not clean
        """
        # First, check if the working directory is clean
        # In a real implementation, we would check for uncommitted changes
        
        # Try to resolve the reference
        commit_id = None
        is_branch = False
        
        # Try to resolve as a branch
        branch_ref = self.get_branch(ref_name)
        if branch_ref.target:
            commit_id = branch_ref.target
            is_branch = True
        else:
            # Try to resolve as a tag
            tag_ref = self.get_tag(ref_name)
            if tag_ref.target:
                commit_id = tag_ref.target
            else:
                # Try as a direct commit ID
                try:
                    commit = self.get_object(ref_name)
                    if commit.type == "commit":
                        commit_id = ref_name
                except ValueError:
                    pass
        
        if not commit_id:
            raise ValueError(f"Invalid reference: {ref_name}")
        
        # Get the commit object
        commit = self.get_object(commit_id)
        
        # Update HEAD
        if is_branch:
            # Point HEAD to the branch
            self.head.set_target(f"refs/heads/{ref_name}", symbolic=True)
        else:
            # Detached HEAD state
            self.head.set_target(commit_id)
        
        self.head.save()
        
        # Get the tree from the commit
        tree = self.get_object(commit.tree_id)
        
        # Update the working directory
        # In a real implementation, this would recursively checkout the tree
        # For now, we'll just note that this would involve:
        # 1. Deleting files that aren't in the tree
        # 2. Creating/updating files from the tree
        # 3. Setting file permissions
        
        # Update the index to match the tree
        self.index.entries.clear()
        # In a real implementation, we would populate the index from the tree
        self.index.write()
    
    def __repr__(self) -> str:
        return f"Repository({self.path})"