# GitEllE Documentation

Welcome to the GitEllE documentation!

## What is GitEllE?

GitEllE is a lightweight, educational implementation of Git written in Python. It aims to provide a clear understanding of Git's internal mechanisms while maintaining compatibility with the original Git commands.

## Features

-   Core Git functionality (init, add, commit, branch, checkout)
-   Compatible with standard Git workflows
-   Pure Python implementation
-   Extensive documentation and tests
-   Simple, readable codebase for educational purposes

## Getting Started

### Installation

```bash
pip install gitelle
```

Or install from source:

```bash
git clone https://github.com/yourusername/gitelle.git
cd gitelle
pip install -e .
```

### Quick Start

```bash
# Initialize a new repository
gitelle init

# Add files to the staging area
gitelle add file.txt

# Commit changes
gitelle commit -m "Initial commit"

# Create and switch to a new branch
gitelle branch feature-branch
gitelle checkout feature-branch

# Check status
gitelle status
```

## User Guide

To learn more about how to use GitEllE, check out the [Usage Guide](usage.md).

## Developer Guide

If you're interested in contributing to GitEllE or understanding its internals, see the [Developer Guide](contributing.md).

## API Reference

For detailed API documentation, see the [API Reference](api/core.md).

## License

GitEllE is licensed under the MIT License. See the [LICENSE](https://github.com/yourusername/gitelle/blob/main/LICENSE) file for details.
