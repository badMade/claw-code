#!/usr/bin/env python3
"""
Self-Heal Repair Script
Performs 6 idempotent steps to attempt repair.
Exits 0 ONLY if healthcheck passes AND there is a diff.
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

def run_healthcheck(root_dir: str) -> bool:
    print("\n[Self-Heal] Running Healthcheck...")
    hc_path = os.path.join(root_dir, "scripts", "healthcheck.py")
    return run_cmd(["python3", hc_path], cwd=root_dir) == 0

def has_diff(root_dir: str) -> bool:
    print("\n[Self-Heal] Checking for diff...")
    result = subprocess.run(["git", "status", "--porcelain"], cwd=root_dir, capture_output=True, text=True)
    return bool(result.stdout.strip())

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Running self-heal repair in {root_dir}")
    rust_dir = os.path.join(root_dir, "rust")
    has_rust = os.path.isdir(rust_dir)

    # Check initial health
    if run_healthcheck(root_dir) and has_diff(root_dir):
        print("✅ Already healthy and diff exists.")
        sys.exit(0)

    steps = [
        ("Step 1: Rebuild/reinstall", [
            # Tools and deps might be updated
            (["pip", "install", "-e", "."], root_dir),
            (["cargo", "clean"], rust_dir) if has_rust else None,
        ]),
        ("Step 2: Lint/format auto-fix", [
            (["ruff", "check", "--fix", "."], root_dir),
            (["ruff", "format", "."], root_dir),
            (["cargo", "fmt", "--all"], rust_dir) if has_rust else None,
            (["cargo", "clippy", "--workspace", "--all-targets", "--fix", "--allow-dirty", "--allow-no-vcs"], rust_dir) if has_rust else None,
        ]),
        ("Step 3: Snapshot/generated updates", [
            # In unittest, no native snapshot update flag, skipping.
            # But we could update stubs or other generated code if necessary.
        ]),
        ("Step 4: Type stubs/analyzer config", [
            # Can run pyright if needed, or pip install types-*
        ]),
        ("Step 5: Dependency re-resolve", [
            # pip-compile if using requirements.in
        ]),
        ("Step 6: Static asset regeneration", [
            # Any codegen scripts
        ])
    ]

    for step_name, commands in steps:
        print(f"\n======================\n{step_name}\n======================")
        for cmd_info in commands:
            if cmd_info:
                cmd, cwd = cmd_info
                print(f"Running: {' '.join(cmd)} in {cwd}")
                run_cmd(cmd, cwd=cwd)

        # After each step, run healthcheck
        if run_healthcheck(root_dir):
            if has_diff(root_dir):
                print(f"✅ Success after {step_name}. Diff exists. Self-heal complete.")
                sys.exit(0)
            else:
                print(f"⚠️ Healthcheck passed after {step_name}, but no diff. Continuing...")
        else:
            print(f"❌ Healthcheck failed after {step_name}. Moving to next step.")

    print("\n❌ All self-heal steps exhausted. Final state is not (Healthy AND Diff).")
    sys.exit(1)

if __name__ == "__main__":
    main()
