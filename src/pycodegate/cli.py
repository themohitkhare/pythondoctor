"""CLI entry point for py-doctor."""

from __future__ import annotations

import sys

import click

from pycodegate import __version__
from pycodegate.config import load_config
from pycodegate.output import output_json, print_scan_result
from pycodegate.scan import scan_project
from pycodegate.types import Severity
from pycodegate.utils.badge import generate_badge, generate_ci_workflow
from pycodegate.utils.fixer import run_ruff_fix
from pycodegate.utils.precommit import install_precommit_hook


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-v", "--version", prog_name="Py Gate")
@click.argument("directory", default=".", type=click.Path(exists=True))
@click.option("--lint/--no-lint", default=True, help="Enable/disable lint checks.")
@click.option(
    "--dead-code/--no-dead-code", default=True, help="Enable/disable dead code detection."
)
@click.option("--verbose", is_flag=True, help="Show file details per rule.")
@click.option("--score", "score_only", is_flag=True, help="Output only the numeric score.")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON.")
@click.option(
    "--diff",
    "diff_base",
    default=None,
    type=str,
    help="Scan only files changed vs base branch.",
)
@click.option(
    "--fail-on",
    type=click.Choice(["error", "warning", "none"]),
    default="none",
    help="Exit with code 1 on this severity level.",
)
@click.option("--fix", "fix", is_flag=True, default=False, help="Auto-fix issues via ruff.")
@click.option(
    "--profile",
    "profile_override",
    type=click.Choice(["cli", "web", "library", "script"]),
    default=None,
    help="Override auto-detected project profile.",
)
@click.option(
    "--badge", "badge", is_flag=True, default=False, help="Output shields.io badge markdown."
)
@click.option(
    "--ci", "ci_workflow", is_flag=True, default=False, help="Output GitHub Actions workflow YAML."
)
@click.option(
    "--pre-commit", "precommit", is_flag=True, default=False, help="Install git pre-commit hook."
)
@click.option(
    "--min-score",
    "min_score",
    type=int,
    default=None,
    help="Minimum score threshold (exit 1 if below).",
)
def main(
    directory: str,
    lint: bool,
    dead_code: bool,
    verbose: bool,
    score_only: bool,
    json_output: bool,
    diff_base: str | None,
    fail_on: str,
    fix: bool,
    profile_override: str | None,
    badge: bool,
    ci_workflow: bool,
    precommit: bool,
    min_score: int | None,
) -> None:
    """Py Gate — Diagnose your Python project's health."""
    if ci_workflow:
        click.echo(generate_ci_workflow(), nl=False)
        return

    if precommit:
        effective_min = min_score if min_score is not None else 50
        msg = install_precommit_hook(directory, min_score=effective_min)
        click.echo(msg)
        return

    if fix:
        fixes = run_ruff_fix(directory)
        if fixes == -1:
            click.echo("ruff not found, skipping auto-fix")
        else:
            click.echo(f"Fixed {fixes} issues via ruff")

    config = load_config(directory)
    config.lint = lint
    config.dead_code = dead_code
    config.verbose = verbose
    config.fail_on = fail_on
    if profile_override is not None:
        config.profile = profile_override

    result = scan_project(directory, config, diff_base=diff_base)

    if badge:
        click.echo(generate_badge(result.score.value, result.score.label))
        return

    if json_output:
        output_json(result)
    elif score_only:
        click.echo(str(result.score.value))
    else:
        print_scan_result(result, verbose=verbose)

    # Exit code based on --fail-on
    has_errors = any(d.severity == Severity.ERROR for d in result.diagnostics)
    if (fail_on == "error" and has_errors) or (fail_on == "warning" and result.diagnostics):
        sys.exit(1)

    if min_score is not None and result.score.value < min_score:
        click.echo(
            f"py-gate: score {result.score.value} is below minimum {min_score}",
            err=True,
        )
        sys.exit(1)
