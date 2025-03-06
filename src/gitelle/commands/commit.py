"""
Implementation of the 'commit' command for GitEllE.
"""
import os
import sys
import time
from typing import Optional

import click

from gitelle.core.objects import Commit
from gitelle.core.repository import Repository


def get_author_info() -> str:
    """
    Get the author information from git config or environment variables.

    Returns:
        A string in the format "Name <email> timestamp"
    """
    # In a real implementation, this would read from git config files
    # For simplicity, we'll use environment variables
    name = os.environ.get("GIT_AUTHOR_NAME", "Unknown")
    email = os.environ.get("GIT_AUTHOR_EMAIL", "unknown@example.com")

    # Get current time
    timestamp = int(time.time())
    timezone_offset = time.strftime("%z")

    return f"{name} <{email}> {timestamp} {timezone_offset}"


def create_commit(
        repo: Repository,
        message: str,
        author: Optional[str] = None) -> str:
    """
    Create a new commit in the repository.

    Args:
        repo: The repository
        message: The commit message
        author: The author information (
if None,
            get_author_info() will be used
        )


    Returns:
        The ID of the new commit

    Raises:
        ValueError: If the index is empty
    """
    # Create a tree from the index
    tree_id = repo.index.get_tree_id()

    if tree_id is None:
        raise ValueError("Nothing to commit (empty index)")

    # Get author and committer information
    author_info = author or get_author_info()
    committer_info = author_info  # Use the same info for committer

    # Create the commit object
    commit = Commit(repo)
    commit.tree_id = tree_id

    # Set parent commit (if HEAD exists)
    head_target = repo.head.get_resolved_target()
    if head_target:
        commit.parent_ids.append(head_target)

    # Set author, committer, and message
    commit.author = author_info
    commit.committer = committer_info
    commit.message = message

    # Write the commit object
    commit_id = commit.write()

    # Update HEAD
    if repo.head.is_symbolic:
        # Update the branch that HEAD points to
        branch_ref = Repository.from_path(repo, repo.head.target)
        branch_ref.set_target(commit_id)
        branch_ref.save()
    else:
        # Update HEAD directly (detached HEAD state)
        repo.head.set_target(commit_id)
        repo.head.save()

    return commit_id


@click.command()
@click.option("-m", "--message", help="Commit message")
@click.option("--author", help="Override author for commit")
def commit(message: Optional[str] = None,
           author: Optional[str] = None) -> None:
    """
    Record changes to the repository.

    Creates a new commit containing the current contents of the index
    with the given message describing the changes.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo(
            "fatal: not a git repository (or any of the parent directories)",
            err=True)
        sys.exit(1)

    # Get the commit message
    if message is None:
        # In a real implementation, this would open an editor
        click.echo("Aborting commit due to empty commit message.", err=True)
        sys.exit(1)

    try:
        # Create the commit
        commit_id = create_commit(repo, message, author)

        # Display the result
        click.echo(
            f"[{repo.head.target.split('/')[-1]} {commit_id[:7]}] {message}")

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
