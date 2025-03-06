"""
Implementation of the 'init' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click

from gitelle.core.repository import Repository


def init_repository(
        path: Optional[str] = None,
        bare: bool = False) -> Repository:
    """
    Initialize a new GitEllE repository.

    Args:
        path: The path where the repository should be initialized.
              If None, the current directory is used.
        bare: Whether to create a bare repository (without a working directory).
              Not fully implemented yet.

    Returns:
        A new Repository instance

    Raises:
        ValueError: If a repository already exists at the given path
    """
    if path is None:
        path = os.getcwd()

    path = Path(path).absolute()
    gitelle_dir = path / Repository.GITELLE_DIR

    # Check if a repository already exists
    if gitelle_dir.exists():
        raise ValueError(f"A GitEllE repository already exists at {path}")

    # Create the repository
    repo = Repository.init(path)

    return repo


@click.command()
@click.option("--bare", is_flag=True, help="Create a bare repository")
@click.argument("path", required=False)
def init(path: Optional[str] = None, bare: bool = False) -> None:
    """
    Initialize a new GitEllE repository.

    If PATH is not specified, the current directory is used.
    """
    try:
        repo = init_repository(path, bare)
        click.echo(
            f"Initialized empty GitEllE repository in {repo.gitelle_dir}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
