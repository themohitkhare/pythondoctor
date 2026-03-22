"""Score calculation from diagnostics."""

from __future__ import annotations

from python_doctor.constants import (
    ERROR_PENALTY,
    LABEL_CRITICAL,
    LABEL_GREAT,
    LABEL_NEEDS_WORK,
    SCORE_GREAT,
    SCORE_NEEDS_WORK,
    WARNING_PENALTY,
)
from python_doctor.types import Diagnostic, Score, Severity


def calculate_score(diagnostics: list[Diagnostic]) -> Score:
    """Calculate a 0-100 health score from diagnostics.

    Only unique rules count — multiple violations of the same rule
    incur a single penalty.
    """
    error_rules: set[str] = set()
    warning_rules: set[str] = set()

    for d in diagnostics:
        if d.severity == Severity.ERROR:
            error_rules.add(d.rule)
        else:
            warning_rules.add(d.rule)

    penalty = len(error_rules) * ERROR_PENALTY + len(warning_rules) * WARNING_PENALTY
    value = max(0, round(100 - penalty))

    if value >= SCORE_GREAT:
        label = LABEL_GREAT
    elif value >= SCORE_NEEDS_WORK:
        label = LABEL_NEEDS_WORK
    else:
        label = LABEL_CRITICAL

    return Score(value=value, label=label)
