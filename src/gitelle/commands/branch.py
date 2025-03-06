"""
Implementation of the 'branch' command for GitEllE.
"""
import sys
from typing import Optional

import click

from gitelle.core.repository import Repository


@click.command()
@click.argument("branch_name", required=False)
@click.option("-d", "--delete", is_flag=True, help="Delete a branch")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def branch(
        branch_name: Optional[str] = None,
        delete: bool = False,
        verbose: bool = False) -> None:
    """
    List, create, or delete branches.

    With no arguments, list all local branches.
    With a branch name, create a new branch.
    With --delete, delete the specified branch.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo(
            "fatal: not a git repository (or any of the parent directories)",
            err=True)
        sys.exit(1)

    try:
        if branch_name and delete:
            # Delete branch
            branch_ref = repo.get_branch(branch_name)
            if not branch_ref.target:
                click.echo(
                    f"error: branch '{branch_name}' not found",
                    err=True)
                sys.exit(1)

            # Check if it's the current branch
            if repo.head.is_symbolic and repo.head.target=
                = f"refs/heads/{branch_name}":
                click.echo(
                    f"error: cannot delete branch '{branch_name}' checked out at '{repo.path}'",
                    err=True)
                sys.exit(1)

            branch_ref.delete()
            click.echo(f"Deleted branch {branch_name}")

        elif branch_name:
            # Create branch
            branch_ref = repo.get_branch(branch_name)
            if branch_ref.target:
                click.echo(
                    f"fatal: a branch named '{branch_name}' already exists",
                    err=True)
                sys.exit(1)

            # Get the current HEAD
            head_target = repo.head.get_resolved_target()
            if not head_target:
                click.echo("error: not a valid object name: 'HEAD'", err=True)
                sys.exit(1)

            # Create the branch
            branch_ref.set_target(head_target)
            branch_ref.save()
            click.echo(f"Branch '{branch_name}' created at {head_target[:7]}")

        else:
            # List branches
            branches = repo.get_branches()

            # Get the current branch
            current_branch = None
            if repo.head.is_symbolic and repo.head.target.startswith(
                    "refs/heads/"):
                current_branch = repo.head.target[11:]

            for branch_name in sorted(branches):
                indicator = "* " if branch_name == current_branch else "  "

                if verbose:
                    # Get the commit ID
                    branch_ref = repo.get_branch(branch_name)
                    commit_id = branch_ref.target
                    commit = repo.get_object(commit_id)
                    message = commit.message.split("\n")[0]
                    click.echo(
                        f"{indicator}{branch_name} {commit_id[:7]} {message}")
                else:
                    click.echo(f"{indicator}{branch_name}")

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
