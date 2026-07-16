# skill-lint

Linter for AI instruction files — skills, prompts, and agent specs.

skill-lint scans AI instruction files (CLAUDE.md, AGENTS.md, GEMINI.md, SKILL.md, .cursorrules, .github/copilot-instructions.md, .github/instructions/, and agent/skill directories) for issues that cause token waste, hallucination risk, and unpredictable agent behavior. 61 rules across 13 categories with fix suggestions and auto-fix support.

## Quick Start

```bash
pip install ai-skill-lint   # or: pipx install ai-skill-lint

skill-lint .                                    # Scan current project
skill-lint /path/to/project                     # Scan a local directory
skill-lint https://github.com/org/repo          # Scan a GitHub repo
skill-lint . --format sarif --fail-on warning   # CI gate (severity)
skill-lint . --fail-under 80                    # CI gate (score)
skill-lint . -v                                 # Verbose
skill-lint . --exclude "vendor/*.md"            # Exclude patterns
skill-lint fix . --dry-run                      # Preview auto-fixes
skill-lint fix .                                # Apply safe fixes
skill-lint rule TCOST001                        # Explain a rule
skill-lint rule                                 # List all 61 rules
```

## What It Checks

| Category | Rules | Examples |
|----------|-------|---------|
| Token cost | 11 | Oversized files, duplicates, filler phrases, hedging |
| Description | 7 | Too long, spec limit, overlap detection, missing trigger conditions |
| Hallucination risk | 5 | Vague instructions, no output format, prompt injection, destructive ops |
| Framing | 4 | Prohibition overuse, emphasis overuse, bare directives |
| Output quality | 3 | No examples, no verification, no role statement |
| Best practice | 6 | No model, no error handling, model-complexity mismatch, options without default |
| Structure | 7 | Broken refs, encoding, file too large |
| Cross-file | 1 | Contradictions between CLAUDE.md and skill files |
| Agent safety | 5 | Math traps, regex, structured data, counting, randomness |
| Supply chain | 2 | Dangerous hooks, dangerous settings keys |
| Security | 1 | Hardcoded API keys and credentials (16 provider patterns) |
| Content | 5 | Unclosed fences, deprecated models, tautologies, placeholders, missing summary |
| Drift | 4 | Package manager, dependency, command, and tool mismatches |

Each file scored 0-100 with actionable fix suggestions.

## CI Integration

### GitHub Actions (recommended)

```yaml
# Basic — one line
- uses: rajusem/skill-lint@v0

# With SARIF upload to GitHub Code Scanning
- uses: rajusem/skill-lint@v0
  with:
    format: sarif
    fail-on: warning
- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: results.sarif

# Score gate — fail if average score below 80
- uses: rajusem/skill-lint@v0
  with:
    fail-under: '80'
```

### Manual (any CI)

```bash
pip install ai-skill-lint
skill-lint . --fail-on warning
```

### pre-commit

```yaml
repos:
  - repo: https://github.com/rajusem/skill-lint
    rev: v0.5.0
    hooks:
      - id: skill-lint
```

### Baseline (incremental adoption)

```bash
skill-lint . --save-baseline   # Save current findings
skill-lint . --diff            # Show only NEW issues
```

### Common include/exclude patterns

| Layout | Pattern |
|--------|---------|
| Prompt directory | `--include "prompts/*.md"` |
| Nested agent docs | `--include "docs/agents/**/*.md"` |
| Custom instruction dir | `--include "instructions/**/*.md"` |
| Exclude vendor | `--exclude "vendor/*.md"` |
| Exclude generated | `--exclude "generated/**/*.md"` |

## Inline Suppression

```markdown
<!-- skill-lint: disable TCOST005 -->
<!-- skill-lint: disable TCOST003, HRISK001 -->
```

## Configuration

For VS Code/Cursor autocomplete, add to the top of your `.skill-lint.yaml`:
```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rajusem/skill-lint/main/skill-lint-schema.json
```

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
exclude:
  - "vendor/*.md"
```

### Option 2: `pyproject.toml`

```toml
[tool.skill-lint]
disable = ["HRISK002", "OQUAL001"]
fail_on = "warning"
fail_under = 80
thresholds = {max_tokens = 8000, max_lines = 800}
include = ["prompts/*.md", "docs/agents/**/*.md"]
exclude = ["vendor/*.md"]
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

## Agent Integration

Want Claude to fix your instruction files automatically? Copy our official skill:

```bash
cp -r examples/fix-instruction-files/ .claude/skills/fix-instruction-files/
```

The skill runs `skill-lint`, interprets findings, and proposes fixes with before/after diffs. See [examples/fix-instruction-files/SKILL.md](examples/fix-instruction-files/SKILL.md).

## Rule Reference

See [docs/rules.md](docs/rules.md) for detailed documentation on all 61 rules.

## License

[Apache-2.0](LICENSE)
