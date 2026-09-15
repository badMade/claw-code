#!/usr/bin/env python3
"""
Computes the dynamic schedule for self-healing runs based on PR telemetry.
Writes the computed schedule back to `.github/self-heal-schedule.yml` using `ruamel.yaml` to preserve structure.
"""
import os
import sys
import subprocess
import datetime
import json
try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml is required. Please install it.")
    sys.exit(1)

SCHEDULE_FILE = ".github/self-heal-schedule.yml"

def get_pr_telemetry():
    """Returns number of merged PRs in the last 7 days."""
    try:
        # Assuming gh cli is configured and available
        result = subprocess.run(
            "gh pr list --state merged --json mergedAt --limit 100",
            shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            return 0 # Fallback

        prs = json.loads(result.stdout)
        now = datetime.datetime.now(datetime.timezone.utc)
        recent_prs = 0
        for pr in prs:
            merged_at_str = pr.get('mergedAt')
            if not merged_at_str:
                continue
            merged_at = datetime.datetime.fromisoformat(merged_at_str.replace('Z', '+00:00'))
            if (now - merged_at).days <= 7:
                recent_prs += 1
        return recent_prs
    except Exception:
        return 0

def get_empty_run_count():
    """
    Dummy telemetry for empty run count.
    In reality, we'd query GH API for recent self-heal PR runs.
    """
    return 0

def compute_schedule(merged_prs, empty_runs=0):
    """
    Computes a cron schedule based on telemetry.
    Tier logic:
      High (>10 PRs/wk) -> Every 4 hours
      Active (5-10 PRs/wk) -> Every 8 hours
      Standard (2-4 PRs/wk) -> Every 12 hours
      Low-churn (<2 PRs/wk) -> Daily
    """
    tier_idx = 0
    tiers = [
        ("0 0 * * *", "Low-churn velocity (<2/wk)"),
        ("0 */12 * * *", "Standard PR velocity (2-4/wk)"),
        ("0 */8 * * *", "Active PR velocity (5-10/wk)"),
        ("0 */4 * * *", "High PR velocity (>10/wk)")
    ]

    if merged_prs > 10:
        tier_idx = 3
    elif merged_prs >= 5:
        tier_idx = 2
    elif merged_prs >= 2:
        tier_idx = 1
    else:
        tier_idx = 0

    if empty_runs >= 3:
        tier_idx = max(0, tier_idx - 1)
        return tiers[tier_idx][0], tiers[tier_idx][1] + " (downgraded due to empty runs)"

    return tiers[tier_idx]

def update_schedule_file(new_cron, rationale):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    if not os.path.exists(SCHEDULE_FILE):
        data = {
            "schedule": new_cron,
            "rationale": rationale,
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        with open(SCHEDULE_FILE, 'w') as f:
            yaml.dump(data, f)
            f.write("# AUTO-UPDATED\n")
        return True

    with open(SCHEDULE_FILE, 'r') as f:
        data = yaml.load(f)

    # Oscillation guard: skip if updated within the last 3 days and schedule changed
    last_updated_str = data.get('last_updated')
    if last_updated_str:
        try:
            last_updated = datetime.datetime.fromisoformat(last_updated_str)
            if (datetime.datetime.now(datetime.timezone.utc) - last_updated).days < 3:
                print("Schedule updated recently. Skipping to prevent oscillation.")
                return False
        except ValueError:
            pass

    if data.get('schedule') == new_cron:
        return False

    data['schedule'] = new_cron
    data['rationale'] = rationale
    data['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(SCHEDULE_FILE, 'w') as f:
        yaml.dump(data, f)
        f.write("# AUTO-UPDATED\n")
    return True

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    prs = get_pr_telemetry()
    empty_runs = get_empty_run_count()
    new_cron, rationale = compute_schedule(prs, empty_runs)

    print(f"Computed schedule: {new_cron} (Reason: {rationale})")

    updated = update_schedule_file(new_cron, rationale)
    if updated:
        print("Schedule file updated.")
    else:
        print("Schedule file unchanged.")

if __name__ == "__main__":
    main()
