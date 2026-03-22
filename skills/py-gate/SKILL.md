---
name: py-gate
description: Run after making Python changes to catch issues early. Use when reviewing code, finishing a feature, or fixing bugs.
version: 1.0.0
---

# Py Gate

Scans your Python codebase for security, performance, correctness, architecture, and structure issues. Outputs a 0-100 score with actionable diagnostics. Auto-detects Django, FastAPI, and Flask to activate framework-specific rules.

## Usage

```bash
uvx py-gate . --verbose --diff
```

## Workflow

Run after making changes. Fix errors first (security, correctness), then warnings (performance, architecture). Re-run to verify the score improved. Target: 80+.

## When to use

- After completing a feature or bug fix
- Before creating a pull request
- During code review
- When refactoring to verify nothing degraded
