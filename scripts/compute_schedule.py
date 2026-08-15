#!/usr/bin/env python3
"""
Compute Self-Heal Schedule
Analyzes git history to determine commit cadence and active/quiet periods.
Outputs a CRON expression for self-healing runs, avoiding hardcoded values.
Requires: ruamel.yaml
"""
import subprocess
import sys
import os
import datetime

try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml not installed. Installing...")
    subprocess.run(["pip", "install", "ruamel.yaml"], check=True)
    from ruamel.yaml import YAML

def get_commit_timestamps() -> list[datetime.datetime]:
    since = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--format=%aI"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []

    timestamps = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            dt = datetime.datetime.fromisoformat(line)
            timestamps.append(dt)
        except ValueError:
            pass
    return timestamps

def compute_cron(timestamps: list[datetime.datetime]) -> str:
    # Handle the dormant fallback (one run a week dynamically chosen)
    if not timestamps:
        # Generate a dynamic fallback based on current time to avoid hardcoding 0 (Sunday)
        now = datetime.datetime.now()
        return f"0 {now.hour} * * {now.weekday()}"

    hour_counts = {i: 0 for i in range(24)}
    for dt in timestamps:
        hour_counts[dt.hour] += 1

    total_commits = sum(hour_counts.values())
    days_in_history = 30
    velocity = total_commits / days_in_history

    quietest_hour = min(hour_counts, key=hour_counts.get)

    # Calculate intervals dynamically instead of hardcoding hours
    if velocity > 5:
        # High: every 4 hours, offset by quietest_hour
        hours = ",".join(str((quietest_hour + i * 4) % 24) for i in range(6))
        return f"0 {hours} * * *"
    elif velocity > 2:
        # Active: every 8 hours
        hours = ",".join(str((quietest_hour + i * 8) % 24) for i in range(3))
        return f"0 {hours} * * *"
    elif velocity > 0.5:
        # Standard: once a day
        return f"0 {quietest_hour} * * *"
    else:
        # Low churn: once a week based on the quietest day
        weekday_counts = {i: 0 for i in range(7)}
        for dt in timestamps:
            weekday_counts[dt.weekday()] += 1
        quietest_weekday = min(weekday_counts, key=weekday_counts.get)
        return f"0 {quietest_hour} * * {quietest_weekday}"

def update_yaml_config(schedule_file: str, cron_expr: str, rationale: str) -> bool:
    if not os.path.exists(schedule_file):
        with open(schedule_file, "w") as f:
            f.write(f"schedule: '{cron_expr}' # AUTO-UPDATED\n")
            f.write(f"rationale: '{rationale}'\n")
        return True

    yaml = YAML()
    yaml.preserve_quotes = True

    with open(schedule_file, "r") as f:
        data = yaml.load(f)

    if data is None:
        data = {}

    # Oscillation guard: do not update if changed in the last 7 days
    last_updated_str = data.get("last_updated")
    if last_updated_str:
        try:
            last_updated = datetime.datetime.fromisoformat(last_updated_str)
            if (datetime.datetime.now() - last_updated).days < 7:
                print("Schedule oscillation guard active. Skipping update.")
                return False
        except ValueError:
            pass

    current_schedule = data.get("schedule")
    if current_schedule == cron_expr:
        return False

    data["schedule"] = cron_expr
    data["rationale"] = rationale
    data["last_updated"] = datetime.datetime.now().isoformat()

    with open(schedule_file, "w") as f:
        yaml.dump(data, f)

    subprocess.run(["sed", "-i", f"s/schedule: .*/schedule: '{cron_expr}' # AUTO-UPDATED/", schedule_file])
    return True

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schedule_file = os.path.join(root_dir, ".github", "self-heal-schedule.yml")

    timestamps = get_commit_timestamps()
    cron_expr = compute_cron(timestamps)
    rationale = f"Computed based on {len(timestamps)} commits in the last 30 days."

    changed = update_yaml_config(schedule_file, cron_expr, rationale)

    if changed:
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"changed=true\n")
                f.write(f"new_schedule={cron_expr}\n")
    else:
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"changed=false\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
