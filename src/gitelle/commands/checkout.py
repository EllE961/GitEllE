"""
Implementation of the 'checkout' command for GitEllE.
"""
import os
import sys

import click

from gitelle.core.repository import Repository
from gitelle.utils.filesystem import write_file


def checkout_tree(repo: Repository, tree_id: str, prefix: str = "") -> None:
    """
    Checkout a tree into the working directory.

    Args:
        repo: The repository
        tree_id: The ID of the tree to checkout
        prefix: The prefix path to checkout to
    """
    tree = repo.get_object(tree_id)

    for entry in tree.entries:
        path = os.path.join(prefix, entry.name)

        if entry.mode.startswith("10"):  # Regular file
            # Get the blob object
            blob = repo.get_object(entry.id)

            # Write the file
            abs_path = repo.path / path
            write_file(abs_path, blob.data)

            # Set the file mode
            if entry.mode == "100755":  # Executable
                os.chmod(abs_path, 0o755)
            else:
                os.chmod(abs_path, 0o644)

        elif entry.mode.startswith("40"):  # Directory
            # Create the directory
            os.makedirs(repo.path / path, exist_ok=True)

            # Checkout the subtree
            checkout_tree(repo, entry.id, path)


def checkout_ref(repo: Repository, ref_name: str) -> None:
    """
    Checkout a reference (branch, tag, or commit).

    Args:
        repo: The repository
        ref_name: The name of the reference to checkout

    Raises:
        ValueError: If the reference is invalid
    """
    # Get the commit ID
    commit_id = None

    # First, try to resolve as a branch
    branch_ref = repo.get_branch(ref_name)
    if branch_ref.target:
        commit_id = branch_ref.target

        # Update HEAD to point to the branch
        repo.head.set_target(f"refs/heads/{ref_name}", symbolic=True)
        repo.head.save()
    else:
        # Try to resolve as a commit ID
        try:
            commit = repo.get_object(ref_name)
            if commit.type == "commit":
                commit_id = ref_name

                # Update HEAD to point directly to the commit
                repo.head.set_target(commit_id)
                repo.head.save()
        except ValueError:
            pass

    if not commit_id:
        raise ValueError(f"invalid reference: {ref_name}")

    # Get the tree from the commit
    commit = repo.get_object(commit_id)
    tree_id = commit.tree_id

    # Checkout the tree
    checkout_tree(repo, tree_id)

    # Update the index
    # In a real implementation, this would update the index to match the tree
    # For simplicity, we'll just clear the index
    repo.index.entries.clear()
    repo.index.write()


@click.command()
@click.argument("ref_name", required=True)
@click.option("-b", "--branch", is_flag=True,
              help="Create and checkout a new branch")
def checkout(ref_name: str, branch: bool = False) -> None:
    """
    Checkout a branch, tag, or commit.

    Updates files in the working tree to match the version in the index
    or the specified tree.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo(
            "fatal: not a git repository (or any of the parent directories)",
            err=True)
        sys.exit(1)

    try:
        if branch:
            # Create and checkout a new branch
            branch_ref = repo.get_branch(ref_name)
            if branch_ref.target:
                click.echo(
                    f"fatal: a branch named '{ref_name}' already exists",
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

            # Checkout the branch
            checkout_ref(repo, ref_name)

            click.echo(f"Switched to a new branch '{ref_name}'")
        else:
            # Checkout an existing reference
            old_branch = None
            if repo.head.is_symbolic and repo.head.target.startswith(
                    "refs/heads/"):
                old_branch = repo.head.target[11:]

            checkout_ref(repo, ref_name)

            if old_branch:
                if ref_name == old_branch:
                    click.echo(f"Already on '{ref_name}'")
                else:
                    click.echo(f"Switched from '{old_branch}' to '{ref_name}'")
            else:
                click.echo(f"Switched to '{ref_name}'")

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
