"""
Implementation of the 'log' command for GitEllE.
"""
import sys
import time
from datetime import datetime, timezone
from typing import List, Optional

import click

from gitelle.core.objects import Commit
from gitelle.core.repository import Repository


def format_commit(commit: Commit, short: bool = False) -> str:
    """
    Format a commit for display.
    
    Args:
        commit: The commit to format
        short: Whether to use a short format
    
    Returns:
        A formatted string representing the commit
    """
    # Parse author info
    author_parts = commit.author.split(" ")
    email_start = commit.author.find("<")
    email_end = commit.author.find(">")
    
    if email_start != -1 and email_end != -1:
        author_name = commit.author[:email_start].strip()
        author_email = commit.author[email_start+1:email_end]
    else:
        author_name = commit.author
        author_email = ""
    
    # Parse timestamp
    timestamp_parts = commit.author.split(" ")
    if len(timestamp_parts) > 2:
        try:
            timestamp = int(timestamp_parts[-2])
            date = datetime.fromtimestamp(timestamp, timezone.utc)
            date_str = date.strftime("%a %b %d %H:%M:%S %Y %z")
        except (ValueError, IndexError):
            date_str = "Unknown date"
    else:
        date_str = "Unknown date"
    
    if short:
        # Use a raw string to avoid the backslash issue
        first_line = commit.message.split("\n")[0]
        return f"commit {commit.id[:7]} - {first_line}"
    else:
        output = [
            f"commit {commit.id}",
            f"Author: {author_name} <{author_email}>",
            f"Date:   {date_str}",
            "",
            f"    {commit.message.strip()}",
            ""
        ]
        return "\n".join(output)


def get_commit_history(repo: Repository, start_commit_id: str, max_count: Optional[int] = None) -> List[Commit]:
    """
    Get the commit history starting from a specific commit.
    
    Args:
        repo: The repository
        start_commit_id: The ID of the commit to start from
        max_count: The maximum number of commits to return
    
    Returns:
        A list of commits in chronological order (newest first)
    """
    commits = []
    current_id = start_commit_id
    count = 0
    
    while current_id and (max_count is None or count < max_count):
        try:
            commit = repo.get_object(current_id)
            commits.append(commit)
            count += 1
            
            # Move to the first parent
            if commit.parent_ids:
                current_id = commit.parent_ids[0]
            else:
                break
        except ValueError:
            break
    
    return commits


@click.command()
@click.option("-n", "--max-count", type=int, help="Limit the number of commits to show")
@click.option("--oneline", is_flag=True, help="Show each commit on a single line")
def log(max_count: Optional[int] = None, oneline: bool = False) -> None:
    """
    Show commit logs.
    
    Displays the commit history of the current branch.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo("fatal: not a git repository (or any of the parent directories)", err=True)
        sys.exit(1)
    
    try:
        # Get the current commit
        head_target = repo.head.get_resolved_target()
        if not head_target:
            click.echo("fatal: your current branch appears to be broken", err=True)
            sys.exit(1)
        
        # Get the commit history
        commits = get_commit_history(repo, head_target, max_count)
        
        # Display the commits
        for commit in commits:
            click.echo(format_commit(commit, oneline))
            if not oneline and commit != commits[-1]:
                click.echo("")
    
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)