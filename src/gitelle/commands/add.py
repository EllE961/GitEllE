"""
Implementation of the 'add' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import List

import click

from gitelle.core.repository import Repository


@click.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
def add(paths: List[str]) -> None:
    """
    Add file contents to the index.

    This command updates the index using the current content found in the
    working tree, to prepare the content staged for the next commit.
    """
    # Find the repository
    repo = Repository.find()
    if repo is None:
        click.echo(
            "fatal: not a git repository (or any of the parent directories)",
            err=True)
        sys.exit(1)

    try:
        # Convert paths to be relative to the repository root
        relative_paths = []
        for path in paths:
            abs_path = Path(path).absolute()
            try:
                rel_path = abs_path.relative_to(repo.path)
                relative_paths.append(rel_path)
            except ValueError:
                click.echo(
                    f"error: pathspec '{path}' did not match any files",
                    err=True)

        # Add the files to the index
        if relative_paths:
            repo.index.add(relative_paths)
            repo.index.write()

            # Print a summary
            file_count = len(relative_paths)
            if file_count == 1:
                click.echo(f"Added 1 file to the index")
            else:
                click.echo(f"Added {file_count} files to the index")

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
