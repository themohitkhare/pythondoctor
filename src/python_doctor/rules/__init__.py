"""Rule registry for python-doctor."""

from __future__ import annotations

from python_doctor.rules.base import BaseRules


def get_all_rule_sets() -> list[BaseRules]:
    """Return all available rule sets."""
    from python_doctor.rules.security import SecurityRules
    from python_doctor.rules.performance import PerformanceRules
    from python_doctor.rules.architecture import ArchitectureRules
    from python_doctor.rules.correctness import CorrectnessRules

    return [SecurityRules(), PerformanceRules(), ArchitectureRules(), CorrectnessRules()]


def get_framework_rules(framework: str | None) -> list[BaseRules]:
    """Return framework-specific rule sets."""
    if framework == "django":
        from python_doctor.rules.django import DjangoRules
        return [DjangoRules()]
    if framework == "fastapi":
        from python_doctor.rules.fastapi import FastAPIRules
        return [FastAPIRules()]
    if framework == "flask":
        from python_doctor.rules.flask import FlaskRules
        return [FlaskRules()]
    return []
