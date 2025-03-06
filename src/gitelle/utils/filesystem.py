"""
File system utility functions for GitEllE.
"""
import os
import stat
from pathlib import Path
from typing import Union


def ensure_directory_exists(path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: The path to the directory
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def is_executable(path: Union[str, Path]) -> bool:
    """
    Check if a file is executable.

    Args:
        path: The path to the file

    Returns:
        True if the file is executable, False otherwise
    """
    return os.access(path, os.X_OK)


def get_file_mode(path: Union[str, Path]) -> int:
    """
    Get the file mode (permissions) for a file.

    Args:
        path: The path to the file

    Returns:
        The file mode as an integer
    """
    return stat.S_IMODE(os.stat(path).st_mode)


def set_file_mode(path: Union[str, Path], mode: int) -> None:
    """
    Set the file mode (permissions) for a file.

    Args:
        path: The path to the file
        mode: The file mode to set
    """
    os.chmod(path, mode)


def walk_files(root: Union[str, Path],
               exclude_gitelle: bool = True) -> list[Path]:
    """
    Recursively list all files in a directory.

    Args:
        root: The root directory to start from
        exclude_gitelle: Whether to exclude .gitelle directory

    Returns:
        A list of file paths relative to the root
    """
    root = Path(root)
    result = []

    for path in root.glob("**/*"):
        if path.is_file():
            # Check if the file should be excluded
            if exclude_gitelle and ".gitelle" in path.parts:
                continue

            result.append(path.relative_to(root))

    return result


def read_file(path: Union[str, Path]) -> bytes:
    """
    Read a file as bytes.

    Args:
        path: The path to the file

    Returns:
        The file contents as bytes
    """
    with open(path, "rb") as f:
        return f.read()


def write_file(path: Union[str, Path], data: bytes) -> None:
    """
    Write bytes to a file, creating parent directories if necessary.

    Args:
        path: The path to the file
        data: The data to write
    """
    path = Path(path)
    ensure_directory_exists(path.parent)

    with open(path, "wb") as f:
        f.write(data)


def remove_file(path: Union[str, Path]) -> None:
    """
    Remove a file if it exists.

    Args:
        path: The path to the file
    """
    path = Path(path)
    if path.exists():
        path.unlink()
