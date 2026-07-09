# skill-lint

Lint your AI skill files before your agents do.

skill-lint scans CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, and agent/skill directories for issues that cause token waste, hallucination risk, and unpredictable agent behavior. 39 rules across 8 categories with fix suggestions.

## Quick Start

```bash
pip install skill-lint   # or: pipx install skill-lint

skill-lint .                                    # Scan current project
skill-lint /path/to/project                     # Scan a local directory
skill-lint https://github.com/org/repo          # Scan a GitHub repo
skill-lint . --format sarif --fail-on warning   # CI gate
skill-lint . -v                                 # Verbose
```

## What It Checks

| Category | Rules | Examples |
|----------|-------|---------|
| Token cost | 11 | Oversized files, duplicates, filler phrases, hedging |
| Description | 5 | Too long, missing trigger conditions |
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
- run: pip install skill-lint
- run: skill-lint . --format sarif --fail-on warning > results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

### pre-commit

```yaml
repos:
  - repo: https://github.com/rajusem/skill-lint
    rev: v0.1.0
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

Create `.skill-lint.yaml` in your project root:

```yaml
disable:
  - HRISK002
  - OQUAL001
fail_on: warning
```

## Philosophy

1. **Help, don't restrict** — every finding is a suggestion, not a gate
2. **Show, don't enforce** — display impact, let users decide
3. **Honest numbers** — no inflated claims; validated across 15+ repos

## License

[Apache-2.0](LICENSE)
