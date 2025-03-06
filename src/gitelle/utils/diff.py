"""
Diff utility functions for GitEllE.
"""
from typing import List, Tuple, Union
from difflib import unified_diff


def create_unified_diff(a_lines: List[str], b_lines: List[str], 
                       a_name: str = "a", b_name: str = "b",
                       context_lines: int = 3) -> str:
    """
    Create a unified diff between two sets of lines.
    
    Args:
        a_lines: Lines from the first file
        b_lines: Lines from the second file
        a_name: Name of the first file
        b_name: Name of the second file
        context_lines: Number of context lines to show
    
    Returns:
        A string containing the unified diff
    """
    diff = unified_diff(
        a_lines, b_lines,
        fromfile=a_name, tofile=b_name,
        lineterm="", n=context_lines
    )
    return "\n".join(diff)


def get_diff_stats(diff: str) -> Tuple[int, int, int]:
    """
    Get statistics from a diff string.
    
    Args:
        diff: The diff string
    
    Returns:
        A tuple of (files_changed, insertions, deletions)
    """
    files_changed = 0
    insertions = 0
    deletions = 0
    
    for line in diff.split("\n"):
        if line.startswith("---") and not line.startswith("--- /dev/null"):
            files_changed += 1
        elif line.startswith("+") and not line.startswith("+++"):
            insertions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    
    return files_changed, insertions, deletions


def generate_patch(diff: str, filename: str) -> None:
    """
    Generate a patch file from a diff string.
    
    Args:
        diff: The diff string
        filename: The name of the patch file to create
    """
    with open(filename, "w") as f:
        f.write(diff)