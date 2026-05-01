#!/usr/bin/env python3
"""Healthcheck for a Python project: lint, typecheck, test, install verify."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

def _run(
    name: str,
    cmd: list[str],
    *,
    required: bool = True,
    cwd: Path | None = None,
) -> bool:
    """Run a command, print status, return True on success."""
    print(f"\n==> {name}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, cwd=cwd)
    if result.returncode != 0:
        print(f"[FAIL] {name} (exit {result.returncode})")
        if required:
            return False
    else:
        print(f"[OK]   {name}")
    return True

def _has_tool(name: str) -> bool:
    """Check if a CLI tool is available."""
    return subprocess.run(
        [sys.executable, "-m", name, "--version"],
        capture_output=True,
    ).returncode == 0

def main() -> int:
    """Run all health checks. Return 0 if all pass, 1 otherwise."""
    root = Path(__file__).resolve().parent.parent
    ok = True

    # 1) Verify editable install works
    with tempfile.TemporaryDirectory() as temp_dir:
        ok &= _run(
            "Install check",
            [sys.executable, "-c", "import src.query_engine; print('query_engine imported successfully')"],
            cwd=Path(temp_dir),
        )

    # 2) Lint (ruff) — skip if not installed
    if _has_tool("ruff"):
        ok &= _run(
            "Lint (ruff)",
            [sys.executable, "-m", "ruff", "check", str(root / "src"), str(root / "tests")],
            cwd=root,
        )
    else:
        print("\n==> Lint: ruff not installed, skipping")

    # 3) Type check (mypy) — skip if not installed
    if _has_tool("mypy"):
        ok &= _run(
            "Typecheck (mypy)",
            [sys.executable, "-m", "mypy", str(root / "src")],
            required=False,  # advisory until fully typed
            cwd=root,
        )
    else:
        print("\n==> Typecheck: mypy not installed, skipping")

    # 4) Tests (unittest)
    ok &= _run(
        "Tests (unittest)",
        [sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-q"],
        cwd=root,
    )

    # 5) Package build check — skip if not installed
    if _has_tool("build"):
        ok &= _run(
            "Build check",
            [sys.executable, "-m", "build", "--no-isolation", "--wheel", str(root)],
            required=False,
            cwd=root,
        )
    else:
        print("\n==> Build check: build not installed, skipping")

    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
