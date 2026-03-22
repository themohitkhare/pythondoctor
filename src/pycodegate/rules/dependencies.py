"""Dependency rules: vulnerability scanning via pip-audit."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from pycodegate.types import Category, Diagnostic, Severity


class DependencyRules:
    """Dependency vulnerability checks using pip-audit (optional)."""

    def _run_pip_audit(self, req_file: Path) -> dict | None:
        """Run pip-audit against *req_file* and return parsed JSON, or None on failure."""
        try:
            result = subprocess.run(
                [
                    "pip-audit",
                    "--requirement",
                    str(req_file),
                    "--format",
                    "json",
                    "--output",
                    "-",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if not result.stdout.strip():
                return None
            return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            return None

    def _build_vuln_diagnostics(self, data: dict) -> list[Diagnostic]:
        """Convert pip-audit JSON output into Diagnostic objects."""
        diags: list[Diagnostic] = []
        for vuln in data.get("dependencies", []):
            pkg_name = vuln.get("name", "unknown")
            version = vuln.get("version", "?")
            for v in vuln.get("vulns", []):
                vuln_id = v.get("id", "unknown")
                fix_versions = v.get("fix_versions", [])
                fix_str = f" (fix: {', '.join(fix_versions)})" if fix_versions else ""
                diags.append(
                    Diagnostic(
                        file_path="requirements",
                        rule="deps/vulnerability",
                        severity=Severity.ERROR,
                        category=Category.DEPENDENCIES,
                        message=f"{pkg_name}=={version} has known vulnerability {vuln_id}{fix_str}",
                        help=f"Upgrade {pkg_name} to a patched version",
                        line=0,
                        cost=3.0,
                    )
                )
        return diags

    def check_project(self, project_path: str) -> list[Diagnostic]:
        if not shutil.which("pip-audit"):
            return []

        path = Path(project_path)
        req_file = self._find_or_export_requirements(path)
        if not req_file:
            return []

        try:
            data = self._run_pip_audit(req_file)
        finally:
            # Clean up temp file if we created one
            if req_file and str(req_file).startswith(tempfile.gettempdir()):
                req_file.unlink(missing_ok=True)

        if data is None:
            return []
        return self._build_vuln_diagnostics(data)

    def _find_or_export_requirements(self, path: Path) -> Path | None:
        # Try existing requirements.txt
        for name in ["requirements.txt", "requirements.lock"]:
            req = path / name
            if req.exists():
                return req

        # Try uv export
        if shutil.which("uv") and (path / "pyproject.toml").exists():
            try:
                tmp = Path(tempfile.gettempdir()) / "pycodegate-reqs.txt"
                result = subprocess.run(
                    [
                        "uv",
                        "export",
                        "--no-dev",
                        "--no-editable",
                        "--no-emit-project",
                        "--format",
                        "requirements-txt",
                        "--quiet",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(path),
                )
                if result.returncode == 0 and result.stdout.strip():
                    tmp.write_text(result.stdout)
                    return tmp
            except (subprocess.TimeoutExpired, OSError):
                pass

        return None
