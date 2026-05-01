#!/usr/bin/env python3
"""Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.

Exit 0 only if a repair produced a passing healthcheck and a non-empty git diff.
"""
from __future__ import annotations

import importlib.util
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def sh(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command with logging."""
    print(f"\n$ {shlex.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=check)

def try_sh(cmd: list[str]) -> bool:
    """Run a command, return True on success."""
    return sh(cmd, check=False).returncode == 0

def has_changes() -> bool:
    """Check if there are uncommitted changes in the working tree."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return bool(result.stdout.strip())

def passes_healthcheck() -> bool:
    """Run healthcheck.py and return True if it passes."""
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "healthcheck.py")],
        cwd=ROOT,
    ).returncode == 0

def main() -> int:
    """Attempt repairs in priority order. Return 0 if any repair succeeds."""
    fixed = False

    # --- Step 1: Reinstall editable + deps ---
    print("\n### Step 1: Reinstall editable package")
    try_sh([sys.executable, "-m", "pip", "install", "-e", ".[dev,selfheal]"])
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("\n[self-heal] Fixed by reinstall.")
            return 0

    # --- Step 2: Lint/format auto-fix ---
    print("\n### Step 2: Lint & format auto-fix")
    try_sh([sys.executable, "-m", "ruff", "check", "--fix", str(ROOT / "src"), str(ROOT / "tests")])
    try_sh([sys.executable, "-m", "ruff", "format", str(ROOT / "src"), str(ROOT / "tests")])
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("\n[self-heal] Fixed by lint/format.")
            return 0

    # --- Step 3: Type stub acquisition ---
    print("\n### Step 3: Type stub acquisition")
    # Common stubs for this project's dependencies
    stubs = [
        "types-requests",
        "types-PyYAML",
        "types-beautifulsoup4",
        "types-Pillow",
    ]
    try_sh([sys.executable, "-m", "pip", "install", *stubs])
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("\n[self-heal] Fixed by type stub install.")
            return 0

    # --- Step 4: Dependency re-resolve ---
    print("\n### Step 4: Dependency re-resolve")
    try_sh([sys.executable, "-m", "pip", "install", "--upgrade", "-e", "."])
    # If a requirements.txt exists, try pip-compile
    req_in = ROOT / "requirements.in"
    req_txt = ROOT / "requirements.txt"
    has_piptools = importlib.util.find_spec("piptools") is not None
    if req_in.exists() and has_piptools:
        try_sh([sys.executable, "-m", "piptools", "compile", str(req_in), "-o", str(req_txt)])
        try_sh([sys.executable, "-m", "pip", "install", "-r", str(req_txt)])
    elif req_txt.exists():
        try_sh([sys.executable, "-m", "pip", "install", "-r", str(req_txt)])
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("\n[self-heal] Fixed by dependency re-resolve.")
            return 0

    # --- Step 5: Known generators (docs, badges, etc.) ---
    print("\n### Step 5: Regenerate static assets")
    generators = [
        ROOT / "scripts" / "update_docs.py",
        ROOT / "scripts" / "generate_badges.py",
    ]
    for gen in generators:
        if gen.exists():
            try_sh([sys.executable, str(gen)])
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("\n[self-heal] Fixed by asset regeneration.")
            return 0

    # --- No fix found ---
    print("\n[self-heal] All repair steps exhausted. No passing fix found.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
