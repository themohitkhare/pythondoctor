"""Rule registry for pycodegate."""

from __future__ import annotations

from pycodegate.rules.architecture import ArchitectureRules
from pycodegate.rules.base import BaseRules
from pycodegate.rules.celery import CeleryRules
from pycodegate.rules.complexity import ComplexityRules
from pycodegate.rules.correctness import CorrectnessRules
from pycodegate.rules.dependencies import DependencyRules as DependencyRules
from pycodegate.rules.django import DjangoRules
from pycodegate.rules.fastapi import FastAPIRules
from pycodegate.rules.flask import FlaskRules
from pycodegate.rules.imports import ImportsRules as ImportsRules
from pycodegate.rules.logging_rules import LoggingRules
from pycodegate.rules.numpy_rules import NumpyRules
from pycodegate.rules.pandas_rules import PandasRules
from pycodegate.rules.performance import PerformanceRules
from pycodegate.rules.pydantic import PydanticRules
from pycodegate.rules.pytest_rules import PytestRules
from pycodegate.rules.requests_rules import RequestsRules
from pycodegate.rules.security import SecurityRules
from pycodegate.rules.sqlalchemy import SQLAlchemyRules
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


_FRAMEWORK_MAP: dict[str, type[BaseRules]] = {
    "django": DjangoRules,
    "fastapi": FastAPIRules,
    "flask": FlaskRules,
    "pydantic": PydanticRules,
    "sqlalchemy": SQLAlchemyRules,
    "celery": CeleryRules,
    "requests": RequestsRules,
    "logging": LoggingRules,
    "pandas": PandasRules,
    "pytest": PytestRules,
    "numpy": NumpyRules,
}


def get_framework_rules(frameworks: list[str]) -> list[BaseRules]:
    """Return framework/library-specific rule sets for all detected frameworks."""
    return [_FRAMEWORK_MAP[f]() for f in frameworks if f in _FRAMEWORK_MAP]
