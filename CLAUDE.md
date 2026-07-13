# skill-lint

Linter for AI instruction files (CLAUDE.md, AGENTS.md, GEMINI.md, SKILL.md, .cursorrules, .github/copilot-instructions.md).

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
├── cli.py              # CLI entry point (Click group + DefaultGroup)
├── rules.py            # Rule metadata for skill-lint rule command
└── scanner.py          # Scanner engine (42 rules across 8 categories)
tests/
├── test_scanner.py     # Scanner tests
└── test_cli.py         # CLI tests
```
