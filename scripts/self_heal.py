#!/usr/bin/env python3
"""
self_heal.py - Automated repair pipeline.

Executes a 6-step idempotent repair pipeline to fix common code rot and drift issues:
1. Rebuild/reinstall (clean install of tooling + deps)
2. Lint/format auto-fix (language-specific formatter)
3. Snapshot/generated updates (test snapshot regeneration)
4. Type stubs/analyzer config (acquire missing types)
5. Dependency re-resolve (lockfile refresh)
6. Static asset regeneration (docs, badges, code-gen)

After each step, a healthcheck is executed. If the healthcheck passes AND a diff is present,
the script exits with 0 (indicating a successful repair). If no fix is found or a diff isn't present
at the end, it exits non-zero.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and return True if successful."""
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(e.output)
        return False
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"Unexpected error running {' '.join(cmd)}: {e}")
        return False

def check_health(root: Path) -> bool:
    """Run the healthcheck script."""
    hc_script = root / "scripts" / "healthcheck.py"
    if not hc_script.exists():
        print("Healthcheck script not found!")
        return False

    result = subprocess.run([sys.executable, str(hc_script)], cwd=root, capture_output=True)
    return result.returncode == 0

def has_diff(root: Path) -> bool:
    """Check if there are any uncommitted changes."""
    result = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
    return bool(result.stdout.strip())

def main():
    root = Path(__file__).resolve().parent.parent

    print("Starting automated repair pipeline...")

    is_python = (root / "src").exists() or (root / "pyproject.toml").exists()
    is_rust = (root / "rust" / "Cargo.toml").exists()

    steps = [
        ("Step 1: Rebuild/reinstall", step_reinstall),
        ("Step 2: Lint/format auto-fix", step_lint_format),
        ("Step 3: Snapshot/generated updates", step_snapshots),
        ("Step 4: Type stubs/analyzer config", step_types),
        ("Step 5: Dependency re-resolve", step_deps),
        ("Step 6: Static asset regeneration", step_assets),
    ]

    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        step_func(root, is_python, is_rust)

        if check_health(root):
            if has_diff(root):
                print(f"\n✅ Healthcheck passed and changes found after {step_name}.")
                sys.exit(0)
            else:
                print(f"Healthcheck passed, but no changes found after {step_name}. Continuing...")
        else:
            print(f"Healthcheck still failing after {step_name}. Continuing to next step...")

    print("\n❌ Exhausted all repair steps. Healthcheck still failing or no changes produced.")
    sys.exit(1)


def step_reinstall(root: Path, is_python: bool, is_rust: bool):
    if is_python:
        if (root / "setup.py").exists() or (root / "pyproject.toml").exists():
             run_command(["pip", "install", "-e", "."], cwd=root)
    if is_rust:
        run_command(["cargo", "clean"], cwd=root / "rust")
        run_command(["cargo", "build"], cwd=root / "rust")

def step_lint_format(root: Path, is_python: bool, is_rust: bool):
    if is_python:
        if run_command(["which", "ruff"], cwd=root):
            run_command(["ruff", "check", "--fix", "."], cwd=root)
            run_command(["ruff", "format", "."], cwd=root)
    if is_rust:
        run_command(["cargo", "fmt", "--all"], cwd=root / "rust")
        run_command(["cargo", "clippy", "--workspace", "--fix", "--allow-dirty", "--allow-staged"], cwd=root / "rust")

def step_snapshots(root: Path, is_python: bool, is_rust: bool):
    if is_python:
        if (root / "tests").exists():
            # Update pytest snapshots if pytest-snapshot is used, or equivalent
            run_command(["pytest", "--snapshot-update"], cwd=root)
    if is_rust:
        # Some rust test frameworks like insta support updates
        run_command(["cargo", "insta", "review", "--accept"], cwd=root / "rust")

def step_types(root: Path, is_python: bool, is_rust: bool):
    if is_python:
        # Common type stubs
        run_command(["pip", "install", "types-requests", "types-PyYAML", "types-beautifulsoup4", "types-Pillow"], cwd=root)

def step_deps(root: Path, is_python: bool, is_rust: bool):
    if is_python:
        if (root / "requirements.in").exists():
            run_command(["pip-compile", "requirements.in", "-o", "requirements.txt"], cwd=root)
    if is_rust:
        run_command(["cargo", "update"], cwd=root / "rust")

def step_assets(root: Path, is_python: bool, is_rust: bool):
    if (root / "scripts" / "update_docs.py").exists():
        run_command(["python3", "scripts/update_docs.py"], cwd=root)
    if (root / "scripts" / "generate_badges.py").exists():
        run_command(["python3", "scripts/generate_badges.py"], cwd=root)

if __name__ == "__main__":
    main()
