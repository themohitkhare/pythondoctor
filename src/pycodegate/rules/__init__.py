"""Rule registry for python-doctor."""

from __future__ import annotations

from pycodegate.rules.architecture import ArchitectureRules
from pycodegate.rules.base import BaseRules
from pycodegate.rules.complexity import ComplexityRules
from pycodegate.rules.correctness import CorrectnessRules
from pycodegate.rules.dependencies import DependencyRules as DependencyRules
from pycodegate.rules.django import DjangoRules
from pycodegate.rules.fastapi import FastAPIRules
from pycodegate.rules.flask import FlaskRules
from pycodegate.rules.imports import ImportsRules as ImportsRules
from pycodegate.rules.performance import PerformanceRules
from pycodegate.rules.security import SecurityRules
from pycodegate.rules.structure import StructureRules as StructureRules


def get_all_rule_sets() -> list[BaseRules]:
    """Return all available rule sets."""
    return [
        SecurityRules(),
        PerformanceRules(),
        ArchitectureRules(),
        CorrectnessRules(),
        ComplexityRules(),
    ]


def get_framework_rules(framework: str | None) -> list[BaseRules]:
    """Return framework-specific rule sets."""
    _framework_map: dict[str, type[BaseRules]] = {
        "django": DjangoRules,
        "fastapi": FastAPIRules,
        "flask": FlaskRules,
    }
    cls = _framework_map.get(framework or "")
    return [cls()] if cls else []
