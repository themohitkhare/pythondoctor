from pycodegate.rules.numpy_rules import NumpyRules


def _run(source: str) -> list:
    return NumpyRules().check(source, "analysis.py")


# ------------------------------------------------------------------
# numpy-array-equality
# ------------------------------------------------------------------
def test_array_equality_in_if():
    source = """
import numpy as np

a = np.array([1, 2, 3])
b = np.array([1, 2, 3])
if a == np.array([1, 2, 3]):
    pass
"""
    diags = _run(source)
    assert any(d.rule == "numpy-array-equality" for d in diags)


def test_array_equal_ok():
    source = """
import numpy as np

a = np.array([1, 2, 3])
b = np.array([1, 2, 3])
if np.array_equal(a, b):
    pass
"""
    diags = _run(source)
    assert not any(d.rule == "numpy-array-equality" for d in diags)


# ------------------------------------------------------------------
# numpy-builtin-on-array
# ------------------------------------------------------------------
def test_builtin_sum_on_array():
    source = """
import numpy as np

total = sum(np.array([1, 2, 3]))
"""
    diags = _run(source)
    assert any(d.rule == "numpy-builtin-on-array" for d in diags)


def test_np_sum_ok():
    source = """
import numpy as np

total = np.sum(np.array([1, 2, 3]))
"""
    diags = _run(source)
    assert not any(d.rule == "numpy-builtin-on-array" for d in diags)


# ------------------------------------------------------------------
# numpy-nan-in-int-array
# ------------------------------------------------------------------
def test_nan_in_int_array():
    source = """
import numpy as np

arr = np.array([1, 2, None])
"""
    diags = _run(source)
    assert any(d.rule == "numpy-nan-in-int-array" for d in diags)


def test_pure_int_array_ok():
    source = """
import numpy as np

arr = np.array([1, 2, 3])
"""
    diags = _run(source)
    assert not any(d.rule == "numpy-nan-in-int-array" for d in diags)
