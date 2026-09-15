# Self-Heal Automation Setup

This repository contains a self-adapting repair automation system for CI failures and drift detection.

## How it works

The automation uses three triggers:
1. **Scheduled:** Runs on an adaptive schedule based on project velocity.
2. **Reactive:** Runs when the main CI workflow fails on `main`.
3. **Manual:** Can be triggered via workflow dispatch.

### Repair Steps

The `scripts/self_heal.py` script executes the following idempotent steps sequentially, checking if the drift or failure has been resolved after each step:
1. Rebuild / reinstall environment
2. Lint / format auto-fix
3. Snapshot / generated updates
4. Type stubs / analyzer config
5. Dependency re-resolve
6. Static asset regeneration

### Self-Scheduling

The schedule is dynamically calculated by `scripts/compute_schedule.py`, driven by the `.github/workflows/compute-schedule.yml` workflow.
It analyzes recent PR merge velocity to assign a cadence tier (High, Active, Standard, Low-churn) and outputs to `.github/self-heal-schedule.yml`.

### Manual Overrides

To manually override the schedule, you can edit `.github/self-heal-schedule.yml` directly. Note that the dynamic compute workflow might override it if the manual configuration doesn't match the required telemetry tier, so you may need to disable `compute-schedule.yml` if you want a permanent manual schedule.

### Reviewer Checklist

When reviewing a self-heal PR, ensure that:
- The changes strictly address the drift or CI failure.
- No business logic or tests were modified (only snapshots).
- No secrets or PII were inadvertently included in the diff.
- The PR was generated safely by the automated system without arbitrary external network calls.
