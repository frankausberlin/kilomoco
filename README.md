# kilomoco
Modus Configurator for the VSCode extension Kilo Code.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and environment handling.

### Prerequisites

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Install uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and set up the development environment:
   ```bash
   git clone <repository-url>
   cd kilomoco
   uv sync --dev
   ```

### Development Workflow

- **Activate the environment**: `uv run python`
- **Run tests**: `uv run pytest`
- **Run linting**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`
- **Type checking**: `uv run mypy .`

### Scripts

Convenience scripts are available in the `scripts/` directory:

- `./scripts/setup-dev.sh` - Set up development environment
- `./scripts/test.sh` - Run tests
- `./scripts/lint.sh` - Run linting and formatting

### Building

Build the package:
```bash
uv build
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Run linting: `uv run ruff check . && uv run ruff format .`
6. Submit a pull request
