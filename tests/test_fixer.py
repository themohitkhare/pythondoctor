"""Tests for run_ruff_fix utility."""

from __future__ import annotations

import tempfile
from pathlib import Path

from pycodegate.utils.fixer import run_ruff_fix


def test_run_ruff_fix_returns_int_on_temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_ruff_fix(tmpdir)
    assert isinstance(result, int)


def test_run_ruff_fix_returns_int_on_python_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "sample.py"
        py_file.write_text("x = 1\n")
        result = run_ruff_fix(tmpdir)
    assert isinstance(result, int)


def test_run_ruff_fix_nonnegative_or_minus_one():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_ruff_fix(tmpdir)
    assert result >= -1
