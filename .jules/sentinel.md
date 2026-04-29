# Sentinel Journal
## 2025-04-13 - [Sentinel] Prevented Path Traversal in Session IDs
**Vulnerability:** Path traversal in session file loading. User-provided session IDs were read directly from disk without sanitization in both Python (`load_session` in `src/session_store.py`) and Rust (`resolve_managed_session_path_for` and related functions in `rust/crates/runtime/src/session_control.rs`), allowing attackers to specify identifiers like `../../../../tmp/file` to read or overwrite arbitrary JSON files on the system under the disguise of a session file.
**Learning:** External session IDs must be considered untrusted user input, even when used internally as filenames, since the application dynamically builds file paths using `f'{session_id}.json'` (Python) or `format!("{id}.{extension}")` (Rust).
**Prevention:** Implemented a centralized `validate_session_id` function in both Python and Rust that strictly forbids path separators (`/`, `\`) and specific filesystem traversal segments (`.`, `..`). This validation is now applied uniformly wherever session IDs are handled before converting them into file paths.

## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.
