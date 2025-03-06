"""
Implementation of the 'status' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import click

from gitelle.core.repository import Repository
from gitelle.utils.filesystem import walk_files


def get_status(repo: Repository) -> Tuple[List[str], List[str], List[str]]:
    """
    Get the status of the working directory.
    
    Args:
        repo: The repository
    
    Returns:
        A tuple of (staged_files, unstaged_files, untracked_files)
    """
    # Get all files in the working directory
    working_files = set(str(f) for f in walk_files(repo.path))
    
    # Get all files in the index
    index_files = set(repo.index.entries.keys())
    
    # Get all files in the current commit (if any)
    head_tree_id = None
    head_target = repo.head.get_resolved_target()
    if head_target:
        head_commit = repo.get_object(head_target)
        head_tree_id = head_commit.tree_id
    
    head_files = set()
    if head_tree_id:
        # In a real implementation, this would traverse the tree
        # For simplicity, we'll assume it's empty
        pass
    
    # Calculate the status
    staged_files = []
    unstaged_files = []
    untracked_files = []
    
    # Files staged for commit (in index but not in HEAD)
    for file in sorted(index_files - head_files):
        if file in working_files:
            # Check if the file has been modified since it was staged
            abs_path = repo.path / file
            if abs_path.exists():
                index_entry = repo.index.entries[file]
                file_stat = abs_path.stat()
                
                # Compare size and modification time
                if (index_entry.size != file_stat.st_size or
                    index_entry.mtime != int(file_stat.st_mtime)):
                    unstaged_files.append(file)
            
            staged_files.append(file)
        else:
            # File was staged for removal
            staged_files.append(file)
    
    # Files modified but not staged (in working dir and HEAD, but different from index)
    for file in sorted(head_files & working_files):
        if file not in index_files:
            unstaged_files.append(file)
    
    # Untracked files (in working dir but not in index or HEAD)
    for file in sorted(working_files - index_files - head_files):
        # Skip files in .gitelle directory
        if not file.startswith(".gitelle/"):
            untracked_files.append(file)
    
    return staged_files, unstaged_files, untracked_files


@click.command()
@click.option("-s", "--short", is_flag=True, help="Give the output in the short format")
def status(short: bool = False) -> None:
    """
    Show the working tree status.
    
    Displays the paths that have differences between the index file and the
    current HEAD commit, paths that have differences between the working
    tree and the index file, and paths in the working tree that are not
    tracked by GitEllE.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo("fatal: not a git repository (or any of the parent directories)", err=True)
        sys.exit(1)
    
    try:
        # Get the current branch name
        branch_name = "detached HEAD"
        if repo.head.is_symbolic:
            ref_name = repo.head.target
            if ref_name.startswith("refs/heads/"):
                branch_name = ref_name[11:]
        
        # Get the status
        staged_files, unstaged_files, untracked_files = get_status(repo)
        
        # Display the status
        if short:
            # Display in short format
            for file in staged_files:
                click.echo(f"A {file}")
            for file in unstaged_files:
                click.echo(f"M {file}")
            for file in untracked_files:
                click.echo(f"? {file}")
        else:
            # Display in long format
            click.echo(f"On branch {branch_name}")
            
            if not staged_files and not unstaged_files and not untracked_files:
                click.echo("nothing to commit, working tree clean")
            else:
                if staged_files:
                    click.echo("\nChanges to be committed:")
                    click.echo("  (use \"gitelle reset HEAD <file>...\" to unstage)")
                    for file in staged_files:
                        click.echo(f"        new file:   {file}")
                
                if unstaged_files:
                    click.echo("\nChanges not staged for commit:")
                    click.echo("  (use \"gitelle add <file>...\" to update what will be committed)")
                    click.echo("  (use \"gitelle checkout -- <file>...\" to discard changes in working directory)")
                    for file in unstaged_files:
                        click.echo(f"        modified:   {file}")
                
                if untracked_files:
                    click.echo("\nUntracked files:")
                    click.echo("  (use \"gitelle add <file>...\" to include in what will be committed)")
                    for file in untracked_files:
                        click.echo(f"        {file}")
    
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)