#!/usr/bin/env python3
"""
compute_schedule.py - Compute optimal schedule expression based on telemetry.

Analyzes commit frequency by hour-of-day, PR velocity, and active periods to compute
an optimal cron expression for the self-heal workflow. Updates both the rationale file
and the workflow file safely using ruamel.yaml.
"""

import subprocess
import sys
import datetime
from pathlib import Path
from collections import Counter

def run_command(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a command and return its standard output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception:
        return ""

def get_telemetry(root: Path) -> dict:
    """Gather git telemetry over a rolling lookback window."""
    # Last 30 days commit count
    commits_last_30d_str = run_command(["git", "rev-list", "--count", "--since=30.days.ago", "HEAD"], cwd=root)
    commits_last_30d = int(commits_last_30d_str) if commits_last_30d_str.isdigit() else 0

    # Hour-of-day commit frequency to find active periods
    hours_output = run_command(["git", "log", "--since=30.days.ago", "--format=%aI"], cwd=root)
    hours = []
    for line in hours_output.splitlines():
        if 'T' in line:
            time_part = line.split('T')[1]
            hour = int(time_part.split(':')[0])
            hours.append(hour)

    # Find the quietest hour (mode of inactivity)
    quietest_hour = 0
    if hours:
        counts = Counter(hours)
        # Find the hour with the least commits
        quietest_hour = min(range(24), key=lambda h: counts.get(h, 0))

    return {
        "commits_last_30d": commits_last_30d,
        "quietest_hour": quietest_hour
    }

def compute_schedule(telemetry: dict) -> tuple[str, str]:
    """Compute cadence tier and corresponding cron schedule dynamically."""
    commits = telemetry.get("commits_last_30d", 0)
    quiet_h = telemetry.get("quietest_hour", 0)

    if commits > 100:
        tier = "high"
        # Most frequent: every 4 hours, aligned to quiet hour
        schedule = f"0 {quiet_h%4}-23/4 * * *"
        rationale = f"High churn (>100 commits in 30d). Scheduled multiple runs (interval 4) aligned to quiet hour {quiet_h}."
    elif commits > 30:
        tier = "active"
        # Frequent: every 8 hours, aligned to quiet hour
        schedule = f"0 {quiet_h%8}-23/8 * * *"
        rationale = f"Active development (>30 commits in 30d). Scheduled multiple runs (interval 8) aligned to quiet hour {quiet_h}."
    elif commits > 10:
        tier = "standard"
        # Moderate: twice a day, aligned to quiet hour
        h2 = (quiet_h + 12) % 24
        h_min, h_max = sorted([quiet_h, h2])
        schedule = f"0 {h_min},{h_max} * * *"
        rationale = f"Standard development (>10 commits in 30d). Scheduled twice a day at {h_min} and {h_max}."
    elif commits > 0:
        tier = "low-churn"
        # Infrequent: once a day at quietest hour
        schedule = f"0 {quiet_h} * * *"
        rationale = f"Low churn (>0 commits in 30d). Scheduled once a day at quietest hour {quiet_h}."
    else:
        tier = "dormant"
        # Rare: once a week (using day 1), at quietest hour
        schedule = f"0 {quiet_h} * * 1"
        rationale = f"Dormant repository (0 commits in 30d). Scheduled once a week at quietest hour {quiet_h}."

    return schedule, rationale

def check_oscillation(root: Path, new_schedule: str) -> bool:
    """Return True if we should skip updating due to recent update or no change."""
    schedule_file = root / ".github" / "self-heal-schedule.yml"
    if not schedule_file.exists():
        return False

    try:
        import yaml
        with open(schedule_file, "r") as f:
            data = yaml.safe_load(f)

        current_schedule = data.get("schedule")
        if current_schedule == new_schedule:
            print("Schedule unchanged. Skipping update.")
            return True

        last_updated_str = data.get("last_updated")
        if last_updated_str:
            last_updated = datetime.datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            # Oscillation guard: at least 7 days between changes
            if (now - last_updated).days < 7:
                print("Schedule changed too recently. Skipping update (oscillation guard).")
                return True

        return False
    except ImportError:
        # If yaml is missing, fallback to string check
        with open(schedule_file, "r") as f:
            content = f.read()
        if f"schedule: '{new_schedule}'" in content or f'schedule: "{new_schedule}"' in content:
            print("Schedule unchanged. Skipping update.")
            return True
        return False
    except Exception as e:
        print(f"Error checking oscillation guard: {e}")
        return False

def update_yaml_files(root: Path, schedule: str, rationale: str):
    """Safely update yaml files using ruamel.yaml."""
    try:
        from ruamel.yaml import YAML
    except ImportError:
        print("ruamel.yaml not installed. Falling back to sed update.")
        update_yaml_files_fallback(root, schedule, rationale)
        return

    yaml = YAML()
    yaml.preserve_quotes = True

    # Update .github/self-heal-schedule.yml
    schedule_file = root / ".github" / "self-heal-schedule.yml"
    schedule_data = {
        "schedule": schedule,
        "rationale": rationale,
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    with open(schedule_file, "w") as f:
        yaml.dump(schedule_data, f)

    # Update .github/workflows/self-heal.yml
    workflow_file = root / ".github" / "workflows" / "self-heal.yml"
    if workflow_file.exists():
        with open(workflow_file, "r") as f:
            workflow_data = yaml.load(f)

        if "on" in workflow_data and "schedule" in workflow_data["on"]:
            workflow_data["on"]["schedule"][0]["cron"] = schedule

            with open(workflow_file, "w") as f:
                yaml.dump(workflow_data, f)

            # Restore the marker via a simple replace
            with open(workflow_file, "r") as f:
                content = f.read()
            content = content.replace(f"- cron: {schedule}", f"- cron: '{schedule}' # AUTO-UPDATED")
            with open(workflow_file, "w") as f:
                f.write(content)

def update_yaml_files_fallback(root: Path, schedule: str, rationale: str):
    """Fallback method using string replacement if ruamel.yaml is missing."""
    import re

    schedule_file = root / ".github" / "self-heal-schedule.yml"
    schedule_content = f"""# Current self-healing schedule
schedule: '{schedule}'
rationale: '{rationale}'
last_updated: '{datetime.datetime.now(datetime.timezone.utc).isoformat()}'
"""
    schedule_file.parent.mkdir(parents=True, exist_ok=True)
    with open(schedule_file, "w") as f:
        f.write(schedule_content)

    workflow_file = root / ".github" / "workflows" / "self-heal.yml"
    if workflow_file.exists():
        with open(workflow_file, "r") as f:
            content = f.read()

        # Find the line with the AUTO-UPDATED marker
        pattern = r"-\s*cron:\s*['\"].*['\"]\s*#\s*AUTO-UPDATED"
        replacement = f"- cron: '{schedule}' # AUTO-UPDATED"

        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            with open(workflow_file, "w") as f:
                f.write(new_content)

def main():
    root = Path(__file__).resolve().parent.parent

    print("Gathering telemetry...")
    telemetry = get_telemetry(root)

    print("Computing new schedule...")
    schedule, rationale = compute_schedule(telemetry)
    print(f"Computed schedule: {schedule}")

    if check_oscillation(root, schedule):
        sys.exit(0)

    print("Updating configuration files...")
    update_yaml_files(root, schedule, rationale)

    print("Schedule update complete.")

if __name__ == "__main__":
    main()
