#!/usr/bin/env python3
"""
Self-Heal Repair Pipeline.
Executes 6 idempotent repair steps.
After each step, it runs healthcheck.py.
If healthcheck passes AND there is a git diff, exits 0 (success, we fixed something).
If healthcheck passes AND there is NO git diff, continues to the next step.
If it goes through all steps and there is no diff, or healthcheck still fails, exits 1.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return its exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode

def has_git_diff(root_dir):
    """Check if there are any uncommitted changes."""
    result = subprocess.run(["git", "status", "--porcelain"], cwd=root_dir, capture_output=True, text=True)
    return bool(result.stdout.strip())

def check_health(root_dir):
    """Run healthcheck script and return True if it passes."""
    healthcheck_script = root_dir / "scripts" / "healthcheck.py"
    return run_command(["python3", str(healthcheck_script)], cwd=root_dir) == 0

def check_and_exit(root_dir, step_name):
    """Check health and diff, exit if we successfully healed something."""
    is_healthy = check_health(root_dir)
    has_diff = has_git_diff(root_dir)

    if is_healthy and has_diff:
        print(f"✅ Self-heal successful after: {step_name}. Diff created.")
        sys.exit(0)
    elif not is_healthy:
        print(f"⚠️ Healthcheck still failing after: {step_name}.")
    elif is_healthy and not has_diff:
        print(f"✅ Healthcheck passing after: {step_name}, but no diff. Continuing...")

def main():
    root_dir = Path(__file__).resolve().parent.parent
    rust_dir = root_dir / "rust"

    print("--- Starting Self-Heal Pipeline ---")

    # Check if already healthy
    if check_health(root_dir):
        if has_git_diff(root_dir):
             print("✅ Already healthy but has diff. Committing current diff.")
             sys.exit(0)
        else:
             print("✅ Already healthy and no diff. Nothing to do.")
             sys.exit(1) # We exit 1 to prevent PR creation if we didn't fix anything

    # Step 1: Rebuild/reinstall (clean install of tooling + deps)
    print("🔧 Step 1: Rebuild/reinstall")
    # Python deps
    run_command(["pip", "install", "-r", "requirements-dev.txt"], cwd=root_dir)
    # Rust is handled via cargo, but we can do a cargo clean / fetch if needed
    # (Skipping aggressive clean for now to save time, fetch is good)
    if rust_dir.exists():
        run_command(["cargo", "fetch"], cwd=rust_dir)
    check_and_exit(root_dir, "Step 1: Rebuild/reinstall")

    # Step 2: Lint/format auto-fix
    print("🔧 Step 2: Lint/format auto-fix")
    # Python
    run_command(["ruff", "check", "--fix", "."], cwd=root_dir)
    run_command(["ruff", "format", "."], cwd=root_dir)
    # Rust
    if rust_dir.exists():
        run_command(["cargo", "fmt", "--all"], cwd=rust_dir)
        run_command(["cargo", "clippy", "--workspace", "--fix", "--allow-dirty", "--allow-staged"], cwd=rust_dir)
    check_and_exit(root_dir, "Step 2: Lint/format auto-fix")

    # Step 3: Snapshot/generated updates
    print("🔧 Step 3: Snapshot/generated updates")
    # No standard snapshot updating tool in this repo yet, but leaving placeholder for parity
    print("No snapshot updates configured for Python/Rust.")
    check_and_exit(root_dir, "Step 3: Snapshot/generated updates")

    # Step 4: Type stubs/analyzer config
    print("🔧 Step 4: Type stubs/analyzer config")
    # Not using mypy currently based on healthcheck
    print("No type stubs fetching configured.")
    check_and_exit(root_dir, "Step 4: Type stubs/analyzer config")

    # Step 5: Dependency re-resolve
    print("🔧 Step 5: Dependency re-resolve")
    # Python doesn't have pip-compile set up yet here, rust we can cargo update
    # Skipping cargo update by default to avoid unexpected breakages, focus on explicit fixes
    print("Skipping aggressive dependency updates.")
    check_and_exit(root_dir, "Step 5: Dependency re-resolve")

    # Step 6: Static asset regeneration
    print("🔧 Step 6: Static asset regeneration")
    print("No static asset generation configured.")
    check_and_exit(root_dir, "Step 6: Static asset regeneration")

    print("❌ Self-heal exhausted all steps without fixing the issue.")
    sys.exit(1)

if __name__ == "__main__":
    main()
