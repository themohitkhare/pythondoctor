from pycodegate.rules.pandas_rules import PandasRules


def _run(source: str) -> list:
    return PandasRules().check(source, "analysis.py")


def test_chained_indexing():
    source = """
df["A"][mask] = 99
"""
    diags = _run(source)
    assert any(d.rule == "pandas-chained-indexing" for d in diags)


def test_single_indexing_ok():
    source = """
df["A"] = 99
"""
    diags = _run(source)
    assert not any(d.rule == "pandas-chained-indexing" for d in diags)


def test_inplace_assignment():
    source = """
df = df.drop(columns=['x'], inplace=True)
"""
    diags = _run(source)
    assert any(d.rule == "pandas-inplace-assignment" for d in diags)


def test_inplace_no_assignment_ok():
    source = """
df.drop(columns=['x'], inplace=True)
"""
    diags = _run(source)
    assert not any(d.rule == "pandas-inplace-assignment" for d in diags)


def test_nan_comparison():
    source = """
result = df["col"] == np.nan
"""
    diags = _run(source)
    assert any(d.rule == "pandas-nan-comparison" for d in diags)


def test_isna_ok():
    source = """
result = df["col"].isna()
"""
    diags = _run(source)
    assert not any(d.rule == "pandas-nan-comparison" for d in diags)
