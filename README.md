# skill-lint

Linter for AI instruction files — skills, prompts, and agent specs.

skill-lint scans AI instruction files (CLAUDE.md, AGENTS.md, GEMINI.md, SKILL.md, .cursorrules, .github/copilot-instructions.md, .github/instructions/, and agent/skill directories) for issues that cause token waste, hallucination risk, and unpredictable agent behavior. 42 rules across 8 categories with fix suggestions.

## Quick Start

```bash
pip install ai-skill-lint   # or: pipx install ai-skill-lint

skill-lint .                                    # Scan current project
skill-lint /path/to/project                     # Scan a local directory
skill-lint https://github.com/org/repo          # Scan a GitHub repo
skill-lint . --format sarif --fail-on warning   # CI gate (severity)
skill-lint . --fail-under 80                    # CI gate (score)
skill-lint . -v                                 # Verbose
skill-lint rule TCOST001                        # Explain a rule
skill-lint rule                                 # List all 42 rules
```

## What It Checks

| Category | Rules | Examples |
|----------|-------|---------|
| Token cost | 11 | Oversized files, duplicates, filler phrases, hedging |
| Description | 7 | Too long, spec limit, overlap detection, missing trigger conditions |
| Hallucination risk | 4 | Vague instructions, no output format, prompt injection risk |
| Framing | 4 | Prohibition overuse, emphasis overuse, bare directives |
| Output quality | 3 | No examples, no verification, no role statement |
| Best practice | 5 | No model, no error handling, model-complexity mismatch |
| Structure | 7 | Broken refs, encoding, file too large |
| Cross-file | 1 | Contradictions between CLAUDE.md and skill files |

Each file scored 0-100 with actionable fix suggestions.

## CI Integration

```yaml
# GitHub Actions
- run: pip install ai-skill-lint
- run: skill-lint . --format sarif --fail-on warning > results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

### pre-commit

```yaml
repos:
  - repo: https://github.com/rajusem/skill-lint
    rev: v0.2.0
    hooks:
      - id: skill-lint
```

### Baseline (incremental adoption)

```bash
skill-lint . --save-baseline   # Save current findings
skill-lint . --diff            # Show only NEW issues
```

## Inline Suppression

```markdown
<!-- skill-lint: disable TCOST005 -->
<!-- skill-lint: disable TCOST003, HRISK001 -->
```

## Configuration

### Option 1: `.skill-lint.yaml`

```yaml
disable:
  - HRISK002
  - OQUAL001
fail_on: warning
fail_under: 80        # exit 1 if avg score < 80
thresholds:
  max_tokens: 8000   # default: 5000
  max_lines: 800     # default: 500
include:
  - "prompts/*.md"
  - "docs/agents/**/*.md"
```

### Option 2: `pyproject.toml`

```toml
[tool.skill-lint]
disable = ["HRISK002", "OQUAL001"]
fail_on = "warning"
fail_under = 80
thresholds = {max_tokens = 8000, max_lines = 800}
include = ["prompts/*.md", "docs/agents/**/*.md"]
```

Precedence: CLI flags > `.skill-lint.yaml` > `pyproject.toml`

## Custom Rules

Write your own rules by extending the `Rule` base class:

```python
from skill_lint.scanner import Rule, Issue, register_rule

class MyRule(Rule):
    id = "CUSTOM_001"
    description = "Check for company-specific patterns"

    def check(self, ctx):
        issues = []
        if "legacy API" in ctx.content:
            issues.append(Issue(
                category="best-practice",
                severity="suggestion",
                message="References legacy API",
                fix="Use the new v2 API instead",
                rule_id=self.id,
            ))
        return issues

register_rule(MyRule())
```

Custom rule IDs must use the `CUSTOM_` prefix. The `ctx` object provides: `content`, `lines`, `regions`, `filepath`, `root`, `tokens`, and `content_text` (code-fence-filtered).

## Philosophy

1. **Help, don't restrict** — every finding is a suggestion, not a gate
2. **Show, don't enforce** — display impact, let users decide
3. **Honest numbers** — no inflated claims; validated across 88+ repos

## License

[Apache-2.0](LICENSE)
