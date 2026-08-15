# Self-Heal Automation Setup

This repository has been equipped with a self-healing automation suite designed to automatically fix code formatting, run linting autofixes, and repair codebase drift without human intervention. The automation opens a pull request with the fixes for you to review.

## Architecture

The automation is split across the following key scripts:
- `scripts/healthcheck.py`: Runs formatters, linters, and tests to determine codebase health. Exits 0 on pass, 1 on fail.
- `scripts/self_heal.py`: Iterates through idempotent repair steps (reinstall, lint autofix, etc.) and tests the codebase health after each. It exits 0 only if the codebase is made healthy and there is an actual git diff.
- `scripts/compute_schedule.py`: Analyzes `git log` telemetry to dynamically calculate the best cron schedule for preventative self-healing runs based on commit cadence.

## GitHub Actions Workflows

- `.github/workflows/self-heal.yml`: The primary workflow. It is triggered via three methods:
  1. **Reactive (CI failure):** If the primary `ci` workflow fails on `main`, this workflow runs to attempt a fix.
  2. **Proactive (Scheduled):** Runs periodically on a cron schedule to fix drift over time.
  3. **Manual (Workflow Dispatch):** Can be triggered manually via the GitHub UI.

- `.github/workflows/compute-schedule.yml`: Runs periodically to recalculate the optimal schedule based on recent git commit velocity. It writes the updated schedule to `.github/self-heal-schedule.yml` and updates the cron trigger in `self-heal.yml`.

## How Self-Scheduling Works

The schedule is not hardcoded. The `compute_schedule.py` script counts commits over the past ~30 days. It groups commits by hour of the day and computes the repository's velocity:
- **High velocity (>5 PRs/day):** Runs every 4 hours.
- **Active velocity (>2 PRs/day):** Runs every 8 hours.
- **Standard velocity (>0.5 PRs/day):** Runs once a day at the quietest hour.
- **Low churn/Dormant:** Runs once a week at the quietest hour.

If the schedule changes, `compute-schedule.yml` opens a PR to apply the update.

## Manual Overrides

If you want to pin a specific schedule and prevent auto-updates, you can modify `.github/self-heal-schedule.yml` directly. Be aware that the `compute-schedule` workflow might attempt to change it back unless you disable that workflow.

## Reviewer Checklist

When reviewing a PR from the `github-actions[bot]` with the `self-heal` label, check the following:
- Ensure the fix doesn't silently remove intended logical changes.
- Verify tests pass.
- For dependency bumps (if enabled in step 5), ensure no breaking changes were pulled in accidentally.
