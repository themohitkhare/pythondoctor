"""Git diff utilities for scanning only changed files."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_changed_files(project_path: str, base: str = "main") -> list[Path] | None:
    """Get Python files changed compared to a base branch. Returns None if git fails."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", base, "--", "*.py"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        root = Path(project_path)
        return [root / f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
