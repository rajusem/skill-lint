"""skill-lint CLI entry point."""

from __future__ import annotations

import sys

import click

from skill_lint import __version__

_VALID_SEVERITIES = {"warning", "suggestion", "info"}
_GROUP_FLAGS = {"--version", "--help", "-h"}


def _validate_severity(ctx, param, value):
    if value is None:
        return None
    parts = [s.strip().lower() for s in value.split(",")]
    for s in parts:
        if s not in _VALID_SEVERITIES:
            raise click.BadParameter(
                f"'{s}' is not a valid severity."
                f" Choose from: {', '.join(sorted(_VALID_SEVERITIES))}"
            )
    return ",".join(parts)


class DefaultGroup(click.Group):
    def parse_args(self, ctx, args):
        if not args or (args[0] not in self.commands and args[0] not in _GROUP_FLAGS):
            args = ["scan"] + args
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup)
@click.version_option(version=__version__)
def main():
    """skill-lint: Linter for AI instruction files.

    Runs scan by default if no subcommand is given.
    """


@main.command()
@click.argument("path", default=".")
@click.option(
    "--format", "fmt",
    type=click.Choice(["table", "json", "sarif"]),
    default="table",
)
@click.option(
    "--severity", default=None, callback=_validate_severity,
    help="Filter by severity (warning,suggestion,info)",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False,
    help="Show all issues (no top-N truncation)",
)
@click.option(
    "--disable", default=None,
    help="Comma-separated rule IDs to suppress (e.g. HRISK002,OQUAL001)",
)
@click.option(
    "--fail-on", "fail_on",
    type=click.Choice(["warning", "suggestion", "info"]),
    default=None,
    help="Exit 1 if issues at this severity or above (for CI)",
)
@click.option(
    "--save-baseline", is_flag=True, default=False,
    help="Save current findings as baseline for future --diff",
)
@click.option(
    "--diff", "diff_baseline", is_flag=True, default=False,
    help="Show only NEW findings not in the saved baseline",
)
@click.option(
    "--baseline-path", default=None,
    help="Override baseline file path",
)
@click.option(
    "--report", is_flag=True, default=False,
    help="Show aggregate summary instead of per-file details",
)
@click.option(
    "--include", "include_patterns", multiple=True,
    help="Additional file patterns to scan (e.g. 'prompts/*.md')",
)
@click.option(
    "--exclude", "exclude_patterns", multiple=True,
    help="File patterns to exclude from scanning (e.g. 'vendor/*.md')",
)
@click.option(
    "--fail-under", "fail_under", type=click.IntRange(0, 100),
    default=None,
    help="Exit 1 if average score is below this threshold (0-100)",
)
def scan(path, fmt, severity, verbose, disable, fail_on,
         save_baseline, diff_baseline, baseline_path, report,
         include_patterns, exclude_patterns, fail_under):
    """Scan AI instruction files for quality issues."""
    from skill_lint.scanner import SEVERITY_ORDER, run_scan

    if save_baseline and diff_baseline:
        click.echo("Error: --save-baseline and --diff are mutually exclusive")
        sys.exit(1)

    disabled_rules = None
    if disable:
        disabled_rules = {
            r.strip().upper() for r in disable.split(",") if r.strip()
        }

    counts = run_scan(
        path=path,
        fmt=fmt,
        severity_filter=severity,
        verbose=verbose,
        disabled_rules=disabled_rules,
        fail_on=fail_on,
        save_baseline=save_baseline,
        diff_baseline=diff_baseline,
        baseline_path=baseline_path,
        report=report,
        include_patterns=list(include_patterns) if include_patterns else None,
        exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
    )

    if counts is None:
        sys.exit(2)

    if fail_on is not None:
        threshold = SEVERITY_ORDER[fail_on]
        has_failing = any(
            counts.get(sev, 0) > 0
            for sev, order in SEVERITY_ORDER.items()
            if order <= threshold
        )
        if has_failing:
            sys.exit(1)

    effective_fail_under = fail_under if fail_under is not None else counts.get("cfg_fail_under")
    if effective_fail_under is not None:
        avg = counts.get("avg_score", 100)
        if avg < effective_fail_under:
            sys.exit(1)


@main.command()
@click.argument("rule_id", required=False)
def rule(rule_id):
    """Show documentation for a rule, or list all rules."""
    from skill_lint.rules import RULES

    if rule_id is None:
        _list_all_rules(RULES)
        return

    rule_id = rule_id.upper()
    if rule_id not in RULES:
        click.echo(f"Unknown rule: {rule_id}")
        click.echo(f"Run 'skill-lint rule' to see all {len(RULES)} rules.")
        sys.exit(1)

    r = RULES[rule_id]
    click.echo(f"{rule_id}: {r['name']}")
    click.echo(f"Category: {r['category']}")
    click.echo(f"Severity: {r['severity']}")
    click.echo()
    click.echo(r["description"])
    click.echo()
    click.echo(f"Fix: {r['fix']}")
    if "threshold" in r:
        click.echo(f"Threshold: {r['threshold']}")


def _list_all_rules(rules):
    categories = {}
    for rid, r in rules.items():
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((rid, r))

    for cat, items in categories.items():
        click.echo(f"\n{cat} ({len(items)} rules)")
        for rid, r in items:
            click.echo(f"  {rid:10s}  {r['severity']:10s}  {r['name']}")
