"""Tests for new security rules: os.system, subprocess shell=True, tempfile.mktemp."""

from pycodegate.rules.security import SecurityRules


def test_os_system_detected():
    diags = SecurityRules().check("import os\nos.system('ls')\n", "app.py")
    assert any(d.rule == "no-os-system" for d in diags)


def test_subprocess_shell_true():
    source = "import subprocess\nsubprocess.run('ls', shell=True)\n"
    diags = SecurityRules().check(source, "app.py")
    assert any(d.rule == "no-subprocess-shell" for d in diags)


def test_subprocess_shell_false_ok():
    source = "import subprocess\nsubprocess.run(['ls'], shell=False)\n"
    diags = SecurityRules().check(source, "app.py")
    assert not any(d.rule == "no-subprocess-shell" for d in diags)


def test_tempfile_mktemp():
    source = "import tempfile\ntempfile.mktemp()\n"
    diags = SecurityRules().check(source, "app.py")
    assert any(d.rule == "no-tempfile-race" for d in diags)


def test_tempfile_mkstemp_ok():
    source = "import tempfile\ntempfile.mkstemp()\n"
    diags = SecurityRules().check(source, "app.py")
    assert not any(d.rule == "no-tempfile-race" for d in diags)
