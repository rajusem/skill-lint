"""skill-lint CLI entry point."""

from __future__ import annotations

import sys

import click

from skill_lint import __version__

_VALID_SEVERITIES = {"warning", "suggestion", "info"}


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


@click.command()
@click.version_option(version=__version__)
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
def main(path, fmt, severity, verbose, disable, fail_on,
         save_baseline, diff_baseline, baseline_path, report):
    """skill-lint: Linter for AI skill files."""
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
    )

    if fail_on is not None:
        threshold = SEVERITY_ORDER[fail_on]
        has_failing = any(
            counts.get(sev, 0) > 0
            for sev, order in SEVERITY_ORDER.items()
            if order <= threshold
        )
        if has_failing:
            sys.exit(1)
