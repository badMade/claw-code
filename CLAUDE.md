# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Detected stack
- Languages: Rust (edition 2021).
- Binary: `claw` (the CLI entrypoint is `rust/crates/rusty-claude-cli/`).
- Workspace: `rust/Cargo.toml` defines 9 crates under `rust/crates/*`.

## Build & verification

All Rust commands must be run from the `rust/` directory.

```sh
cd rust

# Format check (must pass before commit)
cargo fmt --all --check

# Lint (treats warnings as errors in CI)
cargo clippy --workspace --all-targets -- -D warnings

# Run all tests
cargo test --workspace

# Build the binary
cargo build --release -p rusty-claude-cli
```

Run all three checks (`fmt`, `clippy`, `test`) before pushing. CI runs them for `main`, `claude/**`, and PR branches when changes match the Rust workflow's configured paths.

### Running a single crate's tests
```sh
cargo test -p runtime
cargo test -p tools
cargo test -p commands
```

## Repository shape
- `rust/` - Canonical Rust workspace with all active development.
  - `rust/crates/api/` - Provider clients, SSE streaming, request/response types.
  - `rust/crates/commands/` - Slash-command registry, help text generation.
  - `rust/crates/runtime/` - ConversationRuntime, config, permissions, MCP, session persistence.
  - `rust/crates/tools/` - Built-in tools, skill resolution, agent runtime.
  - `rust/crates/plugins/` - Plugin metadata, manager, install/enable/disable.
  - `rust/crates/rusty-claude-cli/` - Main CLI binary (`claw`).
  - `rust/crates/telemetry/` - Session tracing and usage telemetry types.
  - `rust/crates/mock-anthropic-service/` - Deterministic mock for testing.
  - `rust/crates/compat-harness/` - Extracts tool/prompt manifests from upstream TS source.
- `src/` - Python reference implementation; keep consistent with generated guidance.
- `tests/` - Validation surfaces; review alongside code changes.

## Code style & conventions
- **No unsafe code** - the workspace forbids `unsafe_code` via `[workspace.lints.rust]`.
- **Clippy pedantic** enabled workspace-wide. Allowed exceptions: `module_name_repetitions`, `missing_panics_doc`, `missing_errors_doc`.
- Prefer small, focused functions. Keep public API surfaces minimal.
- When adding a new module to a crate, re-export it from the crate's `lib.rs`.
- When changing behavior, update both `src/` and `tests/` surfaces together.

## CI / GitHub Actions
- Workflow: `.github/workflows/rust-ci.yml` runs on push to `main`, `claude/**`, `gaebal/**`, `omx-issue-*`, and PRs to `main`.
- Four parallel jobs: `doc-source-of-truth`, `fmt`, `clippy-workspace`, `test-workspace`.
- Release workflow: `.github/workflows/release.yml` builds binaries for `linux-x64` and `macos-arm64`.

## Working agreement
- Prefer small, reviewable changes.
- Keep shared defaults in `.claude.json`; reserve `.claude/settings.local.json` for machine-local overrides.
- Shared tool permissions live in `.claude/settings.json`.
- Do not overwrite existing `CLAUDE.md` content automatically; update it intentionally when repo workflows change.
- Branch naming for Claude Code sessions: `claude/<description>`.
