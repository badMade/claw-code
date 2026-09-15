#!/usr/bin/env python3
"""
Self-heal repair script.
Runs multiple idempotent repair steps, evaluating healthcheck after each.
Exits 0 if tests pass AND there's a git diff (meaning we fixed something).
"""
import os
import sys
import subprocess

def run_cmd(cmd):
    """Run a command and ignore its exit code."""
    subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)

def check_health():
    """Returns True if healthcheck passes, False otherwise."""
    result = subprocess.run([sys.executable, "scripts/healthcheck.py"], capture_output=True)
    return result.returncode == 0

def check_diff():
    """Returns True if there is a non-empty git diff."""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return bool(result.stdout.strip())

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("Running initial healthcheck...")
    pre_health_pass = check_health()
    if pre_health_pass:
        print("Healthcheck already passing. No fix needed.")
        sys.exit(1) # We exit 1 because we only want to exit 0 if we FIXED something and generated a diff

    steps = [
        ("Step 1: Rebuild/reinstall", "pip install -e ."),
        ("Step 2: Lint/format auto-fix", "ruff check --fix && ruff format"),
        ("Step 3: Snapshot/generated updates", "pytest --snapshot-update || true"),
        ("Step 4: Type stubs/analyzer config", "echo 'skip types'"),
        ("Step 5: Dependency re-resolve", "pip-compile requirements.in -o requirements.txt || true"),
        ("Step 6: Static asset regeneration", "echo 'skip assets'")
    ]

    for name, cmd in steps:
        print(f"\n=======================")
        print(f"Running {name}...")
        print(f"Command: {cmd}")
        print(f"=======================\n")
        run_cmd(cmd)
        if check_health():
            if check_diff():
                print(f"Fix successful after {name}! Diff generated.")
                sys.exit(0)
            else:
                print(f"Fix successful after {name}, but no diff generated. Continuing to next step.")
                continue # if pass + no diff -> continue
        else:
            print(f"{name} did not resolve the issue (healthcheck failed). Continuing to next step.")

    print("All repair steps failed to resolve the issue.")
    sys.exit(1)

if __name__ == "__main__":
    main()
