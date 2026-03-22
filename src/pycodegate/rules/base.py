"""Base class for rule sets."""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod

from pycodegate.types import Diagnostic


class BaseRules(ABC):
    """Base class that all rule sets inherit from."""

    @abstractmethod
    def check(self, source: str, filename: str) -> list[Diagnostic]:
        """Analyze source code and return diagnostics."""

    def _parse(self, source: str) -> ast.Module | None:
        """Safely parse Python source into AST."""
        try:
            return ast.parse(source)
        except SyntaxError:
            return None
