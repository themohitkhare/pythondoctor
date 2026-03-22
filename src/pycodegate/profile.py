"""Project profile detection and rule/scoring adjustments."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pycodegate._compat import tomllib


@dataclass(frozen=True)
class Profile:
    name: str  # "cli", "web", "library", "script"
    suppressed_rules: frozenset[str] = field(default_factory=frozenset)
    max_deduction_overrides: dict[str, int] = field(default_factory=dict)


# Profile definitions
PROFILES = {
    "web": Profile(name="web"),
    "cli": Profile(
        name="cli",
        suppressed_rules=frozenset({"no-subprocess", "no-shell-exec"}),
        max_deduction_overrides={"Security": 15},
    ),
    "library": Profile(name="library"),
    "script": Profile(
        name="script",
        suppressed_rules=frozenset({"structure/no-tests", "structure/no-license"}),
        max_deduction_overrides={"Structure": 5},
    ),
}


def detect_profile(project_path: str) -> Profile:
    """Auto-detect project profile from project structure and dependencies."""
    path = Path(project_path)
    pyproject = path / "pyproject.toml"

    deps: set[str] = set()
    has_build_system = False
    has_scripts = False

    if pyproject.exists():
        try:
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
            # Collect dependency names
            for dep in data.get("project", {}).get("dependencies", []):
                deps.add(
                    dep.split("[")[0]
                    .split(">")[0]
                    .split("<")[0]
                    .split("=")[0]
                    .split("!")[0]
                    .strip()
                    .lower()
                )
            has_build_system = "build-system" in data
            has_scripts = bool(data.get("project", {}).get("scripts"))
        except Exception:
            pass

    # Also check requirements.txt
    for req_file in ["requirements.txt", "requirements-dev.txt"]:
        req_path = path / req_file
        if req_path.exists():
            try:
                for line in req_path.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        deps.add(
                            line.split("[")[0]
                            .split(">")[0]
                            .split("<")[0]
                            .split("=")[0]
                            .split("!")[0]
                            .strip()
                            .lower()
                        )
            except Exception:
                pass

    # Web frameworks
    web_deps = {"flask", "django", "fastapi", "starlette", "tornado", "aiohttp", "sanic", "bottle"}
    if deps & web_deps:
        return PROFILES["web"]

    # CLI tools
    cli_deps = {"click", "typer", "fire", "cement", "cliff", "argparse"}
    if (deps & cli_deps) or has_scripts:
        return PROFILES["cli"]

    # Library
    if has_build_system and not has_scripts:
        return PROFILES["library"]

    # Script: no __init__.py and few .py files
    py_files = list(path.glob("*.py"))
    has_init = (path / "__init__.py").exists() or any(
        (path / d / "__init__.py").exists() for d in ["src", "lib"]
    )
    if not has_init and len(py_files) <= 5:
        return PROFILES["script"]

    # Default to library
    return PROFILES["library"]
