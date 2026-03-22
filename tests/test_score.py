from pycodegate.score import calculate_score
from pycodegate.types import Category, Diagnostic, Severity


def _make_diag(
    rule: str,
    severity: Severity = Severity.ERROR,
    category: Category = Category.SECURITY,
    cost: float = 1.0,
) -> Diagnostic:
    return Diagnostic(
        file_path="app.py",
        rule=rule,
        severity=severity,
        category=category,
        message="test",
        help="test",
        line=1,
        cost=cost,
    )


def test_perfect_score():
    score = calculate_score([])
    assert score.value == 100
    assert score.label == "Excellent"


def test_single_error_deduction():
    diag = _make_diag("no-eval", category=Category.SECURITY, cost=3.0)
    score = calculate_score([diag])
    assert score.value == 97
    assert score.label == "Excellent"


def test_category_cap():
    """Many findings in one category don't exceed its max_deduction cap."""
    diags = [_make_diag(f"sec-rule-{i}", category=Category.SECURITY, cost=3.0) for i in range(10)]
    score = calculate_score(diags)
    assert score.value >= 77
    assert score.value != 70


def test_diminishing_returns():
    """4+ findings in same category: first 3 at full cost, rest at 10%."""
    diags = [
        _make_diag(f"dc-{i}", severity=Severity.WARNING, category=Category.DEAD_CODE, cost=1.0)
        for i in range(4)
    ]
    score = calculate_score(diags)
    assert score.value == 97


def test_multiple_categories():
    diags = [
        _make_diag("sec-1", category=Category.SECURITY, cost=3.0),
        _make_diag("corr-1", severity=Severity.ERROR, category=Category.CORRECTNESS, cost=2.0),
    ]
    score = calculate_score(diags)
    assert score.value == 95
    assert score.label == "Excellent"


def test_max_deduction_override():
    diag = _make_diag("no-eval", category=Category.SECURITY, cost=3.0)
    score = calculate_score([diag], max_deduction_overrides={Category.SECURITY: 1})
    assert score.value == 99


def test_framework_category_mapping():
    """Django diagnostics count under security budget (not a separate category)."""
    django_diag = _make_diag("no-debug-true", category=Category.DJANGO, cost=3.0)
    sec_diag = _make_diag("no-eval", category=Category.SECURITY, cost=3.0)
    score_combined = calculate_score([django_diag, sec_diag])
    assert score_combined.value == 94

    score_django_only = calculate_score([django_diag])
    assert score_django_only.value == 97


def test_score_floors_at_zero():
    all_cats = [
        Category.SECURITY,
        Category.CORRECTNESS,
        Category.COMPLEXITY,
        Category.ARCHITECTURE,
        Category.PERFORMANCE,
        Category.DEAD_CODE,
    ]
    diags = [_make_diag(f"rule-{i}", category=cat, cost=100.0) for i, cat in enumerate(all_cats)]
    overrides = {cat: 20 for cat in all_cats}
    score = calculate_score(diags, max_deduction_overrides=overrides)
    assert score.value == 0
    assert score.label == "Critical"


def test_label_thresholds():
    assert calculate_score([]).label == "Excellent"

    diag_great = _make_diag("sec-1", category=Category.SECURITY, cost=15.0)
    score_great = calculate_score([diag_great], max_deduction_overrides={Category.SECURITY: 15})
    assert score_great.value == 85
    assert score_great.label == "Great"

    diag_needs_work = _make_diag("sec-1", category=Category.SECURITY, cost=40.0)
    score_needs_work = calculate_score(
        [diag_needs_work], max_deduction_overrides={Category.SECURITY: 40}
    )
    assert score_needs_work.value == 60
    assert score_needs_work.label == "Needs work"

    diag_critical = _make_diag("sec-1", category=Category.SECURITY, cost=60.0)
    score_critical = calculate_score(
        [diag_critical], max_deduction_overrides={Category.SECURITY: 60}
    )
    assert score_critical.value == 40
    assert score_critical.label == "Critical"
