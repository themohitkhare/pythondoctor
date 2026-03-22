from pycodegate.rules.requests_rules import RequestsRules


def _run(source: str) -> list:
    return RequestsRules().check(source, "app.py")


# -- http-missing-timeout --------------------------------------------------


def test_missing_timeout_flagged():
    source = """
import requests

resp = requests.get("https://example.com")
"""
    diags = _run(source)
    assert any(d.rule == "http-missing-timeout" for d in diags)


def test_timeout_present_ok():
    source = """
import requests

resp = requests.get("https://example.com", timeout=10)
"""
    diags = _run(source)
    assert not any(d.rule == "http-missing-timeout" for d in diags)


# -- http-no-status-check --------------------------------------------------


def test_no_status_check_flagged():
    source = """
import requests

def fetch():
    resp = requests.get("https://example.com", timeout=10)
    data = resp.json()
    return data
"""
    diags = _run(source)
    assert any(d.rule == "http-no-status-check" for d in diags)


def test_status_check_present_ok():
    source = """
import requests

def fetch():
    resp = requests.get("https://example.com", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data
"""
    diags = _run(source)
    assert not any(d.rule == "http-no-status-check" for d in diags)


# -- http-verify-disabled ---------------------------------------------------


def test_verify_disabled_flagged():
    source = """
import requests

resp = requests.get("https://example.com", verify=False, timeout=10)
"""
    diags = _run(source)
    assert any(d.rule == "http-verify-disabled" for d in diags)


def test_verify_not_disabled_ok():
    source = """
import requests

resp = requests.get("https://example.com", timeout=10)
"""
    diags = _run(source)
    assert not any(d.rule == "http-verify-disabled" for d in diags)
