"""Scan orchestration: runs lint + dead code in parallel, produces ScanResult."""

from __future__ import annotations

import fnmatch
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from python_doctor.discover import discover_project
from python_doctor.rules import get_all_rule_sets, get_framework_rules
from python_doctor.rules.dead_code import DeadCodeRules
from python_doctor.score import calculate_score
from python_doctor.types import Diagnostic, ScanResult
from python_doctor.utils.file_discovery import find_python_files

if TYPE_CHECKING:
    from pathlib import Path

    from python_doctor.config import Config


def scan_project(
    project_path: str,
    config: Config,
    diff_base: str | None = None,
) -> ScanResult:
    """Run full scan and return results."""
    start = time.monotonic()

    project = discover_project(project_path)

    # Determine files to scan
    if diff_base:
        from python_doctor.utils.diff import get_changed_files
        files = get_changed_files(project_path, diff_base)
        if files is None:
            files = find_python_files(project_path)
    else:
        files = find_python_files(project_path)

    # Run lint + dead code in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        lint_future = executor.submit(
            _run_lint, files, project.framework, config
        ) if config.lint else None
        dead_code_future = executor.submit(
            _run_dead_code, project_path, config
        ) if config.dead_code else None

        lint_diags = lint_future.result() if lint_future else []
        dead_code_diags = dead_code_future.result() if dead_code_future else []

    all_diags = lint_diags + dead_code_diags

    # Apply ignore rules
    if config.ignore_rules:
        all_diags = [d for d in all_diags if d.rule not in config.ignore_rules]

    # Apply ignore files
    if config.ignore_files:
        all_diags = [
            d for d in all_diags
            if not any(fnmatch.fnmatch(d.file_path, pat) for pat in config.ignore_files)
        ]

    score = calculate_score(all_diags)
    elapsed = int((time.monotonic() - start) * 1000)

    return ScanResult(
        score=score,
        diagnostics=all_diags,
        project=project,
        elapsed_ms=elapsed,
    )


def _run_lint(
    files: list[Path],
    framework: str | None,
    config: Config,
) -> list[Diagnostic]:
    """Run all rule sets against all files."""
    rule_sets = get_all_rule_sets() + get_framework_rules(framework)
    diags: list[Diagnostic] = []

    for file_path in files:
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        for rules in rule_sets:
            diags.extend(rules.check(source, str(file_path)))

    return diags


def _run_dead_code(project_path: str, config: Config) -> list[Diagnostic]:
    """Run dead code detection."""
    return DeadCodeRules().check_project(project_path)
