# Installation Guide

This guide will help you install GitEllE on your system.

## Prerequisites

Before installing GitEllE, ensure you have the following:

-   Python 3.8 or newer
-   pip (Python package installer)

## Installation Methods

### From PyPI (Recommended)

The easiest way to install GitEllE is via pip:

```bash
pip install gitelle
```

This will install GitEllE and all its dependencies.

### From Source

If you prefer to install from source, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/EllE961/gitelle.git
    cd gitelle
    ```

2. Install the package in development mode:

    ```bash
    pip install -e .
    ```

    This installs GitEllE in development mode, allowing you to modify the code and see changes immediately without reinstalling.

3. Verify the installation:

    ```bash
    gitelle --version
    ```

## Dependencies

GitEllE depends on the following Python packages:

-   click: For command-line interface
-   zlib-wrapper: For compression
-   pathlib: For file system operations
-   pyyaml: For configuration files

These dependencies are automatically installed when you install GitEllE using pip.

## Platform-specific Notes

### Windows

On Windows, you might need to ensure that the Python Scripts directory is in your PATH. If you encounter a "command not found" error, try adding the Scripts directory to your PATH:

```
set PATH=%PATH%;C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts
```

Replace `Python3X` with your Python version.

### Linux/macOS

On Linux and macOS, you might need to use `pip3` explicitly if both Python 2 and 3 are installed:

```bash
pip3 install gitelle
```

## Development Installation

If you plan to contribute to GitEllE, you should install the development dependencies:

```bash
pip install -e ".[dev]"
```

This installs additional packages needed for development, such as pytest for testing and black for code formatting.

## Troubleshooting

If you encounter any issues during installation:

1. Ensure you're using a compatible Python version (3.8+)
2. Try upgrading pip: `pip install --upgrade pip`
3. If you're installing from source, ensure you have the necessary build tools installed
4. Check the [GitHub Issues](https://github.com/EllE961/gitelle/issues) to see if others have encountered similar problems

If problems persist, please [open an issue](https://github.com/EllE961/gitelle/issues/new) with details about your environment and the error you're experiencing.
