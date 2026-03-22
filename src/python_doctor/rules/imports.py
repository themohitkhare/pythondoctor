"""Import rules: circular dependency detection."""

from __future__ import annotations

import ast
import os
from collections import defaultdict
from pathlib import Path

from python_doctor.types import Category, Diagnostic, Severity


class ImportsRules:
    """Project-level import analysis."""

    def check_project(self, project_path: str, source_files: list[str]) -> list[Diagnostic]:
        """Detect circular imports across the project."""
        return self._check_circular_imports(project_path, source_files)

    def _check_circular_imports(
        self, project_path: str, source_files: list[str]
    ) -> list[Diagnostic]:
        # Build import graph: module_name -> set of imported module_names
        graph: dict[str, set[str]] = defaultdict(set)
        file_map: dict[str, str] = {}  # module_name -> file_path

        root = Path(project_path).resolve()

        for filepath in source_files:
            try:
                source = Path(filepath).read_text()
                tree = ast.parse(source)
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue

            module_name = self._file_to_module(filepath, str(root))
            if not module_name:
                continue
            file_map[module_name] = filepath

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        graph[module_name].add(node.module)

        # Detect direct A↔B cycles
        diags: list[Diagnostic] = []
        seen_pairs: set[tuple[str, str]] = set()

        for mod_a, imports in graph.items():
            for mod_b in imports:
                if mod_b in graph and mod_a in graph[mod_b]:
                    pair = tuple(sorted([mod_a, mod_b]))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        file_a = file_map.get(mod_a, mod_a)
                        diags.append(
                            Diagnostic(
                                file_path=file_a,
                                rule="imports/circular",
                                severity=Severity.ERROR,
                                category=Category.IMPORTS,
                                message=f"Circular import between '{mod_a}' and '{mod_b}'",
                                help="Break the cycle by moving shared code to a third module",
                                line=1,
                                cost=3.0,
                            )
                        )

        return diags

    def _file_to_module(self, filepath: str, root: str) -> str | None:
        """Convert a file path to a dotted module name."""
        try:
            rel = os.path.relpath(filepath, root)
        except ValueError:
            return None

        # Remove .py extension
        if rel.endswith(".py"):
            rel = rel[:-3]
        else:
            return None

        # Remove __init__ suffix
        if rel.endswith("__init__"):
            rel = rel[:-9].rstrip(os.sep)

        if not rel:
            return None

        # Convert path separators to dots
        return rel.replace(os.sep, ".").replace("/", ".")
