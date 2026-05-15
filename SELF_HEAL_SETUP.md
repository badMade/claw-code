# Self-Heal Automation Setup

This repository is configured with an adaptive self-healing automation system that repairs codebase drift, automatically fixes linting errors, and regenerates snapshots and assets.

## How it works

The automation runs on three triggers:
1. **Scheduled:** Proactively runs to fix drift based on an adaptive schedule.
2. **Reactive:** Triggers automatically if the `ci` workflow fails.
3. **Manual:** Can be triggered via the Actions tab.

When triggered, it runs an idempotent 6-step repair pipeline:
1. Rebuilds and reinstalls tooling.
2. Runs language-specific formatters and linters (e.g., `ruff`, `cargo fmt`).
3. Regenerates test snapshots.
4. Updates missing type stubs.
5. Re-resolves dependencies.
6. Regenerates static assets (like docs or badges).

If any step fixes failing health checks and creates a diff, a pull request is automatically opened for human review.

## Self-Scheduling Logic

The proactive scheduled cadence is not hardcoded. Instead, a weekly cron job (`.github/workflows/compute-schedule.yml`) analyzes the repository's git telemetry (e.g., commit frequency over a 30-day window). It computes an optimal schedule expression based on activity tiers:
- **High Churn:** Every 4 hours.
- **Active:** Every 8 hours.
- **Standard:** Twice a day.
- **Low Churn:** Once a day.
- **Dormant:** Once a week.

This automatically scales the self-healing frequency up when development is active, and dials it down when dormant.

## Overriding the Schedule

If you want to manually override the schedule, you can edit `.github/workflows/self-heal.yml` or `.github/self-heal-schedule.yml` directly. Be aware that the automated scheduler might override your changes in the future. To prevent that, you would need to adjust the logic in `scripts/compute_schedule.py`.

## Reviewer Checklist for Self-Heal PRs

When reviewing a PR opened by the `self-heal` automation:
- [ ] Verify the PR title clearly states the trigger (Scheduled, Reactive, or Manual).
- [ ] Ensure changes are limited to formatting, linting fixes, snapshots, dependency updates, or generated assets.
- [ ] Confirm no secrets, API keys, or `.env` files are included.
- [ ] Check the CI checks on the PR pass successfully.
- [ ] Merge only if you understand and agree with the automated changes.
