# Utilities API Reference

This document describes the utility functions of GitEllE, focusing on the modules in the `gitelle.utils` package.

## Filesystem Utilities

The `gitelle.utils.filesystem` module provides functions for working with the file system.

```python
from gitelle.utils.filesystem import (
    ensure_directory_exists,
    is_executable,
    get_file_mode,
    set_file_mode,
    walk_files,
    read_file,
    write_file,
    remove_file,
)
```

### Directory Operations

```python
def ensure_directory_exists(path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: The path to the directory
    """
```

### File Operations

```python
def is_executable(path: Union[str, Path]) -> bool:
    """
    Check if a file is executable.

    Args:
        path: The path to the file

    Returns:
        True if the file is executable, False otherwise
    """

def get_file_mode(path: Union[str, Path]) -> int:
    """
    Get the file mode (permissions) for a file.

    Args:
        path: The path to the file

    Returns:
        The file mode as an integer
    """

def set_file_mode(path: Union[str, Path], mode: int) -> None:
    """
    Set the file mode (permissions) for a file.

    Args:
        path: The path to the file
        mode: The file mode to set
    """

def read_file(path: Union[str, Path]) -> bytes:
    """
    Read a file as bytes.

    Args:
        path: The path to the file

    Returns:
        The file contents as bytes
    """

def write_file(path: Union[str, Path], data: bytes) -> None:
    """
    Write bytes to a file, creating parent directories if necessary.

    Args:
        path: The path to the file
        data: The data to write
    """

def remove_file(path: Union[str, Path]) -> None:
    """
    Remove a file if it exists.

    Args:
        path: The path to the file
    """
```

### File Traversal

```python
def walk_files(root: Union[str, Path], exclude_gitelle: bool = True) -> list[Path]:
    """
    Recursively list all files in a directory.

    Args:
        root: The root directory to start from
        exclude_git
```
