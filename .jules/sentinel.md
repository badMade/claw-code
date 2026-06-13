## 2025-04-11 - Path Traversal Vulnerability in Session IDs
**Vulnerability:** The Python `src/session_store.py` and Rust `rust/crates/runtime/src/session_control.rs` allow path traversal (e.g. `../` or `/`) via the `session_id` property when saving and loading sessions.
**Learning:** This exposes a critical vulnerability where an attacker controlling the `session_id` can write or read arbitrary `.json` / `.jsonl` files on the filesystem. The session identifiers must be strictly validated to exclude path separators ('/', '\') and special segments ('.', '..') to mitigate path traversal vulnerabilities.
**Prevention:** Explicitly validate input IDs to ensure they only contain safe characters (e.g., alphanumeric, hyphens, underscores) or strictly reject path separators and directory traversal sequences.

## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.
