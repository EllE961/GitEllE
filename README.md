# GitEllE

[![PyPI version](https://badge.fury.io/py/gitelle.svg?v=1)](https://pypi.org/project/gitelle/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

GitEllE is a lightweight, educational implementation of Git written in Python. It aims to provide a clear understanding of Git's internal mechanisms while maintaining compatibility with the original Git commands.

## Features

-   Core Git functionality (init, add, commit, branch, checkout)
-   Compatible with standard Git workflows
-   Pure Python implementation
-   Extensive documentation and tests
-   Simple, readable codebase for educational purposes

## Installation

```bash
pip install gitelle
```

Or install from source:

```bash
git clone https://github.com/yourusername/gitelle.git
cd gitelle
pip install -e .
```

## Quick Start

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

## Documentation

For detailed documentation, visit the [docs](docs/index.md) directory or our [documentation site](https://gitelle.readthedocs.io/).

## Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md) before getting started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   Inspired by the original [Git](https://git-scm.com/) project
-   Thanks to all contributors who have helped shape GitEllE
