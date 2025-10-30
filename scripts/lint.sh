#!/bin/bash
# Run linting and code quality checks with uv

set -e

echo "Running code quality checks..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Run ./scripts/setup-dev.sh first."
    exit 1
fi

# Run ruff check (linting)
echo "Running ruff check..."
uv run ruff check .

# Run ruff format (formatting check)
echo "Running ruff format check..."
uv run ruff format --check .

# Run mypy (type checking)
echo "Running mypy type checking..."
uv run mypy .

echo "All code quality checks passed!"