from pycodegate.rules.pytest_rules import PytestRules


def _run(source: str) -> list:
    return PytestRules().check(source, "test_app.py")


# -- pytest-assert-tuple --------------------------------------------------


def test_assert_tuple_detected():
    diags = _run("assert(x > 0, 'must be positive')")
    assert any(d.rule == "pytest-assert-tuple" for d in diags)


def test_assert_tuple_ok():
    diags = _run("assert x > 0, 'must be positive'")
    assert not any(d.rule == "pytest-assert-tuple" for d in diags)


# -- pytest-raises-instead-of-try -----------------------------------------


def test_raises_instead_of_try_detected():
    source = """\
def test_division():
    try:
        1 / 0
    except ZeroDivisionError:
        pass
"""
    diags = _run(source)
    assert any(d.rule == "pytest-raises-instead-of-try" for d in diags)


def test_raises_instead_of_try_ok():
    source = """\
def test_division():
    try:
        result = 1 / 0
    except ZeroDivisionError:
        result = None
    assert result is None
"""
    diags = _run(source)
    assert not any(d.rule == "pytest-raises-instead-of-try" for d in diags)


# -- pytest-float-equality ------------------------------------------------


def test_float_equality_detected():
    source = """\
def test_compute():
    result = 0.1 + 0.2
    assert result == 0.3
"""
    diags = _run(source)
    assert any(d.rule == "pytest-float-equality" for d in diags)


def test_float_equality_ok():
    source = """\
def test_count():
    assert len(items) == 3
"""
    diags = _run(source)
    assert not any(d.rule == "pytest-float-equality" for d in diags)
