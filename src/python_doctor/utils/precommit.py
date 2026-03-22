"""Pre-commit hook installer."""

from __future__ import annotations

from pathlib import Path


def install_precommit_hook(project_path: str, min_score: int = 50) -> str:
    """Install a git pre-commit hook that runs py-gate."""
    hooks_dir = Path(project_path) / ".git" / "hooks"
    if not hooks_dir.exists():
        return "Error: not a git repository"

    hook_path = hooks_dir / "pre-commit"
    hook_content = f"""#!/bin/sh
# py-gate pre-commit hook
SCORE=$(py-gate . --score 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "py-gate not found. Install with: uvx py-gate"
    exit 0
fi
if [ "$SCORE" -lt {min_score} ]; then
    echo "py-gate: score $SCORE is below minimum {min_score}. Fix issues before committing."
    py-gate . 2>/dev/null
    exit 1
fi
echo "py-gate: score $SCORE/{min_score} — passed"
"""

    # Don't overwrite existing hook — append or warn
    if hook_path.exists():
        existing = hook_path.read_text()
        if "py-gate" in existing:
            hook_path.write_text(hook_content)
            hook_path.chmod(0o755)
            return f"Updated pre-commit hook at {hook_path} (min-score: {min_score})"
        else:
            # Append to existing hook
            # Strip the shebang line before appending
            lines = hook_content.splitlines(keepends=True)
            body = "".join(lines[1:]) if lines[0].startswith("#!/") else hook_content
            with open(hook_path, "a") as f:
                f.write("\n" + body)
            return f"Appended py-gate to existing pre-commit hook at {hook_path}"

    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)
    return f"Installed pre-commit hook at {hook_path} (min-score: {min_score})"
