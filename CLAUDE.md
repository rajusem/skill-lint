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
├── fixer.py            # Auto-fix engine (skill-lint fix)
├── rules.py            # Rule metadata for skill-lint rule command
└── scanner.py          # Scanner engine (61 rules across 13 categories)
tests/
├── test_scanner.py     # Scanner tests
└── test_cli.py         # CLI tests
```
