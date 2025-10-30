#!/bin/bash
# Setup development environment with uv

set -e

echo "Setting up development environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Sync dependencies
echo "Installing dependencies..."
uv sync --dev

echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  uv run python     - Run Python in the virtual environment"
echo "  uv run pytest     - Run tests"
echo "  uv run ruff check .  - Run linting"
echo "  uv run ruff format . - Format code"
echo "  uv run mypy .     - Run type checking"