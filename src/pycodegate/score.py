"""Score calculation from diagnostics using weighted category-budget scoring."""

from __future__ import annotations

from collections import defaultdict

from pycodegate.constants import (
    CATEGORY_WEIGHTS,
    FRAMEWORK_CATEGORY_MAP,
    LABEL_CRITICAL,
    LABEL_EXCELLENT,
    LABEL_GREAT,
    LABEL_NEEDS_WORK,
)
from pycodegate.types import Diagnostic, Score


def _build_budget(
    max_deduction_overrides: dict | None,
) -> dict:
    """Return per-category maximum deduction budget normalised to sum to 100."""
    total_weight = sum(CATEGORY_WEIGHTS.values())
    max_deductions = {cat: round(w / total_weight * 100) for cat, w in CATEGORY_WEIGHTS.items()}

    # Fix rounding: adjust highest-weight category so sum == 100
    diff = 100 - sum(max_deductions.values())
    if diff != 0:
        highest = max(CATEGORY_WEIGHTS, key=CATEGORY_WEIGHTS.get)
        max_deductions[highest] += diff

    if max_deduction_overrides:
        for cat, val in max_deduction_overrides.items():
            if cat in max_deductions:
                max_deductions[cat] = val

    return max_deductions


def _score_label(value: int) -> str:
    """Return a human-readable label for a numeric score."""
    if value >= 90:
        return LABEL_EXCELLENT
    if value >= 75:
        return LABEL_GREAT
    if value >= 50:
        return LABEL_NEEDS_WORK
    return LABEL_CRITICAL


def calculate_score(
    diagnostics: list[Diagnostic], max_deduction_overrides: dict | None = None
) -> Score:
    """Calculate a 0-100 health score from diagnostics using category budgets.

    Each category has a weight that determines its maximum deduction budget.
    Within a category, the top 3 findings are counted at full cost; additional
    findings apply diminishing returns (10% each) to reward fixing top issues.
    """
    max_deductions = _build_budget(max_deduction_overrides)

    # Group diagnostics by resolved category
    by_category: dict = defaultdict(list)
    for d in diagnostics:
        resolved = FRAMEWORK_CATEGORY_MAP.get(d.category, d.category)
        by_category[resolved].append(d)

    # Calculate deduction per category with diminishing returns
    total_deduction = 0.0
    for cat, diags in by_category.items():
        costs = sorted([d.cost for d in diags], reverse=True)
        # Top 3 at full cost, rest at 10%
        cat_total = sum(c if i < 3 else c * 0.1 for i, c in enumerate(costs))
        cap = max_deductions.get(cat, 10)
        total_deduction += min(cat_total, cap)

    value = max(0, round(100 - total_deduction))
    return Score(value=value, label=_score_label(value))
