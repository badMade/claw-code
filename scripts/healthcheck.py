#!/usr/bin/env python3
"""
healthcheck.py - Verify project health across tests, linting, and building.

This script executes various checks based on the detected project configuration.
It exits 0 if all checks pass, and 1 if any check fails.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and return True if successful."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if result.returncode != 0:
            print(f"Error executing {' '.join(cmd)}:")
            print(result.stdout)
            return False
        return True
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"Unexpected error running {' '.join(cmd)}: {e}")
        return False

def main():
    root = Path(__file__).resolve().parent.parent
    success = True

    print("Running project health checks...")

    # Python checks
    if (root / "src").exists() or (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        print("\n--- Python Checks ---")

        # Test
        if (root / "tests").exists():
            success &= run_command(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root)
        else:
            success &= run_command(["pytest"], cwd=root)

        # Lint
        if run_command(["which", "ruff"], cwd=root):
            success &= run_command(["ruff", "check", "."], cwd=root)
            success &= run_command(["ruff", "format", "--check"], cwd=root)

    # Rust checks
    if (root / "rust" / "Cargo.toml").exists():
        print("\n--- Rust Checks ---")
        rust_dir = root / "rust"
        success &= run_command(["cargo", "fmt", "--all", "--check"], cwd=rust_dir)
        success &= run_command(["cargo", "clippy", "--workspace", "--", "-D", "warnings"], cwd=rust_dir)
        success &= run_command(["cargo", "test", "--workspace"], cwd=rust_dir)

    if success:
        print("\n✅ All health checks passed.")
        sys.exit(0)
    else:
        print("\n❌ Health checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
