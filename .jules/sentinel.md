## 2024-04-10 - Path Traversal in Session Storage
**Vulnerability:** Path traversal existed in both the Python (`src/session_store.py`) and Rust (`rust/crates/runtime/src/session_control.rs`) implementations because unsanitized `session_id` strings were used directly in file paths.
**Learning:** Both reference implementations lacked central validation logic for system identifiers derived from external/user input.
**Prevention:** Always validate and restrict identifier parameters (like session IDs) by checking for explicit disallow-lists (like path separators `/`, `\`, and directory traversal markers `.`, `..`) before using them in file operations.
