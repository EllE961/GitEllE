# Commands API Reference

This document describes the command-line interface components of GitEllE, focusing on the classes and functions in the `gitelle.commands` module.

## Command Structure

All GitEllE commands follow a consistent structure using the Click library:

1. A main function decorated with `@click.command()`
2. Arguments and options defined with `@click.argument()` and `@click.option()`
3. Implementation that performs the command's operations

Each command is defined in its own module under `gitelle.commands`.

## Core Commands

### Init Command

```python
from gitelle.commands.init import init, init_repository
```

The `init` command initializes a new Git repository.

#### Function: `init_repository`

```python
def init_repository(path: Optional[str] = None, bare: bool = False) -> Repository:
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
```

#### Command: `init`

```
gitelle init [directory]
```

Options:

-   `--bare`: Create a bare repository

### Add Command

```python
from gitelle.commands.add import add
```

The `add` command adds files to the staging area.

#### Command: `add`

```
gitelle add <paths>...
```

### Commit Command

```python
from gitelle.commands.commit import commit, create_commit
```

The `commit` command records changes to the repository.

#### Function: `create_commit`

```python
def create_commit(repo: Repository, message: str, author: Optional[str] = None) -> str:
    """
    Create a new commit in the repository.

    Args:
        repo: The repository
        message: The commit message
        author: The author information (if None, get_author_info() will be used)

    Returns:
        The ID of the new commit

    Raises:
        ValueError: If the index is empty
    """
```

#### Command: `commit`

```
gitelle commit -m <message>
```

Options:

-   `-m, --message`: Commit message
-   `--author`: Override author for commit

### Status Command

```python
from gitelle.commands.status import status, get_status
```

The `status` command shows the working tree status.

#### Function: `get_status`

```python
def get_status(repo: Repository) -> Tuple[List[str], List[str], List[str]]:
    """
    Get the status of the working directory.

    Args:
        repo: The repository

    Returns:
        A tuple of (staged_files, unstaged_files, untracked_files)
    """
```

#### Command: `status`

```
gitelle status
```

Options:

-   `-s, --short`: Give the output in short format

### Branch Command

```python
from gitelle.commands.branch import branch
```

The `branch` command lists, creates, or deletes branches.

#### Command: `branch`

```
gitelle branch [branch_name]
```

Options:

-   `-d, --delete`: Delete a branch
-   `-v, --verbose`: Show commit message in output

### Checkout Command

```python
from gitelle.commands.checkout import checkout, checkout_ref
```

The `checkout` command switches branches or restores working tree files.

#### Function: `checkout_ref`

```python
def checkout_ref(repo: Repository, ref_name: str) -> None:
    """
    Checkout a reference (branch, tag, or commit).

    Args:
        repo: The repository
        ref_name: The name of the reference to checkout

    Raises:
        ValueError: If the reference is invalid
    """
```

#### Command: `checkout`

```
gitelle checkout <ref_name>
```

Options:

-   `-b, --branch`: Create and checkout a new branch

### Log Command

```python
from gitelle.commands.log import log, get_commit_history
```

The `log` command shows commit logs.

#### Function: `get_commit_history`

```python
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
```

#### Command: `log`

```
gitelle log
```

Options:

-   `-n, --max-count`: Limit the number of commits to output
-   `--oneline`: Show each commit on a single line

### Clone Command

```python
from gitelle.commands.clone import clone
```

The `clone` command clones a repository into a new directory.

#### Command: `clone`

```
gitelle clone <url> [directory]
```

Options:

-   `--depth`: Create a shallow clone with a history truncated to the specified number of commits

### Diff Command

```python
from gitelle.commands.diff import diff, diff_index_to_worktree
```

The `diff` command shows changes between commits, commit and working tree, etc.

#### Function: `diff_index_to_worktree`

```python
def diff_index_to_worktree(repo: Repository, paths: List[Path] = None) -> str:
    """
    Show changes between index and working tree.

    Args:
        repo: The repository
        paths: The paths to show changes for (default: all)

    Returns:
        A string containing the unified diff
    """
```

#### Command: `diff`

```
gitelle diff [paths]...
```

Options:

-   `--cached`: Show changes in the index

### Reset Command

```python
from gitelle.commands.reset import reset, reset_hard, reset_mixed, reset_soft
```

The `reset` command resets current HEAD to the specified state.

#### Functions

```python
def reset_hard(repo: Repository, commit_id: str) -> None:
    """
    Reset the working directory and index to a specific commit.

    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """

def reset_mixed(repo: Repository, commit_id: str) -> None:
    """
    Reset the index but not the working directory to a specific commit.

    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """

def reset_soft(repo: Repository, commit_id: str) -> None:
    """
    Reset only the HEAD ref to a specific commit.

    Args:
        repo: The repository
        commit_id: The ID of the commit to reset to
    """
```

#### Command: `reset`

```
gitelle reset [--soft|--mixed|--hard] [commit]
```

Options:

-   `--soft`: Reset only the HEAD
-   `--mixed`: (Default) Reset HEAD and index
-   `--hard`: Reset HEAD, index, and working directory

## Using Commands Programmatically

While the commands are primarily designed for CLI use, you can also use their underlying functions programmatically:

```python
from gitelle.core.repository import Repository
from gitelle.commands.init import init_repository
from gitelle.commands.add import add_files_to_index
from gitelle.commands.commit import create_commit

# Initialize a repository
repo = init_repository("/path/to/repo")

# Add files to the index
add_files_to_index(repo, ["file1.txt", "file2.txt"])

# Create a commit
commit_id = create_commit(repo, "Add initial files")
```

## Extending the Command Line Interface

To add a new command to GitEllE:

1. Create a new module in `gitelle.commands`
2. Implement your command using Click
3. Register it in `gitelle.cli`

Example:

```python
# In gitelle/commands/new_command.py
import click
from gitelle.core.repository import Repository

@click.command()
@click.argument("arg")
def new_command(arg):
    """
    Your command description.
    """
    repo = Repository.find()
    if repo is None:
        click.echo("Not a git repository", err=True)
        return 1

    # Command implementation
    click.echo(f"Executed new command with {arg}")
    return 0

# In gitelle/cli.py
from gitelle.commands.new_command import new_command

# ...

main.add_command(new_command)
```

## Error Handling

Commands should handle errors gracefully and provide informative error messages:

1. Catch exceptions and display user-friendly error messages
2. Return appropriate exit codes (0 for success, non-zero for errors)
3. Use `click.echo()` with `err=True` for error messages to output to stderr

```python
try:
    # Command logic
    pass
except Exception as e:
    click.echo(f"Error: {e}", err=True)
    return 1
```
