#!/usr/bin/env python3
"""
Computes the optimal schedule for self-healing runs based on PR telemetry.
Updates .github/self-heal-schedule.yml and .github/workflows/self-heal.yml.
"""
import subprocess
import sys
import json
from pathlib import Path

def run_command_json(cmd, cwd=None):
    """Run a gh command that outputs JSON and parse it."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to run {' '.join(cmd)}: {e}")
        return []

def compute_schedule(root_dir):
    """
    Compute schedule based on recent PR activity.
    Fallback to standard if telemetry is not available.
    """
    # Try to get recent merged PRs (last 30)
    prs = run_command_json(["gh", "pr", "list", "--state", "merged", "--limit", "30", "--json", "mergedAt"], cwd=root_dir)

    # If we have many recent PRs, it's active. Let's just use simple logic for now.
    pr_count = len(prs)
    if pr_count > 20:
        tier = "high"
        cron = "0 */4 * * *" # Every 4 hours
        rationale = "High PR velocity (>20 recent merges), running frequently."
    elif pr_count > 5:
        tier = "active"
        cron = "0 8,20 * * *" # Twice a day
        rationale = "Active PR velocity (5-20 recent merges), running twice daily."
    else:
        tier = "standard"
        cron = "0 2 * * *" # Once a day at 2 AM
        rationale = "Standard PR velocity (<5 recent merges), running once daily."

    return cron, rationale, tier

def update_files(root_dir, cron, rationale):
    """Update YAML files using ruamel.yaml for safe round-trip editing."""
    try:
        from ruamel.yaml import YAML
    except ImportError:
        print("ruamel.yaml not installed, skipping schedule update. (Run pip install ruamel.yaml)")
        sys.exit(1)

    yaml = YAML()
    yaml.preserve_quotes = True

    # Update self-heal-schedule.yml
    schedule_file = root_dir / ".github" / "self-heal-schedule.yml"
    schedule_data = {
        "schedule": cron,
        "rationale": rationale,
        "marker": "# AUTO-UPDATED"
    }
    with open(schedule_file, "w") as f:
        yaml.dump(schedule_data, f)

    print(f"Updated {schedule_file} with: {cron}")

    # Update self-heal.yml
    workflow_file = root_dir / ".github" / "workflows" / "self-heal.yml"
    if not workflow_file.exists():
         print(f"Workflow file {workflow_file} does not exist yet. Skipping workflow update.")
         return

    with open(workflow_file, "r") as f:
        data = yaml.load(f)

    # Ensure structure exists
    if "on" in data and "schedule" in data["on"]:
        # Data["on"]["schedule"] is a list of dicts. We update the first one's cron.
        if len(data["on"]["schedule"]) > 0 and "cron" in data["on"]["schedule"][0]:
            data["on"]["schedule"][0]["cron"] = cron

            with open(workflow_file, "w") as f:
                yaml.dump(data, f)
            print(f"Updated {workflow_file} schedule to: {cron}")

def main():
    root_dir = Path(__file__).resolve().parent.parent

    cron, rationale, tier = compute_schedule(root_dir)
    print(f"Computed schedule: '{cron}' ({tier}) - {rationale}")

    update_files(root_dir, cron, rationale)
    sys.exit(0)

if __name__ == "__main__":
    main()
