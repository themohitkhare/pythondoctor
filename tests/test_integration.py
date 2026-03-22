from pathlib import Path

from python_doctor.config import Config
from python_doctor.scan import scan_project

FIXTURES = Path(__file__).parent / "fixtures"


def test_basic_python_has_issues():
    result = scan_project(str(FIXTURES / "basic_python"), Config(dead_code=False))
    assert result.score.value < 100
    rules_found = {d.rule for d in result.diagnostics}
    assert "no-eval" in rules_found
    assert "no-hardcoded-secret" in rules_found
    assert "no-bare-except" in rules_found
    assert "no-star-import" in rules_found


def test_clean_project_scores_high():
    result = scan_project(str(FIXTURES / "clean_project"), Config(dead_code=False))
    assert result.score.value >= 90


def test_scan_nonexistent_returns_empty():
    """Scanning a dir with no Python files should still work."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        result = scan_project(tmp, Config())
        assert result.score.value == 100
        assert result.diagnostics == []
