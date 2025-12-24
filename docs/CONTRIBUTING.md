# Contributing to Agent League System

Thank you for your interest in contributing to the Agent League System! This document provides guidelines for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AIAgents3997-HW7
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Upgrade pip and install dependencies**:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Set up configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

6. **Run tests to verify setup**:
   ```bash
   pytest tests/
   ```

## Code Standards

### Python Style

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Line length**: Maximum 100 characters
- **Formatting**: Use `black` for automatic formatting
- **Import sorting**: Use `isort` for import organization
- **Linting**: Code must pass `ruff` checks

### Code Quality

- **Type hints**: Use type hints for all function signatures
- **Docstrings**: All public functions/classes must have docstrings
- **Comments**: Explain "why", not "what"
- **Error handling**: Use specific exceptions, avoid bare `except`

### Running Code Quality Tools

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linter
ruff check src/ tests/

# Type checking (if mypy is configured)
mypy src/
```

## Testing Requirements

### Test Coverage

- All new code must include tests
- Maintain minimum 80% code coverage
- Critical paths require 100% coverage

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/common/test_protocol.py

# Run with verbose output
pytest tests/ -v
```

### Test Organization

- Unit tests: `tests/<module>/test_<functionality>.py`
- Integration tests: `tests/integration/test_<feature>.py`
- Fixtures: `tests/fixtures/`

### Test Standards

- Use descriptive test names: `test_<what>_<condition>_<expected>`
- One assertion per test (when possible)
- Use fixtures for common setup
- Mock external dependencies

## Pull Request Process

### Before Submitting

1. ✅ Create a feature branch from `main`
2. ✅ Write tests for your changes
3. ✅ Ensure all tests pass
4. ✅ Run code quality tools
5. ✅ Update documentation
6. ✅ Add entry to CHANGELOG (if applicable)

### Branch Naming

- Feature: `feature/<description>`
- Bug fix: `fix/<description>`
- Documentation: `docs/<description>`
- Refactor: `refactor/<description>`

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Example**:
```
feat(scheduler): add Swiss-system tournament support

Implement Swiss-system pairing algorithm as an alternative to
round-robin scheduling for large tournaments.

Closes #123
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added for changes
- [ ] All tests pass
```

### Review Process

1. Submit PR with clear description
2. Wait for CI checks to pass
3. Request review from maintainers
4. Address review comments
5. Obtain approval from at least one maintainer
6. Squash and merge when approved

## Issue Reporting

### Bug Reports

Include:
- **Description**: Clear description of the bug
- **Steps to reproduce**: Minimal reproduction steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, dependencies
- **Logs**: Relevant error messages/stack traces

### Feature Requests

Include:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches
- **Additional context**: Examples, mockups, etc.

## Development Workflow

### Adding a New Game

1. Create game module in `src/referee/games/<game_name>.py`
2. Implement `GameReferee` interface
3. Add game configuration to `config.yaml`
4. Write comprehensive tests
5. Update documentation in `docs/EXTENSIBILITY.md`

### Adding a New Player Strategy

1. Create strategy in `src/player/strategies/<strategy_name>.py`
2. Implement `PlayerStrategy` interface
3. Add strategy tests
4. Document in `README.md`

### Modifying Protocol

1. Update protocol in `src/common/protocol.py`
2. Update protocol version
3. Ensure backward compatibility OR document breaking change
4. Update all affected components
5. Add migration guide if breaking

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize project goals over personal preferences

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Publishing private information

## Getting Help

- **Documentation**: See `docs/` directory
- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: (Add if applicable)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Agent League System!** 🎮
