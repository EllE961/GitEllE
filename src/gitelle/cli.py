"""
Command-line interface for GitEllE.
"""
import sys
from pathlib import Path
from typing import Optional

import click

from gitelle.commands.add import add
from gitelle.commands.branch import branch
from gitelle.commands.checkout import checkout
from gitelle.commands.clone import clone
from gitelle.commands.commit import commit
from gitelle.commands.diff import diff
from gitelle.commands.init import init
from gitelle.commands.log import log
from gitelle.commands.reset import reset
from gitelle.commands.status import status


@click.group()
@click.version_option(package_name="gitelle")
def main():
    """
    GitEllE: A lightweight Git implementation in Python.
    
    GitEllE is an educational implementation of Git that aims to provide
    a clear understanding of Git's internal mechanisms while maintaining
    compatibility with the original Git commands.
    """
    pass


# Register commands
main.add_command(init)
main.add_command(clone)
main.add_command(add)
main.add_command(commit)
main.add_command(status)
main.add_command(branch)
main.add_command(checkout)
main.add_command(log)
main.add_command(diff)
main.add_command(reset)


if __name__ == "__main__":
    main()