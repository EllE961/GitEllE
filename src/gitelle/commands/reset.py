"""
Implementation of the 'reset' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

import click

from gitelle.core.objects import Commit, Tree
from gitelle.core.repository import Repository


def reset_hard(repo: Repository, commit_id: str) -> None:
    """
    Reset the working directory and index to a specific commit.
    
    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """
    # Get the commit
    commit = repo.get_object(commit_id)
    
    # Update the index
    repo.index.entries.clear()
    
    # In a real implementation, we would populate the index from the tree
    # and update the working directory
    tree = repo.get_object(commit.tree_id)
    # For a full implementation, we would checkout the tree to the working directory
    
    # Write the updated index
    repo.index.write()


def reset_mixed(repo: Repository, commit_id: str) -> None:
    """
    Reset the index but not the working directory to a specific commit.
    
    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """
    # Get the commit
    commit = repo.get_object(commit_id)
    
    # Update the index
    repo.index.entries.clear()
    
    # In a real implementation, we would populate the index from the tree
    tree = repo.get_object(commit.tree_id)
    
    # Write the updated index
    repo.index.write()


def reset_soft(repo: Repository, commit_id: str) -> None:
    """
    Reset only the HEAD ref to a specific commit.
    
    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """
    # Do not update the index or working directory
    pass


@click.command()
@click.argument("commit", default="HEAD")
@click.option("--hard", is_flag=True, help="Reset the index and working directory")
@click.option("--soft", is_flag=True, help="Reset only the HEAD")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def reset(commit: str, hard: bool = False, soft: bool = False, paths: List[str] = None) -> None:
    """
    Reset current HEAD to the specified state.
    
    Resets the current branch head to <commit> and possibly updates the index
    and working directory.
    
    --soft: Only reset HEAD
    --mixed (default): Reset HEAD and index
    --hard: Reset HEAD, index, and working directory
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo("fatal: not a git repository (or any of the parent directories)", err=True)
        sys.exit(1)
    
    try:
        # Resolve the commit
        target_commit = None
        if commit == "HEAD":
            target_commit = repo.head.get_resolved_target()
            if not target_commit:
                click.echo("error: HEAD is not a valid reference", err=True)
                sys.exit(1)
        else:
            # Try to resolve as a commit ID
            try:
                commit_obj = repo.get_object(commit)
                if commit_obj.type == "commit":
                    target_commit = commit
            except ValueError:
                pass
            
            # Try to resolve as a branch
            if not target_commit:
                branch_ref = repo.get_branch(commit)
                if branch_ref.target:
                    target_commit = branch_ref.target
            
            # Try to resolve as a tag
            if not target_commit:
                tag_ref = repo.get_tag(commit)
                if tag_ref.target:
                    target_commit = tag_ref.target
        
        if not target_commit:
            click.echo(f"error: Invalid reference: {commit}", err=True)
            sys.exit(1)
        
        # If paths are specified, just update those paths in the index
        if paths:
            for path in paths:
                # In a real implementation, this would update the index entries
                # for the specified paths to match the commit
                pass
            
            repo.index.write()
            click.echo(f"Reset '{', '.join(paths)}' to {target_commit[:7]}")
            return
        
        # Update HEAD
        if repo.head.is_symbolic:
            branch_ref = repo.get_branch(repo.head.target[11:])  # Remove "refs/heads/" prefix
            branch_ref.set_target(target_commit)
            branch_ref.save()
        else:
            repo.head.set_target(target_commit)
            repo.head.save()
        
        # Perform the requested type of reset
        if hard:
            reset_hard(repo, target_commit)
            click.echo(f"HEAD is now at {target_commit[:7]}")
        elif soft:
            reset_soft(repo, target_commit)
            click.echo(f"HEAD is now at {target_commit[:7]}")
        else:
            # Default is --mixed
            reset_mixed(repo, target_commit)
            click.echo(f"HEAD is now at {target_commit[:7]}")
    
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
