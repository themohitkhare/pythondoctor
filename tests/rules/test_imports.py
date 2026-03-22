"""Tests for circular import detection."""

from __future__ import annotations

from python_doctor.rules.imports import ImportsRules


def test_circular_import_detected(tmp_path):
    """Two files that import each other should trigger imports/circular."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import a\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert any(d.rule == "imports/circular" for d in diags)


def test_no_circular_import(tmp_path):
    """One-directional import should not trigger."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("x = 1\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert not any(d.rule == "imports/circular" for d in diags)


def test_from_import_circular(tmp_path):
    """from X import Y style should also be detected."""
    (tmp_path / "a.py").write_text("from b import foo\n")
    (tmp_path / "b.py").write_text("from a import bar\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert any(d.rule == "imports/circular" for d in diags)


def test_circular_reported_once(tmp_path):
    """A↔B cycle should produce exactly one diagnostic, not two."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import a\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    circular = [d for d in diags if d.rule == "imports/circular"]
    assert len(circular) == 1


def test_empty_project(tmp_path):
    """No files should produce no diagnostics."""
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [])
    assert diags == []
