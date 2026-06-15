# Self-Heal Auto-Repair

This repository is equipped with an adaptive self-healing automation designed to automatically correct drift (such as linting errors, formatting inconsistencies, and minor code breakages).

## Triggers
1. **Scheduled:** Runs on an adaptive schedule based on recent PR activity.
2. **Reactive:** Runs automatically when a run on the main CI workflow fails on `main`.
3. **Manual:** Can be triggered via the `workflow_dispatch` event in the GitHub Actions UI.

## The Repair Pipeline
When triggered, `scripts/self_heal.py` performs the following idempotent steps:
1. Rebuild/Reinstall tools and dependencies.
2. Auto-fix linting and formatting issues (Python via `ruff`, Rust via `cargo fmt`/`clippy`).
3. Regenerate snapshots (if applicable).
4. Fetch missing type stubs (if applicable).
5. Re-resolve dependencies (if configured).
6. Regenerate static assets (if configured).

After each step, it runs `scripts/healthcheck.py` to see if the issue is resolved. If the healthcheck passes and there is a diff, a pull request is automatically created.

## Self-Scheduling
The schedule is not hardcoded. `scripts/compute_schedule.py` runs periodically via `.github/workflows/compute-schedule.yml`. It analyzes PR merge frequency using the `gh` CLI to assign a cadence tier (e.g., standard, active, high). If the computed schedule changes, a PR is created to update both `.github/workflows/self-heal.yml` and `.github/self-heal-schedule.yml`.

### Manual Overrides
To manually override the schedule, you can edit `.github/self-heal-schedule.yml` directly, but ensure the `# AUTO-UPDATED` marker is kept if you want the system to eventually regain control, or remove it/adjust the script if you want a permanent override.

## Reviewer Checklist for Self-Heal PRs
- [ ] Check if the changes accurately reflect intended auto-formatting/fixes.
- [ ] Ensure no application logic has been incorrectly modified.
- [ ] Verify that CI passes on the self-heal PR.
