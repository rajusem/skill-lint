# skill-lint

Linter for AI skill files (SKILL.md, CLAUDE.md, AGENTS.md, .cursorrules).

## Commands

```bash
uv sync --extra dev    # install deps
uv run skill-lint .    # run linter
uv run pytest -v       # run tests
uv run ruff check src/ # lint
```

## Project Structure

```
src/skill_lint/
├── cli.py              # CLI entry point (Click)
└── scanner.py          # Scanner engine (39 rules across 8 categories)
tests/
├── test_scanner.py     # Scanner tests
└── test_cli.py         # CLI tests
```
