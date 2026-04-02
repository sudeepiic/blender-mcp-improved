# Contributing to Blender MCP

Thank you for your interest in contributing to Blender MCP! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch for your changes
4. Make your changes following the guidelines below
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or newer
- Blender 3.0 or newer (for addon development)
- uv package manager
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/blender-mcp.git
cd blender-mcp

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest --cov=blender_mcp --cov-report=html
```

### Development Workflow

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/

# Run all checks at once
pre-commit run --all-files
```

## Coding Standards

### Python Code Style

We follow standard Python conventions with the following tools:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting (combines flake8, isort, pyupgrade)
- **mypy** for type checking (gradually being added)

### Type Hints

Type hints are encouraged for all new code:

```python
from typing import Optional, List

def get_object_names(include_hidden: bool = False) -> List[str]:
    """Get list of object names from the current scene."""
    ...
```

### Documentation

All public functions should have docstrings:

```python
def process_texture(texture_id: str, resolution: str = "1k") -> dict:
    """
    Process a texture from Poly Haven.

    Args:
        texture_id: The Poly Haven asset ID
        resolution: Resolution to download (1k, 2k, 4k, 8k)

    Returns:
        Dictionary with processing result and metadata

    Raises:
        ValueError: If texture_id is invalid
        ConnectionError: If download fails
    """
```

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## Testing

### Writing Tests

Tests are located in the `tests/` directory:

```python
# tests/test_server.py
def test_get_scene_info(blender_connection):
    """Test getting scene information."""
    result = blender_connection.send_command("get_scene_info", {})
    assert result["status"] == "success"
    assert "objects" in result["result"]
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_server.py        # MCP server tests
├── test_handlers.py      # Blender addon handler tests
└── test_integration.py   # End-to-end tests
```

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support forSketchfab model search

Fixes #123

- Add search_sketchfab_models tool
- Implement model preview thumbnails
- Add download_and_import functionality
```

### Pull Request Guidelines

1. **Title**: Use a clear title describing the change
2. **Description**: Include:
   - What problem you're solving
   - How you solved it
   - Any relevant context
3. **Link Issues**: Reference related issues with `Fixes #123`
4. **Tests**: Include tests for new functionality
5. **Docs**: Update documentation if needed

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commits are clean and well-described
- [ ] PR title is descriptive

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Search for similar problems

### Bug Report Template

```markdown
**Description**
A clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Blender version: X.Y.Z
- OS: Linux/macOS/Windows
- Python version: X.Y.Z

**Logs/Error Messages**
```
(Paste logs here)
```
```

## Feature Requests

We welcome feature requests! Please:

1. Check if it's already been requested
2. Describe the use case clearly
3. Explain why it would be useful
4. Consider if you can contribute it yourself

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Discord**: [Join our community](https://discord.gg/z5apgR8TFU)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
