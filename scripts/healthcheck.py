#!/usr/bin/env python3
"""
Healthcheck script to verify project linting, typing, tests, and build.
Returns 0 if everything is clean, 1 if any check fails.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a shell command and return its exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    return result.returncode

def main():
    root_dir = Path(__file__).resolve().parent.parent
    rust_dir = root_dir / "rust"

    print("--- Starting Healthcheck ---")

    # 1. Rust Formatting
    if rust_dir.exists():
        if run_command(["cargo", "fmt", "--all", "--check"], cwd=rust_dir) != 0:
            print("❌ Rust formatting failed.")
            sys.exit(1)

        # 2. Rust Clippy (Linting)
        if run_command(["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"], cwd=rust_dir) != 0:
            print("❌ Rust clippy failed.")
            sys.exit(1)

        # 3. Rust Tests
        if run_command(["cargo", "test", "--workspace"], cwd=rust_dir) != 0:
            print("❌ Rust tests failed.")
            sys.exit(1)

        # 4. Rust Build
        if run_command(["cargo", "build", "--release", "-p", "rusty-claude-cli"], cwd=rust_dir) != 0:
            print("❌ Rust build failed.")
            sys.exit(1)

    # 5. Python Linting (ruff)
    if run_command(["ruff", "check", "."], cwd=root_dir) != 0:
        print("❌ Python linting (ruff check) failed.")
        sys.exit(1)

    # 6. Python Formatting (ruff format)
    if run_command(["ruff", "format", "--check", "."], cwd=root_dir) != 0:
        print("❌ Python formatting (ruff format) failed.")
        sys.exit(1)

    # 7. Python Tests
    # Set PYTHONPATH to include the root directory to resolve src modules correctly
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir)
    if run_command(["python3", "-m", "unittest", "discover", "tests"], cwd=root_dir, env=env) != 0:
        print("❌ Python tests failed.")
        sys.exit(1)

    print("✅ All healthchecks passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
