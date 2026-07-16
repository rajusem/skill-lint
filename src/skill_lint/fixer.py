"""skill-lint fixer — safe deterministic auto-fixes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skill_lint.scanner import Issue


_FILLER_PATS = [
    (re.compile(r"\bplease\s+", re.I), ""),
    (re.compile(r"\bkindly\s+", re.I), ""),
    (re.compile(r"\bmake sure to\s+", re.I), ""),
    (re.compile(r"\bensure that you\s+", re.I), ""),
    (re.compile(r"\bit is important that\s+", re.I), ""),
    (re.compile(r"\bremember to\s+", re.I), ""),
    (re.compile(r"\bdon'?t forget to\s+", re.I), ""),
    (re.compile(r"\byou should always\s+", re.I), ""),
]

_HEDGING_PATS = [
    (re.compile(r"\btry to\s+", re.I), ""),
    (re.compile(r"\bwhere appropriate\s*", re.I), ""),
    (re.compile(r"\bwhen possible\s*", re.I), ""),
    (re.compile(r"\bif you can\s*,?\s*", re.I), ""),
]

_ZERO_VALUE_PATS = [
    re.compile(r"^\s*you are a helpful assistant\.?\s*$", re.I),
    re.compile(r"^\s*thank you\.?\s*$", re.I),
    re.compile(r"^\s*great job\.?\s*$", re.I),
    re.compile(r"^\s*i appreciate.*$", re.I),
]

def _recapitalize(text: str) -> str:
    """Re-capitalize the first letter if at sentence start."""
    if text and text[0].islower():
        return text[0].upper() + text[1:]
    return text


def _fix_filler_phrases(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        for pat, repl in _FILLER_PATS:
            if pat.search(line):
                new_line = pat.sub(repl, line)
                new_line = _recapitalize(new_line.lstrip())
                if line.startswith(" " * 2):
                    new_line = line[: len(line) - len(line.lstrip())] + new_line
                line = new_line
        result.append(line)
    return result


def _fix_hedging(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        for pat, repl in _HEDGING_PATS:
            if pat.search(line):
                new_line = pat.sub(repl, line)
                new_line = _recapitalize(new_line.lstrip())
                if line.startswith(" " * 2):
                    new_line = line[: len(line) - len(line.lstrip())] + new_line
                line = new_line
        result.append(line)
    return result


def _fix_zero_value_lines(lines: list[str]) -> list[str]:
    return [line for line in lines if not any(p.match(line) for p in _ZERO_VALUE_PATS)]


def _fix_unclosed_fence(lines: list[str]) -> list[str]:
    return lines + ["```"]


def apply_fixes(
    filepath: Path, issues: list[Issue], dry_run: bool = False,
) -> tuple[str, str]:
    """Apply safe deterministic fixes. Returns (original, fixed) content."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    rule_ids = {i.rule_id for i in issues}
    fixed_lines = lines[:]

    if "TCOST006" in rule_ids:
        fixed_lines = _fix_filler_phrases(fixed_lines)
    if "TCOST008" in rule_ids:
        fixed_lines = _fix_hedging(fixed_lines)
    if "TCOST009" in rule_ids:
        fixed_lines = _fix_zero_value_lines(fixed_lines)
    if "CONTENT008" in rule_ids:
        fixed_lines = _fix_unclosed_fence(fixed_lines)

    fixed = "\n".join(fixed_lines)
    if content.endswith("\n") and not fixed.endswith("\n"):
        fixed += "\n"

    if not dry_run and fixed != content:
        filepath.write_text(fixed, encoding="utf-8")

    return content, fixed
