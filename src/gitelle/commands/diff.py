"""
Implementation of the 'diff' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from gitelle.core.objects import Blob
from gitelle.core.repository import Repository
from gitelle.utils.diff import create_unified_diff, get_diff_stats
from gitelle.utils.filesystem import read_file


def get_blob_content(repo: Repository, blob_id: str) -> List[str]:
    """
    Get the content of a blob as a list of lines.
    
    Args:
        repo: The repository
        blob_id: The ID of the blob
    
    Returns:
        The content of the blob as a list of lines
    """
    try:
        blob = repo.get_object(blob_id)
        content = blob.data.decode('utf-8', errors='replace')
        return content.splitlines()
    except Exception:
        return []


def get_file_content(path: Path) -> List[str]:
    """
    Get the content of a file as a list of lines.
    
    Args:
        path: The path to the file
    
    Returns:
        The content of the file as a list of lines
    """
    try:
        content = read_file(path)
        return content.decode('utf-8', errors='replace').splitlines()
    except Exception:
        return []


def diff_index_to_worktree(repo: Repository, paths: List[Path] = None) -> str:
    """
    Show changes between index and working tree.
    
    Args:
        repo: The repository
        paths: The paths to show changes for (default: all)
    
    Returns:
        A string containing the unified diff
    """
    result = []
    
    # Get all the files in the index
    index_files = list(repo.index.entries.keys())
    
    # Filter by paths if specified
    if paths:
        path_strs = [str(p) for p in paths]
        index_files = [f for f in index_files if f in path_strs]
    
    # Compare each file in the index with the working tree
    for index_file in sorted(index_files):
        index_entry = repo.index.entries[index_file]
        file_path = repo.path / index_file
        
        # Skip files that don't exist in the working tree
        if not file_path.exists():
            continue
        
        # Get the content of the blob in the index
        index_content = get_blob_content(repo, index_entry.object_id)
        
        # Get the content of the file in the working tree
        worktree_content = get_file_content(file_path)
        
        # Create a diff
        diff = create_unified_diff(
            index_content, worktree_content,
            f"a/{index_file}", f"b/{index_file}"
        )
        
        if diff:
            result.append(diff)
    
    return "\n\n".join(result)


def diff_commits(repo: Repository, commit1_id: str, commit2_id: str, paths: List[Path] = None) -> str:
    """
    Show changes between two commits.
    
    Args:
        repo: The repository
        commit1_id: The ID of the first commit
        commit2_id: The ID of the second commit
        paths: The paths to show changes for (default: all)
    
    Returns:
        A string containing the unified diff
    """
    # In a real implementation, this would:
    # 1. Get the tree for each commit
    # 2. Compare the trees to find changed files
    # 3. Generate diffs for the changed files
    
    return "Diff between commits not implemented in this educational version."


@click.command()
@click.option("--cached", is_flag=True, help="Show changes in the index")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def diff(cached: bool = False, paths: List[str] = None) -> None:
    """
    Show changes between commits, commit and working tree, etc.
    
    By default, shows changes between the working tree and the index.
    With --cached, shows changes between the index and the current HEAD.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo("fatal: not a git repository (or any of the parent directories)", err=True)
        sys.exit(1)
    
    try:
        # Convert paths to Path objects
        path_objs = None
        if paths:
            path_objs = [Path(p).relative_to(repo.path) for p in paths]
        
        if cached:
            # Show diff between HEAD and index
            head_target = repo.head.get_resolved_target()
            if not head_target:
                click.echo("error: HEAD is not a valid reference", err=True)
                sys.exit(1)
            
            # In a real implementation, this would generate a diff
            # between the HEAD commit and the index
            click.echo("Diff between HEAD and index not implemented in this educational version.")
        else:
            # Show diff between index and working tree
            diff_output = diff_index_to_worktree(repo, path_objs)
            if diff_output:
                click.echo(diff_output)
            else:
                click.echo("No changes.")
    
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)