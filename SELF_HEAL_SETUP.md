# Self-Heal Automation Setup

This repository has a self-heal automation workflow designed to automatically detect and fix code drift, lint issues, formatting differences, type stub requirements, and out-of-date static assets.

## Triggers
1. **Daily (Proactive):** Scheduled to run daily at 9:00 AM UTC (Mon-Fri) via cron (`0 9 * * 1-5`) to catch upstream toolchain drift.
2. **CI Failure (Reactive):** Runs automatically when the primary "Rust CI" workflow fails on the `main` branch.
3. **Manual (Dispatch):** Can be run manually from the GitHub Actions tab.

## Workflow Steps
The `scripts/self_heal.sh` script executes the following idempotent steps:
1. **Rebuild/reinstall:** Ensures all tools and dependencies are clean.
2. **Lint/format auto-fix:** Runs `ruff` and `cargo fmt` / `cargo clippy`.
3. **Snapshot/generated updates:** Regenerates snapshots if tests fail due to changes.
4. **Type stubs:** Downloads necessary missing type definitions.
5. **Dependency re-resolve:** Runs lockfile refreshes.
6. **Static asset regeneration:** Regenerates docs and badges if relevant scripts exist.

After each step, `scripts/healthcheck.sh` validates the state of the codebase. A PR is generated only if all checks pass AND there is a non-empty Git diff.

## Reviewer Checklist
When a `[Self-Heal]` PR is opened, humans should verify:
- [ ] No secrets, credentials, or API keys are accidentally committed.
- [ ] The generated diff represents expected drift (e.g., a lint rule change) rather than a regressions.
- [ ] No business logic was unintentionally modified by an auto-fix.
- [ ] The build and test suites pass completely.

## Tuning and Customization
- **Cron Tuning:** If your repo is high-velocity, consider twice daily (`0 9,21 * * *`). Modify `.github/workflows/self-heal.yml`.
- **Dependencies:** Add additional `types-*` packages or auto-fix tools to `requirements-selfheal.txt`.
