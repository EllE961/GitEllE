"""
Implementation of the 'clone' command for GitEllE.
"""
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import click

from gitelle.commands.init import init_repository


@click.command()
@click.argument("url", required=True)
@click.argument("directory", required=False)
@click.option("--depth", type=int,
              help=
                  'Create a shallow clone with a history truncated to the spe' +
                      'cified number of commits')
def clone(
        url: str,
        directory: Optional[str] = None,
        depth: Optional[int] = None) -> None:
    """
    Clone a repository into a new directory.

    Note: In this educational implementation, we don't actually fetch from remote repositories.
    This command creates an empty repository structure that simulates a cloned \
        \
        repository.
    """
    try:
        # Parse the URL to get the repository name
        parsed_url = urlparse(url)
        repo_name = os.path.basename(parsed_url.path)
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        # Determine the target directory
        target_dir = directory or repo_name
        target_path = Path(target_dir)

        # Check if the target directory already exists
        if target_path.exists() and os.listdir(target_path):
            click.echo(
                'fatal: destination path '{target_dir}' already exists and i' +
                    's not an empty directory',
                err=True)
            sys.exit(1)

        # Create the directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)

        # Initialize a new repository
        repo = init_repository(target_path)

        # In a real implementation, we would now fetch objects from the
            remote repository
        # and update the local references. For this simplified version, we'll just
        # acknowledge that we've created an empty repository structure.

        # Set up a remote
        config_file = repo.gitelle_dir / "config"
        with open(config_file, "w") as f:
            f.write("""[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "origin"]
        url = {url}
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
        remote = origin
        merge = refs/heads/main
""")

        click.echo(f"Initialized empty GitEllE repository in {target_path}")
        click.echo(
            'Note: This is a simulated clone and' +
                'does not actually fetch from the remote.')
        click.echo(
            f'To work with a real Git repository, use: git clone {url} {targe' +
                't_dir}')

    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
