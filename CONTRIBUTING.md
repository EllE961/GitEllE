# Contributing to GitEllE

Thank you for your interest in contributing to GitEllE! This document outlines the process for contributing to the project.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/EllE961/gitelle.git
   cd gitelle
   ```
3. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a branch for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding style and guidelines

3. Add tests for your changes and ensure all tests pass:

   ```bash
   pytest
   ```

4. Format your code:

   ```bash
   black .
   isort .
   ```

5. Run linting and type checking:

   ```bash
   flake8
   mypy src tests
   ```

6. Commit your changes with a descriptive commit message:

   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. Push your branch to GitHub:

   ```bash
   git push origin feature/your-feature-name
   ```

8. Submit a pull request on GitHub

## Pull Request Guidelines

- Fill in the pull request template completely
- Link any relevant issues
- Include screenshots or animated GIFs if applicable
- Add or update documentation as needed
- Make sure all checks pass
- Be responsive to feedback and questions

## Coding Style

GitEllE follows Python's PEP 8 style guide with a few modifications:

- We use Black for code formatting with a line length of 88 characters
- We use isort for import ordering
- Type annotations are required for function parameters and return values
- Docstrings should follow the Google style

## Testing

All new features should include appropriate tests. We strive for high test coverage and use pytest for testing.

## Documentation

Documentation is a crucial part of GitEllE. Please update the documentation when adding or modifying features.

## Project Structure

```
gitelle/
├── src/            # Source code
│   ├── core/       # Core Git functionality
│   ├── commands/   # Command implementations
│   └── utils/      # Utility functions
├── tests/          # Test suite
├── docs/           # Documentation
└── examples/       # Example usage
```

## License

By contributing to GitEllE, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have questions about contributing, feel free to open an issue on GitHub or reach out to the maintainers directly.

Thank you for your contributions!
