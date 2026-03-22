from pycodegate.rules.architecture import ArchitectureRules


def _run(source: str) -> list:
    return ArchitectureRules().check(source, "app.py")


def test_giant_module():
    source = "\n".join([f"x_{i} = {i}" for i in range(501)])
    diags = _run(source)
    assert any(d.rule == "no-giant-module" for d in diags)


def test_small_module_ok():
    source = "\n".join([f"x_{i} = {i}" for i in range(50)])
    diags = _run(source)
    assert not any(d.rule == "no-giant-module" for d in diags)


def test_deep_nesting():
    source = """
def foo():
    if True:
        for x in range(10):
            if x > 5:
                while True:
                    if x > 7:
                        pass
"""
    diags = _run(source)
    assert any(d.rule == "no-deep-nesting" for d in diags)


def test_god_function():
    lines = ["def huge_function():"]
    for i in range(55):
        lines.append(f"    x_{i} = {i}")
    source = "\n".join(lines)
    diags = _run(source)
    assert any(d.rule == "no-god-function" for d in diags)


def test_too_many_args():
    source = "def foo(a, b, c, d, e, f, g, h):\n    pass"
    diags = _run(source)
    assert any(d.rule == "too-many-arguments" for d in diags)


def test_reasonable_args_ok():
    source = "def foo(a, b, c):\n    pass"
    diags = _run(source)
    assert not any(d.rule == "too-many-arguments" for d in diags)
