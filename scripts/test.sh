#!/bin/bash
# Run tests with uv

set -e

echo "Running tests..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Run ./scripts/setup-dev.sh first."
    exit 1
fi

# Run tests
uv run pytest tests/ -v

echo "Tests completed successfully!"