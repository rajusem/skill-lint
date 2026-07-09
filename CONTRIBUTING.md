# Contributing to skill-lint

## Getting Started

```bash
git clone https://github.com/rajusem/skill-lint.git
cd skill-lint
uv sync --extra dev
uv run skill-lint .
uv run pytest -v
```

## Development

```bash
make install     # Install deps
make test        # Run tests
make lint        # Run linter
make scan        # Scan this project
make help        # Show all targets
```

## Code Standards

- Python 3.11+
- `uv run ruff check src/ tests/` must pass before committing
- All new rules need tests (positive + negative cases)
- Follow existing rule ID conventions (TCOST, HRISK, FRAME, etc.)

## Adding a New Rule

1. Add check logic in the appropriate `_check_*` function in `scanner.py`
2. Use an existing prefix (TCOST, STRUCT, DESC, HRISK, OQUAL, FRAME, BPRAC, CROSS) or CUSTOM_ for custom rules
3. Add tests in `tests/test_scanner.py`
4. Test against real repos to validate for false positives

## Commits

```bash
git commit -s -m "Add HRISK006: detect XYZ pattern"
```

Always sign off with `-s`.

## License

[Apache-2.0](LICENSE)
