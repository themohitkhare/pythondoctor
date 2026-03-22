"""Common AST traversal utilities."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def parse_file(file_path: Path) -> tuple[str, ast.Module | None]:
    """Read and parse a Python file. Returns (source, tree) or (source, None) on error."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
        return source, tree
    except (SyntaxError, UnicodeDecodeError):
        return "", None
