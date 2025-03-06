# Usage Guide

This guide covers the basic commands and workflow of GitEllE.

## Getting Started

After [installing GitEllE](installation.md), you can start using it from the command line.

### Basic Workflow

The typical Git workflow with GitEllE involves:

1. Creating or cloning a repository
2. Making changes to files
3. Staging changes for commit
4. Committing changes
5. Working with branches

## Command Reference

### Initialize a Repository

To create a new repository:

```bash
gitelle init [directory]
```

If `directory` is omitted, the current directory is used.

Example:

```bash
mkdir my-project
cd my-project
gitelle init
```

### Clone a Repository

To clone an existing repository:

```bash
gitelle clone <url> [directory]
```

Example:

```bash
gitelle clone https://github.com/example/repo.git my-local-repo
```

Note: In this educational implementation, cloning creates an empty repository structure rather than actually fetching remote content.

### Check Repository Status

To see the status of your working directory:

```bash
gitelle status
```

This shows:

-   Which branch you're on
-   Changes staged for commit
-   Changes not staged for commit
-   Untracked files

### Add Files to the Staging Area

To stage files for the next commit:

```bash
gitelle add <file1> [file2] [...]
```

To stage all changes:

```bash
gitelle add .
```

### Commit Changes

To commit staged changes:

```bash
gitelle commit -m "Commit message"
```

### Working with Branches

Create a new branch:

```bash
gitelle branch <branch-name>
```

List all branches:

```bash
gitelle branch
```

Switch to a branch:

```bash
gitelle checkout <branch-name>
```

Create and switch to a new branch:

```bash
gitelle checkout -b <branch-name>
```

### View Commit History

To see the commit history:

```bash
gitelle log
```

For a condensed one-line view:

```bash
gitelle log --oneline
```

Limit the number of commits shown:

```bash
gitelle log -n 5
```

### Compare Changes

View differences between the working directory and the staging area:

```bash
gitelle diff
```

View staged changes:

```bash
gitelle diff --cached
```

### Reset Changes

Reset to a specific commit:

```bash
gitelle reset <commit>
```

Reset options:

-   `--soft`: Keep changes in staging area
-   `--mixed` (default): Keep changes in working directory
-   `--hard`: Discard all changes

Example:

```bash
gitelle reset --hard HEAD~1  # Discard the last commit
```

## Advanced Usage

### Working with Remotes

Note: In this educational implementation, remote operations are simulated.

Add a remote:

```bash
gitelle remote add <name> <url>
```

List remotes:

```bash
gitelle remote -v
```

### Git Configuration

GitEllE reads Git configuration from:

-   System level: `/etc/gitconfig`
-   Global level: `~/.gitconfig`
-   Repository level: `.gitelle/config`

## Examples

### Complete Workflow Example

```bash
# Create a new repository
mkdir example-project
cd example-project
gitelle init

# Create a file and make initial commit
echo "# Example Project" > README.md
gitelle add README.md
gitelle commit -m "Initial commit"

# Create a feature branch
gitelle checkout -b feature-branch

# Make changes
echo "New feature content" > feature.txt
gitelle add feature.txt
gitelle commit -m "Add new feature"

# Switch back to main branch
gitelle checkout main

# Merge feature branch (in a full implementation)
# gitelle merge feature-branch

# View history
gitelle log
```

## Differences from Git

As an educational implementation, GitEllE has some limitations compared to the full Git:

-   Remote operations (push, pull, fetch) are simulated
-   Some advanced features like submodules, reflogs, and merging are not fully implemented
-   Performance optimizations present in Git are not implemented

These limitations make GitEllE simpler to understand while still demonstrating the core concepts of Git.
