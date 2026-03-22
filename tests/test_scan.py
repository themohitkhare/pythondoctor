from python_doctor.config import Config
from python_doctor.scan import scan_project


def test_scan_clean_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "clean"\ndependencies = []\n')
    (tmp_path / "app.py").write_text("""
def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet("world"))
""")
    result = scan_project(str(tmp_path), Config())
    assert result.score.value >= 75
    assert result.project.path == str(tmp_path)
    assert result.elapsed_ms >= 0


def test_scan_project_with_issues(tmp_path):
    (tmp_path / "app.py").write_text("""
result = eval(user_input)
exec(code)
API_KEY = "sk-1234567890abcdef1234567890abcdef"
""")
    result = scan_project(str(tmp_path), Config())
    assert result.score.value < 100
    assert len(result.diagnostics) > 0


def test_scan_respects_ignore_rules(tmp_path):
    (tmp_path / "app.py").write_text('result = eval("1+1")')
    config = Config(ignore_rules=["no-eval"])
    result = scan_project(str(tmp_path), config)
    assert not any(d.rule == "no-eval" for d in result.diagnostics)


def test_scan_lint_disabled(tmp_path):
    (tmp_path / "app.py").write_text('result = eval("1+1")')
    config = Config(lint=False, dead_code=False)
    result = scan_project(str(tmp_path), config)
    assert result.diagnostics == []


def test_scan_dead_code_disabled(tmp_path):
    (tmp_path / "app.py").write_text("""
def unused():
    pass
""")
    config = Config(dead_code=False)
    result = scan_project(str(tmp_path), config)
    assert not any(d.rule == "dead-code" for d in result.diagnostics)
