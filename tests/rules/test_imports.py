"""Tests for circular import detection."""

from __future__ import annotations

from pycodegate.rules.imports import ImportsRules


def test_circular_import_detected(tmp_path):
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import a\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert any(d.rule == "imports/circular" for d in diags)


def test_no_circular_import(tmp_path):
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("x = 1\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert not any(d.rule == "imports/circular" for d in diags)


def test_from_import_circular(tmp_path):
    (tmp_path / "a.py").write_text("from b import foo\n")
    (tmp_path / "b.py").write_text("from a import bar\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert any(d.rule == "imports/circular" for d in diags)


def test_circular_reported_once(tmp_path):
    """A<->B cycle should produce exactly one diagnostic, not two."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import a\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    circular = [d for d in diags if d.rule == "imports/circular"]
    assert len(circular) == 1


def test_lazy_import_not_flagged(tmp_path):
    """Imports inside functions (lazy imports) should not count as circular."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("def foo():\n    import a\n")
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert not any(d.rule == "imports/circular" for d in diags)


def test_type_checking_import_not_flagged(tmp_path):
    """Imports under TYPE_CHECKING guard should not count as circular."""
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text(
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    import a\n"
    )
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [str(tmp_path / "a.py"), str(tmp_path / "b.py")])
    assert not any(d.rule == "imports/circular" for d in diags)


def test_empty_project(tmp_path):
    rules = ImportsRules()
    diags = rules.check_project(str(tmp_path), [])
    assert diags == []
