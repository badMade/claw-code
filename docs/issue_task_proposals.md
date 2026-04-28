# Codebase issue scan: proposed fix tasks

## 1) Naming consistency task
- **Issue:** The HTTP user agent string uses `clawd-rust-tools/0.1`, while the codebase appears to use a mix of `claw*` and `clawd*` identifiers across repository/product naming, telemetry, env vars, and file prefixes.
- **Impact:** Inconsistent telemetry/log tagging and harder grep/observability across services when searching for either `claw` or `clawd` identifiers.
- **Task proposal:** Decide on the intended prefix convention for these identifiers (`claw*` vs `clawd*`), update the user-agent token to match that convention (ideally via a centrally-defined crate/version-derived user-agent constant), and update any tests that assert the old literal.
- **Acceptance criteria:** The chosen naming convention is applied consistently to the user-agent token and any related references/tests updated by this task; no behavior changes beyond identifier consistency.

## 2) Bug fix task
- **Issue:** `src.main` ignores filtering flags (e.g., `--no-plugin-commands`, `--no-skill-commands` for `commands`; `--simple-mode`, `--no-mcp`, `--deny-tool` for `tools`) when `--query ...` is used. This happens because the query paths call `render_command_index(...)` or `render_tool_index(...)` directly without applying the include/exclude filters.
- **Impact:** CLI behavior is inconsistent and user-provided filtering flags are silently ignored for query usage.
- **Task proposal:** Refactor command and tool index rendering so query and non-query paths share the same filtered source (e.g., call `get_commands(...)`/`get_tools(...)` first, then apply query search over that filtered set).
- **Acceptance criteria:** `commands --query X --no-plugin-commands` and `tools --query Y --no-mcp` produce outputs that respect each exclusion flag.

## 3) Code comment/documentation discrepancy task
- **Issue:** The lane completion module-level docs say completion is detected when "Code pushed (has output file)", but `detect_lane_completion(...)` does not inspect `output_file`; it only trusts the external boolean `has_pushed`.
- **Impact:** The inline documentation overstates what this function validates itself, which can mislead future maintainers and reviewers.
- **Task proposal:** Align docs/comments with implementation **or** update implementation to validate `output.output_file` semantics directly (and document exact source-of-truth for "pushed").
- **Acceptance criteria:** Comments/docs and runtime behavior agree on how push status is determined.

## 4) Test improvement task
- **Issue:** Snapshot-size tests in `tests/test_porting_workspace.py` use hard minimums (`>=150` commands, `>=100` tools, coverage thresholds), which are brittle for legitimate snapshot churn and can produce noisy failures.
- **Impact:** Reduced test signal quality; harmless snapshot updates can fail CI even when behavior remains correct.
- **Task proposal:** Replace absolute magic-number thresholds with invariant-based assertions (e.g., non-empty snapshots, monotonic schema checks, command/tool lookup sanity) plus a single snapshot-contract check tied to explicit version metadata.
- **Acceptance criteria:** Tests fail only on semantic regressions, not ordinary curated snapshot updates.
