#!/usr/bin/env python3
"""
Self-Heal Healthcheck Script
Verifies formatting, types, and tests.
Exits 0 if everything passes, 1 if anything fails.
"""
import subprocess
import sys
import os

def run_cmd(cmd: list[str], cwd: str = ".") -> int:
    try:
        result = subprocess.run(cmd, cwd=cwd, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return 1

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Running healthcheck in {root_dir}")

    # Python checks (assuming src/ and tests/ exist)
    python_failed = False

    print("\n--- Python: Ruff Check ---")
    if run_cmd(["ruff", "check", "."], cwd=root_dir) != 0:
        python_failed = True

    print("\n--- Python: Ruff Format ---")
    if run_cmd(["ruff", "format", "--check", "."], cwd=root_dir) != 0:
        python_failed = True

    print("\n--- Python: Tests ---")
    if run_cmd(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root_dir) != 0:
        python_failed = True

    # Rust checks
    rust_failed = False
    rust_dir = os.path.join(root_dir, "rust")
    if os.path.isdir(rust_dir):
        print("\n--- Rust: Cargo Fmt ---")
        if run_cmd(["cargo", "fmt", "--all", "--check"], cwd=rust_dir) != 0:
            rust_failed = True

        print("\n--- Rust: Cargo Clippy ---")
        if run_cmd(["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"], cwd=rust_dir) != 0:
            rust_failed = True

        print("\n--- Rust: Cargo Test ---")
        if run_cmd(["cargo", "test", "--workspace"], cwd=rust_dir) != 0:
            rust_failed = True

    if python_failed or rust_failed:
        print("\n❌ Healthcheck failed.")
        sys.exit(1)

    print("\n✅ Healthcheck passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
