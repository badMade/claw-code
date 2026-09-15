#!/usr/bin/env python3
"""
Healthcheck script to verify the project's health.
It checks Python code formatting, types, and runs tests.
Exits 0 if all checks pass, otherwise 1.
"""
import sys
import subprocess
import os

def run_cmd(cmd):
    """Run a command and return its exit code."""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(f"FAILED: {cmd}")
        if result.stdout:
            print(result.stdout.decode('utf-8'))
    return result.returncode

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("Running healthchecks...")

    exit_code = 0

    print("Running linting checks...")
    lint_result = run_cmd("ruff check .")
    if lint_result != 0:
        exit_code = 1

    format_result = run_cmd("ruff format --check .")
    if format_result != 0:
        exit_code = 1

    print("Running tests...")
    # Use python3 -m unittest to match the project's setup instead of pytest
    test_result = run_cmd("PYTHONPATH=. python3 -m unittest discover -s tests -v")
    if test_result != 0:
        exit_code = 1

    print(f"Healthcheck finished with exit code {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
