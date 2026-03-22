import json
from unittest.mock import MagicMock, patch

from pycodegate.rules.dependencies import DependencyRules


def test_no_pip_audit_returns_empty(tmp_path):
    """When pip-audit is not installed, return empty list."""
    with patch("shutil.which", return_value=None):
        diags = DependencyRules().check_project(str(tmp_path))
    assert diags == []


def test_vulnerability_detected(tmp_path):
    """Mock pip-audit finding a vulnerability."""
    (tmp_path / "requirements.txt").write_text("requests==2.25.0\n")
    mock_result = MagicMock()
    mock_result.stdout = json.dumps(
        {
            "dependencies": [
                {
                    "name": "requests",
                    "version": "2.25.0",
                    "vulns": [{"id": "CVE-2023-1234", "fix_versions": ["2.31.0"]}],
                }
            ]
        }
    )
    mock_result.returncode = 1
    with (
        patch("shutil.which", return_value="/usr/bin/pip-audit"),
        patch("subprocess.run", return_value=mock_result),
    ):
        diags = DependencyRules().check_project(str(tmp_path))
    assert len(diags) == 1
    assert diags[0].rule == "deps/vulnerability"
    assert "requests" in diags[0].message
    assert "CVE-2023-1234" in diags[0].message


def test_no_vulnerabilities(tmp_path):
    """Clean project should return no diagnostics."""
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")
    mock_result = MagicMock()
    mock_result.stdout = json.dumps({"dependencies": []})
    mock_result.returncode = 0
    with (
        patch("shutil.which", return_value="/usr/bin/pip-audit"),
        patch("subprocess.run", return_value=mock_result),
    ):
        diags = DependencyRules().check_project(str(tmp_path))
    assert diags == []


def test_no_requirements_file(tmp_path):
    """No requirements.txt and no uv should return empty."""
    with patch("shutil.which") as mock_which:
        mock_which.side_effect = lambda x: "/usr/bin/pip-audit" if x == "pip-audit" else None
        diags = DependencyRules().check_project(str(tmp_path))
    assert diags == []
