# Core API Reference

This document describes the core functionality of GitEllE, focusing on the classes and functions in the `gitelle.core` module.

## Repository

The `Repository` class is the central component of GitEllE. It represents a Git repository and provides access to all its components.

### Repository Class

```python
from gitelle.core.repository import Repository
```

#### Creating a Repository

```python
# Initialize a new repository
repo = Repository.init("/path/to/repo")

# Find a repository from a path
repo = Repository.find("/path/to/file/in/repo")

# Open an existing repository
repo = Repository("/path/to/repo")
```

#### Repository Properties

```python
# Get the repository's path
path = repo.path  # Returns a Path object

# Get the repository's index (staging area)
index = repo.index  # Returns an Index object

# Get the repository's HEAD reference
head = repo.head  # Returns a Reference object
```

#### Repository Methods

```python
# Get an object from the repository
blob = repo.get_object("0123456789abcdef0123456789abcdef01234567")

# Get a branch reference
main_branch = repo.get_branch("main")

# Get a tag reference
tag = repo.get_tag("v1.0.0")

# Get a list of all branches
branches = repo.get_branches()

# Get a list of all tags
tags = repo.get_tags()

# Create a commit
commit_id = repo.commit("Commit message")

# Checkout a reference
repo.checkout("main")
```

## Objects

Git objects are the building blocks of a Git repository. There are three main types of Git objects: blobs, trees, and commits.

### Blob Class

The `Blob` class represents a file in a Git repository.

```python
from gitelle.core.objects import Blob
```

#### Creating a Blob

```python
# Create a blob from data
blob = Blob(repo, b"File content")

# Create a blob from a file
blob = Blob.from_file(repo, "/path/to/file")
```

#### Blob Methods

```python
# Get the blob's ID
blob_id = blob.id

# Write the blob to the repository
blob.write()
```

### Tree Class

The `Tree` class represents a directory in a Git repository.

```python
from gitelle.core.objects import Tree
```

#### Creating a Tree

```python
# Create an empty tree
tree = Tree(repo)

# Add an entry to the tree
tree.add_entry("100644", "file.txt", "0123456789abcdef0123456789abcdef01234567")
```

#### Tree Methods

```python
# Get the tree's ID
tree_id = tree.id

# Write the tree to the repository
tree.write()
```

### Commit Class

The `Commit` class represents a commit in a Git repository.

```python
from gitelle.core.objects import Commit
```

#### Creating a Commit

```python
# Create a commit
commit = Commit(repo)
commit.tree_id = "0123456789abcdef0123456789abcdef01234567"
commit.parent_ids = ["abcdef0123456789abcdef0123456789abcdef01"]
commit.author = "Author Name <author@example.com> 1577836800 +0000"
commit.committer = "Committer Name <committer@example.com> 1577836800 +0000"
commit.message = "Commit message"
```

#### Commit Methods

```python
# Get the commit's ID
commit_id = commit.id

# Write the commit to the repository
commit.write()
```

## Index

The `Index` class represents the staging area in a Git repository.

```python
from gitelle.core.index import Index
```

#### Index Methods

```python
# Add files to the index
index.add([Path("file1.txt"), Path("file2.txt")])

# Remove files from the index
index.remove([Path("file3.txt")])

# Write the index to disk
index.write()

# Read the index from disk
index.read()

# Create a tree from the index
tree_id = index.get_tree_id()
```

## References

The `Reference` class represents a Git reference, such as a branch or tag.

```python
from gitelle.core.refs import Reference, BranchReference, TagReference
```

#### Creating References

```python
# Create a reference
ref = Reference(repo, "refs/heads/main")

# Create a branch reference
branch = BranchReference(repo, "feature-branch")

# Create a tag reference
tag = TagReference(repo, "v1.0.0")
```

#### Reference Methods

```python
# Set the target of a reference
ref.set_target("0123456789abcdef0123456789abcdef01234567")

# Set a symbolic target
ref.set_target("refs/heads/main", symbolic=True)

# Save the reference to disk
ref.save()

# Delete the reference
ref.delete()

# Get the resolved target of a reference
target = ref.get_resolved_target()
```

## Error Handling

Most methods in the core API can raise exceptions:

-   `ValueError`: For invalid inputs or states
-   `FileNotFoundError`: When a required file is missing
-   `PermissionError`: When there are permission issues
-   Other exceptions as appropriate

It's recommended to catch these exceptions and handle them appropriately in your code.

## Example Usage

Here's a complete example that creates a repository, adds a file, and makes a commit:

```python
from pathlib import Path
from gitelle.core.repository import Repository

# Initialize a repository
repo = Repository.init("/path/to/repo")

# Create a file
file_path = repo.path / "README.md"
with open(file_path, "w") as f:
    f.write("# My Project")

# Add the file to the index
repo.index.add([Path("README.md")])

# Make a commit
commit_id = repo.commit("Initial commit")

print(f"Created commit: {commit_id}")
```
